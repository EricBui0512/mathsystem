# Django settings for Mathsystem project.

import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS
DAJAXICE_MEDIA_PREFIX="dajaxice"


# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES = { 'default' : dj_database_url.config()}


#online database
if 'VCAP_SERVICES' in os.environ:
	import json
	vcap_services = json.loads(os.environ['VCAP_SERVICES'])
	psql_srv = vcap_services['postgresql-9.3'][0]
	cred = psql_srv['credentials']
	
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
			'NAME': cred['name'],                      # Or path to database file if using sqlite3.
			'USER': cred['user'],                      # Not used with sqlite3.
			'PASSWORD': cred['password'],                  # Not used with sqlite3.
			'HOST': cred['hostname'],                      # Set to empty string for localhost. Not used with sqlite3.
			'PORT': cred['port'],                      # Set to empty string for default. Not used with sqlite3.
		}
	}
else:
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
			"NAME": "mathsystem",
			"USER": "postgres",
			"PASSWORD": "buivantuong1991",
			"HOST": "localhost",
			"PORT": "5432",
		}
	}


	
	
	
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/


#BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	#os.path.join(BASE_DIR, 'resource/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

#STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'




# Make this unique, and don't share it with anybody.
SECRET_KEY = 'p!%rp5#5k1!_8c81v&9_n@o!0upj9=kji6b+iifplynu0^@=pk'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'wsgi.application'

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.path.join(os.path.dirname(__file__),'Templates').replace('\\','/')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
	'DBManagement',
	'resource',
	'dajaxice',
	'storages',
	'boto',
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
			'filters': [],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# # Allow all host hosts/domain names for this site
ALLOWED_HOSTS = ['*']



# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

#Storage on S3 settings are stored as os.environs to keep settings.py clean
if not DEBUG:
   AWS_STORAGE_BUCKET_NAME = os.environ['mathsystem']
   AWS_ACCESS_KEY_ID = os.environ['AKIAIGOZ6EAD65JR7VOA']
   AWS_SECRET_ACCESS_KEY = os.environ['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']
   STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
   S3_URL = 'http://%s.s3.amazonaws.com/' % mathsystem
   STATIC_URL = S3_URL

