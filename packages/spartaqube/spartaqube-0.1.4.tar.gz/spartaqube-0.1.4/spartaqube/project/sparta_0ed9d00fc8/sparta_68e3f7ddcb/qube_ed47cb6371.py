_A=None
import pandas as pd,pymysql,pymysql.cursors,pandas as pd
from sqlalchemy import create_engine
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_b71ed16be8 import qube_b71ed16be8
class db_connection_mysql(db_connection_sql):
	def __init__(A):
		D='NAME';A.hostname='localhost';A.user='root';A.schemaName=_A;A.db='qbm';A.port=3306;A.path=_A;A.password='';A.connection=-1;A.bPrint=False
		try:
			from django.conf import settings as C
			if C.PLATFORM in C.USE_DEFAULT_DB_SETTINGS:B=C.DATABASES['default'];A.hostname=B['HOST'];A.user=B['USER'];A.schemaName=B[D];A.db=B[D];A.password=B['PASSWORD'];A.port=int(B['PORT'])
		except:pass
	def get_db_type(A):return 1
	def set_connection(A,hostname,username,name,password='',port=3306,schemaName=_A):
		B=schemaName;C=name;A.hostname=hostname;A.user=username;A.db=C;A.password=password
		if B is _A:A.schemaName=C
		elif len(B)>0:A.schemaName=B
		else:A.schemaName=C
		if len(str(port))>0:A.port=int(port)
	def create_connection(A):
		if A.bPrint:print('create_connection for MYSQL');print('self.hostname => '+str(A.hostname));print('self.user => '+str(A.user));print('self.password => '+str(A.password));print('self.port => '+str(A.port))
		if A.schemaName is _A:A.schemaName=A.user
		if len(str(A.port))>0:A.connection=pymysql.connect(host=A.hostname,user=A.user,password=A.password,db=A.db,port=A.port)
		else:A.connection=pymysql.connect(host=A.hostname,user=A.user,password=A.password,db=A.db)