_A6='plot_db_chart_obj'
_A5='code_editor_notebook_cells'
_A4='chart_config'
_A3='chart_params'
_A2='plot_library'
_A1='has_write_rights'
_A0='chartConfigDict'
_z='chartParams'
_y='dataSourceArr'
_x='typeChart'
_w='has_access'
_v='data_source_list'
_u='date_created'
_t='last_update'
_s='is_static_data'
_r='is_expose_widget'
_q='slug'
_p='bExposeAsWidget'
_o='plotDes'
_n='bStaticDataPlot'
_m='codeEditorNotebookCells'
_l='bApplyFilter'
_k='table_name'
_j='password'
_i='is_owner'
_h='xAxis'
_g='has_widget_password'
_f='type_chart'
_e='plotName'
_d='widgetPassword'
_c='split'
_b='You do not have access to this connector'
_a='db_engine'
_Z='redis_db'
_Y='socket_url'
_X='json_url'
_W='read_only'
_V='csv_delimiter'
_U='csv_path'
_T='database_path'
_S='library_arctic'
_R='keyspace'
_Q='oracle_service_name'
_P='database'
_O='user'
_N='port'
_M='host'
_L='%Y-%m-%d'
_K='errorMsg'
_J='connector_id'
_I='bWidgetPassword'
_H='description'
_G='name'
_F='data'
_E='plot_chart_id'
_D=False
_C=True
_B=None
_A='res'
import re,json,base64,asyncio,subprocess,tinykernel,cloudpickle,uuid,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from django.utils.text import slugify
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared,CodeEditorNotebook,NewPlotApiVariables
from project.models import ShareRights
from project.sparta_25e81b3097.sparta_50ce1a8de2 import qube_9b698c371a as qube_9b698c371a
from project.sparta_25e81b3097.sparta_3007b0e958 import qube_292124302a
from project.sparta_25e81b3097.sparta_be54b67461 import qube_090f252a01 as qube_090f252a01
from project.sparta_25e81b3097.sparta_3007b0e958.qube_e57b60034d import Connector as Connector
INPUTS_KEYS=[_h,'yAxisArr','labelsArr','radiusBubbleArr','rangesAxisArr','measuresAxisArr','markersAxisArr']
def sparta_0c4c8f0657(user_obj):
	A=qube_9b698c371a.sparta_df75aac471(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_ff2da64ac7(json_data,user_obj):
	B=user_obj;D=sparta_0c4c8f0657(B)
	if len(D)>0:C=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=D,db_connector__is_delete=0)|Q(is_delete=0,user=B,db_connector__is_delete=0))
	else:C=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0)
	E=[]
	if C.count()>0:
		for F in C:A=F.db_connector;E.append({_J:A.connector_id,_M:A.host,_N:A.port,_O:A.user,_P:A.database,_Q:A.oracle_service_name,_R:A.keyspace,_S:A.library_arctic,_T:A.database_path,_U:A.csv_path,_V:A.csv_delimiter,_W:A.read_only,_X:A.json_url,_Y:A.socket_url,_Z:A.redis_db,_a:A.db_engine,_G:A.name,_H:A.description,_i:F.is_owner})
	return{_A:1,'db_connectors':E}
def sparta_f61f16b553():return{_A:1,'available_engines':qube_292124302a.sparta_f61f16b553()}
def sparta_c0787e8889(json_data):
	A=json_data;B=''
	try:C=Connector(db_engine=A[_a]);C.init_with_params(host=A[_M],port=A[_N],user=A[_O],password=A[_j],database=A[_P],oracle_service_name=A[_Q],csv_path=A[_U],csv_delimiter=A[_V],keyspace=A[_R],library_arctic=A[_S],database_path=A[_T],read_only=A[_W],json_url=A[_X],socket_url=A[_Y],redis_db=A[_Z]);D=C.test_connection()
	except Exception as E:D=_D;B=str(E)
	return{_A:1,'is_connector_working':D,_K:B}
