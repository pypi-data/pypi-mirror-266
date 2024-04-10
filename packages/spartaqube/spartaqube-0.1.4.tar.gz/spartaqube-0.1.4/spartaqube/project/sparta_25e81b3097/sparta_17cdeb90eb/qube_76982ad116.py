_A=None
from email.utils import make_msgid
from django.contrib.auth.models import User
from project.sparta_25e81b3097.sparta_6730d44407 import qube_6a3e5e2e02 as qube_6a3e5e2e02
from spartaqube.secrets import sparta_93a34a7f9f
def send(emailObj,USERNAME_SMTP=_A,PASSWORD_SMTP=_A,EMAIL_SMTP=_A,HOST=_A,PORT=25,SENDERNAME=_A):return sendEmailFunc(emailObj,USERNAME_SMTP,PASSWORD_SMTP,EMAIL_SMTP,HOST,PORT,SENDERNAME)
def sendEmailFunc(emailObj,USERNAME_SMTP=_A,PASSWORD_SMTP=_A,EMAIL_SMTP=_A,HOST=_A,PORT=25,SENDERNAME=_A):
	K='attachment; filename="%s"';L='Content-Disposition';M='base64';N='Content-Transfer-Encoding';O='errorMsg';P='res';Q=PASSWORD_SMTP;H=EMAIL_SMTP;F=SENDERNAME;G=USERNAME_SMTP;C=emailObj;import smtplib as U,email.utils;from email.mime.multipart import MIMEMultipart as V;from email.mime.text import MIMEText as W;from email.mime.image import MIMEImage;from email.mime.base import MIMEBase as R;I=','.join(C.getRecipients())
	if F is _A:F='My Project'
	if G is _A:D=sparta_93a34a7f9f();HOST=D['EMAIL_HOST_SMTP'];G=D['EMAIL_USERNAME_SMTP'];H=D['EMAIL_RECIPIENT'];Q=D['EMAIL_PASSWORD_SMTP'];PORT=D['EMAIL_PORT_SMTP'];F=D['EMAIL_SENDERNAME']
	if G is _A:return{P:-1,O:'You need to configure an email sender service in your profile view'}
	X=C.getEmailTitle();Y=C.getHTML();B=V('related');B['Subject']=X;B['From']=email.utils.formataddr((F,H));B['To']=I;B['Message-ID']=make_msgid();print('RECIPIENT');print(I);Z=C.getEmailB64ImgList();a=C.getEmailImgNameArr()
	for(J,b)in enumerate(Z):A=R('image','png');A.set_payload(b);A.add_header(N,M);c=a[J];A[L]=K%c;B.attach(A)
	d=C.getFilesArr();e=C.getFilesNameArr()
	for(J,f)in enumerate(d):A=R('application','octet-stream');A.set_payload(f);A.add_header(N,M);S=e[J];print('fileName > '+str(S));A[L]=K%S;B.attach(A)
	g=W(Y,'html');B.attach(g);print('SEND EMAIL NOW')
	try:E=U.SMTP(HOST,PORT);E.ehlo();E.starttls();E.ehlo();E.login(G,Q);E.sendmail(H,I,B.as_string());E.close()
	except Exception as T:print('Error: ',T);return{P:-1,O:str(T)}
	else:return'Email sent!'