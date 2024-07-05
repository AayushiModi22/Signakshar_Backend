from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'mainapp' / 'email-format' / 'otp-template'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-!!)&me%s=q9b(e)s8nvo33sd*=&epu^2(sqk2rju8*+57wh%3@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["192.168.1.58","192.168.1.63","localhost","127.0.0.1","*"]
# ALLOWED_HOSTS=["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'mainapp',
    'django_celery_results',
    'django_celery_beat',
    'send_mail_app',
    'rest_framework_simplejwt',
    'rest_framework',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]

ROOT_URLCONF = 'hastakshar_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'mainapp' / 'email-format'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
            ],
        },
    },
]

WSGI_APPLICATION = 'hastakshar_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'hastakshar',
#         'USER': 'root',
#         'PASSWORD': '',
#         'HOST': 'localhost',  # Change this to your MySQL server's hostname or IP address
#         'PORT': '3306',       # Change this to your MySQL server's port
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'signakshar',
        'USER': 'avnadmin',
        'PASSWORD': 'AVNS_EUHuRflCHDzhA37zq_5',
        'HOST': 'mysql-31695c3c-signakshar-qit.j.aivencloud.com', 
        'PORT': '25587',      
    }
}


# ///// aws
AWS_ACCESS_KEY_ID = 'AKIA2P56CA5N2YZNAK26'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'


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

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'social_core.backends.google.GoogleOAuth2',  #social app custom settings
]

AUTH_USER_MODEL = 'mainapp.User'

# CORS_ORIGIN_ALLOW_ALL = True


LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_URL = 'logout'
LOGOUT_REDIRECT_URL = 'login'


SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='491814227776-nv1lkg7sfsfvshsblt0jrrk62l5lejam.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='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'


# Celery Configuration
CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT=['application/json']
CELERY_RESULT_SERIALIZER='json'
CELERY_TASK_SERIALIZER='json'
CELERY_TIMEZONE='Asia/Kolkata'

#celery beat
CELERY_BEAT_SCHEDULER='django_celery_beat.schedulers:DatabaseScheduler'

EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS=True
EMAIL_HOST="smtp.gmail.com"
EMAIL_PORT=587
# EMAIL_HOST_USER='rajeshree24patel@gmail.com'
# EMAIL_HOST_PASSWORD="nblk bbal jreu wosf"
# DEFAULT_FROM_EMAIL='Celery <rajeshree24patel@gmail.com>'

EMAIL_HOST_USER='signakshar.qit@gmail.com'
EMAIL_HOST_PASSWORD="vbhi ywif azxn glxt"
DEFAULT_FROM_EMAIL='Celery <signakshar.qit@gmail.com>'


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://192.168.1.59:3000"
]
