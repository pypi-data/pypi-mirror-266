from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class RedisConnector(EngineBuilder):
	def __init__(A,host,port,user=None,password=None,db=0):super().__init__(host=host,port=port,user=user,password=password,engine_name='redis');A.connector=A.build_redis(db=db)
	def test_connection(A):0