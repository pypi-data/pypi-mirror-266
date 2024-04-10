_G='Request could not be executed with error 2 '
_F='This table does not exist...'
_E='strReq => '
_D='SELECT count(*) FROM '
_C='TABLE_NAME'
_B='table_name'
_A=None
import json,pandas as pd,pymysql,pymysql.cursors,psycopg2,pyodbc,pymssql,pandas as pd,pandas.io.sql as psql
from sqlalchemy import create_engine
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_b71ed16be8 import qube_b71ed16be8
class db_connection_mssql(db_connection_sql):
	def __init__(A):
		D='NAME';A.hostname='localhost';A.user='root';A.schemaName=_A;A.db='qbm';A.port=3306;A.path=_A;A.password='';A.connection=-1;A.bPrint=False
		try:
			from django.conf import settings as C
			if C.PLATFORM in C.USE_DEFAULT_DB_SETTINGS:B=C.DATABASES['default'];A.hostname=B['HOST'];A.user=B['USER'];A.schemaName=B[D];A.db=B[D];A.password=B['PASSWORD'];A.port=int(B['PORT'])
		except:pass
	def getDBType(A):return 4
	def setConnection(A,hostname,username,name,password='',port=3306,schemaName=_A):
		B=schemaName;C=name;A.hostname=hostname;A.user=username;A.db=C;A.password=password
		if B is _A:A.schemaName=C
		elif len(B)>0:A.schemaName=B
		else:A.schemaName=C
		if len(str(port))>0:A.port=int(port)
	def create_connection(A):
		if A.bPrint:print('MSSQL');print('create_connection for MS SQL now');print('self.hostname => '+str(A.hostname));print('self.user => '+str(A.user));print('self.password => '+str(A.password));print('self.port => '+str(A.port));print('self.schemaName => '+str(A.schemaName));print('self.database => '+str(A.db))
		if A.schemaName is _A:A.schemaName=A.user
		if len(str(A.port))>0:A.connection=pymssql.connect(host=A.hostname,user=A.user,password=A.password,database=A.db,port=A.port)
		else:A.connection=pymssql.connect(host=A.hostname,user=A.user,password=A.password,database=A.db)
	def getAllTables(A):B='SELECT * FROM sys.Tables';A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def getAllTablesAndColumns(A):D=A.schemaName;B='SELECT * FROM information_schema.columns ORDER BY table_name,ordinal_position';A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def getAllTablesAndColumnsRenamed(B):A=B.getAllTablesAndColumns();A.columns=[A.lower()for A in A.columns.tolist()];A=A[[_B,'column_name','data_type']];A.rename(columns={_B:_C},inplace=True);print('schemas_df');print(A);return A
	def getAllTablesNbRecords(A):C='TABLE_ROWS';D=A.schemaName;E="WITH tbl AS             (SELECT table_schema,                     TABLE_NAME             FROM information_schema.tables             WHERE TABLE_NAME not like 'pg_%'                 AND table_schema = '"+str(D)+"')             SELECT table_schema,                 TABLE_NAME,                 (xpath('/row/c/text()', query_to_xml(format('select count(*) as c from %I.%I', table_schema, TABLE_NAME), FALSE, TRUE, '')))[1]::text::int AS rows_n             FROM tbl             ORDER BY rows_n DESC;";A.create_connection();B=pd.read_sql(E,con=A.connection);B.rename(columns={_B:_C,'rows_n':C},inplace=True);B=B[[_C,C]];A.close_connection();return B
	def getAllTablesNbRecords2(A,tableNameArr,websocket):
		F='table';G='recordsNb';H='res';I=websocket;A.create_connection()
		for B in tableNameArr:
			try:C=A.connection.cursor();J=_D+B.replace("'","''")+'';C.execute(J);K=C.fetchone()[0];D={H:1,G:K,F:B};E=json.dumps(D);I.send(text_data=E)
			except:D={H:-1,G:0,F:B};E=json.dumps(D);I.send(text_data=E)
		C.close();A.close_connection()
	def getCountTable(A,tableName):
		A.create_connection();B=A.connection.cursor();C=_D+tableName.replace("'","''")+''
		if A.bPrint:print(C)
		B.execute(C);D=B.fetchone()[0];B.close();A.close_connection();return D
	def getAllSChemas(A):B="SELECT schema_name FROM information_schema.SCHEMATA WHERE schema_name IN ('"+A.db+"')";A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def getThisSchema(A,schemaName):B="SELECT schema_name FROM information_schema.SCHEMATA WHERE schema_name NOT IN ('information_schema', 'mysql') AND schema_name IN ('"+schemaName+"')";A.create_connection();C=pd.read_sql(B,con=A.connection);A.close_connection();return C
	def checkTableExists(A,tableName):
		A.create_connection();B=A.connection.cursor();C="select table_name from information_schema.tables where table_name='"+tableName.replace("'","''")+"'"
		if A.bPrint:print(C)
		B.execute(C);D=B.fetchone();B.close();A.close_connection()
		if D:return True
		else:return False
	def pd2DB(A,tableName,thisDf):B=create_engine('mssql://'+str(A.user)+':'+str(A.password)+'@'+str(A.hostname)+':'+str(A.port)+'/'+str(A.db));thisDf.to_sql(name=tableName,con=B,if_exists='append')
	def getDataFrame(A,tableName):
		B=tableName
		try:
			C='SELECT * FROM "'+B+'"'
			if A.bPrint:print(_E+str(C))
			A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
		except Exception as E:
			A.close_connection()
			if not A.checkTableExists(B):
				if A.bPrint:print(_F)
			elif A.bPrint:print(_G+str(E))
			return
	def getDataFrameLimit(A,tableName,limit=100):
		B=tableName
		try:
			C='SELECT TOP '+str(limit)+' * FROM "'+B+'"'
			if A.bPrint:print(_E+str(C))
			A.create_connection();D=pd.read_sql(C,con=A.connection);A.close_connection();return D
		except Exception as E:
			A.close_connection()
			if not A.checkTableExists(B):
				if A.bPrint:print(_F)
			elif A.bPrint:print(_G+str(E))
			return