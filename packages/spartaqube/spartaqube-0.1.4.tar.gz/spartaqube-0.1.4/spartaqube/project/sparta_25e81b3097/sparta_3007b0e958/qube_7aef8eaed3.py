_A=None
import time,pandas as pd,psycopg2,mysql.connector,pyodbc,cx_Oracle,redis,duckdb,sqlite3
from arctic import Arctic
from pymongo import MongoClient
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from sqlalchemy import create_engine,MetaData,Table,select,inspect,text
from multiprocessing import Pool
class EngineBuilder:
	def __init__(A,host,port,user=_A,password=_A,database=_A,engine_name='postgresql'):B=database;C=password;A.host=host;A.port=port;A.user=user;A.password=C;A.database=B;A.url_engine=f"{engine_name}://{user}:{C}@{host}:{port}/{B}"
	def set_url_engine(A,url_engine):A.url_engine=url_engine
	def set_database(A,database):A.database=database
	def set_file_path(A,file_path):A.file_path=file_path
	def set_keyspace_cassandra(A,keyspace_cassandra):A.keyspace_cassandra=keyspace_cassandra
	def set_redis_db(A,redis_db):A.redis_db=redis_db
	def set_database_path(A,database_path):A.database_path=database_path
	def set_socket_url(A,socket_url):A.socket_url=socket_url
	def set_json_url(A,json_url):A.json_url=json_url
	def set_library_arctic(A,library_arctic):A.library_arctic=library_arctic
	def build_postgres(A):B=psycopg2.connect(user=A.user,password=A.password,host=A.host,port=A.port,database=A.database);return B
	def build_mysql(A):B=mysql.connector.connect(host=A.host,user=A.user,passwd=A.password,port=A.port,database=A.database);return B
	def build_mssql(B):A=pyodbc.connect('Driver={SQL Server};Server=DESKTOP-TLF7IMQ\\SQLEXPRESS;Database=retail;Trusted_Connection=yes;');return A
	def build_oracle(A,oracle_service_name='orcl'):B=cx_Oracle.makedsn(A.host,A.port,service_name=oracle_service_name);C=cx_Oracle.connect(user=A.user,password=A.password,dsn=B);return C
	def build_arctic(A,library_arctic):B=library_arctic;A.set_library_arctic(B);C=Arctic(A.host);D=C[B];return D
	def build_cassandra(A,keyspace):A.set_keyspace_cassandra(keyspace);B=[A.host];C=PlainTextAuthProvider(username=A.user,password=A.password)if A.user and A.password else _A;D=Cluster(contact_points=B,port=A.port,auth_provider=C);return D
	def build_redis(A,db=0):A.set_redis_db(db);B=redis.StrictRedis(host=A.host,port=A.port,password=A.password,db=db);return B
	def build_duckdb(B,database_path,read_only=False):A=database_path;B.set_database_path(A);C=duckdb.connect(A,read_only=read_only);return C
	def build_sqlite(B,database_path):A=database_path;B.set_database_path(A);C=sqlite3.connect(A);return C
	def build_questdb(A):B=f"{A.host}:{A.port}";C=Connection(B,username=A.user,password=A.password);return C
	def build_mongo(A):B=MongoClient(host=A.host,username=A.user,password=A.password);C=B[A.database];return C
	def build_csv(A,file_path):A.set_file_path(file_path);return A
	def build_xls(A,file_path):A.set_file_path(file_path);return A
	def build_json_api(A,json_url):A.set_json_url(json_url)
	def build_wss(A,socket_url):A.set_socket_url(socket_url)
	def get_sqlachemy_engine(A):return create_engine(A.url_engine)
	def get_available_tables(A):
		try:B=A.get_sqlachemy_engine();C=inspect(B);D=C.get_table_names();return sorted(D)
		except Exception as E:print('Exception get available tables metadata');print(E);return[]
	def get_table_columns(C,table_name):
		A='type'
		try:
			D=C.get_sqlachemy_engine();E=inspect(D);B=E.get_columns(table_name)
			if B:return[{'column':B['name'],A:str(B[A])}for B in B]
		except Exception as F:print('Exception get table columuns metadata');print(F)
		return[]
	def get_data_table(B,table_name):
		A=table_name
		try:
			C=B.get_sqlachemy_engine();D=text(f"SELECT * FROM {A}")
			with C.connect()as E:F=E.execute(D);G=F.fetchall();return G
		except Exception as H:print(f"Exception while loading data from table '{A}'");print(H)
		return[]