def sparta_d37e08d2ec(json_data,user_obj):A=json_data;B=datetime.now().astimezone(UTC);C=str(uuid.uuid4());D=DBConnector.objects.create(connector_id=C,host=A[_M],port=A[_N],user=A[_O],password_e=qube_292124302a.sparta_e594220c6d(A[_j]),database=A[_P],oracle_service_name=A[_Q],keyspace=A[_R],library_arctic=A[_S],database_path=A[_T],csv_path=A[_U],csv_delimiter=A[_V],read_only=A[_W],json_url=A[_X],socket_url=A[_Y],redis_db=A[_Z],db_engine=A[_a],name=A[_G],description=A[_H],date_created=B,last_update=B);E=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=B);DBConnectorUserShared.objects.create(db_connector=D,user=user_obj,date_created=B,share_rights=E,is_owner=_C);return{_A:1}
def sparta_b9b0a8db1a(json_data,user_obj):
	C=user_obj;B=json_data;H=B[_J];D=DBConnector.objects.filter(connector_id=H,is_delete=_D).all()
	if D.count()>0:
		A=D[D.count()-1];F=sparta_0c4c8f0657(C)
		if len(F)>0:E=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=F,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=C,db_connector__is_delete=0,db_connector=A))
		else:E=DBConnectorUserShared.objects.filter(is_delete=0,user=C,db_connector__is_delete=0,db_connector=A)
		if E.count()>0:
			I=E[0];G=I.share_rights
			if G.is_admin or G.has_write_rights:J=datetime.now().astimezone(UTC);A.host=B[_M];A.port=B[_N];A.user=B[_O];A.password_e=qube_292124302a.sparta_e594220c6d(B[_j]);A.database=B[_P];A.oracle_service_name=B[_Q];A.keyspace=B[_R];A.library_arctic=B[_S];A.database_path=B[_T];A.csv_path=B[_U];A.csv_delimiter=B[_V];A.read_only=B[_W];A.json_url=B[_X];A.socket_url=B[_Y];A.redis_db=B[_Z];A.db_engine=B[_a];A.name=B[_G];A.description=B[_H];A.last_update=J;A.save()
	return{_A:1}
def sparta_8bb5e2db49(json_data,user_obj):
	B=user_obj;F=json_data[_J];C=DBConnector.objects.filter(connector_id=F,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];E=sparta_0c4c8f0657(B)
		if len(E)>0:D=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=E,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A))
		else:D=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A)
		if D.count()>0:
			G=D[0];H=G.share_rights
			if H.is_admin:A.is_delete=_C;A.save()
	return{_A:1}
def sparta_9a3eda7bad(connector_id,user_obj):
	B=user_obj;C=DBConnector.objects.filter(connector_id=connector_id,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];D=sparta_0c4c8f0657(B)
		if len(D)>0:E=DBConnectorUserShared.objects.filter(Q(is_delete=0,user_group__in=D,db_connector__is_delete=0,db_connector=A)|Q(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A))
		else:E=DBConnectorUserShared.objects.filter(is_delete=0,user=B,db_connector__is_delete=0,db_connector=A)
		if E.count()>0:return A
def sparta_e50890ff8d(json_data,user_obj):
	C=json_data[_J];A=sparta_9a3eda7bad(C,user_obj)
	if A is _B:return{_A:-1,_K:_b}
	B=Connector(db_engine=A.db_engine);B.init_with_model(A);D=B.get_available_tables();return{_A:1,'tables_explorer':D}
def sparta_c4a839d982(json_data,user_obj):
	A=json_data;H=A[_J];E=A[_k];F=A[_l];B=[];C=sparta_9a3eda7bad(H,user_obj)
	if C is _B:return{_A:-1,_K:_b}
	D=Connector(db_engine=C.db_engine);D.init_with_model(C)
	if F:
		if F:0
		else:G=D.get_data_table(E)
		I=list(I.columns)
		for(J,K)in zip(G.columns,G.dtypes):L={_G:J,'type':str(K)};B.append(L)
	else:B=D.get_table_columns(E)
	return{_A:1,'table_columns':B}
def sparta_93cf4e2ed4(json_data,user_obj):
	A=json_data;G=A[_J];D=A[_k];E=A[_l];B=sparta_9a3eda7bad(G,user_obj)
	if B is _B:return{_A:-1,_K:_b}
	C=Connector(db_engine=B.db_engine);C.init_with_model(B)
	if E:
		if E:0
		else:F=C.get_data_table(D)
	else:F=C.get_data_table(D)
	return{_A:1,_F:F.to_json(orient=_c,date_format='iso')}
def sparta_cfce35859b(json_data,user_obj):
	A=json_data;G=A[_J];D=A[_k];E=A[_l];B=sparta_9a3eda7bad(G,user_obj)
	if B is _B:return{_A:-1,_K:_b}
	C=Connector(db_engine=B.db_engine);C.init_with_model(B)
	if E:
		if E:0
		else:F=C.get_data_table(D)
	else:F=C.get_data_table(D)
	H=F.describe();return{_A:1,_F:H.to_json(orient=_c)}
