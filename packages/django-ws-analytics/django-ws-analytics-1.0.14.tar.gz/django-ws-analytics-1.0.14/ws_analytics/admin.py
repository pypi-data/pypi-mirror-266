from django.contrib import admin

from ws_analytics.models import AnalyticsRequest, AnalyticsDevice, AnalyticsSession


# Register your models here.
@admin.register(AnalyticsRequest)
class AnalyticsRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_id', 'method', 'path', 'query_params', 'status_code', 'execution_time', 'http_referer', 'city',
        'country',
        'timestamp')
    readonly_fields = (
        'request_id', 'method', 'path', 'query_params', 'status_code', 'execution_time', 'http_referer', 'location',
        'session', 'timestamp')


@admin.register(AnalyticsDevice)
class AnalyticsDeviceAdmin(admin.ModelAdmin):
    list_display = (
    'session_key', 'fingerprint', 'device_type', 'device', 'browser', 'browser_version', 'system', 'system_version',
    'expire_date')


@admin.register(AnalyticsSession)
class AnalyticsSessionAdmin(admin.ModelAdmin):
    list_display = ('session_key', 'device', 'expire_date')
