_O='Please send valid data'
_N='dist/project/auth/resetPasswordChange.html'
_M='captcha'
_L='password'
_K='login'
_J='POST'
_I=False
_H='error'
_G='form'
_F='email'
_E='res'
_D='home'
_C='manifest'
_B='errorMsg'
_A=True
import json,hashlib,uuid
from datetime import datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.urls import reverse
import project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a as qube_316bac807a
from project.forms import ConnexionForm,RegistrationTestForm,RegistrationBaseForm,RegistrationForm,ResetPasswordForm,ResetPasswordChangeForm
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_7dc1413727
from project.sparta_25e81b3097.sparta_5f5d899812 import qube_dc69199006 as qube_dc69199006
from project.sparta_652c521b39.sparta_4bc8af297f import qube_12561d14ba as qube_12561d14ba
from project.models import LoginLocation,UserProfile
def sparta_c6898b0339():return{'bHasCompanyEE':-1}
def sparta_4eedcc4c3b(request):B=request;A=qube_316bac807a.sparta_a7855bf3fb(B);A[_C]=qube_316bac807a.sparta_dd9ffdc2ee();A['forbiddenEmail']=conf_settings.FORBIDDEN_EMAIL;return render(B,'dist/project/auth/banned.html',A)
@sparta_7dc1413727
def sparta_1ddb3af221(request):
	C=request;B='/';A=C.GET.get(_K)
	if A is not None:D=A.split(B);A=B.join(D[1:]);A=A.replace(B,'$@$')
	return sparta_88b51c045a(C,A)
def sparta_fdd532ba16(request,redirectUrl):return sparta_88b51c045a(request,redirectUrl)
def sparta_88b51c045a(request,redirectUrl):
	D=redirectUrl;A=request
	if A.user.is_authenticated:return redirect(_D)
	F=_I;H='Email or password incorrect'
	if A.method==_J:
		C=ConnexionForm(A.POST)
		if C.is_valid():
			I=C.cleaned_data[_F];J=C.cleaned_data[_L];E=authenticate(username=I,password=J)
			if E:
				if qube_dc69199006.sparta_b7e8525807(E):return sparta_4eedcc4c3b(A)
				login(A,E);K,L=qube_316bac807a.sparta_d668fb7a0a();LoginLocation.objects.create(user=E,hostname=K,ip=L,date_login=datetime.now())
				if D is not None:
					G=D.split('$@$')
					if len(G)>1:M=G[-2];N=G[-1];return redirect(reverse(M,args=[N]))
					return redirect(D)
				return redirect(_D)
			else:F=_A
		else:F=_A
	C=ConnexionForm();B=qube_316bac807a.sparta_a7855bf3fb(A);B.update(qube_316bac807a.sparta_cf4fb1eef3(A));B[_C]=qube_316bac807a.sparta_dd9ffdc2ee();B[_G]=C;B[_H]=F;B['redirectUrl']=D;B[_B]=H;B.update(sparta_c6898b0339());return render(A,'dist/project/auth/login.html',B)
@sparta_7dc1413727
def sparta_84bd9cc51c(request):
	A=request
	if A.user.is_authenticated:return redirect(_D)
	E='';D=_I;F=qube_dc69199006.sparta_1015a2e179()
	if A.method==_J:
		if F:B=RegistrationForm(A.POST)
		else:B=RegistrationBaseForm(A.POST)
		if B.is_valid():
			I=B.cleaned_data;H=None
			if F:
				H=B.cleaned_data['code']
				if not qube_dc69199006.sparta_ca5c00b566(H):D=_A;E='Wrong guest code'
			if not D:
				J=A.META['HTTP_HOST'];G=qube_dc69199006.sparta_9c9ebd38a8(I,J)
				if int(G[_E])==1:K=G['userObj'];login(A,K);return redirect(_D)
				else:D=_A;E=G[_B]
		else:D=_A;E=B.errors.as_data()
	if F:B=RegistrationForm()
	else:B=RegistrationBaseForm()
	C=qube_316bac807a.sparta_a7855bf3fb(A);C.update(qube_316bac807a.sparta_cf4fb1eef3(A));C[_C]=qube_316bac807a.sparta_dd9ffdc2ee();C[_G]=B;C[_H]=D;C[_B]=E;C.update(sparta_c6898b0339());return render(A,'dist/project/auth/registration.html',C)
