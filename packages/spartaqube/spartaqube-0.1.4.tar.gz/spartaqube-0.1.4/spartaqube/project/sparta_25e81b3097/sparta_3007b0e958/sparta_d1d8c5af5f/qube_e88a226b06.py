from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class WssConnector(EngineBuilder):
	def __init__(A,socket_url):super().__init__(host=None,port=None);A.connector=A.build_csv(socket_url=socket_url)
	def test_connection(A):0