import uuid

from django.contrib.gis.db import models
from django.contrib.sessions.base_session import AbstractBaseSession
from django.contrib.sessions.models import Session
from django.utils.translation import gettext_lazy as _

from ws_analytics.sessions import SessionStore, DeviceStore


# Create your models here.
class AnalyticsRequest(models.Model):
    request_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    method = models.CharField(max_length=10, editable=False)
    path = models.CharField(max_length=1000, editable=False)
    http_referer = models.URLField(max_length=2000, editable=False)
    query_params = models.JSONField(editable=False)
    status_code = models.PositiveSmallIntegerField(editable=False)
    execution_time = models.FloatField(editable=False)
    location = models.JSONField(null=True, blank=True, editable=False)
    session = models.ForeignKey("AnalyticsSession", on_delete=models.SET_NULL, null=True, blank=True, editable=False)

    timestamp = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _("request")
        verbose_name_plural = _("requests")

    @property
    def city(self):
        return self.location['city']

    @property
    def country(self):
        return self.location['country_name']


class AnalyticsDevice(AbstractBaseSession):
    PC = 'pc'
    MOBILE = 'mobile'
    TABLET = 'tablet'
    BOT = 'bot'
    UNKNOWN = 'unknown'
    DEVICE_TYPE = (
        (PC, 'PC'),
        (MOBILE, 'Mobile'),
        (TABLET, 'Tablet'),
        (BOT, 'Bot'),
        (UNKNOWN, 'Unknown'),
    )
    fingerprint = models.CharField(max_length=32, null=True, blank=True, unique=True, db_index=True)
    device_type = models.CharField(
        max_length=10,
        choices=DEVICE_TYPE,
        default=UNKNOWN
    )
    device = models.CharField(max_length=30, blank=True)
    browser = models.CharField(max_length=30, blank=True)
    browser_version = models.CharField(max_length=30, blank=True)
    system = models.CharField(max_length=30, blank=True)
    system_version = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")

    @classmethod
    def get_session_store_class(cls):
        return DeviceStore


class AnalyticsSession(AbstractBaseSession):
    device = models.ForeignKey(AnalyticsDevice, on_delete=models.CASCADE, related_name='sessions', null=True,
                               blank=True)

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")
        ordering = ('-expire_date',)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore
