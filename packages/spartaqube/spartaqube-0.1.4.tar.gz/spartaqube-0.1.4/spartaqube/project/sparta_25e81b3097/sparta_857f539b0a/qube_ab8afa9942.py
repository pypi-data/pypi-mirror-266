import os,zipfile,pytz
UTC=pytz.utc
from django.conf import settings as conf_settings
def sparta_9bf2d5c083():
	B='APPDATA'
	if conf_settings.PLATFORMS_NFS:
		A='/var/nfs/notebooks/'
		if not os.path.exists(A):os.makedirs(A)
		return A
	if conf_settings.PLATFORM=='LOCAL_DESKTOP'or conf_settings.IS_LOCAL_PLATFORM:
		if conf_settings.PLATFORM_DEBUG=='DEBUG-CLIENT-2':return os.path.join(os.environ[B],'SpartaQuantNB/CLIENT2')
		return os.path.join(os.environ[B],'SpartaQuantNB')
	if conf_settings.PLATFORM=='LOCAL_CE':return'/app/notebooks/'
def sparta_0782b69d8f(userId):A=sparta_9bf2d5c083();B=os.path.join(A,userId);return B
def sparta_2f76f3aa45(notebookProjectId,userId):A=sparta_0782b69d8f(userId);B=os.path.join(A,notebookProjectId);return B
def sparta_ae7fd26341(notebookProjectId,userId):A=sparta_0782b69d8f(userId);B=os.path.join(A,notebookProjectId);return os.path.exists(B)
def sparta_4ed2e14cd5(notebookProjectId,userId,ipynbFileName):A=sparta_0782b69d8f(userId);B=os.path.join(A,notebookProjectId);return os.path.isfile(os.path.join(B,ipynbFileName))
def sparta_328b624052(notebookProjectId,userId):
	B=userId;C=notebookProjectId;D=sparta_2f76f3aa45(C,B);G=sparta_0782b69d8f(B);A=f"{G}/zipTmp/"
	if not os.path.exists(A):os.makedirs(A)
	H=f"{A}/{C}.zip";E=zipfile.ZipFile(H,'w',zipfile.ZIP_DEFLATED);I=len(D)+1
	for(J,M,K)in os.walk(D):
		for L in K:F=os.path.join(J,L);E.write(F,F[I:])
	return E
def sparta_a2d436a7a0(notebookProjectId,userId):B=userId;A=notebookProjectId;sparta_328b624052(A,B);C=f"{A}.zip";D=sparta_0782b69d8f(B);E=f"{D}/zipTmp/{A}.zip";F=open(E,'rb');return{'zipName':C,'zipObj':F}