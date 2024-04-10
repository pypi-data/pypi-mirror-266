_M='An error occurred, please try again'
_L='Invalid captcha'
_K='password_confirmation'
_J='password'
_I='jsonData'
_H='api_token_id'
_G='notLoggerAPI'
_F='is_created'
_E='utf-8'
_D='errorMsg'
_C=False
_B=True
_A='res'
import hashlib,re,uuid,json,requests,socket,base64
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth import logout,login
from django.http import HttpResponseRedirect
from django.conf import settings as conf_settings
from django.urls import reverse
from project.models import UserProfile,GuestCode,GuestCodeGlobal,LocalApp,SpartaQubeCode
from project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a import sparta_ca44ca5c66
from project.sparta_25e81b3097.sparta_6730d44407 import qube_6a3e5e2e02 as qube_6a3e5e2e02
from project.sparta_25e81b3097.sparta_ba8e24badd import qube_79120e6572 as qube_79120e6572
from project.sparta_25e81b3097.sparta_17cdeb90eb.qube_83b1d5f68d import Email as Email
def sparta_7dc1413727(function):
	def A(request,*D,**E):
		A=request;B=_B
		if not A.user.is_active:B=_C;logout(A)
		if not A.user.is_authenticated:B=_C;logout(A)
		if not B:
			C=A.GET.get(_H)
			if C is not None:F=qube_79120e6572.sparta_8709d2911e(C);login(A,F)
		return function(A,*D,**E)
	return A
def sparta_bde60771e2(function):
	def A(request,*B,**C):
		A=request
		if not A.user.is_active:return HttpResponseRedirect(reverse(_G))
		if A.user.is_authenticated:return function(A,*B,**C)
		else:return HttpResponseRedirect(reverse(_G))
	return A
def sparta_5f9bce2192(function):
	def A(request,*D,**E):
		A=request;B=_C
		try:
			F=json.loads(A.body);G=json.loads(F[_I]);H=G[_H];C=qube_79120e6572.sparta_8709d2911e(H)
			if C is not None:B=_B;A.user=C
		except Exception as I:print('exception pip auth');print(I)
		if B:return function(A,*D,**E)
		else:return HttpResponseRedirect(reverse(_G))
	return A
def sparta_68cd4f4099(code):
	try:
		B=SpartaQubeCode.objects.all()
		if B.count()==0:return code=='admin'
		else:C=B[0].spartaqube_code;A=hashlib.md5(code.encode(_E)).hexdigest();A=base64.b64encode(A.encode(_E));A=A.decode(_E);return A==C
	except Exception as D:pass
	return _C
def sparta_704bf5d35b():
	A=LocalApp.objects.all()
	if A.count()==0:B=str(uuid.uuid4());LocalApp.objects.create(app_id=B,date_created=datetime.now());return B
	else:return A[0].app_id
def sparta_ba28f0f17c():A=socket.gethostname();B=socket.gethostbyname(A);return B
def sparta_da793574ea(json_data):
	C='ip_addr';A=json_data;del A[_J];del A[_K]
	try:A[C]=sparta_ba28f0f17c()
	except:A[C]=-1
	D=dict();D[_I]=json.dumps(A);B=requests.post(f"{conf_settings.SPARTAQUBE_WEBSITE}/create-user",data=json.dumps(D))
	if B.status_code==200:
		try:
			A=json.loads(B.text)
			if A[_A]==1:return{_A:1,_F:_B}
			else:A[_F]=_C;return A
		except Exception as E:return{_A:-1,_F:_C,_D:str(E)}
	return{_A:1,_F:_C,_D:f"status code: {B.status_code}. Please check your internet connection"}
