from django.contrib.sessions.backends.db import SessionStore as DBStore

from ws_analytics.settings import get_config


class SessionStore(DBStore):
    def __init__(self, session_key=None):
        super().__init__(session_key)

    @classmethod
    def get_model_class(cls):
        from ws_analytics.models import AnalyticsSession
        return AnalyticsSession

    def create_model_instance(self, data):
        obj = super().create_model_instance(data)
        try:
            device_id = data.get("_device_key")
        except (ValueError, TypeError):
            device_id = None
        obj.device_id = device_id
        return obj


class DeviceStore(DBStore):

    def __init__(self, session_key=None):
        super().__init__(session_key)
        self.DEVICE_COOKIE_AGE = get_config()['DEVICE_COOKIE_AGE']
        self.DEVICE_COOKIE_NAME = get_config()['DEVICE_COOKIE_NAME']

    @classmethod
    def get_model_class(cls):
        from ws_analytics.models import AnalyticsDevice
        return AnalyticsDevice

    def create_model_instance(self, data):
        obj = super().create_model_instance(data)
        try:
            fingerprint = data.get("_fingerprint")
            device_type = data.get("_device_type")
            device = data.get("_device")
            browser = data.get("_browser")
            browser_version = data.get("_browser_version")
            system = data.get("_system")
            system_version = data.get("_system_version")
        except (ValueError, TypeError):
            fingerprint = None
            device_type = None
            device = None
            browser = None
            browser_version = None
            system = None
            system_version = None
        obj.fingerprint = fingerprint
        obj.device_type = device_type
        obj.device = device
        obj.browser = browser
        obj.browser_version = browser_version
        obj.system = system
        obj.system_version = system_version
        return obj

    def get_session_cookie_age(self):
        return self.DEVICE_COOKIE_AGE

    @property
    def fingerprint(self):
        try:
            return self._session['_fingerprint']
        except KeyError:
            return None
