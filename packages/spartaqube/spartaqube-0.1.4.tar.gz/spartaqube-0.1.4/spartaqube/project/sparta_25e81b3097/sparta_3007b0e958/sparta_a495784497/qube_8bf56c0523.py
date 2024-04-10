from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class PostgresConnector(EngineBuilder):
	def __init__(A,host,port,user,password,database):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='postgresql');A.connector=A.build_postgres()
	def test_connection(A):
		B=False
		try:
			if A.connector:A.connector.close();return True
			else:return B
		except Exception as C:print(f"Error: {C}");return B