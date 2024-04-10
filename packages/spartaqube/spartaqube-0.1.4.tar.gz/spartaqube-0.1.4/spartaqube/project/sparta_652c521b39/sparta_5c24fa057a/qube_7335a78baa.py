import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_25e81b3097.sparta_d5e15c8729 import qube_32104e8b1b as qube_32104e8b1b
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_bde60771e2,sparta_5f9bce2192
@csrf_exempt
@sparta_bde60771e2
def sparta_15088311fc(request):C='api_func';D='key';E='utf-8';A=request;F=A.body.decode(E);F=A.POST.get(D);G=A.body.decode(E);G=A.POST.get(C);B=dict();B[D]=F;B[C]=G;H=qube_32104e8b1b.sparta_15088311fc(B,A.user);I=json.dumps(H);return HttpResponse(I)