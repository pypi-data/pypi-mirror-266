_G='message'
_F='errorMsg'
_E='date_created'
_D='ticket_id'
_C=True
_B=False
_A='res'
import json,base64,requests,hashlib
from datetime import datetime,timedelta
from dateutil import parser
import pytz
UTC=pytz.utc
from django.conf import settings as conf_settings
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturalday
from django.forms.models import model_to_dict
from project.models import UserProfile,ticket,ticketMessage
from project.sparta_25e81b3097.sparta_0a82db77e0 import qube_6c72fd4753 as qube_6c72fd4753
from project.sparta_25e81b3097.sparta_6730d44407 import qube_6a3e5e2e02 as qube_6a3e5e2e02
from project.sparta_25e81b3097.sparta_50ce1a8de2 import qube_9b698c371a as qube_9b698c371a
from project.sparta_25e81b3097.sparta_17cdeb90eb.qube_83b1d5f68d import Email as Email
from project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a import sparta_a2439e19e6
from project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a import sparta_ca44ca5c66
ADMIN_EMAIL=conf_settings.ADMIN_EMAIL_TICKET
MAX_TICKETS=conf_settings.MAX_TICKETS
def sparta_0732af0353(json_data,user_obj):
	F='typeCase';G='captcha';B=json_data;A=user_obj;M=B[G];H=B['titleCase'];I=B['messageCase'];J=B[F];N=datetime.now()-timedelta(1);C=datetime.now().astimezone(UTC);D=str(str(A.email)+str(C)).encode('utf-8');D=hashlib.md5(D).hexdigest();O=ticket.objects.filter(date_created__gte=N,user=A);K=len(O)
	if K<=MAX_TICKETS:
		E={G:M,'title':H,_G:I,F:J,_D:D,'email':A.email,'first_name':A.first_name,'last_name':A.last_name};E['jsonData']=json.dumps(E);P=requests.post(f"{conf_settings.SPARTAQUBE_WEBSITE}/help-center-new-case",data=json.dumps(E))
		if P.status_code==200:
			try:C=datetime.now().astimezone(UTC);Q=ticket.objects.create(ticket_id=D,type_ticket=J,title=H,date_created=C,user=A);ticketMessage.objects.create(ticket=Q,message=I,user=A,date_created=C);L=UserProfile.objects.get(user=A);L.has_open_tickets=_C;L.save()
			except Exception as R:return{_A:-1,_F:str(R)}
		return{_A:1,'nbTickets':K}
	else:return{_A:-1,_F:'You have reached the maximum tickets limit'}
def sparta_49d6235ce3(message,typeCase=0,companyName=None):
	B='Type';C=companyName;D=typeCase;E='BUG'
	if int(D)==0:E='GENERAL'
	F=User.objects.filter(is_staff=_C)
	if F.count()>0:
		G=F[0];A=Email(G.username,[conf_settings.CONTACT_US_EMAIL],'New case opened','New case of type > '+str(E))
		if C is not None:A.addOneRow('Company',C);A.addLineSeparator()
		A.addOneRow('Message',message);A.addLineSeparator()
		if int(D)==0:A.addOneRow(B,'General question')
		else:A.addOneRow(B,'Report Bug')
		A.send()
def sparta_d9f64a1014(json_data,user_obj):
	E='arrRes';F='user';G=user_obj;H=json_data['has_user_closed']
	if G.is_staff:
		B=ticket.objects.filter(is_delete=0,has_user_closed=H).order_by('status_ticket');C=[]
		if B.count()>0:
			for D in B:A=sparta_a2439e19e6(model_to_dict(D));del A[F];A[_E]=naturalday(parser.parse(str(A[_E])));C.append(A)
		return{_A:1,E:C}
	else:
		B=ticket.objects.filter(user=G,is_delete=0,has_user_closed=H).order_by('-date_created');C=[]
		if B.count()>0:
			for D in B:A=sparta_a2439e19e6(model_to_dict(D));del A[F];C.append(A)
		return{_A:1,E:C}
def sparta_88e9dae2ce(json_data,user_obj):
	D=user_obj;I=json_data[_D]
	if D.is_staff:F=ticket.objects.filter(ticket_id=I,is_delete=0)
	else:F=ticket.objects.filter(user=D,ticket_id=I,is_delete=0)
	E=[]
	if F.count()>0:
		G=F[0]
		if not D.is_staff:G.b_show_user_notification=_B;G.save()
		B=ticketMessage.objects.filter(ticket=G)
		if B.count()>0:
			J=B[0].user;C=[]
			for(K,L)in enumerate(B):
				H=L.user;A=sparta_a2439e19e6(model_to_dict(L));A[_E]=naturalday(parser.parse(str(A[_E])))
				if D==H:A['me']=1
				else:A['me']=0
				if H==J:
					C.append(A)
					if K==len(B)-1:E.append(C)
				else:
					E.append(C);C=[A]
					if K==len(B)-1:E.append(C)
				J=H
	return{_A:1,'arrMsg':E}
def sparta_789bc859e9(json_data,user_obj):
	D=json_data;B=user_obj;E=D[_D];F=D[_G]
	if B.is_staff:C=ticket.objects.filter(ticket_id=E)
	else:C=ticket.objects.filter(user=B,ticket_id=E)
	if C.count()>0:
		A=C[0];H=datetime.now().astimezone(UTC);ticketMessage.objects.create(ticket=A,message=F,user=B,date_created=H)
		if A.b_send_email and not B.is_staff:A.b_send_email=_B;A.save();sparta_49d6235ce3(F,A.type_ticket,None)
		if B.is_staff:A.status_ticket=2;A.b_send_email=_C;A.has_user_closed=_B;A.b_show_user_notification=_C;A.save();G=UserProfile.objects.get(user=A.user);G.has_open_tickets=_C;G.save()
		else:A.status_ticket=1;A.has_user_closed=_B;A.b_send_email=_B;A.b_show_user_notification=_B;A.save()
		return{_A:1}
	return{_A:-1,_F:'An unexpected error occurred'}
def sparta_1cb810cb61(json_data,user_obj):
	B=user_obj;C=json_data[_D]
	if B.is_staff:A=ticket.objects.filter(ticket_id=C)
	else:A=ticket.objects.filter(user=B,ticket_id=C)
	if A.count()>0:D=A[0];D.has_user_closed=_C;D.save()
	return{_A:1}
def sparta_da7c47284f(json_data):
	A=json_data;D=A['userId'];E=A[_D];B=ticket.objects.filter(user_id=D,ticket_id=E)
	if B.count()>0:C=B[0];C.b_show_user_notification=_B;C.save()
	return{_A:1}
def sparta_782304f068(user_obj):A=ticket.objects.filter(user=user_obj,b_show_user_notification=_C,has_user_closed=_B);return{_A:1,'nbNotifications':A.count()}