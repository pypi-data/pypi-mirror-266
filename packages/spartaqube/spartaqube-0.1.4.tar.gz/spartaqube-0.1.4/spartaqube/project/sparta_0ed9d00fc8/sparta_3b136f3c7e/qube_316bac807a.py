_C='manifest'
_B=False
_A=None
import os,socket,json,requests
from datetime import date
from project.models import UserProfile
from django.conf import settings as conf_settings
from spartaqube.secrets import sparta_93a34a7f9f
class dotdict(dict):__getattr__=dict.get;__setattr__=dict.__setitem__;__delattr__=dict.__delitem__
def sparta_a2439e19e6(appViewsModels):
	A=appViewsModels
	if isinstance(A,list):
		for C in A:
			for B in list(C.keys()):
				if isinstance(C[B],date):C[B]=str(C[B])
	else:
		for B in list(A.keys()):
			if isinstance(A[B],date):A[B]=str(A[B])
	return A
def sparta_dac213e967(thisText):A=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));A=A+str('/log/log.txt');B=open(A,'a');B.write(thisText);B.writelines('\n');B.close()
def sparta_cf4fb1eef3(request):A=request;return{'appName':'Project','user':A.user,'ip_address':A.META['REMOTE_ADDR']}
def sparta_5065200553():return conf_settings.PLATFORM
def sparta_dd9ffdc2ee():
	A=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));A=os.path.dirname(os.path.dirname(A));D=A+'/static/dist/manifest.json';E=open(D);B=json.load(E)
	if conf_settings.B_TOOLBAR:
		F=list(B.keys())
		for C in F:B[C]=A+'/static'+B[C]
	return B
def sparta_a7855bf3fb(request):
	A='';B=''
	if len(A)>0:A='/'+str(A)
	if len(B)>0:B='/'+str(B)
	C=conf_settings.HOST_WS_PREFIX;D=conf_settings.WEBSOCKET_PREFIX;E={'PROJECT_NAME':conf_settings.PROJECT_NAME,'CAPTCHA_SITEKEY':conf_settings.CAPTCHA_SITEKEY,'WEBSOCKET_PREFIX':D,'URL_PREFIX':A,'URL_WS_PREFIX':B,'HOST_WS_PREFIX':C};return E
def sparta_ca44ca5c66(captcha):
	C='errorMsg';A='res';B=captcha
	try:
		if B is not _A:
			if len(B)>0:
				D=sparta_93a34a7f9f()['CAPTCHA_SECRET_KEY'];print(D);F=f"https://www.google.com/recaptcha/api/siteverify?secret={D}&response={B}";E=requests.get(F)
				if int(E.status_code)==200:
					G=json.loads(E.text)
					if G['success']:return{A:1}
	except Exception as H:return{A:-1,C:str(H)}
	return{A:-1,C:'Invalid captcha'}
def sparta_49c2928dba(password):
	A=password;B=UserProfile.objects.filter(email=conf_settings.ADMIN_DEFAULT_EMAIL).all()
	if B.count()==0:return conf_settings.ADMIN_DEFAULT==A
	else:C=B[0];D=C.user;return D.check_password(A)
def sparta_d3146d6bca(code):
	A=code
	try:
		if A is not _A:
			if len(A)>0:
				B=os.getenv('SPARTAQUBE_PASSWORD','admin')
				if B==A:return True
	except:return _B
	return _B
def sparta_ec1a87b7f8(user):
	E='default';A=dict()
	if not user.is_anonymous:
		F=UserProfile.objects.filter(user=user)
		if F.count()>0:
			B=F[0];D=B.avatar
			if D is not _A:D=B.avatar.avatar
			A['avatar']=D;A['userProfile']=B;C=B.editor_theme
			if C is _A:C=E
			elif len(C)==0:C=E
			else:C=B.editor_theme
			A['theme']=C;A['B_DARK_THEME']=B.is_dark_theme
	A[_C]=sparta_dd9ffdc2ee();return A
def sparta_8417b20121(user):A=dict();A[_C]=sparta_dd9ffdc2ee();return A
def sparta_4ec268daed():
	try:socket.create_connection(('1.1.1.1',53));return True
	except OSError:pass
	return _B
def sparta_d668fb7a0a():A=socket.gethostname();B=socket.gethostbyname(A);return A,B