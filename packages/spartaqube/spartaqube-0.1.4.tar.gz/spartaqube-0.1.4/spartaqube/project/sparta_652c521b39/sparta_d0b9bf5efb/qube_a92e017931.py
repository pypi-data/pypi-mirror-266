_I='error.txt'
_H='zipName'
_G='utf-8'
_F='attachment; filename={0}'
_E='appId'
_D='Content-Disposition'
_C='res'
_B='projectPath'
_A='jsonData'
import json,base64
from django.http import HttpResponse,Http404
from django.views.decorators.csrf import csrf_exempt
from project.sparta_25e81b3097.sparta_857f539b0a import qube_c82989d216 as qube_c82989d216
from project.sparta_25e81b3097.sparta_857f539b0a import qube_e8610a79cf as qube_e8610a79cf
from project.sparta_25e81b3097.sparta_0a82db77e0 import qube_6c72fd4753 as qube_6c72fd4753
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_bde60771e2
@csrf_exempt
@sparta_bde60771e2
def sparta_78521f6336(request):
	B='files[]';A=request;E=A.POST.dict();C=A.FILES
	if B in C:D=qube_c82989d216.sparta_4a8f36f838(E,A.user,C[B])
	else:D={_C:1}
	F=json.dumps(D);return HttpResponse(F)
@csrf_exempt
@sparta_bde60771e2
def sparta_91a6eeffc8(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_9026c85e8f(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_03e870097e(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_2b035617ee(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_563a34af92(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_0a2e7b3b32(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_72f64cbf1d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_e8610a79cf.sparta_23d3a89ecf(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_0e36f45897(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_85b6bf3d0b(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_5a1d6f2bd9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_8ac1d6aa5a(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_798c0155e9(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_c1a8f6ee04(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_6ba0c7d83d(request):A=request;B=json.loads(A.body);C=json.loads(B[_A]);D=qube_c82989d216.sparta_9df95139d1(C,A.user);E=json.dumps(D);return HttpResponse(E)
@csrf_exempt
@sparta_bde60771e2
def sparta_30bd2e2821(request):
	B='filePath';C='fileName';A=request;D=A.GET[C];G=A.GET[B];H=A.GET[_B];I=A.GET[_E];J={C:D,B:G,_E:I,_B:base64.b64decode(H).decode(_G)};E=qube_c82989d216.sparta_e3a697e181(J,A.user)
	if E[_C]==1:
		try:
			with open(E['fullPath'],'rb')as K:F=HttpResponse(K.read(),content_type='application/force-download');F[_D]='attachment; filename='+str(D);return F
		except Exception as L:pass
	raise Http404
@csrf_exempt
@sparta_bde60771e2
def sparta_340de3930a(request):
	D='folderName';C=request;F=C.GET[_B];E=C.GET[D];G={_B:base64.b64decode(F).decode(_G),D:E};B=qube_c82989d216.sparta_9c1b4f9773(G,C.user);print(_C);print(B)
	if B[_C]==1:H=B['zip'];I=B[_H];A=HttpResponse();A.write(H.getvalue());A[_D]=_F.format(f"{I}.zip")
	else:A=HttpResponse();J=f"Could not download the folder {E}, please try again";K=_I;A.write(J);A[_D]=_F.format(K)
	return A
@csrf_exempt
@sparta_bde60771e2
def sparta_8049b2ca8f(request):
	B=request;D=B.GET[_E];E=B.GET[_B];F={_E:D,_B:base64.b64decode(E).decode(_G)};C=qube_c82989d216.sparta_a49acbaf67(F,B.user)
	if C[_C]==1:G=C['zip'];H=C[_H];A=HttpResponse();A.write(G.getvalue());A[_D]=_F.format(f"{H}.zip")
	else:A=HttpResponse();I='Could not download the application, please try again';J=_I;A.write(I);A[_D]=_F.format(J)
	return A