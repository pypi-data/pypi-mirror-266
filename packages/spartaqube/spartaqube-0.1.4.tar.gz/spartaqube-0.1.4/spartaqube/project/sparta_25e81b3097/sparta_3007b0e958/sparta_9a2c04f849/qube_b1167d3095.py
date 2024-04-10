from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class DuckDBConnector(EngineBuilder):
	def __init__(A,database_path,read_only=False):super().__init__(host=None,port=None);A.connector=A.build_duckdb(database_path=database_path,read_only=read_only)
	def test_connection(A):0