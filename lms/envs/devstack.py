"""
Specific overrides to the base prod settings to make development easier.
"""
from os.path import abspath, dirname, join
SECRET_KEY = '85920908f28904ed733fe576320db18cabd7b6cd'
from .aws import *  # pylint: disable=wildcard-import, unused-wildcard-import

# Don't use S3 in devstack, fall back to filesystem
del DEFAULT_FILE_STORAGE
MEDIA_ROOT = "/edx/var/edxapp/uploads"


DEBUG = True
USE_I18N = True
DEFAULT_TEMPLATE_ENGINE['OPTIONS']['debug'] = True
SITE_NAME = 'localhost:8000'
PLATFORM_NAME = ENV_TOKENS.get('PLATFORM_NAME', 'Devstack')
# By default don't use a worker, execute tasks as if they were local functions
CELERY_ALWAYS_EAGER = True
HTTPS = 'off'

LMS_ROOT_URL = 'http://localhost:8000'

################################ LOGGERS ######################################

# Silence noisy logs
import logging
LOG_OVERRIDES = [
    ('track.contexts', logging.CRITICAL),
    ('track.middleware', logging.CRITICAL),
    ('dd.dogapi', logging.CRITICAL),
    ('django_comment_client.utils', logging.CRITICAL),
]
for log_name, log_level in LOG_OVERRIDES:
    logging.getLogger(log_name).setLevel(log_level)


################################ EMAIL ########################################

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

########################## ANALYTICS TESTING ########################

ANALYTICS_SERVER_URL = "http://127.0.0.1:9000/"
ANALYTICS_API_KEY = ""

# Set this to the dashboard URL in order to display the link from the
# dashboard to the Analytics Dashboard.
ANALYTICS_DASHBOARD_URL = None

############################ PYFS XBLOCKS SERVICE #############################
# Set configuration for Django pyfilesystem

DJFS = {
    'type': 'osfs',
    'directory_root': 'lms/static/djpyfs',
    'url_root': '/static/djpyfs',
}

################################ DEBUG TOOLBAR ################################

INSTALLED_APPS += ('debug_toolbar', 'debug_toolbar_mongo')
MIDDLEWARE_CLASSES += (
    'django_comment_client.utils.QueryCountDebugMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar_mongo.panel.MongoDebugPanel',
    # ProfilingPanel has been intentionally removed for default devstack.py
    # runtimes for performance reasons. If you wish to re-enable it in your
    # local development environment, please create a new settings file
    # that imports and extends devstack.py.
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': 'lms.envs.devstack.should_show_debug_toolbar'
}


def should_show_debug_toolbar(_):
    return True  # We always want the toolbar on devstack regardless of IP, auth, etc.


########################### PIPELINE #################################

PIPELINE_ENABLED = False
STATICFILES_STORAGE = 'openedx.core.storage.DevelopmentStorage'

