_A='jsonData'
import json,inspect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from project.sparta_25e81b3097.sparta_e016dca9f5 import qube_c1172ff413 as qube_c1172ff413
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_bde60771e2
@csrf_exempt
@sparta_bde60771e2
def sparta_4cf93c1295(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c1172ff413.sparta_4cf93c1295(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_571baabe12(request):
	B='userObj';C=request;D=json.loads(C.body);E=json.loads(D[_A]);F=C.user;A=qube_c1172ff413.sparta_571baabe12(E,F)
	if A['res']==1:
		if B in list(A.keys()):login(C,A[B]);A.pop(B,None)
	G=json.dumps(A);return HttpResponse(G)
@csrf_exempt
@sparta_bde60771e2
def sparta_2f15562c71(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=A.user;E=qube_c1172ff413.sparta_2f15562c71(C,D);F=json.dumps(E);return HttpResponse(F)
@csrf_exempt
@sparta_bde60771e2
def sparta_8f3957cdc6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c1172ff413.sparta_8f3957cdc6(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_3e0ba3a345(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c1172ff413.sparta_3e0ba3a345(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_0183596f27(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c1172ff413.sparta_0183596f27(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_e7c6d54db4(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_c1172ff413.token_reset_password_worker(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
@sparta_bde60771e2
def sparta_f154bb0fc6(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c1172ff413.network_master_reset_password(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
def sparta_d0216152d8(request):A=json.loads(request.body);B=json.loads(A[_A]);C=qube_c1172ff413.sparta_d0216152d8(B);D=json.dumps(C);return HttpResponse(D)
@csrf_exempt
def sparta_5d6751063e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c1172ff413.sparta_5d6751063e(A,C);E=json.dumps(D);return HttpResponse(E)