def sparta_28267d5b95(request):A=request;B=qube_316bac807a.sparta_a7855bf3fb(A);B[_C]=qube_316bac807a.sparta_dd9ffdc2ee();return render(A,'dist/project/auth/registrationPending.html',B)
def sparta_1f371a42f5(request,token):
	A=request;B=qube_dc69199006.sparta_e7e3bb720e(token)
	if int(B[_E])==1:C=B['user'];login(A,C);return redirect(_D)
	D=qube_316bac807a.sparta_a7855bf3fb(A);D[_C]=qube_316bac807a.sparta_dd9ffdc2ee();return redirect(_K)
def sparta_1ef9797ac7(request):logout(request);return redirect(_K)
def sparta_2fd9da2223(request):A={_E:-100,_B:'You are not logged...'};B=json.dumps(A);return HttpResponse(B)
@csrf_exempt
def sparta_e785615d5a(request):
	A=request;E='';F=_I
	if A.method==_J:
		B=ResetPasswordForm(A.POST)
		if B.is_valid():
			H=B.cleaned_data[_F];I=B.cleaned_data[_M];G=qube_dc69199006.sparta_e785615d5a(H.lower(),I)
			try:
				if int(G[_E])==1:C=qube_316bac807a.sparta_a7855bf3fb(A);C.update(qube_316bac807a.sparta_cf4fb1eef3(A));B=ResetPasswordChangeForm(A.POST);C[_C]=qube_316bac807a.sparta_dd9ffdc2ee();C[_G]=B;C[_F]=H;C[_H]=F;C[_B]=E;return render(A,_N,C)
				elif int(G[_E])==-1:E=G[_B];F=_A
			except Exception as J:print('exception ');print(J);E='Could not send reset email, please try again';F=_A
		else:E=_O;F=_A
	else:B=ResetPasswordForm()
	D=qube_316bac807a.sparta_a7855bf3fb(A);D.update(qube_316bac807a.sparta_cf4fb1eef3(A));D[_C]=qube_316bac807a.sparta_dd9ffdc2ee();D[_G]=B;D[_H]=F;D[_B]=E;D.update(sparta_c6898b0339());return render(A,'dist/project/auth/resetPassword.html',D)
@csrf_exempt
def sparta_556f3cdc10(request):
	D=request;E='';B=_I
	if D.method==_J:
		C=ResetPasswordChangeForm(D.POST)
		if C.is_valid():
			I=C.cleaned_data['token'];F=C.cleaned_data[_L];J=C.cleaned_data['password_confirmation'];K=C.cleaned_data[_M];G=C.cleaned_data[_F].lower()
			if len(F)<6:E='Your password must be at least 6 characters';B=_A
			if F!=J:E='The two passwords must be identical...';B=_A
			if not B:
				H=qube_dc69199006.sparta_556f3cdc10(K,I,G.lower(),F)
				try:
					if int(H[_E])==1:L=User.objects.get(username=G);login(D,L);return redirect(_D)
					else:E=H[_B];B=_A
				except Exception as M:E='Could not change your password, please try again';B=_A
		else:E=_O;B=_A
	else:return redirect('reset-password')
	A=qube_316bac807a.sparta_a7855bf3fb(D);A.update(qube_316bac807a.sparta_cf4fb1eef3(D));A[_C]=qube_316bac807a.sparta_dd9ffdc2ee();A[_G]=C;A[_H]=B;A[_B]=E;A[_F]=G;A.update(sparta_c6898b0339());return render(D,_N,A)