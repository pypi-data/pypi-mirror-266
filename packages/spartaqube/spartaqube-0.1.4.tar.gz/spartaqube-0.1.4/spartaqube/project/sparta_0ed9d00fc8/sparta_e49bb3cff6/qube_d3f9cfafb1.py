_B=True
_A=None
import os,json,platform,websocket,threading,time,pandas as pd
from project.sparta_25e81b3097.sparta_a8d141ad6b.qube_074d5bdef3 import IPythonKernel as IPythonKernel
from project.sparta_25e81b3097.sparta_a8d141ad6b.qube_82c76e4ac9 import sparta_1c32cb2bab
from project.sparta_25e81b3097.sparta_0a82db77e0.qube_6c72fd4753 import sparta_7c44a3e3d7
IS_WINDOWS=False
if platform.system()=='Windows':IS_WINDOWS=_B
from channels.generic.websocket import WebsocketConsumer
from project.sparta_0ed9d00fc8.sparta_3b136f3c7e import qube_316bac807a as qube_316bac807a
from project.sparta_25e81b3097.sparta_0a82db77e0 import qube_6c72fd4753 as qube_6c72fd4753
class NotebookWS(WebsocketConsumer):
	channel_session=_B;http_user_and_session=_B
	def connect(A):print('Connect Now');A.accept();A.user=A.scope['user'];A.json_data_dict=dict();A.kernel_obj=_A
	def disconnect(A,close_code):
		print('Disconnect')
		try:A.kernel_obj.stop_kernel()
		except Exception as B:print('Exception disconnect kernel');print(B)
		A.kernel_obj=_A
	def start_kernel(A):
		B=False
		if A.kernel_obj is _A:B=_B
		elif not A.kernel_obj.get_kernel_client().is_alive():B=_B;A.kernel_obj.stop_kernel()
		print('bStartIpythonKernel  > > > '+str(B))
		if B:A.kernel_obj=IPythonKernel()
	def receive(A,text_data):
		K='name';L='value';M='cellId';N='cellCode';O=text_data;H='kernel_variable_arr';G='res';F='service'
		if len(O)>0:
			D=json.loads(O);print(f"NOTEBOOK KERNEL json_data");print(D);B=D[F]
			if B=='init-socket':E={G:1,F:B};A.start_kernel();C=json.dumps(E);A.send(text_data=C);return
			elif B=='exec':
				if A.kernel_obj is _A:A.start_kernel()
				R=time.time();print('='*50);A.kernel_obj.execute(D[N],websocket=A,cell_id=D[M])
				try:P=sparta_1c32cb2bab(D[N])
				except:P=[]
				print('='*50);S=time.time()-R;C=json.dumps({G:2,F:B,'elapsed_time':round(S,2),'cell_id':D[M],'updated_plot_variables':P});A.send(text_data=C)
			elif B=='reset':
				if A.kernel_obj is _A:A.start_kernel()
				A.kernel_obj.reset_kernel_workspace();E={G:1,F:B};C=json.dumps(E);A.send(text_data=C)
			elif B=='workspace-list':
				if A.kernel_obj is _A:A.start_kernel()
				T=A.kernel_obj.list_workspace_variables();E={G:1,F:B,'workspace_variables':T};E.update(D);C=json.dumps(E);A.send(text_data=C)
			elif B=='workspace-get-variable-as-df':
				if A.kernel_obj is _A:A.start_kernel()
				Q=[]
				for U in D[H]:
					V=A.kernel_obj.get_workspace_variable(kernel_variable=U);I=sparta_7c44a3e3d7(V)
					if I is not _A:0
					else:I=pd.DataFrame()
					Q.append(I.to_json(orient='split',date_format='iso'))
				E={G:1,F:B,H:D[H],'workspace_variable_arr':Q};C=json.dumps(E);A.send(text_data=C)
			elif B=='workspace-get-variable':
				if A.kernel_obj is _A:A.start_kernel()
				W=A.kernel_obj.get_kernel_variable_repr(kernel_variable=D['kernel_variable']);E={G:1,F:B,'workspace_variable':W};C=json.dumps(E);A.send(text_data=C)
			elif B=='workspace-set-variable-from-datasource':
				if A.kernel_obj is _A:A.start_kernel()
				J=json.loads(D[L]);X=pd.DataFrame(J['data'],columns=J['columns'],index=J['index']);A.kernel_obj.set_workspace_variable(name=D[K],value=X);E={G:1,F:B};C=json.dumps(E);A.send(text_data=C)
			elif B=='workspace-set-variable':
				if A.kernel_obj is _A:A.start_kernel()
				A.kernel_obj.set_workspace_variable(name=D[K],value=json.loads(D[L]));E={G:1,F:B};C=json.dumps(E);A.send(text_data=C)