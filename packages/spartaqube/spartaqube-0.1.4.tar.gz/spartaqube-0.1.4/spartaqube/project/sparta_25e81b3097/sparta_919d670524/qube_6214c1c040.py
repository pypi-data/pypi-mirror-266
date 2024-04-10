from datetime import datetime
import hashlib,os,sys,django
def sparta_2fbe58e6d4():B='/';C='\\';D=os.path.dirname(os.path.abspath(__file__)).replace(C,B);A=os.path.dirname(D).replace(C,B);A=os.path.dirname(A).replace(C,B);A=os.path.dirname(A).replace(C,B);sys.path.append(A);print('oneLevelUpPath');print(A);os.environ.setdefault('DJANGO_SETTINGS_MODULE','spartaqube.settings');os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']='true';django.setup()
def sparta_795d246066():
	G='utf-8';B='admin';from django.contrib.auth.models import User as H;from project.models import UserProfile as I
	if not H.objects.filter(username=B).exists():C='admin@spartaqube.com';A=H.objects.create_user(B,first_name=B,last_name=B,email=C,password=B);A.is_superuser=True;A.is_staff=True;A.save();D=I(user=A);E=str(A.id)+'_'+str(A.email);E=E.encode(G);F=hashlib.md5(E).hexdigest()+str(datetime.now());F=F.encode(G);D.userId=hashlib.sha256(F).hexdigest();D.email=C;D.save();print(f"Admin {C} created")
if __name__=='__main__':sparta_2fbe58e6d4();sparta_795d246066()