def sparta_f25bd6beec(json_data,user_obj):
	A=json_data;print('SAVE json_data');print(A);J=A[_I];D=_B
	if J:D=A[_d];D=qube_090f252a01.sparta_fd2ae7f85e(D)
	K=A[_m];L=str(uuid.uuid4());C=datetime.now().astimezone(UTC);M=CodeEditorNotebook.objects.create(notebook_id=L,cells=K,date_created=C,last_update=C);E=str(uuid.uuid4());F=A[_n];G=A['is_new_plot_api']
	if G:F=_C
	B=A['plotSlug']
	if len(B)==0:B=A[_e]
	H=slugify(B);B=H;I=1
	while PlotDBChart.objects.filter(slug=B).exists():B=f"{H}-{I}";I+=1
	N=PlotDBChart.objects.create(plot_chart_id=E,type_chart=A[_x],name=A[_e],slug=B,description=A[_o],is_expose_widget=A[_p],is_static_data=F,has_widget_password=A[_I],widget_password_e=D,data_source_list=A[_y],chart_params=A[_z],chart_config=A[_A0],code_editor_notebook=M,is_created_from_api=G,date_created=C,last_update=C);O=ShareRights.objects.create(is_admin=_C,has_write_rights=_C,has_reshare_rights=_C,last_update=C);PlotDBChartShared.objects.create(plot_db_chart=N,user=user_obj,share_rights=O,is_owner=_C,date_created=C);return{_A:1,_E:E}
def sparta_dc063c4032(json_data,user_obj):
	E=user_obj;B=json_data;K=B[_E];F=PlotDBChart.objects.filter(plot_chart_id=K,is_delete=_D).all()
	if F.count()>0:
		A=F[F.count()-1];H=sparta_0c4c8f0657(E)
		if len(H)>0:G=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=H,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:G=PlotDBChartShared.objects.filter(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A)
		if G.count()>0:
			L=G[0];I=L.share_rights
			if I.is_admin or I.has_write_rights:
				M=B[_I];C=_B
				if M:C=B[_d];C=qube_090f252a01.sparta_fd2ae7f85e(C)
				J=datetime.now().astimezone(UTC);A.type_chart=B[_x];A.name=B[_e];A.description=B[_o];A.is_expose_widget=B[_p];A.is_static_data=B[_n];A.has_widget_password=B[_I];A.widget_password_e=C;A.data_source_list=B[_y];A.chart_params=B[_z];A.chart_config=B[_A0];A.last_update=J;A.save();D=A.code_editor_notebook
				if D is not _B:D.cells=B[_m];D.last_update=J;D.save()
	return{_A:1}
def sparta_e36843de88(json_data,user_obj):0
def sparta_1e2541bd29(json_data,user_obj):
	B=user_obj;D=sparta_0c4c8f0657(B)
	if len(D)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=D,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0))
	else:E=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0)
	F=[]
	for C in E:
		A=C.plot_db_chart;I=C.share_rights;G=_B
		try:G=str(A.last_update.strftime(_L))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_L))
		except Exception as J:print(J)
		F.append({_E:A.plot_chart_id,_f:A.type_chart,_G:A.name,_q:A.slug,_H:A.description,_r:A.is_expose_widget,_s:A.is_static_data,_g:A.has_widget_password,_i:C.is_owner,_A1:I.has_write_rights,_t:G,_u:H})
	return{_A:1,_A2:F}
def exec_notebook_and_get_workspace_variables(full_code,data_source_variables,workspace_variables):
	B=dict();A=tinykernel.TinyKernel()
	for(D,E)in data_source_variables.items():A;A.glb[D]=E
	A(full_code)
	for C in workspace_variables:B[C]=A(C)
	return B
def sparta_c3252b51ff(json_data,user_obj):
	L='kernelVariableName';M='isNotebook';C=user_obj;E=json_data[_E];F=PlotDBChart.objects.filter(plot_chart_id__startswith=E,is_delete=_D).all()
	if F.count()==1:
		A=F[F.count()-1];E=A.plot_chart_id;N=sparta_0c4c8f0657(C)
		if len(N)>0:G=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=N,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:G=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=A)
		if G.count()>0:
			H=[];S=G[0];A=S.plot_db_chart;T=A.is_static_data
			if T:0
			else:
				for B in A.data_source_list:
					I=B[M]
					if I:H.append(B[L])
					else:
						O=sparta_93cf4e2ed4(B,C)
						if O[_A]==1:U=O[_F];B[_F]=U
			P=A.code_editor_notebook
			if P is not _B:D=P.cells
			else:D=_B
			if len(H)>0:
				if D is not _B:
					V='\n'.join([A['code']for A in json.loads(D)]);R=dict()
					for J in A.data_source_list:
						if J['isDataSource']:K=json.loads(J[_F]);R[J['table_name_workspace']]=pd.DataFrame(K[_F],index=K['index'],columns=K['columns'])
					W=exec_notebook_and_get_workspace_variables(V,R,H)
					for B in A.data_source_list:
						I=B[M]
						if I:X=W[B[L]];B[_F]=X.to_json(orient=_c)
			def Y(s):s=s.lower();A='-_.() %s%s'%(re.escape('/'),re.escape('\\'));B=re.sub('[^A-Za-z0-9%s]'%A,'_',s);return B
			return{_A:1,_E:E,_f:A.type_chart,_G:A.name,_q:A.slug,'name_file':Y(A.name),_H:A.description,_r:A.is_expose_widget,_s:A.is_static_data,_g:A.has_widget_password,_v:A.data_source_list,_A3:A.chart_params,_A4:A.chart_config,_A5:D}
	return{_A:-1}