def sparta_9c9ebd38a8(json_data,hostname_url):
	L='emailExist';M='passwordConfirm';G='email';B=json_data;H={M:'The two passwords must be the same...',G:'Email address is not valid...','form':'The form you sent is not valid...',L:'This email is already registered...'};E=_C;P=B['firstName'].capitalize();Q=B['lastName'].capitalize();C=B[G].lower();N=B[_J];R=B[_K];S=B['code'];B['app_id']=sparta_704bf5d35b()
	if not sparta_68cd4f4099(S):return{_A:-1,_D:'Invalid spartaqube code, please contact your administrator'}
	if N!=R:E=_B;F=H[M]
	if not re.match('[^@]+@[^@]+\\.[^@]+',C):E=_B;F=H[G]
	if User.objects.filter(username=C).exists():E=_B;F=H[L]
	if not E:
		O=sparta_da793574ea(B);T=O[_F]
		if not T:F=O[_D]
		else:A=User.objects.create_user(C,C,N);A.is_staff=_C;A.username=C;A.first_name=P;A.last_name=Q;A.is_active=_B;A.save();D=UserProfile(user=A);I=str(A.id)+'_'+str(A.email);I=I.encode(_E);J=hashlib.md5(I).hexdigest()+str(datetime.now());J=J.encode(_E);U=str(uuid.uuid4());D.user_profile_id=hashlib.sha256(J).hexdigest();D.email=C;D.api_key=str(uuid.uuid4());D.registration_token=U;D.save();K={_A:1,'userObj':A};return K
	K={_A:-1,_D:F};return K
def sparta_22d1604aaf(user_obj,hostname_url,registration_token):B='Validate your account';C=user_obj;A=Email(C.username,[C.email],f"Welcome to {conf_settings.PROJECT_NAME}",B);A.addOneRow(B);A.addSpaceSeparator();A.addOneRow('Click on the link below to validate your account');D=f"{hostname_url.rstrip('/')}/registration-validation/{registration_token}";A.addOneCenteredButton('Validate',D);A.send()
def sparta_e7e3bb720e(token):
	C=UserProfile.objects.filter(registration_token=token)
	if C.count()>0:A=C[0];A.registration_token='';A.is_account_validated=_B;A.save();B=A.user;B.is_active=_B;B.save();return{_A:1,'user':B}
	return{_A:-1,_D:'Invalid registration token'}
def sparta_1015a2e179():return conf_settings.IS_GUEST_CODE_REQUIRED
def sparta_ca5c00b566(guest_code):
	if GuestCodeGlobal.objects.filter(guest_id=guest_code,is_active=_B).count()>0:return _B
	return _C
def sparta_2afcad49cc(guest_code,user_obj):
	C=user_obj;D=guest_code
	if GuestCodeGlobal.objects.filter(guest_id=D,is_active=_B).count()>0:return _B
	A=GuestCode.objects.filter(user=C)
	if A.count()>0:return _B
	else:
		A=GuestCode.objects.filter(guest_id=D,is_used=_C)
		if A.count()>0:B=A[0];B.user=C;B.is_used=_B;B.save();return _B
	return _C
def sparta_b7e8525807(user):
	A=UserProfile.objects.filter(user=user)
	if A.count()==1:return A[0].is_banned
	else:return _C
def sparta_e785615d5a(email,captcha):
	D=sparta_ca44ca5c66(captcha)
	if D[_A]!=1:return{_A:-1,_D:_L}
	B=UserProfile.objects.filter(user__username=email)
	if B.count()==0:return{_A:-1,_D:_M}
	A=B[0];C=str(uuid.uuid4());A.token_reset_password=C;A.save();sparta_d07abb0d90(A.user,C);return{_A:1}
def sparta_d07abb0d90(user_obj,token_reset_password):B=user_obj;A=Email(B.username,[B.email],'Reset Password','Reset Password Message');A.addOneRow('Reset code','Copy the following code to reset your password');A.addSpaceSeparator();A.addOneRow(token_reset_password);A.send()
def sparta_556f3cdc10(captcha,token,email,password):
	D=sparta_ca44ca5c66(captcha)
	if D[_A]!=1:return{_A:-1,_D:_L}
	B=UserProfile.objects.filter(user__username=email)
	if B.count()==0:return{_A:-1,_D:_M}
	A=B[0]
	if not token==A.token_reset_password:return{_A:-1,_D:'Invalid token..., please try again'}
	A.token_reset_password='';A.save();C=A.user;C.set_password(password);C.save();return{_A:1}