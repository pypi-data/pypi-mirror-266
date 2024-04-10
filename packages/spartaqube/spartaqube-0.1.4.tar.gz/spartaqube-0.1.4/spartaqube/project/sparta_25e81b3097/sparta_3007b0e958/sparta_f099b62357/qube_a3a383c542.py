_A='get available tables error'
import sqlite3
from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class SqliteConnector(EngineBuilder):
	def __init__(A,database_path):B=database_path;super().__init__(host=None,port=None,engine_name='sqlite');A.database_path=B;A.set_url_engine(f"sqlite:///{A.database_path}");A.connector=A.build_sqlite(database_path=B)
	def test_connection(A):
		B=False
		try:
			if A.connector:A.connector.close();return True
			else:return B
		except Exception as C:print(f"Error: {C}");return B
	def get_available_tables(C):
		try:A=C.connector;B=A.cursor();B.execute("SELECT name FROM sqlite_master WHERE type='table';");D=B.fetchall();A.close();return sorted([A[0]for A in D])
		except Exception as E:print(_A);print(E)
		try:A.close()
		except:pass
		return[]
	def get_table_columns(C,table_name):
		try:A=C.connector;B=A.cursor();B.execute(f"PRAGMA table_info({table_name});");D=B.fetchall();E=[{'column':A[1],'type':A[2]}for A in D];A.close();return E
		except Exception as F:print(_A);print(F)
		try:A.close()
		except:pass
		return[]