from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class QuestDBConnector(EngineBuilder):
	def __init__(A,host,port,user,password,database):super().__init__(host=host,port=port,user=user,password=password,database=database,engine_name='questdb');A.connector=A.build_questdb()
	def test_connection(A):0