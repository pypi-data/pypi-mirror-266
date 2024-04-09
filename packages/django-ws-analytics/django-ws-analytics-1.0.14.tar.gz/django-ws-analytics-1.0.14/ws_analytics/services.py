import hashlib
import json
import logging
from functools import lru_cache

from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from geoip2.errors import AddressNotFoundError

from ws_analytics.models import AnalyticsDevice, AnalyticsRequest

logger = logging.getLogger('ws_analytics')


class DeviceData(object):
    ip: str
    device_type: str
    device: str
    browser: str
    browser_version: str
    system: str
    system_version: str

    def __init__(self, ip: str, device_type: str, device: str, browser: str, browser_version: str, system: str,
                 system_version: str):
        self.ip = ip
        self.device_type = device_type
        self.device = device
        self.browser = browser
        self.browser_version = browser_version
        self.system = system
        self.system_version = system_version

    def __dict__(self) -> dict:
        return {
            'ip': self.ip,
            'device_type': self.device_type,
            'device': self.device,
            'browser': self.browser,
            'browser_version': self.browser_version,
            'system': self.system,
            'system_version': self.system_version
        }


@lru_cache
def get_point_for_ip(ip_address: str):
    logger.debug("get_point_for_ip for ip_address.")
    try:
        g = GeoIP2(path=settings.GEOIP_PATH)
        return g.geos(ip_address)
    except AddressNotFoundError as e:
        logger.warning(f"Geo Point for IP not found: {e}")
        return None


@lru_cache
def get_city_for_geoip(ip_address: str):
    logger.debug("get_city_for_geoip for ip_address.")
    try:
        g = GeoIP2(path=settings.GEOIP_PATH)
        return g.city(ip_address)
    except AddressNotFoundError as e:
        logger.warning(f"City for IP not found: {e}")
        return None


@lru_cache
def generate_device_key(*args, **kwargs):
    logger.debug("generate_device_key for request.")
    sorted_data = json.dumps(kwargs, sort_keys=True)

    md5_hash = hashlib.md5()
    md5_hash.update(sorted_data.encode('utf-8'))

    return md5_hash.hexdigest()[:32]


def get_device_data(request):
    logger.debug("get_device_data for request.")
    if request.user_agent.is_mobile:
        device_type = AnalyticsDevice.MOBILE
    elif request.user_agent.is_tablet:
        device_type = AnalyticsDevice.TABLET
    elif request.user_agent.is_pc:
        device_type = AnalyticsDevice.PC
    elif request.user_agent.is_bot:
        device_type = AnalyticsDevice.BOT
    else:
        device_type = AnalyticsDevice.UNKNOWN

    client_ip = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0].strip() if request.META.get(
        'HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')
    device_data = DeviceData(
        ip=client_ip,
        device_type=device_type,
        device=request.user_agent.device.family,
        browser=request.user_agent.browser.family[:30],
        browser_version=request.user_agent.browser.version_string,
        system=request.user_agent.os.family,
        system_version=request.user_agent.os.version_string
    )

    device_data_dict = device_data.__dict__()
    device_key = generate_device_key(**device_data_dict)
    del device_data_dict['ip']
    device_data_dict.update({'fingerprint': device_key})

    return device_data_dict


def create_analytics_request(*args, **kwargs):
    client_ip = kwargs.pop('client_ip')
    analytics_data = kwargs.copy()
    client_location = get_city_for_geoip(client_ip)
    analytics_data['location'] = client_location

    AnalyticsRequest.objects.create(**analytics_data)