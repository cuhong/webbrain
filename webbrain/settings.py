import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = 'e$mu))=4o0(x4=n5auxg=^+w^oy7z2*@l%i8^g&wh$6on@prqw'

DEBUG = True

ALLOWED_HOSTS = ['13.124.82.23', '127.0.0.1']

INSTALLED_APPS = [
    'jet',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'taggit',
    'bootstrap4',
    'mathfilters',
    'ordered_model',
    'django_json_widget',
    'django_summernote',
    'solo',
    'users.apps.UsersConfig',
    'administration.apps.AdministrationConfig',
    'research.apps.ResearchConfig',
    'participate.apps.ParticipateConfig'
]

JET_SIDE_MENU_COMPACT = True

JET_SIDE_MENU_ITEMS = {
    'research_admin_site': [
        {'label': '연구관리', 'items': [
            {'name': 'research.researchadminproxyforresearch', 'label': '연구'},
            {'name': 'admin.participateadminproxy', 'label': '결과'}
        ]},
    ],
    'administration_admin': [
        {'label': '디자인관리', 'items': [
            {'name': 'administration.mainpage', 'label': '메인페이지'}
        ]},
        {'label': '사용자관리', 'items': [
            {'name': 'users.researcheruser', 'label': '연구자'},
            {'name': 'users.staffuser', 'label': '관리자'},
            {'name': 'users.participantuser', 'label': '참여자'},
        ]},
        {'label': '연구관리', 'items': [
            {'name': 'research.researchadminproxy', 'label': '연구목록'},
        ]},
    ],
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'webbrain.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'webbrain.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'web',
        'USER': 'webrain',
        'PASSWORD': 'webrain1!',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}

AUTH_USER_MODEL = 'users.customuser'

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

LANGUAGE_CODE = 'ko-kr'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'templates', 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SUMMERNOTE_THEME = 'lite'

LOGIN_REDIRECT_URL = '/'
