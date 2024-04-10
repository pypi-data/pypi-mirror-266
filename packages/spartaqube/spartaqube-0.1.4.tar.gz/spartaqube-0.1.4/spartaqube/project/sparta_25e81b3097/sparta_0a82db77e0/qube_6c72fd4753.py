import os,shutil,requests,simplejson as json,datetime,pandas as pd
def sparta_bbd6410fbf(textOutputArr):
	A=textOutputArr
	try:A=[A for A in A if len(A)>0];A=[A for A in A if A!='Welcome to SpartaQuant API'];A=[A for A in A if A!="<span style='color:#0ab70a'>You are logged</span>"];A=[A for A in A if A!='You are logged']
	except Exception as B:pass
	return A
def sparta_c9493c9f38(input2JsonEncode,dateFormat=None):
	C=dateFormat;import numpy as B
	class D(json.JSONEncoder):
		def default(E,obj):
			A=obj
			if isinstance(A,B.integer):return int(A)
			if isinstance(A,B.floating):return float(A)
			if isinstance(A,B.ndarray):return A.tolist()
			if isinstance(A,datetime.datetime):
				if C is not None:return A.strftime(C)
				else:return str(A)
			return super(D,E).default(A)
	A=json.dumps(input2JsonEncode,ignore_nan=True,cls=D);return A
def sparta_2e3901f254(path):
	A=path
	try:os.rmdir(A)
	except:
		try:os.system('rmdir /S /Q "{}"'.format(A))
		except:
			try:shutil.rmtree(A)
			except:
				try:os.remove(A)
				except:pass
def sparta_e97ef55b01(file_path):
	A=file_path
	try:os.remove(A);print(f"File '{A}' has been deleted.")
	except Exception as B:
		try:os.unlink(A);print(f"File '{A}' has been forcefully deleted.")
		except Exception as B:print(f"An error occurred while deleting the file: {B}")
def sparta_7c44a3e3d7(input_data):
	A=input_data
	try:
		if isinstance(A,pd.DataFrame):return A
		if isinstance(A,pd.Series):return A.to_frame()
		if isinstance(A,dict):return pd.DataFrame.from_dict(A)
		if isinstance(A,(list,tuple)):return pd.DataFrame(A)
		if'numpy'in str(type(A)).lower():return pd.DataFrame(A)
		if isinstance(A,(int,str,float,bool,complex,type(None),bytes,bytearray,pd.Timestamp,pd.Timedelta,pd.Period,pd.Interval,pd.Categorical,pd.IntervalDtype,pd.CategoricalDtype,pd.SparseDtype,pd.Int8Dtype,pd.Int16Dtype,pd.Int32Dtype,pd.Int64Dtype,pd.UInt8Dtype,pd.UInt16Dtype,pd.UInt32Dtype,pd.UInt64Dtype,pd.Float32Dtype,pd.Float64Dtype,pd.BooleanDtype,pd.StringDtype,pd.offsets.DateOffset)):return pd.DataFrame([A])
		try:return pd.DataFrame([A])
		except:return
	except Exception as B:print(f"Error: {B}");return