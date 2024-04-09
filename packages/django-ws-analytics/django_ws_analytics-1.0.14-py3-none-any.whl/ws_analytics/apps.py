from django.apps import AppConfig
from django.conf import settings
from django.core.checks import register, Error


def _init_settings():
    from django.conf import settings
    from ws_analytics.settings import get_config
    setattr(settings, "SESSION_ENGINE", "ws_analytics.sessions")
    setattr(settings, "SESSION_COOKIE_NAME", get_config()["SESSION_COOKIE_NAME"])
    setattr(settings, "SESSION_COOKIE_AGE", get_config()["SESSION_COOKIE_AGE"])
    setattr(settings, "SESSION_SAVE_EVERY_REQUEST", get_config()["SESSION_SAVE_EVERY_REQUEST"])
    setattr(settings, "GEOIP_PATH", get_config()["GEOIP_PATH"])


class WsAnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ws_analytics'

    def ready(self):
        _init_settings()


@register()
def check_gis_database_configured(app_configs, **kwargs):
    errors = []
    # Überprüfen, ob 'ENGINE' der Datenbankkonfiguration 'django.contrib.gis.db.backends' enthält
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'django.contrib.gis.db.backends' not in db_engine:
        errors.append(
            Error(
                'GIS database is not configured.',
                hint='Ensure that the database configuration uses a GIS database.',
                id='ws_analytics.W001',
            )
        )
    return errors
