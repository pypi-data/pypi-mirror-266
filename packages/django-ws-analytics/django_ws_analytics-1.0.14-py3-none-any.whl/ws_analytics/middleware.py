import logging
import time
import uuid
from importlib import import_module

from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.contrib.sessions.exceptions import SessionInterrupted
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import resolve
from django.utils import timezone
from django.utils.cache import patch_vary_headers
from django.utils.functional import SimpleLazyObject
from django.utils.http import http_date
from django_q.tasks import async_task
from django_user_agents.utils import get_user_agent

from ws_analytics.models import AnalyticsDevice
from ws_analytics.services import get_device_data, create_analytics_request
from ws_analytics.settings import get_config

logger = logging.getLogger('ws_analytics')


class AnalyticsMiddleware(SessionMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.start_time = None
        self.loggable_view_names = get_config()['LOGGABLE_VIEW_NAMES']
        self.DEVICE_COOKIE_NAME = get_config()['DEVICE_COOKIE_NAME']

        engine = import_module(settings.SESSION_ENGINE)
        self.DeviceStore = engine.DeviceStore
        self.SessionStore = engine.SessionStore

    def process_request_device(self, request):
        device_key = request.COOKIES.get(self.DEVICE_COOKIE_NAME)
        if device_key and AnalyticsDevice.objects.filter(session_key=device_key).exists():
            request.device = self.DeviceStore(device_key)
        else:
            device_data = get_device_data(request)
            try:
                analytics_device = AnalyticsDevice.objects.get(fingerprint=device_data['fingerprint'])
                request.device = self.DeviceStore(analytics_device.session_key)

                last_device_session = analytics_device.sessions.filter(expire_date__gt=timezone.now()).order_by(
                    '-expire_date').first()
                if last_device_session:
                    last_session_key = last_device_session.session_key
                    request.session = self.SessionStore(last_session_key)
                    request.session.modified = True
            except AnalyticsDevice.DoesNotExist:
                request.device = self.DeviceStore()
                for key, val in device_data.items():
                    request.device[f"_{key}"] = val
                request.device.save()
            request.device.modified = True

    def process_request_analytics(self, request):
        self.start_time = time.time()
        request.request_id = uuid.uuid4()

        if not request.session.session_key:
            request.session['_device_key'] = request.device.session_key
            request.session.modified = True
            request.session.save()

    def process_response_device(self, request, response):

        try:
            accessed = request.device.accessed
            modified = request.device.modified
            empty = request.device.is_empty()

            if self.DEVICE_COOKIE_NAME in request.COOKIES and empty:
                response.delete_cookie(
                    self.DEVICE_COOKIE_NAME,
                    path=settings.SESSION_COOKIE_PATH,
                    domain=settings.SESSION_COOKIE_DOMAIN,
                    samesite=settings.SESSION_COOKIE_SAMESITE,
                )
                patch_vary_headers(response, ("Cookie",))
            else:
                if accessed:
                    patch_vary_headers(response, ("Cookie",))
                if (modified or settings.SESSION_SAVE_EVERY_REQUEST) and not empty:
                    max_age = request.device.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = http_date(expires_time)
                    # Save the device data and refresh the client cookie.
                    # Skip device save for 5xx responses.
                    if response.status_code < 500:
                        try:
                            request.device.save()
                        except UpdateError:
                            raise SessionInterrupted(
                                "The request's decive was deleted before the "
                                "request completed."
                            )
                        response.set_cookie(
                            self.DEVICE_COOKIE_NAME,
                            request.device.session_key,
                            max_age=max_age,
                            expires=expires,
                            domain=settings.SESSION_COOKIE_DOMAIN,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                            samesite=settings.SESSION_COOKIE_SAMESITE,
                        )
        except Exception as e:
            logger.warning(str(e))

        return response

    def process_response_analytics(self, request, response):
        try:
            end_time = time.time()
            execution_time = end_time - self.start_time

            client_ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0].strip() if request.META.get(
                'HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')

            analytics_data = {
                'request_id': request.request_id,
                'method': request.method,
                'path': request.path,
                'http_referer': request.META.get('HTTP_REFERER', ''),
                'query_params': request.GET.dict(),
                'status_code': response.status_code,
                'execution_time': execution_time,
                'client_ip': client_ip,
                'session_id': request.session.session_key
            }
            async_task(create_analytics_request, **analytics_data)
        except Exception as e:
            logger.warning(str(e))

        return response

    def process_request(self, request):
        request.user_agent = SimpleLazyObject(lambda: get_user_agent(request))
        self.process_request_device(request)
        self.process_request_analytics(request)

    def process_response(self, request, response):
        response = self.process_response_device(request, response)
        response = self.process_response_analytics(request, response)

        return response

    def __call__(self, request):
        try:
            resolved_view = resolve(request.path)
            view_name = resolved_view.view_name
            if view_name in self.loggable_view_names:
                return super().__call__(request)
        except Exception as e:
            logger.warning(str(e))

        response = self.get_response(request)
        return response
