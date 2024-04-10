_L='stdout'
_K=False
_J='idle'
_I='busy'
_H='type'
_G='name'
_F='res'
_E='data'
_D='execution_state'
_C='output'
_B='content'
_A=None
import json,time,websocket,cloudpickle,base64,re
from django.conf import settings as conf_settings
from jupyter_client import KernelManager
from IPython.display import display,Javascript
from pprint import pprint
from IPython.core.magics.namespace import NamespaceMagics
from nbconvert.filters import strip_ansi
from project.sparta_0ed9d00fc8.qube_422fe9b100 import timeout
B_DEBUG=_K
def sparta_490cb10cb2():return conf_settings.DEFAULT_TIMEOUT
class KernelException(Exception):
	def __init__(B,message):
		A=message;super().__init__(A)
		if B_DEBUG:print('KernelException message');print(A)
		B.traceback_msg=A
	def get_traceback_errors(A):return A.traceback_msg
class IPythonKernel:
	def __init__(A):
		B='***********************************************************';print(B);print('Instantiate new Kernel');print(B);A.workspaceVarNameArr=[];A.kernel_manager=KernelManager();A.kernel_manager.start_kernel();A.kernel_client=A.kernel_manager.client();A.kernel_client.start_channels()
		try:A.kernel_client.wait_for_ready();print('Ready, initialize with Django');A.initialize_kernel()
		except RuntimeError:A.kernel_client.stop_channels();A.kernel_manager.shutdown_kernel()
	def get_kernel_manager(A):return A.kernel_manager
	def get_kernel_client(A):return A.kernel_client
	def initialize_kernel(B):A='import os\n';A+='import django\n';A+='os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"\n';A+='django.setup()\n';B.execute(A);B.execute(f"del os");B.execute(f"del django")
	def stop_kernel(A):A.kernel_client.stop_channels();A.kernel_manager.interrupt_kernel();A.kernel_manager.shutdown_kernel(now=True)
	def cd_to_notebook_folder(C,notebook_path,websocket=_A):B=notebook_path;A=f"import os, sys\n";A+=f"os.chdir('{B}')\n";A+=f"sys.path.insert(0, '{B}')";C.execute(A,websocket)
	def escape_ansi(C,line):A=re.compile('\\x1B(?:[@-Z\\\\-_]|\\[[0-?]*[ -/]*[@-~])');A=re.compile('(?:\\x1B[@-_]|[\\x80-\\x9F])[0-?]*[ -/]*[@-~]');A=re.compile('(\\x9B|\\x1B\\[)[0-?]*[ -/]*[@-~]');B='\\x1b((\\[\\??\\d+[hl])|([=<>a-kzNM78])|([\\(\\)][a-b0-2])|(\\[\\d{0,2}[ma-dgkjqi])|(\\[\\d+;\\d+[hfy]?)|(\\[;?[hf])|(#[3-68])|([01356]n)|(O[mlnp-z]?)|(/Z)|(\\d+)|(\\[\\?\\d;\\d0c)|(\\d;\\dR))';A=re.compile(B,flags=re.IGNORECASE);return A.sub('',line)
	def execute(E,cmd,websocket=_A,cell_id=_A):
		K='resJson';L='traceback';M='/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/*/';F='exec';G='service';H='cell_id';I=cell_id;C=websocket;S=E.kernel_client.execute(cmd);N=_I;D=_A
		while N!=_J and E.kernel_client.is_alive():
			try:
				O=E.kernel_client.get_iopub_msg()
				if not _B in O:continue
				A=O[_B]
				if B_DEBUG:print(M);print(type(A));print(A);print(A.keys());print(M)
				if L in A:
					if B_DEBUG:print('TRACEBACK RAISE EXCEPTION NOW')
					Q=re.compile('<ipython-input-\\d+-[0-9a-f]+>');P=[re.sub(Q,'<IPY-INPUT>',strip_ansi(A))for A in A[L]];D=KernelException('\n'.join(P))
					if C is not _A:B=json.dumps({_F:-1,H:I,G:F,'errorMsg':'\n'.join(P)});C.send(text_data=B)
				if _G in A:
					if A[_G]==_L:
						D=A['text']
						if C is not _A:
							J=E.format_output(D);B=json.dumps({_F:1,G:F,_C:J,H:I})
							if B_DEBUG:print(K);print(B)
							C.send(text_data=B)
				if _E in A:
					D=A[_E]
					if C is not _A:
						J=E.format_output(D);B=json.dumps({_F:1,G:F,_C:J,H:I})
						if B_DEBUG:print(K);print(B)
						C.send(text_data=B)
				if _D in A:N=A[_D]
			except Exception as R:print('Execute exception EXECUTION');print(R)
		return D
	def list_workspace_variables(C):
		E='preview'
		def H(data,trunc_size):B=trunc_size;A=data;A=A[:B]+'...'if len(A)>B else A;return A
		I='%whos';K=C.kernel_client.execute(I);F=_I;A=[]
		while F!=_J and C.kernel_client.is_alive():
			try:
				G=C.kernel_client.get_iopub_msg()
				if not _B in G:continue
				B=G[_B]
				if _G in B:
					if B[_G]==_L:A.append(B['text'])
				if _D in B:F=B[_D]
			except Exception as J:print(J);pass
		try:
			A=[A for A in A if len(A)>0];A=''.join(A).split('\n');A=A[2:-1];A=[re.split('\\s+',A)for A in A];A=[{_G:A[0],_H:A[1],E:' '.join(A[2:])}for A in A]
			for D in A:D['preview_display']=H(D[E],30);D['b_datasource']=_K
		except:pass
		return A
	def get_kernel_variable_repr(A,kernel_variable):
		F=f"{kernel_variable}";J=A.kernel_client.execute(F);C=_I;D=json.dumps({_F:-1})
		while C!=_J and A.kernel_client.is_alive():
			try:
				E=A.kernel_client.get_iopub_msg()
				if not _B in E:continue
				B=E[_B]
				if _E in B:G=B[_E];H=A.format_output(G);D=json.dumps({_F:1,_C:H})
				if _D in B:C=B[_D]
			except Exception as I:print(I);pass
		return D
	def format_output(E,output):
		C='image/png';D='text/html';B='text/plain';A=output
		if isinstance(A,dict):
			if D in A:return{_C:A[D],_H:D}
			if C in A:return{_C:A[C],_H:C}
			if B in A:return{_C:A[B],_H:B}
		return{_C:A,_H:B}
	def get_workspace_variable(A,kernel_variable):
		C=_A
		try:
			F=f"import cloudpickle\nimport base64\ntmp_sq_ans = _\nbase64.b64encode(cloudpickle.dumps({kernel_variable})).decode()";J=A.kernel_client.execute(F);D=_I
			while D!=_J and A.kernel_client.is_alive():
				try:
					E=A.kernel_client.get_iopub_msg()
					if not _B in E:continue
					B=E[_B]
					if _E in B:G=B[_E];H=A.format_output(G);C=cloudpickle.loads(base64.b64decode(H[_C]))
					if _D in B:D=B[_D]
				except Exception as I:print(I);pass
		except:pass
		A.execute(f"del tmp_sq_ans");A.execute(f"del cloudpickle");A.execute(f"del base64");return C
	def set_workspace_variable(A,name,value,websocket=_A):
		try:B=f'import cloudpickle\nimport base64\n{name} = cloudpickle.loads(base64.b64decode("{base64.b64encode(cloudpickle.dumps(value)).decode()}"))';A.execute(B,websocket)
		except Exception as C:print('Exception setWorkspaceVariable');print(C)
		A.execute(f"del cloudpickle");A.execute(f"del base64")
	def reset_kernel_workspace(A):B='%reset -f';A.execute(B)
	def execute_code(A,cmd,websocket=_A,cell_id=_A,bTimeout=_K):
		B=cell_id;C=websocket
		if bTimeout:return A.execute_code_timeout(cmd,websocket=C,cell_id=B)
		else:return A.execute_code_no_timeout(cmd,websocket=C,cell_id=B)
	@timeout(sparta_490cb10cb2())
	def execute_code_timeout(self,cmd,websocket=_A,cell_id=_A):return self.execute(cmd,websocket=websocket,cell_id=cell_id)
	def execute_code_no_timeout(A,cmd,websocket=_A,cell_id=_A):return A.execute(cmd,websocket=websocket,cell_id=cell_id)
	def getLastExecutedVariable(A,websocket):
		try:B=f"import cloudpickle\nimport base64\ntmp_sq_ans = _\nbase64.b64encode(cloudpickle.dumps(tmp_sq_ans)).decode()";return cloudpickle.loads(base64.b64decode(A.format_output(A.execute(B,websocket))))
		except Exception as C:print('Excep last exec val');raise C
	def get_kernel_variable(A,nameVar):
		try:B=f"import cloudpickle\nimport base64\ntmp_sq_ans = _\nbase64.b64encode(cloudpickle.dumps({nameVar})).decode()";return cloudpickle.loads(base64.b64decode(A.format_output(A.execute(B))))
		except Exception as C:print('Exception get_kernel_variable');print(C);return
	def removeWorkspaceVariable(A,name):
		try:del A.workspaceVarNameArr[name]
		except Exception as B:print('Exception removeWorkspaceVariable');print(B)
	def getWorkspaceVariables(A):return[]