import json,base64,asyncio,subprocess,uuid,requests,pandas as pd
from subprocess import PIPE
from django.db.models import Q
from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from project.models_spartaqube import DBConnector,DBConnectorUserShared,PlotDBChart,PlotDBChartShared
from project.models import ShareRights
from project.sparta_25e81b3097.sparta_50ce1a8de2 import qube_9b698c371a as qube_9b698c371a
from project.sparta_25e81b3097.sparta_3007b0e958 import qube_292124302a
from project.sparta_25e81b3097.sparta_be54b67461 import qube_090f252a01 as qube_090f252a01
from project.sparta_25e81b3097.sparta_3007b0e958.qube_e57b60034d import Connector as Connector
def sparta_15088311fc(json_data,user_obj):
	B='key';A=json_data;print('Call autocompelte api');print(A);C=A[B];E=A['api_func'];D=[]
	if E=='tv_symbols':D=sparta_a6ff44a99b(C)
	return{'res':1,'output':D,B:C}
def sparta_a6ff44a99b(key_symbol):
	C='</em>';D='<em>';B='symbol_id';G=f"https://symbol-search.tradingview.com/symbol_search/v3/?text={key_symbol}&hl=1&exchange=&lang=en&search_type=undefined&domain=production&sort_by_country=US";E=requests.get(G)
	try:
		if int(E.status_code)==200:
			H=json.loads(E.text);F=H['symbols']
			for A in F:A[B]=A['symbol'].replace(D,'').replace(C,'');A['title']=A[B];A['subtitle']=A['description'].replace(D,'').replace(C,'');A['value']=A[B]
			return F
		return[]
	except:return[]