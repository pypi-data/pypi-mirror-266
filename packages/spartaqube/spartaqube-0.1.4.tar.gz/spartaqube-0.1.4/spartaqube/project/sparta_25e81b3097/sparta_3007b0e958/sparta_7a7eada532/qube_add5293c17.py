from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class OracleConnector(EngineBuilder):
	def __init__(A,host,port,user,password,database=None,oracle_service_name='orcl'):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='oracle+cx_oracle');A.connector=A.build_oracle(oracle_service_name)
	def test_connection(A):0