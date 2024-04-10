from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_7dc1413727
from project.sparta_25e81b3097.sparta_40132c8067 import qube_8c1df4cb1f as qube_8c1df4cb1f
from project.models import UserProfile
import project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a as qube_316bac807a
@sparta_7dc1413727
@login_required(redirect_field_name='login')
def sparta_cb691044f9(request):
	C='avatarImg';B=request;A=qube_316bac807a.sparta_a7855bf3fb(B);A['menuBar']=-1;F=qube_316bac807a.sparta_ec1a87b7f8(B.user);A.update(F);A[C]='';D=UserProfile.objects.filter(user=B.user)
	if D.count()>0:
		E=D[0];G=E.avatar
		if G is not None:H=E.avatar.image64;A[C]=H
	A['bInvertIcon']=0;return render(B,'dist/project/helpCenter/helpCenter.html',A)
@sparta_7dc1413727
@login_required(redirect_field_name='login')
def sparta_5eadb669d2(request):
	A=request;B=UserProfile.objects.filter(user=A.user)
	if B.count()>0:C=B[0];C.has_open_tickets=False;C.save()
	return sparta_cb691044f9(A)