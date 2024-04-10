_T='token_reset'
_S='Invalid captcha'
_R='Passwords must be the same'
_Q='new_password_confirm'
_P='Password must be at least 5 characters'
_O='Please put the same passwords'
_N='The current password is not correct'
_M='oldPassword'
_L='passwordConfirm'
_K='password'
_J='Invalid email'
_I='Invalid spartaqube admin password'
_H='new_password'
_G='admin'
_F='email'
_E='captcha'
_D='utf-8'
_C='message'
_B='errorMsg'
_A='res'
import os,json,uuid,base64,random,string
from datetime import datetime
import hashlib,requests,hashlib
from cryptography.fernet import Fernet
from random import randint
import pytz
UTC=pytz.utc
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.contrib.auth.hashers import make_password
from django.conf import settings as conf_settings
from django.contrib.auth import login
from project.models import UserProfile,Avatar,contactUS,SpartaQubeCode
from project.sparta_25e81b3097.sparta_6730d44407 import qube_6a3e5e2e02 as qube_6a3e5e2e02
from project.sparta_25e81b3097.sparta_17cdeb90eb.qube_83b1d5f68d import Email as Email
from project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a import sparta_ca44ca5c66,sparta_d3146d6bca,sparta_49c2928dba
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_68cd4f4099
def sparta_4cf93c1295(json_data,user_obj):
	B=user_obj;A=json_data;D=A['messageContactUs'];E=A['titleContactUs'];G=A[_E];H=datetime.now();contactUS.objects.create(message=D,title=E,user=B,date_created=H);I={_C:D,'title':E,_E:G,_F:B.email,'first_name':B.first_name,'last_name':B.last_name};F=dict();F['jsonData']=json.dumps(I);C=requests.post(f"{conf_settings.SPARTAQUBE_WEBSITE}/contact-us-app",data=json.dumps(F))
	if C.status_code==200:
		try:print('response.text');print(C.text);A=json.loads(C.text);return A
		except Exception as J:return{_A:-1,_B:str(J)}
	K={_A:-1,_B:'An unexpected error occurred, please check your internet connection and try again'};return K
def sparta_1be26f2d1b(message,typeCase=0,companyName=None):
	B='Type';C=companyName;D=User.objects.filter(is_staff=True)
	if D.count()>0:
		E=D[0];A=Email(E.username,[conf_settings.CONTACT_US_EMAIL],'Contact US','Contact US new message')
		if C is not None:A.addOneRow('Company',C);A.addLineSeparator()
		A.addOneRow('Message',message);A.addLineSeparator()
		if int(typeCase)==0:A.addOneRow(B,'General question')
		else:A.addOneRow(B,'Report Bug')
		A.send()
def sparta_571baabe12(json_data,userObj):
	C=json_data;A=userObj;D=C[_K];E=C[_L];F=C[_M]
	if len(D)>4:
		if D==E:
			if A.check_password(F):G=make_password(D);A.password=G;A.save();B={_A:1,'userObj':A}
			else:B={_A:-1,_C:_N}
		else:B={_A:-1,_C:_O}
	else:B={_A:-1,_C:_P}
	return B
def sparta_745b7e65a0(json_data,userObj):
	B=json_data;C=B[_K];D=B[_L];E=B[_M]
	if len(C)>4:
		if C==D:
			if userObj.check_password(E):A={_A:1}
			else:A={_A:-1,_C:_N}
		else:A={_A:-1,_C:_O}
	else:A={_A:-1,_C:_P}
	return A
def sparta_2f15562c71(json_data,userObj):
	D=json_data;F=D['old_spartaqube_code'];G=D['new_spartaqube_code']
	if not sparta_68cd4f4099(F):return{_A:-1,_B:'Invalid current code'}
	A=hashlib.md5(G.encode(_D)).hexdigest();A=base64.b64encode(A.encode(_D));A=A.decode(_D);B=datetime.now().astimezone(UTC);E=SpartaQubeCode.objects.all()
	if E.count()==0:SpartaQubeCode.objects.create(spartaqube_code=A,date_created=B,last_update=B)
	else:C=E[0];C.spartaqube_code=A;C.last_update=B;C.save()
	return{_A:1}
def sparta_8f3957cdc6(json_data,userObj):A=userObj;C=json_data['base64image'];K=hashlib.sha256((str(A.id)+'_'+A.email+str(datetime.now())).encode(_D)).hexdigest();D,E=C.split(';base64,');F,L=D.split('/');G=F.split(':')[-1];B=UserProfile.objects.get(user=A);H=datetime.now();I=Avatar.objects.create(avatar=G,image64=E,date_created=H);B.avatar=I;B.save();J={_A:1};return J
def sparta_3e0ba3a345(json_data,userObj):B=json_data['bDarkTheme'];A=UserProfile.objects.get(user=userObj);A.is_dark_theme=B;A.save();C={_A:1};return C
def sparta_0183596f27(json_data,userObj):B=json_data['theme'];A=UserProfile.objects.get(user=userObj);A.editor_theme=B;A.save();C={_A:1};return C
def sparta_5c7a96095c():B='spartaqube-reset-password';A=B.encode(_D);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_D));return A.decode(_D)
def sparta_d0216152d8(json_data):
	A=json_data;C=A[_F];E=A[_G];B=A[_H];F=A[_Q]
	if not sparta_49c2928dba(E):return{_A:-1,_B:_I}
	if not User.objects.filter(username=C).exists():return{_A:-1,_B:_J}
	if B!=F:return{_A:-1,_B:_R}
	D=User.objects.filter(username=C).all()[0];G=make_password(B);D.password=G;D.save();return{_A:1,_H:B}
def sparta_5c7f47359d(json_data):
	A=json_data;E=A[_E];B=A[_F];F=A[_G];G=sparta_ca44ca5c66(E)
	if G[_A]!=1:return{_A:-1,_B:_S}
	if not sparta_d3146d6bca(F):return{_A:-1,_B:_I}
	if not User.objects.filter(username=B).exists():return{_A:-1,_B:_J}
	H=User.objects.filter(username=B).all()[0];C=db_functions.get_user_profile_obj(H);D=''.join(random.choice(string.ascii_uppercase+string.digits)for A in range(5));C.token_reset_password=D;C.save();return{_A:1,_T:D}
def sparta_5d6751063e(request,json_data):
	A=json_data;F=A[_E];D=A[_F];G=A[_G];H=A[_T];E=A[_H];I=A[_Q];J=sparta_ca44ca5c66(F)
	if J[_A]!=1:return{_A:-1,_B:_S}
	if not sparta_d3146d6bca(G):return{_A:-1,_B:_I}
	if not User.objects.filter(username=D).exists():return{_A:-1,_B:_J}
	if E!=I:return{_A:-1,_B:_R}
	B=User.objects.filter(username=D).all()[0];C=db_functions.get_user_profile_obj(B)
	if C.token_reset_password!=H:return{_A:-1,_B:'Invalid reset token'}
	C.token_reset_password='';C.save();K=make_password(E);B.password=K;B.save();login(request,B);return{_A:1}