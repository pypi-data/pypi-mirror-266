_C='localhost'
_B='NAME'
_A=True
from pathlib import Path
import os,socket
from itertools import product
from spartaqube.secrets import sparta_93a34a7f9f
secrets_dict=sparta_93a34a7f9f()
BASE_DIR=Path(__file__).resolve().parent.parent
LOGIN_URL='/login'
SECRET_KEY=secrets_dict['DJANGO_SECRET_KEY']
DEBUG=_A
DEFAULT_TIMEOUT=60
PROJECT_NAME='SpartaQube'
IS_GUEST_CODE_REQUIRED=False
WEBSOCKET_PREFIX='ws'
HOST_WS_PREFIX=WEBSOCKET_PREFIX+'://'
CAPTCHA_SITEKEY=secrets_dict['CAPTCHA_SITEKEY']
CAPTCHA_SECRET=secrets_dict['CAPTCHA_SECRET_KEY']
SPARTAQUBE_WEBSITE='https://www.spartaqube.com'
FORBIDDEN_EMAIL='forbidden@spartaqube.com'
CONTACT_US_EMAIL=secrets_dict['CONTACT_US_EMAIL']
ADMIN_EMAIL_TICKET='contact@mysite.com'
ADMIN_DEFAULT_USER='admin'
ADMIN_DEFAULT_EMAIL='admin@spartaqube.com'
ADMIN_DEFAULT_PWD='admin'
URL_TERMS='www.spartaqube.com/terms'
URL_WEBSITE='www.spartaqube.com'
COMPANY_NAME='Spartacus Lab'
COMPANY_SLOGAN='A plug and play solution to visualize your data and build web components'
MAX_TICKETS=5
B_TOOLBAR=False
DAPHNE_PREFIX=''
GITHUB_TOKEN_DEMO='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'
def sparta_ba28f0f17c():A=socket.gethostname();B=socket.gethostbyname(A);return B
allowed_domains=['https://*.127.0.0.1','http://*.127.0.0.1','http://localhost','http://*','https://*']
ALLOWED_HOSTS=['django',_C,'localhost:*','localhost:81','*']+allowed_domains
CSRF_TRUSTED_ORIGINS=['http://localhost:*','http://localhost:81/*']+allowed_domains
ports=range(1,65536)
protocols=['http','https']
hostnames=[_C,sparta_ba28f0f17c()]
CSRF_TRUSTED_ORIGINS=[f"{A}://{B}:{C}/*"for(A,B,C)in product(protocols,hostnames,ports)]
CSRF_COOKIE_NAME='csrftoken'
CORS_ALLOW_CREDENTIALS=_A
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','corsheaders','channels','project']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF='spartaqube.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[os.path.join(BASE_DIR,'templates'),os.path.join(BASE_DIR,'project/templates')],'APP_DIRS':_A,'OPTIONS':{'context_processors':['django.template.context_processors.debug','django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION='spartaqube.wsgi.application'
ASGI_APPLICATION='spartaqube.routing.application'
X_FRAME_OPTIONS='ALLOWALL'
from spartaqube.db_path import sparta_54f6936d07
LOCAL_DB_PATH=sparta_54f6936d07()
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3',_B:LOCAL_DB_PATH}}
AUTH_PASSWORD_VALIDATORS=[{_B:'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},{_B:'django.contrib.auth.password_validation.MinimumLengthValidator'},{_B:'django.contrib.auth.password_validation.CommonPasswordValidator'},{_B:'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE='en-us'
TIME_ZONE='UTC'
USE_I18N=_A
USE_TZ=_A
STATIC_URL='/static/'
STATICFILES_DIRS=os.path.join(BASE_DIR,'static'),os.path.join(BASE_DIR,'static/dist/')
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'