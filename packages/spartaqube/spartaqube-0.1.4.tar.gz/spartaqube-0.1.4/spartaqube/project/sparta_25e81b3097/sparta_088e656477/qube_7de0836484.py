from datetime import datetime,timedelta
import pytz
UTC=pytz.utc
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from project.models import User,UserProfile,UserGroup,notificationShare,notificationGroup,notificationShare
from project.sparta_0ed9d00fc8.sparta_3b136f3c7e.qube_316bac807a import sparta_a2439e19e6
def sparta_ee9fe677f6(json_data,user_obj):
	J='humanDate';K='userFromName';L=False;G=True;D=user_obj;M=datetime.today()-timedelta(days=3);E=0;N=list(notificationShare.objects.filter(user=D,is_delete=0,is_seen=L));N+=list(notificationShare.objects.filter(user=D,is_delete=0,is_seen=G,date_seen__gt=M));F=[];P=['id','user','user_group','is_delete','date_seen']
	for A in N:
		B=sparta_a2439e19e6(model_to_dict(A));Q=int(A.typeObject)
		if not A.is_seen:print('Add 1');E+=1
		for R in P:B.pop(R,None)
		C=User.objects.get(id=A.user_from.id);H=C.first_name+' '+C.last_name;I=A.date_created.astimezone(UTC);B[K]=H;B[J]=sparta_9ed90f9585(I)
		if Q==0:0
	O=list(notificationGroup.objects.filter(user=D,is_delete=0,is_seen=L));O+=list(notificationGroup.objects.filter(user=D,is_delete=0,is_seen=G,date_seen__gt=M))
	for A in O:
		if not A.is_seen:E+=1
		B=sparta_a2439e19e6(model_to_dict(A));C=User.objects.get(id=A.user_from.id);H=C.first_name+' '+C.last_name;I=A.dateCreated.astimezone(UTC);B[K]=H;B['type_object']=-2;B[J]=sparta_9ed90f9585(I);F.append(B)
	F=sorted(F,key=lambda obj:obj['dateCreated'],reverse=G);print('nb_notification_not_seen > '+str(E));return{'res':1,'resNotifications':F,'nbNotificationNotSeen':E}
def sparta_9ed90f9585(dateCreated):
	A=dateCreated;B=datetime.now().astimezone(UTC)
	if A.day==B.day:
		if int(B.hour-A.hour)==0:return'A moment ago'
		elif int(B.hour-A.hour)==1:return'1 hour ago'
		return str(B.hour-A.hour)+' hours ago'
	elif A.month==B.month:
		if int(B.day-A.day)==1:return'Yesterday'
		return str(B.day-A.day)+' days ago'
	elif A.year==B.year:
		if int(B.month-A.month)==1:return'Last month'
		return str(B.month-A.month)+' months ago'
	return str(A)
def sparta_44dbfbd38a(json_data,user_obj):
	B=user_obj;C=datetime.now().astimezone(UTC);D=notificationShare.objects.filter(user=B,is_delete=0,is_seen=0)
	for A in D:
		if A.dateSeen is not None:
			if abs(A.date_seen.day-A.date_created.day)>2:A.is_delete=1
		A.is_seen=1;A.date_seen=C;A.save()
	E=notificationGroup.objects.filter(user=B,is_delete=0,is_seen=0)
	for A in E:
		if A.date_seen is not None:
			if abs(A.date_seen.day-A.date_created.day)>2:A.is_delete=1
		A.is_seen=1;A.date_seen=C;A.save()
	return{'res':1}