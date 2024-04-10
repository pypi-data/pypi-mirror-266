_B='postgres'
_A=None
import time,pandas as pd
from pandas.api.extensions import no_default
import project.sparta_25e81b3097.sparta_3007b0e958.qube_292124302a as qube_292124302a
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_b04d748735.qube_a0a51836e0 import ArcticConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_3b70f5e000.qube_919b50e10b import CassandraConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_a0aded3826.qube_ab02de1607 import CsvConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_9a2c04f849.qube_b1167d3095 import DuckDBConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_445577b91a.qube_9dfd8f9f54 import JsonApiConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_11920d788d.qube_5e5a7fc16e import MongoConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_27f51a7b4d.qube_dd582b705e import MssqlConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_8eab919a9b.qube_ba01e7deae import MysqlConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_7a7eada532.qube_add5293c17 import OracleConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_a495784497.qube_8bf56c0523 import PostgresConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_c300fc6390.qube_02e5c11b16 import QuestDBConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_d0d5c58e7d.qube_9732ef5321 import RedisConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_f099b62357.qube_a3a383c542 import SqliteConnector
from project.sparta_25e81b3097.sparta_3007b0e958.sparta_d1d8c5af5f.qube_e88a226b06 import WssConnector
class Connector:
	def __init__(A,db_engine=_B):A.db_engine=db_engine
	def init_with_model(B,connector_obj):
		A=connector_obj;D=A.host;E=A.port;F=A.user;G=A.password_e
		try:C=qube_292124302a.sparta_35b35865b9(G)
		except:C=_A
		H=A.database;I=A.oracle_service_name;J=A.keyspace;K=A.library_arctic;L=A.database_path;M=A.read_only;N=A.json_url;O=A.socket_url;P=A.db_engine;Q=A.csv_path;R=A.csv_delimiter;B.db_engine=P;B.init_with_params(host=D,port=E,user=F,password=C,database=H,oracle_service_name=I,csv_path=Q,csv_delimiter=R,keyspace=J,library_arctic=K,database_path=L,read_only=M,json_url=N,socket_url=O)
	def init_with_params(A,host,port,user=_A,password=_A,database=_A,oracle_service_name='orcl',csv_path=_A,csv_delimiter=_A,keyspace=_A,library_arctic=_A,database_path=_A,read_only=False,json_url=_A,socket_url=_A,redis_db=0):
		G=database_path;F=database;B=password;C=user;D=port;E=host
		if A.db_engine=='arctic':A.db_connector=ArcticConnector(host=E,port=D,user=C,password=B,library_arctic=library_arctic)
		if A.db_engine=='cassandra':A.db_connector=CassandraConnector(host=E,port=D,user=C,password=B,keyspace=keyspace)
		if A.db_engine=='csv':A.db_connector=CsvConnector(csv_path=csv_path,csv_delimiter=csv_delimiter)
		if A.db_engine=='duckdb':A.db_connector=DuckDBConnector(database_path=G,read_only=read_only)
		if A.db_engine=='json_api':A.db_connector=JsonApiConnector(json_url=json_url)
		if A.db_engine=='mongo':A.db_connector=MongoConnector(host=E,port=D,user=C,password=B,database=F)
		if A.db_engine=='mssql':A.db_connector=MssqlConnector(host=E,port=D,user=C,password=B,database=F)
		if A.db_engine=='mysql':A.db_connector=MysqlConnector(host=E,port=D,user=C,password=B,database=F)
		if A.db_engine=='oracle':A.db_connector=OracleConnector(host=E,port=D,user=C,password=B,database=F,oracle_service_name=oracle_service_name)
		if A.db_engine==_B:A.db_connector=PostgresConnector(host=E,port=D,user=C,password=B,database=F)
		if A.db_engine=='questdb':A.db_connector=QuestDBConnector(host=E,port=D,user=C,password=B,database=F)
		if A.db_engine=='redis':A.db_connector=RedisConnector(host=E,port=D,user=C,password=B,db=redis_db)
		if A.db_engine=='sqlite':A.db_connector=SqliteConnector(database_path=G)
		if A.db_engine=='wss':A.db_connector=WssConnector(socket_url=socket_url)
	def test_connection(A):return A.db_connector.test_connection()
	def get_available_tables(A):B=A.db_connector.get_available_tables();return B
	def get_table_columns(A,table_name):B=A.db_connector.get_table_columns(table_name);return B
	def get_data_table(A,table_name):B=A.db_connector.get_data_table(table_name);return pd.DataFrame(B)
	def read_sql_query(A,sql,index_col=_A,coerce_float=True,params=_A,parse_dates=_A,chunksize=_A,dtype=_A,dtype_backend=no_default):return pd.read_sql_query(sql,con=A.db_connector.connector,index_col=index_col,coerce_float=coerce_float,params=params,parse_dates=parse_dates,chunksize=chunksize,dtype=dtype,dtype_backend=dtype_backend)