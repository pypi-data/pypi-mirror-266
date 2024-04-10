import uuid,hashlib
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from project.models import UserProfile
class Command(BaseCommand):
	help='Create a public user'
	def handle(C,*K,**L):
		G='utf-8';D='public_spartaqube';H='public@spartaqube.com';I='public'
		if not User.objects.filter(username=D).exists():A=User.objects.create_user(username=D,email=H,password=I);C.stdout.write(C.style.SUCCESS('Public user created successfully'))
		else:A=User.objects.filter(username=D).all()[0];C.stdout.write(C.style.WARNING('Public user already exists'))
		if not UserProfile.objects.filter(user=A).exists():B=UserProfile(user=A);E=str(A.id)+'_'+str(A.email);E=E.encode(G);F=hashlib.md5(E).hexdigest()+str(datetime.now());F=F.encode(G);J=str(uuid.uuid4());B.user_profile_id=hashlib.sha256(F).hexdigest();B.email=H;B.api_key=str(uuid.uuid4());B.registration_token=J;B.save()