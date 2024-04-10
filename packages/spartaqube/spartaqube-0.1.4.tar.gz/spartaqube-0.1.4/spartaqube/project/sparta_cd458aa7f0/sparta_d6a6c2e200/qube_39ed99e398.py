_K='plot_name'
_J='plot_chart_id'
_I='has_access'
_H=False
_G='session'
_F='plot_db_chart_obj'
_E='login'
_D='bCodeMirror'
_C='menuBar'
_B=None
_A=True
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a as qube_316bac807a
from project.sparta_25e81b3097.sparta_5f5d899812.qube_dc69199006 import sparta_7dc1413727
from project.sparta_25e81b3097.sparta_be54b67461 import qube_4f68fd90e5 as qube_4f68fd90e5
@csrf_exempt
@sparta_7dc1413727
@login_required(redirect_field_name=_E)
def sparta_55849df67e(request):
	B=request;C=B.GET.get('edit')
	if C is _B:C='-1'
	A=qube_316bac807a.sparta_a7855bf3fb(B);A[_C]=7;D=qube_316bac807a.sparta_ec1a87b7f8(B.user);A.update(D);A[_D]=_A;A['edit_chart_id']=C;return render(B,'dist/project/plot-db/plotDB.html',A)
@csrf_exempt
@sparta_7dc1413727
@login_required(redirect_field_name=_E)
def sparta_003fbeab78(request):
	A=request;C=A.GET.get('id');D=_H
	if C is _B:D=_A
	else:E=qube_4f68fd90e5.sparta_0520d3d8bd(C,A.user);D=not E[_I]
	if D:return sparta_55849df67e(A)
	B=qube_316bac807a.sparta_a7855bf3fb(A);B[_C]=7;F=qube_316bac807a.sparta_ec1a87b7f8(A.user);B.update(F);B[_D]=_A;B[_J]=C;G=E[_F];B[_K]=G.name;return render(A,'dist/project/plot-db/plotFull.html',B)
@csrf_exempt
@sparta_7dc1413727
@login_required(redirect_field_name=_E)
def sparta_2c7f0e4182(request):
	A=request;C='-1'
	try:C=A.GET.get(_G);C='-1'if C is _B else C
	except:pass
	E=A.GET.get('id');D=_H
	if E is _B:D=_A
	else:F=qube_4f68fd90e5.sparta_0520d3d8bd(E,A.user);D=not F[_I]
	if D:return sparta_55849df67e(A)
	B=qube_316bac807a.sparta_a7855bf3fb(A);B[_C]=7;H=qube_316bac807a.sparta_ec1a87b7f8(A.user);B.update(H);B[_D]=_A;G=F[_F];B[_J]=G.plot_chart_id;B[_K]=G.name;B[_G]=str(C);return render(A,'dist/project/plot-db/widgets.html',B)
@csrf_exempt
@sparta_7dc1413727
@login_required(redirect_field_name=_E)
def sparta_91b26c54f5(request):B=request;A=qube_316bac807a.sparta_a7855bf3fb(B);A[_C]=7;C=qube_316bac807a.sparta_ec1a87b7f8(B.user);A.update(C);A[_D]=_A;A[_G]=B.GET.get(_G);return render(B,'dist/project/plot-db/plotNewAPI.html',A)
@csrf_exempt
@sparta_7dc1413727
@login_required(redirect_field_name=_E)
def sparta_22e9650b80(request):
	G=',\n    ';B=request;C=B.GET.get('id');E=_H
	if C is _B:E=_A
	else:F=qube_4f68fd90e5.sparta_0520d3d8bd(C,B.user);E=not F[_I]
	if E:return sparta_55849df67e(B)
	K=qube_4f68fd90e5.sparta_5f4e0084cc(F[_F]);D='';H=0
	for(I,J)in K.items():
		if H>0:D+=G
		if J==1:D+=f"{I}=input_1"
		else:L=str(G.join([f"input_{A}"for A in range(J)]));D+=f"{I}=[{L}]"
		H+=1
	M=f'Spartaqube().get_widget(\n    "{C}"\n)';N=f'Spartaqube().plot_data(\n    "{C}",\n    {D}\n)';A=qube_316bac807a.sparta_a7855bf3fb(B);A[_C]=7;O=qube_316bac807a.sparta_ec1a87b7f8(B.user);A.update(O);A[_D]=_A;A[_J]=C;P=F[_F];A[_K]=P.name;A['plot_data_cmd']=M;A['plot_data_cmd_inputs']=N;return render(B,'dist/project/plot-db/plotNewAPISaved.html',A)