import os,json,base64,subprocess,pandas as pd
from datetime import datetime,timedelta
from dateutil import parser
import pytz
UTC=pytz.utc
from django.db.models import Q
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from django.utils.text import Truncator
from django.db.models import CharField,TextField
from django.db.models.functions import Lower
CharField.register_lookup(Lower)
TextField.register_lookup(Lower)
from project.models import User,UserProfile,PlotDBChart,PlotDBChartShared
from project.sparta_25e81b3097.sparta_50ce1a8de2 import qube_9b698c371a as qube_9b698c371a
from project.sparta_25e81b3097.sparta_1a62ce0548 import qube_3e70a69d94 as qube_3e70a69d94
def sparta_0c4c8f0657(user_obj):
	A=qube_9b698c371a.sparta_df75aac471(user_obj)
	if len(A)>0:B=[A.user_group for A in A]
	else:B=[]
	return B
def sparta_00d318cbc1(json_data,user_obj):
	E='widgets';B=user_obj;C=json_data['keyword'].lower();F=120;G=sparta_0c4c8f0657(B)
	if len(G)>0:D=PlotDBChartShared.objects.filter(Q(is_delete=0,user_group__in=G,plot_db_chart__is_delete=0,plot_db_chart=A,plot_db_chart__name__lower__icontains=C)|Q(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=C))
	else:D=PlotDBChartShared.objects.filter(is_delete=0,user=B,plot_db_chart__is_delete=0,plot_db_chart__name__lower__icontains=C)
	K=D.count();H=[]
	for L in D[:5]:A=L.plot_db_chart;H.append({'plot_chart_id':A.plot_chart_id,'type_chart':A.type_chart,'name':A.name,'name_trunc':Truncator(A.name).chars(F),'description':A.description,'description_trunc':Truncator(A.description).chars(F)})
	I=0;J={E:K}
	for(N,M)in J.items():I+=M
	return{'res':1,E:H,'cntTotal':I,'counter_dict':J}