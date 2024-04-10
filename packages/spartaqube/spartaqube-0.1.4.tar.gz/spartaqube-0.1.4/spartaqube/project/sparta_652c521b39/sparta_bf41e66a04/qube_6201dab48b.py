_A='jsonData'
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings as conf_settings
from project.models import UserProfile
from project.sparta_25e81b3097.sparta_088e656477 import qube_7de0836484 as qube_7de0836484
from project.sparta_25e81b3097.sparta_40132c8067 import qube_8c1df4cb1f as qube_8c1df4cb1f
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_bde60771e2
@csrf_exempt
@sparta_bde60771e2
def sparta_ee9fe677f6(request):
	B=request;I=json.loads(B.body);C=json.loads(I[_A]);A=B.user;D=0;E=UserProfile.objects.filter(user=A)
	if E.count()>0:
		F=E[0]
		if F.has_open_tickets:
			C['userId']=F.user_profile_id;G=qube_8c1df4cb1f.sparta_782304f068(A)
			if G['res']==1:D=int(G['nbNotifications'])
	H=qube_7de0836484.sparta_ee9fe677f6(C,A);H['nbNotificationsHelpCenter']=D;J=json.dumps(H);return HttpResponse(J)
@csrf_exempt
@sparta_bde60771e2
def sparta_e3f73caf01(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_7de0836484.sparta_44dbfbd38a(C,A.user);E=json.dumps(D);return HttpResponse(E)