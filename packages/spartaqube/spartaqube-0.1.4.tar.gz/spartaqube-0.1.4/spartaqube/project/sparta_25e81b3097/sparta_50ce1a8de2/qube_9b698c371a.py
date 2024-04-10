_K='b_admin'
_J='membersArr'
_I='groupName'
_H='group_user_id'
_G='name'
_F='nonAdmin'
_E='admin'
_D=False
_C='groupId'
_B=True
_A='res'
import hashlib
from datetime import datetime
from project.models import UserProfile,UserGroup,UserGroupUser,notificationGroup
def sparta_b6eadccccc(json_data,user_obj,group_id=None):
	D=json_data;B=group_id;C=user_obj;E=D[_I];G=D[_J];A=datetime.now()
	if B is None:B=hashlib.sha256((str(C.id)+'_'+str(E.lower())+'_'+str(datetime.now())).encode('utf-8')).hexdigest()
	F=UserGroup.objects.create(name=E,group_id=B,user_creator=C,date_created=A,last_update=A);UserGroupUser.objects.create(user_group=F,user=C,b_admin=_B,date_created=A,last_update=A);sparta_0e00bf2797(G,F,A,C);H={_A:1,_C:B};return H
def sparta_0e00bf2797(membersArr,user_group_obj,dateCreation,userMe):
	A=dateCreation;B=user_group_obj;F=UserGroupUser.objects.filter(is_delete=0,user_group=B).all();G=[A.user.email for A in F]
	for H in membersArr:
		D=H['member'];I=hashlib.sha256((str(D)+'_'+str(B.name.lower())+'_'+str(datetime.now())).encode('utf-8')).hexdigest();E=UserProfile.objects.get(userId=D)
		if E is not None:
			C=E.user
			if C.email not in G:UserGroupUser.objects.create(user_group=B,group_user_id=I,user=C,date_created=A,last_update=A);notificationGroup.objects.create(userFrom=userMe,user=C,date_created=A)
			else:print('member already in group')
def sparta_024d66899f(user_obj):A=user_obj;B=UserGroupUser.objects.filter(is_delete=0,user=A,b_admin=_B,user_group__is_delete=0).all();C=UserGroupUser.objects.filter(is_delete=0,user=A,b_admin=_D,user_group__is_delete=0).all();D={_E:B,_F:C};return D
def sparta_df75aac471(user_obj):return UserGroupUser.objects.filter(is_delete=0,user=user_obj,user_group__is_delete=0)
def sparta_a1d044affc(json_data,user_obj):A=sparta_024d66899f(user_obj);B=[{_C:A.user_group.groupId,_G:A.user_group.name}for A in A[_E]];C=[{_C:A.user_group.groupId,_G:A.user_group.name}for A in A[_F]];return{_A:1,_E:B,_F:C}
def sparta_f0f84e23a9(json_data,user_obj):
	C=user_obj;F=str(json_data[_C]);D=UserGroup.objects.filter(is_delete=0,groupId=F).all()
	if D.count()>0:
		E=D[0];A=UserGroupUser.objects.filter(is_delete=0,user_group=E,user=C,b_admin=_B)
		if A.count()>0:A=UserGroupUser.objects.filter(is_delete=0,user_group=E);G=[{_G:A.user.first_name+' '+str(A.user.last_name),_H:A.group_user_id,_K:A.b_admin}for A in A if A.user.email!=C.email];B={_A:1,'membersArrDict':G};return B
	B={_A:-1};return B
def sparta_7461eb80ed(json_data,user_obj):
	C=user_obj;B=json_data;E=B[_C];F=B[_I];G=B[_J];D=UserGroup.objects.filter(is_delete=0,groupId=E).all()
	if D.count()>0:
		A=D[0];H=UserGroupUser.objects.filter(is_delete=0,user_group=A,user=C,b_admin=_B).all()
		if H.count()>0:A.name=F;A.save();I=datetime.now();sparta_0e00bf2797(G,A,I,C)
	J={_A:1};return J
def sparta_d655046b41(json_data,user_obj):
	D=user_obj;E=json_data;F=E[_H];G=int(E[_K]);B=UserGroupUser.objects.filter(is_delete=0,group_user_id=F).all()
	if B.count()>0:
		A=B[0]
		if G==1:
			C=A.user_group;B=UserGroupUser.objects.filter(is_delete=0,user_group=C,user=D,b_admin=_B).all()
			if B.count()>0:A.b_admin=_B;A.save()
		else:
			C=A.user_group;H=C.user_creator
			if D.email==H.email:A.b_admin=_D;A.save()
	I={_A:1};return I
def sparta_837dc0ec25(json_data,user_obj):
	C=json_data[_C];A=UserGroup.objects.filter(is_delete=0,groupId=C,user_creator=user_obj).all()
	if A.count()>0:B=A[0];B.is_delete=1;B.save()
	D={_A:1};return D
def sparta_f3a452212c(json_data,user_obj):
	D=user_obj;E=json_data[_H];B=UserGroupUser.objects.filter(is_delete=0,group_user_id=E).all()
	if B.count()>0:
		A=B[0];F=A.b_admin
		if not F:
			C=A.user_group;B=UserGroupUser.objects.filter(is_delete=0,user_group=C,user=D,b_admin=_B).all()
			if B.count()>0:A.is_delete=1;A.save()
		else:
			C=A.user_group;G=C.user_creator
			if D.email==G.email:A.is_delete=1;A.save()
	H={_A:1};return H
def sparta_dab13215b4(json_data,user_obj):
	D=json_data[_C];A=UserGroup.objects.filter(is_delete=0,groupId=D).all()
	if A.count()>0:
		E=A[0];B=UserGroupUser.objects.filter(is_delete=0,user_group=E,user=user_obj,b_admin=_D).all()
		if B.count()>0:C=B[0];C.is_delete=1;C.save()
	F={_A:1};return F