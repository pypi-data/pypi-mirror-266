django-ws-analytics
====================

**django-ws-analytics** offers a novel approach to user tracking within Django applications, circumventing the need for cookies by leveraging request metadata. This package computes a unique hash value for each user, derived from their IP, device type, browser, and system specifications, enabling seamless user identification and analytics.

Key Features
------------

- **Cookie-less Tracking**: Utilize request metadata for user identification, offering privacy-compliant tracking.

- **Customizable Tracking**: Adjust tracking parameters and configurations to match specific analytics needs.

- **GeoIP Integration**: Leverage MaxMind's GeoIP databases for enriched location data and insights.

- **Extensible Example**: A fully functional Django example project to demonstrate setup and usage.

Getting Started
---------------

Prerequisites
--------------

- A MaxMind account for GeoIP databases. `Sign up here <https://www.maxmind.com/en/home>`_.

Installation
------------

Install `django-ws-analytics` using pip:

.. code-block:: bash

    pip install django-ws-analytics
    python manage.py migrate

Django Project Configuration
----------------------------

To fully integrate `django-ws-analytics` into your Django project, make the following adjustments in your `settings.py`:

1. **Database Engine**: It's crucial to use PostGIS as your database engine for the analytics to function correctly:

.. code-block:: python

    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ.get('POSTGRES_DB', 'ws_analytics'),
            'USER': os.environ.get('POSTGRES_USER', 'ws_analytics'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'ws_analytics'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }

2. **Middleware, Installed Apps, and Analytics Configuration**: Ensure the required middleware and apps are included, and configure the analytics behavior:

.. code-block:: python

    MIDDLEWARE = [
        ...
        'django.contrib.sessions.middleware.SessionMiddleware',
        'ws_analytics.middleware.AnalyticsMiddleware',
        ...
    ]

    INSTALLED_APPS = [
        ...
        'django.contrib.sessions',
        'django.contrib.gis',
        'django_user_agents',
        'ws_analytics',
        ...
    ]

    WS_ANALYTICS_CONFIG = {
        'SESSION_COOKIE_AGE': 30 * 60,  # Session ID expiration (default: 30 minutes)
        'SESSION_COOKIE_NAME': '_sid',
        'DEVICE_COOKIE_AGE': 60 * 60 * 24 * 365,  # Device ID expiration (default: 1 year)
        'DEVICE_COOKIE_NAME': '_did',
        'LOGGABLE_VIEW_NAMES': ['home'],  # Specify view names for tracking
        'SESSION_SAVE_EVERY_REQUEST': False,
        'GEOIP_PATH': os.environ.get('GEOIP_PATH', 'GeoIP2-City.mmdb'),
    }

3. **GeoIP Library Paths**: Specify the paths for GDAL and GEOS libraries if they're not automatically detected:

.. code-block:: python

    GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')
    GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
