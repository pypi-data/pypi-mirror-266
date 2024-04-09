import os
from functools import lru_cache

from django.conf import settings

CONFIG_DEFAULTS = {
    'SESSION_COOKIE_AGE': 30*60,
    'SESSION_COOKIE_NAME': '_sid',
    'DEVICE_COOKIE_AGE': 60 * 60 * 24 * 7 * 52,
    'DEVICE_COOKIE_NAME': '_did',
    'LOGGABLE_VIEW_NAMES': [],
    'SESSION_SAVE_EVERY_REQUEST': False,
    'GEOIP_PATH': os.environ.get('GEOIP_PATH', 'GeoIP2-City.mmdb'),
}


@lru_cache(maxsize=None)
def get_config():
    USER_CONFIG = getattr(settings, 'WS_ANALYTICS_CONFIG', {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG
