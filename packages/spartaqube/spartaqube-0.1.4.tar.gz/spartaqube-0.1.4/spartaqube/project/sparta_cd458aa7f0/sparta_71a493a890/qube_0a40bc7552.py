from urllib.parse import urlparse,urlunparse
from django.contrib.auth.decorators import login_required
from django.conf import settings as conf_settings
from django.shortcuts import render
import project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a as qube_316bac807a
from project.models import UserProfile
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_7dc1413727
from project.sparta_cd458aa7f0.sparta_e8474e0f4f.qube_e187fd446e import sparta_c6898b0339
@sparta_7dc1413727
@login_required(redirect_field_name='login')
def sparta_b6ac1f10a0(request,idSection=1):
	B=request;D=UserProfile.objects.get(user=B.user);E=D.avatar
	if E is not None:E=D.avatar.avatar
	C=urlparse(conf_settings.URL_TERMS)
	if not C.scheme:C=urlunparse(C._replace(scheme='http'))
	F={'item':1,'idSection':idSection,'userProfil':D,'avatar':E,'url_terms':C};A=qube_316bac807a.sparta_a7855bf3fb(B);A.update(qube_316bac807a.sparta_ec1a87b7f8(B.user));A.update(F);G='';A['accessKey']=G;A.update(sparta_c6898b0339());return render(B,'dist/project/auth/settings.html',A)