def sparta_a3dfbe2804(json_data,user_obj):
	R='column';S='is_index';T=json_data;J=user_obj;E='uuid'
	try:
		U=T[_E];Z=T['session_id'];K=PlotDBChart.objects.filter(plot_chart_id=U,is_delete=_D).all()
		if K.count()>0:
			A=K[K.count()-1];V=sparta_0c4c8f0657(J)
			if len(V)>0:L=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=V,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=J,plot_db_chart__is_delete=0,plot_db_chart=A))
			else:L=PlotDBChartShared.objects.filter(is_delete=0,user=J,plot_db_chart__is_delete=0,plot_db_chart=A)
			if L.count()>0:
				a=L[0];A=a.plot_db_chart;W=NewPlotApiVariables.objects.filter(session_id=Z).all()
				if W.count()>0:
					b=W[0];c=b.pickled_variables;F=cloudpickle.loads(c.encode('latin1'));G=dict()
					for H in A.data_source_list:C=H[E];G[C]=pd.DataFrame()
					M=json.loads(A.chart_config)
					for B in M.keys():
						if B in INPUTS_KEYS:
							if B==_h:
								N=M[B];C=N[E];O=N[S];P=N[R];D=G[C]
								if O:D.index=F[B]
								else:D[P]=F[B]
							else:
								d=M[B]
								for(X,I)in enumerate(d):
									if I is not _B:
										C=I[E];O=I[S];P=I[R];D=G[C]
										if O:D.index=F[B][X]
										else:D[P]=F[B][X]
					for H in A.data_source_list:C=H[E];H[_F]=G[C].to_json(orient=_c)
				return{_A:1,_E:U,_f:A.type_chart,_G:A.name,_H:A.description,_r:A.is_expose_widget,_s:A.is_static_data,_g:A.has_widget_password,_v:A.data_source_list,_A3:A.chart_params,_A4:A.chart_config,_A5:_B}
	except Exception as Y:print('Error exception > '+str(Y));return{_A:-1,_K:str(Y)}
def sparta_d7d077fbe4(json_data,user_obj):
	A=user_obj;G=json_data[_E];B=PlotDBChart.objects.filter(plot_chart_id=G,is_delete=_D).all()
	if B.count()>0:
		C=B[B.count()-1];E=sparta_0c4c8f0657(A)
		if len(E)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart=C)|Q(is_delete=0,user=A,plot_db_chart__is_delete=0,plot_db_chart=C))
		else:D=PlotDBChartShared.objects.filter(is_delete=0,user=A,plot_db_chart__is_delete=0,plot_db_chart=C)
		if D.count()>0:F=D[0];F.is_delete=_C;F.save()
	return{_A:1}
def sparta_0520d3d8bd(plot_chart_id,user_obj):
	F=plot_chart_id;C=user_obj;A=PlotDBChart.objects.filter(plot_chart_id__startswith=F,is_delete=_D).all();D=_D
	if A.count()==1:D=_C
	else:
		H=F;A=PlotDBChart.objects.filter(slug__startswith=H,is_delete=_D).all()
		if A.count()==1:D=_C
	if D:
		B=A[A.count()-1];G=sparta_0c4c8f0657(C)
		if len(G)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=B)|Q(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=B))
		else:E=PlotDBChartShared.objects.filter(is_delete=0,user=C,plot_db_chart__is_delete=0,plot_db_chart=B)
		if E.count()>0:I=E[0];B=I.plot_db_chart;return{_A:1,_w:_C,_A6:B}
	return{_A:1,_w:_D}
