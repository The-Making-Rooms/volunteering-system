"""
VolunteeringSystem

This project is distributed under the CC BY-NC-SA 4.0 license. See LICENSE for details.

Django settings for volunteeringSystem project.

"""

from pathlib import Path
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/


# SECURITY WARNING: keep the secret key used in production secret!

# SECURITY WARNING: don't run with debug turned on in production!

ALLOWED_HOSTS = ['127.0.0.1', 'volunteerapp.makingrooms.org', 'chipinbwd.co.uk', 'chipinbwd.co.uk']
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.gmail.com'
EMAIL_PORT = 25
EMAIL_USE_TLS = True
DATA_UPLOAD_MAX_NUMBER_FILES = 10
# Application definition

if os.environ.get('DJANGO_ENV') == 'production':
    SECRET_KEY = os.environ.get('SECRET_KEY')
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    #EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
    NOUN_PROJECT_API_KEY = os.environ.get('NOUN_PROJECT_API_KEY')
    NOUN_PROJECT_SECRET_KEY = os.environ.get('NOUN_PROJECT_SECRET_KEY')
    WEBPUSH_SETTINGS = {
        "VAPID_PUBLIC_KEY": os.environ.get('VAPID_PUBLIC_KEY'), #Update in nav_template
        "VAPID_PRIVATE_KEY": os.environ.get('VAPID_PRIVATE_KEY'),
        "VAPID_ADMIN_EMAIL": os.environ.get('VAPID_ADMIN_EMAIL')
    }
    DEBUG = False
    
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': 'localhost',
            'PORT': '',
        }
    }

    
    
else:
    SECRET_KEY = 'django-insecure-rd6@o^$_u7tniw&^#dg-0vr88$*r^b^4%3fkyr6c@r_i5^g!s8'
    EMAIL_HOST_USER = 'no-reply@chipinbwd.co.uk'
    DEFAULT_FROM_EMAIL = 'no-reply@chipinbwd.co.uk'
    #EMAIL_HOST_PASSWORD = 'whrk uszz eebt mjvx'
    NOUN_PROJECT_API_KEY = "a5f9c58009584357b678c737e8cb871f"
    NOUN_PROJECT_SECRET_KEY = "7c76f3fa935445669bf4f2b8ac906d90"
    WEBPUSH_SETTINGS = {
        "VAPID_PUBLIC_KEY": "BNRVbyR3auCqhbrnRcQcBXiAdDoP_-wVe16VMCpSaXJ9TN1PqbtwRQXOnHoDmg013wiFotc5y8hHWl3Bn4YcwE0", #Update in nav_template
        "VAPID_PRIVATE_KEY":"kO5i2K4COSjMISdogh4C7NQuf91NSi5Gpwnp4m8h7C4",
        "VAPID_ADMIN_EMAIL": "info@makingrooms.org"
    }
    DEBUG = True


    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


INSTALLED_APPS = [
    "django.contrib.admin",  # required
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'recurrence',
    'organisations',
    'volunteer',
    'forms',
    'explore',
    'opportunities',
    'commonui',
    'volunteeringSystem',
    'compressor',
     "django_extensions",
     'pwa',
     'org_admin', 
     'webpush',
     'communications',
     
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

RECURRENCE_USE_TZ = False
USE_TZ = False

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',  # <-- And here
        
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ROOT_URLCONF = 'volunteeringSystem.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'volunteeringSystem.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases



# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static/'

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


COMPRESS_ROOT = BASE_DIR / 'static'
COMPRESS_ENABLED = True
STATICFILES_FINDERS = ('compressor.finders.CompressorFinder',)

PWA_SERVICE_WORKER_PATH = BASE_DIR / 'static' / 'js' / 'sw.js'
CSRF_TRUSTED_ORIGINS = ['http://volunteerapp.makingrooms.org', 'https://chipinbwd.co.uk']
PWA_APP_NAME = 'Chip In'
PWA_APP_DESCRIPTION = "Find Volunteering Opportunities in your area!"
PWA_APP_THEME_COLOR = '#0A0302'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
      "src": "static/images/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png"
    },
    {
      "src": "static/images/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/images/my_apple_icon.png',
        'sizes': '160x160'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/images/icons/splash-640x1136.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'en-US'
PWA_APP_SHORTCUTS = [
    {
        'name': 'Shortcut',
        'url': '/target',
        'description': 'Shortcut to a page in my application'
    }
]
PWA_APP_SCREENSHOTS = [
    {
      'src': '/static/images/icons/splash-750x1334.png',
      'sizes': '750x1334',
      "type": "image/png"
    }
]

