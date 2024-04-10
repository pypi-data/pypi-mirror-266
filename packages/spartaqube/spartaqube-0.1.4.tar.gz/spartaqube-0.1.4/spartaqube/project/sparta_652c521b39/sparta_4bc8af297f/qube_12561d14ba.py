import json
from django.contrib.auth import logout
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from project.sparta_25e81b3097.sparta_5f5d899812 import qube_dc69199006 as qube_dc69199006
@csrf_exempt
def sparta_9c9ebd38a8(request):A=json.loads(request.body);B=json.loads(A['jsonData']);return qube_dc69199006.sparta_9c9ebd38a8(B)
@csrf_exempt
def sparta_a1ec9dacae(request):logout(request);A={'res':1};B=json.dumps(A);return HttpResponse(B)