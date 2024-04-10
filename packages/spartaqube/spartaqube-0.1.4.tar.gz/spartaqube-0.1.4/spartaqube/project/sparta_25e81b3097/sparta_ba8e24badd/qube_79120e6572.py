_B='res'
_A='utf-8'
import os,json,base64,uuid,hashlib,cloudpickle
from random import randint
import pandas as pd
from cryptography.fernet import Fernet
from subprocess import PIPE
from datetime import datetime,timedelta
from django.contrib.auth.models import User
from django.db.models import Q
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared,CodeEditorNotebook
from project.models import ShareRights,UserProfile,NewPlotApiVariables
from project.sparta_25e81b3097.sparta_50ce1a8de2 import qube_9b698c371a as qube_9b698c371a
from project.sparta_25e81b3097.sparta_be54b67461 import qube_4f68fd90e5 as qube_4f68fd90e5
from project.sparta_25e81b3097.sparta_0a82db77e0.qube_6c72fd4753 import sparta_7c44a3e3d7
def sparta_65a7ca3055():B='spartaqube-api-key';A=B.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A.decode(_A)
def sparta_5c7a96095c():B='spartaqube-internal-decoder-api-key';A=B.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A.decode(_A)
def sparta_1ec083aa43(f,str_to_encrypt):B=str_to_encrypt.encode(_A);A=f.encrypt(B).decode(_A);A=base64.b64encode(A.encode(_A)).decode(_A);return A
def sparta_8709d2911e(api_token_id):
	A=api_token_id
	if A=='public':
		try:return User.objects.filter(username='public_spartaqube').all()[0]
		except:return
	try:
		C=Fernet(sparta_5c7a96095c().encode(_A));D=C.decrypt(base64.b64decode(A)).decode(_A).split('@')[1];B=UserProfile.objects.filter(api_key=D,is_banned=False).all()
		if B.count()==1:return B[0].user
		return
	except Exception as E:print('Could not authenticate api with error msg:');print(E);return
def sparta_9a0f29b1e3(json_data,user_obj):
	B=UserProfile.objects.get(user=user_obj);A=B.api_key
	if A is None:A=str(uuid.uuid4());B.api_key=A;B.save()
	D=json_data['domain'];E=str(randint(0,1000));C=f"apikey@{A}@{E}";F=Fernet(sparta_5c7a96095c().encode(_A));G=sparta_1ec083aa43(F,C);C=f"apikey@{D}@{G}";H=Fernet(sparta_65a7ca3055().encode(_A));I=sparta_1ec083aa43(H,C);return{_B:1,'token':I}
def sparta_d64bc47fe8(json_data,user_obj):A=UserProfile.objects.get(user=user_obj);B=str(uuid.uuid4());A.api_key=B;A.save();return{_B:1}
def sparta_8a23fd1002(json_data,user_obj):
	D=json_data['session'];A=NewPlotApiVariables.objects.filter(session_id=D).all();print(f"new_plot_api_variables_set with session_id {D}");print(A)
	if A.count()>0:
		E=A[0];F=E.pickled_variables;G=cloudpickle.loads(F.encode('latin1'));B=[]
		for H in G:
			C=sparta_7c44a3e3d7(H)
			if C is not None:0
			else:C=pd.DataFrame()
			B.append(C.to_json(orient='split',date_format='iso'))
		print(B);return{_B:1,'notebook_variables':B}
	return{_B:-1}
def sparta_a2d278c262(json_data,user_obj):
	C=user_obj;D=json_data;A=D['api_service']
	if A=='get_status':B=sparta_b8eaa119ee()
	elif A=='get_library':B=sparta_af5d0f31e7()
	elif A=='get_widgets':B=sparta_90a9d089de(C)
	elif A=='get_widget_data':return sparta_33542eda51(D,C)
	elif A=='new_plot_api_variables':return sparta_0ca1eb6dc8(D,C)
	elif A=='get_connectors':B=sparta_5848d4a096()
	elif A=='get_data_from_connector':B=sparta_723520f593()
	return{_B:1,'output':B}
def sparta_b8eaa119ee():return 1
def sparta_af5d0f31e7():return[1,2,3]
def sparta_90a9d089de(user_obj):return qube_4f68fd90e5.sparta_cbf5f30f17(user_obj)
def sparta_33542eda51(json_data,user_obj):return qube_4f68fd90e5.sparta_541bb65deb(json_data,user_obj)
def sparta_0ca1eb6dc8(json_data,user_obj):A=datetime.now().astimezone(UTC);B=str(uuid.uuid4());C=json_data['data'];NewPlotApiVariables.objects.create(user=user_obj,session_id=B,pickled_variables=C,date_created=A,last_update=A);return{_B:1,'session_id':B}
def sparta_0deffb89ed():return[1,2,3]
def sparta_5848d4a096():return[1,2,3]
def sparta_723520f593():return[1,2,3]