def sparta_5f4e0084cc(plot_db_chart_obj):
	C=json.loads(plot_db_chart_obj.chart_config);B=dict()
	for A in C.keys():
		if A in INPUTS_KEYS:
			if A==_h:B[A]=1
			else:
				D=len([A for A in C[A]if A is not _B])
				if D>0:B[A]=D
	return B
def sparta_043866cc31(json_data,user_obj):
	B=user_obj;D=sparta_0c4c8f0657(B)
	if len(D)>0:E=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=D,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__is_expose_widget=_C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C))
	else:E=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C)
	F=[]
	for C in E:
		A=C.plot_db_chart;I=C.share_rights;G=_B
		try:G=str(A.last_update.strftime(_L))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_L))
		except Exception as J:print(J)
		F.append({_E:A.plot_chart_id,_f:A.type_chart,_g:A.has_widget_password,_G:A.name,_q:A.slug,_H:A.description,_i:C.is_owner,_A1:I.has_write_rights,_t:G,_u:H})
	return{_A:1,_A2:F}
def sparta_3f8eedb01d(json_data,user_obj):
	E=user_obj;B=json_data;K=B[_E];L=B['isCalledFromLibrary'];F=PlotDBChart.objects.filter(plot_chart_id=K,is_delete=_D).all()
	if F.count()>0:
		A=F[F.count()-1];H=sparta_0c4c8f0657(E)
		if len(H)>0:G=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=H,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:G=PlotDBChartShared.objects.filter(is_delete=0,user=E,plot_db_chart__is_delete=0,plot_db_chart=A)
		if G.count()>0:
			M=G[0];I=M.share_rights
			if I.is_admin or I.has_write_rights:
				N=B[_I];C=_B
				if N:C=B[_d];C=qube_090f252a01.sparta_fd2ae7f85e(C)
				J=datetime.now().astimezone(UTC);A.has_widget_password=B[_I];A.widget_password_e=C;A.name=B[_e];A.plotDes=B[_o];A.is_expose_widget=B[_p];A.is_static_data=B[_n];A.last_update=J;A.save()
				if L:0
				else:
					D=A.code_editor_notebook
					if D is not _B:D.cells=B[_m];D.last_update=J;D.save()
	return{_A:1}
def sparta_ecfb9a3303(json_data,user_obj):
	D=user_obj;B=json_data;I=B[_E];E=PlotDBChart.objects.filter(plot_chart_id=I,is_delete=_D).all()
	if E.count()>0:
		A=E[E.count()-1];G=sparta_0c4c8f0657(D)
		if len(G)>0:F=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:F=PlotDBChartShared.objects.filter(is_delete=0,user=D,plot_db_chart__is_delete=0,plot_db_chart=A)
		if F.count()>0:
			J=F[0];H=J.share_rights
			if H.is_admin or H.has_write_rights:
				K=B[_I];C=_B
				if K:C=B[_d];C=qube_090f252a01.sparta_fd2ae7f85e(C)
				L=datetime.now().astimezone(UTC);A.has_widget_password=B[_I];A.widget_password_e=C;A.last_update=L;A.save()
	return{_A:1}
def sparta_3a79edae46(json_data,user_obj):
	B=user_obj;G=json_data[_E];C=PlotDBChart.objects.filter(plot_chart_id=G,is_delete=_D).all()
	if C.count()>0:
		A=C[C.count()-1];E=sparta_0c4c8f0657(B)
		if len(E)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=E,plot_db_chart__is_delete=0,plot_db_chart=A)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A))
		else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart=A)
		if D.count()>0:
			H=D[0];F=H.share_rights
			if F.is_admin or F.has_write_rights:I=datetime.now().astimezone(UTC);A.is_expose_widget=_D;A.last_update=I;A.save()
	return{_A:1}
def sparta_cbf5f30f17(user_obj):
	B=user_obj;C=sparta_0c4c8f0657(B)
	if len(C)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=C,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__is_expose_widget=_C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C))
	else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__is_expose_widget=_C)
	E=[]
	for F in D:
		A=F.plot_db_chart;J=F.share_rights;G=_B
		try:G=str(A.last_update.strftime(_L))
		except:pass
		H=_B
		try:H=str(A.date_created.strftime(_L))
		except Exception as I:print(I)
		E.append({'id':A.plot_chart_id,_G:A.name,_H:A.description,_t:G,_u:H})
	return E
def sparta_541bb65deb(json_data,user_obj):
	B=user_obj;A=json_data;C=sparta_0520d3d8bd(A['widget_id'],B);D=C[_w]
	if D:E=C[_A6];A[_E]=E.plot_chart_id;F=sparta_c3252b51ff(A,B);return{_A:1,_F:[A[_F]for A in F[_v]]}
	return{_A:-1}