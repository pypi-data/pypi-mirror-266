import pandas as pd
from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class CassandraConnector(EngineBuilder):
	def __init__(A,host,port,user,password,keyspace):C=password;B=keyspace;A.keyspace=B;super().__init__(host=host,port=port,user=user,password=C,engine_name='cassandra');A.set_url_engine(f"cassandra://{user}:{C}@{host}:{port}/{B}");A.cluster=A.build_cassandra(A.keyspace);A.connector=A.cluster.connect(B)
	def test_connection(A):
		B=False
		try:
			C=A.connector
			if C.is_open:print('Connected to Cassandra cluster');C.shutdown();A.cluster.shutdown();return True
			else:print('Failed to connect to Cassandra cluster');return B
		except Exception as D:print(f"Error: {D}");return B