# Revert to the default set of finders as we don't want the production pipeline
STATICFILES_FINDERS = [
    'openedx.core.djangoapps.theming.finders.ThemeFilesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Disable JavaScript compression in development
PIPELINE_JS_COMPRESSOR = None

# Whether to run django-require in debug mode.
REQUIRE_DEBUG = DEBUG

PIPELINE_SASS_ARGUMENTS = '--debug-info'

########################### VERIFIED CERTIFICATES #################################

FEATURES['AUTOMATIC_VERIFY_STUDENT_IDENTITY_FOR_TESTING'] = True
FEATURES['ENABLE_PAYMENT_FAKE'] = True

CC_PROCESSOR_NAME = 'CyberSource2'
CC_PROCESSOR = {
    'CyberSource2': {
        "PURCHASE_ENDPOINT": '/shoppingcart/payment_fake/',
        "SECRET_KEY": 'abcd123',
        "ACCESS_KEY": 'abcd123',
        "PROFILE_ID": 'edx',
    }
}

########################### External REST APIs #################################
FEATURES['ENABLE_OAUTH2_PROVIDER'] = True
OAUTH_OIDC_ISSUER = 'http://127.0.0.1:8000/oauth2'
FEATURES['ENABLE_MOBILE_REST_API'] = True
FEATURES['ENABLE_VIDEO_ABSTRACTION_LAYER_API'] = True

########################## SECURITY #######################
FEATURES['ENFORCE_PASSWORD_POLICY'] = False
FEATURES['ENABLE_MAX_FAILED_LOGIN_ATTEMPTS'] = False
FEATURES['SQUELCH_PII_IN_LOGS'] = False
FEATURES['PREVENT_CONCURRENT_LOGINS'] = False
FEATURES['ADVANCED_SECURITY'] = False
PASSWORD_MIN_LENGTH = None
PASSWORD_COMPLEXITY = {}


########################### Milestones #################################
FEATURES['MILESTONES_APP'] = True

########################### Milestones #################################
FEATURES['ORGANIZATIONS_APP'] = True

########################### Entrance Exams #################################
FEATURES['ENTRANCE_EXAMS'] = True

################################ COURSE LICENSES ################################
FEATURES['LICENSING'] = True


########################## Courseware Search #######################
FEATURES['ENABLE_COURSEWARE_SEARCH'] = True
SEARCH_ENGINE = "search.elastic.ElasticSearchEngine"


########################## Dashboard Search #######################
FEATURES['ENABLE_DASHBOARD_SEARCH'] = True


########################## Certificates Web/HTML View #######################
FEATURES['CERTIFICATES_HTML_VIEW'] = True


########################## Course Discovery #######################
LANGUAGE_MAP = {'terms': {lang: display for lang, display in ALL_LANGUAGES}, 'name': 'Language'}
COURSE_DISCOVERY_MEANINGS = {
    'org': {
        'name': 'Organization',
    },
    'modes': {
        'name': 'Course Type',
        'terms': {
            'honor': 'Honor',
            'verified': 'Verified',
        },
    },
    'language': LANGUAGE_MAP,
}

FEATURES['ENABLE_COURSE_DISCOVERY'] = True
# Setting for overriding default filtering facets for Course discovery
# COURSE_DISCOVERY_FILTERS = ["org", "language", "modes"]
FEATURES['COURSES_ARE_BROWSEABLE'] = True
HOMEPAGE_COURSE_MAX = 9

# Software secure fake page feature flag
FEATURES['ENABLE_SOFTWARE_SECURE_FAKE'] = True

# Setting for the testing of Software Secure Result Callback
VERIFY_STUDENT["SOFTWARE_SECURE"] = {
    "API_ACCESS_KEY": "BBBBBBBBBBBBBBBBBBBB",
    "API_SECRET_KEY": "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC",
}

# Skip enrollment start date filtering
SEARCH_SKIP_ENROLLMENT_START_DATE_FILTERING = True


########################## Shopping cart ##########################
FEATURES['ENABLE_SHOPPING_CART'] = True
FEATURES['STORE_BILLING_INFO'] = True
FEATURES['ENABLE_PAID_COURSE_REGISTRATION'] = True
FEATURES['ENABLE_COSMETIC_DISPLAY_PRICE'] = True

########################## Third Party Auth #######################

if FEATURES.get('ENABLE_THIRD_PARTY_AUTH') and 'third_party_auth.dummy.DummyBackend' not in AUTHENTICATION_BACKENDS:
    AUTHENTICATION_BACKENDS = ['third_party_auth.dummy.DummyBackend'] + list(AUTHENTICATION_BACKENDS)

############## ECOMMERCE API CONFIGURATION SETTINGS ###############
ECOMMERCE_PUBLIC_URL_ROOT = "http://localhost:8002"

###################### Cross-domain requests ######################
FEATURES['ENABLE_CORS_HEADERS'] = True
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = ()
CORS_ORIGIN_ALLOW_ALL = True

# JWT settings for devstack
PUBLIC_RSA_KEY = """\
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApCujf5oZBGK4MafMRGY9
+zdRRI9YDm1r+81coDCysSrwkhTkFIwP2dmS6lYvJuQ5wifuQa3WFv1Kh9Nr2XRJ
1m9OL3/JpmMyTi/YuwD7tIf65tab1SOSRYkoxOKRuuvZuXQG9nWbXrGDncnwuWxf
eymwWaIrAhALUS5+nDa7dauj8VngsWauMrEA/MWShEzsR53wGKlciEZA1r/AfQ55
XS42GvBobhhy9SeZ3B6LHiaAEywpwFmKPssuoHSNhbPa49LW3gXJ6CsFGRDcBFKd
xJ/l8O847Q7kg1lvckpLsKyu5167NK9Qj1X/O3SwVBL3cxx1HpQ6+q3SGLZ4ngow
hwIDAQAB
-----END PUBLIC KEY-----"""

PRIVATE_RSA_KEY = """\
-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCkK6N/mhkEYrgx
p8xEZj37N1FEj1gObWv7zVygMLKxKvCSFOQUjA/Z2ZLqVi8m5DnCJ+5BrdYW/UqH
02vZdEnWb04vf8mmYzJOL9i7APu0h/rm1pvVI5JFiSjE4pG669m5dAb2dZtesYOd
yfC5bF97KbBZoisCEAtRLn6cNrt1q6PxWeCxZq4ysQD8xZKETOxHnfAYqVyIRkDW
v8B9DnldLjYa8GhuGHL1J5ncHoseJoATLCnAWYo+yy6gdI2Fs9rj0tbeBcnoKwUZ
ENwEUp3En+Xw7zjtDuSDWW9ySkuwrK7nXrs0r1CPVf87dLBUEvdzHHUelDr6rdIY
tnieCjCHAgMBAAECggEBAJvTiAdQPzq4cVlAilTKLz7KTOsknFJlbj+9t5OdZZ9g
wKQIDE2sfEcti5O+Zlcl/eTaff39gN6lYR73gMEQ7h0J3U6cnsy+DzvDkpY94qyC
/ZYqUhPHBcnW3Mm0vNqNj0XGae15yBXjrKgSy9lUknSXJ3qMwQHeNL/DwA2KrfiL
g0iVjk32dvSSHWcBh0M+Qy1WyZU0cf9VWzx+Q1YLj9eUCHteStVubB610XV3JUZt
UTWiUCffpo2okHsTBuKPVXK/5BL+BpGplcxRSlnSbMaI611kN3iKlO8KGISXHBz7
nOPdkfZC9poEXt5SshtINuGGCCc8hDxpg1otYqCLaYECgYEA1MSCPs3pBkEagchV
g0rxYmDUC8QkeIOBuZFjhkdoUgZ6rFntyRZd1NbCUi3YBbV1YC12ZGohqWUWom1S
AtNbQ2ZTbqEnDKWbNvLBRwkdp/9cKBce85lCCD6+U2o2Ha8C0+hKeLBn8un1y0zY
1AQTqLAz9ItNr0aDPb89cs5voWcCgYEAxYdC8vR3t8iYMUnK6LWYDrKSt7YiorvF
qXIMANcXQrnO0ptC0B56qrUCgKHNrtPi5bGpNBJ0oKMfbmGfwX+ca8sCUlLvq/O8
S2WZwSJuaHH4lEBi8ErtY++8F4B4l3ENCT84Hyy5jiMpbpkHEnh/1GNcvvmyI8ud
3jzovCNZ4+ECgYEA0r+Oz0zAOzyzV8gqw7Cw5iRJBRqUkXaZQUj8jt4eO9lFG4C8
IolwCclrk2Drb8Qsbka51X62twZ1ZA/qwve9l0Y88ADaIBHNa6EKxyUFZglvrBoy
w1GT8XzMou06iy52G5YkZeU+IYOSvnvw7hjXrChUXi65lRrAFqJd6GEIe5MCgYA/
0LxDa9HFsWvh+JoyZoCytuSJr7Eu7AUnAi54kwTzzL3R8tE6Fa7BuesODbg6tD/I
v4YPyaqePzUnXyjSxdyOQq8EU8EUx5Dctv1elTYgTjnmA4szYLGjKM+WtC3Bl4eD
pkYGZFeqYRfAoHXVdNKvlk5fcKIpyF2/b+Qs7CrdYQKBgQCc/t+JxC9OpI+LhQtB
tEtwvklxuaBtoEEKJ76P9vrK1semHQ34M1XyNmvPCXUyKEI38MWtgCCXcdmg5syO
PBXdDINx+wKlW7LPgaiRL0Mi9G2aBpdFNI99CWVgCr88xqgSE24KsOxViMwmi0XB
Ld/IRK0DgpGP5EJRwpKsDYe/UQ==
-----END PRIVATE KEY-----"""

JWT_AUTH.update({
    'JWT_SECRET_KEY': 'lms-secret',
    'JWT_ISSUER': 'http://127.0.0.1:8000/oauth2',
    'JWT_AUDIENCE': 'lms-key',
})

#####################################################################
# See if the developer has any local overrides.
if os.path.isfile(join(dirname(abspath(__file__)), 'private.py')):
    from .private import *  # pylint: disable=import-error,wildcard-import

#####################################################################
# Lastly, run any migrations, if needed.
MODULESTORE = convert_module_store_setting_if_needed(MODULESTORE)


# devstack_appsembler.py

import os

from .appsembler import *


if FEATURES.get('ENABLE_TAXOMAN', False):
    try:
        # Just a check, we don't need it for the settings
        import taxoman_api
        # We need this for webpack loader
        import taxoman.settings
        TAXOMAN_ENABLED = True
    except ImportError:
        TAXOMAN_ENABLED = False
else:
    TAXOMAN_ENABLED = False


ENV_APPSEMBLER_FEATURES = ENV_TOKENS.get('APPSEMBLER_FEATURES', {})
for feature, value in ENV_APPSEMBLER_FEATURES.items():
    APPSEMBLER_FEATURES[feature] = value

# disable caching in dev environment
for cache_key in CACHES.keys():
    CACHES[cache_key]['BACKEND'] = 'django.core.cache.backends.dummy.DummyCache'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# INSTALLED_APPS += (
#     #'appsembler',
#     'appsembler_api',
# )

DEFAULT_TEMPLATE_ENGINE['OPTIONS']['context_processors'] += ('etcapi.context_processors.intercom',)

CUSTOM_LOGOUT_REDIRECT_URL = ENV_TOKENS.get('CUSTOM_LOGOUT_REDIRECT_URL', '/')

TPA_CLEAN_USERNAMES_KEEP_DOMAIN_PART = ENV_TOKENS.get('TPA_CLEAN_USERNAMES_KEEP_DOMAIN_PART', False)
TPA_CLEAN_USERNAMES_REPLACER_CHAR = ENV_TOKENS.get('TPA_CLEAN_USERNAMES_REPLACER_CHAR', "")
TPA_CLEAN_USERNAMES_ADD_RANDOM_INT = ENV_TOKENS.get('TPA_CLEAN_USERNAMES_ADD_RANDOM_INT', False)

# if APPSEMBLER_FEATURES.get('ENABLE_EXTERNAL_COURSES', False):
#     INSTALLED_APPS += (
#         'openedx.core.djangoapps.appsembler.external_courses',
#     )

EDX_ORG_COURSE_API_URL = ENV_TOKENS.get('EDX_ORG_COURSE_API_URL', False)
EDX_ORG_COURSE_API_TOKEN_URL = AUTH_TOKENS.get('EDX_ORG_COURSE_API_TOKEN_URL', False)
EDX_ORG_COURSE_API_CLIENT_ID = AUTH_TOKENS.get('EDX_ORG_COURSE_API_CLIENT_ID', False)
EDX_ORG_COURSE_API_CLIENT_SECRET = AUTH_TOKENS.get('EDX_ORG_COURSE_API_CLIENT_SECRET', False)
EDX_ORG_COURSE_API_TOKEN_TYPE = AUTH_TOKENS.get('EDX_ORG_COURSE_API_TOKEN_TYPE', False)
EDX_ORG_COURSE_API_CATALOG_IDS = ENV_TOKENS.get('EDX_ORG_COURSE_API_CATALOG_IDS', False)

if APPSEMBLER_FEATURES.get('ENABLE_EXTERNAL_COURSES', False):
    if ENV_TOKENS.get('EXTERNAL_COURSES_FETCH_PERIOD_HOURS', 24) is not None:
        CELERYBEAT_SCHEDULE['fetch-external-courses'] = {
            'task': 'openedx.core.djangoapps.appsembler.external_courses.tasks.fetch_courses',
            'schedule': datetime.timedelta(
                hours=ENV_TOKENS.get('EXTERNAL_COURSES_FETCH_PERIOD_HOURS', 24)
            ),
        }

if (APPSEMBLER_FEATURES.get('ENABLE_USAGE_TRACKING', False) or
    APPSEMBLER_FEATURES.get('ENABLE_USAGE_AGGREGATION', False)
):
    # enable both apps for either feature flag, because
    #
    # * appsembler_usage depends on souvenirs models
    #
    # * appsembler_usage adds backfill_usage and email_usage management
    #   commands even if the aggregation DB isn't available.
    #
    INSTALLED_APPS += (
        'souvenirs',
        # 'openedx.core.djangoapps.appsembler.usage',  # appsembler_usage
    )

    if APPSEMBLER_FEATURES.get('ENABLE_USAGE_TRACKING', False):
        # enable live usage tracking via middleware
        MIDDLEWARE_CLASSES += (
            'souvenirs.middleware.SouvenirsMiddleware',
        )

    # router to send aggregation to cloud sql.
    # this should be enabled even if the aggregation DB isn't available,
    # to avoid trying to run migrations or store aggregation data in MySQL.
    DATABASE_ROUTERS += [
        'openedx.core.djangoapps.appsembler.usage.routers.AppsemblerUsageRouter',
    ]

    # appsembler devstack has dummy caches, but souvenirs needs a real cache
    # for rate-limiting writes to DB.
    SOUVENIRS_CACHE_NAME = 'souvenirs'
    CACHES[SOUVENIRS_CACHE_NAME] = {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'souvenirs',
    }

    # operator can override DB auth for migrations
    if ('appsembler_usage' in DATABASES and
        os.environ.get('APPSEMBLER_USAGE_DB_AUTH')
    ):
        _user, _password = os.environ['APPSEMBLER_USAGE_DB_AUTH'].split(':', 1)
        DATABASES['appsembler_usage'].update({
            'USER': _user,
            'PASSWORD': _password,
        })

    # custom reports function to count learners, staff, etc.
    SOUVENIRS_USAGE_REPORTS_FUNCTION = 'openedx.core.djangoapps.appsembler.usage.reports.usage_for_periods'

elif 'appsembler_usage' in DATABASES:
    # if the AppsemblerUsageRouter isn't enabled, then avoid mistakes by
    # removing the database alias
    del DATABASES['appsembler_usage']

CUSTOM_SSO_FIELDS_SYNC = ENV_TOKENS.get('CUSTOM_SSO_FIELDS_SYNC', {})
# to allow to run python-saml with custom port
SP_SAML_RESTRICT_MODE = False

#configure auth backends
if 'LMS_AUTHENTICATION_BACKENDS' in APPSEMBLER_FEATURES.keys():
    #default behavior is to replace the existing backends with those in APPSEMBLER_FEATURES
    AUTHENTICATION_BACKENDS = tuple(APPSEMBLER_FEATURES['LMS_AUTHENTICATION_BACKENDS'])

EXCLUSIVE_SSO_LOGISTRATION_URL_MAP = ENV_TOKENS.get('EXCLUSIVE_SSO_LOGISTRATION_URL_MAP', {})

#attempt to import model from our custom fork of edx-organizations
# if it works, then also add the middleware
# try:
#     from organizations.models import UserOrganizationMapping
#     MIDDLEWARE_CLASSES += (
#         'organizations.middleware.OrganizationMiddleware',
#     )
# except ImportError:
#     pass

# override devstack.py automatic enabling of courseware discovery
FEATURES['ENABLE_COURSE_DISCOVERY'] = ENV_TOKENS['FEATURES'].get('ENABLE_COURSE_DISCOVERY', FEATURES['ENABLE_COURSE_DISCOVERY'])

if TAXOMAN_ENABLED:
    WEBPACK_LOADER['TAXOMAN_APP'] = {
        'BUNDLE_DIR_NAME': taxoman.settings.bundle_dir_name,
        'STATS_FILE': taxoman.settings.stats_file,
    }

AUDIT_CERT_CUTOFF_DATE = None

# MANDRILL
MANDRILL_API_KEY = AUTH_TOKENS.get('MANDRILL_API_KEY', False)
EDX_APP_ETC_API_KEY = AUTH_TOKENS.get('EDX_APP_ETC_API_KEY')

ENABLE_REDIRECT_REGISTER = ENV_TOKENS.get('ENABLE_REDIRECT_REGISTER', False)
REGISTER_REDIRECT_URL = ENV_TOKENS.get('REGISTER_REDIRECT_URL', '')
