import os
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_afce30863b import qube_afce30863b
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_ed47cb6371 import qube_ed47cb6371
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_5ea25cefdf import qube_5ea25cefdf
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_3e8266c96a import qube_3e8266c96a
class db_connection:
	def __init__(A,dbType=0):A.dbType=dbType;A.dbCon=None
	def get_db_type(A):return A.dbType
	def getConnection(A):
		if A.dbType==0:
			from django.conf import settings as B
			if B.PLATFORM in['SANDBOX','SANDBOX_MYSQL']:return
			A.dbCon=qube_afce30863b()
		elif A.dbType==1:A.dbCon=qube_ed47cb6371()
		elif A.dbType==2:A.dbCon=qube_5ea25cefdf()
		elif A.dbType==4:A.dbCon=qube_3e8266c96a()
		return A.dbCon