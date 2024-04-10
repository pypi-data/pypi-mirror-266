from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class JsonApiConnector(EngineBuilder):
	def __init__(A,json_url):super().__init__(host=None,port=None);A.connector=A.build_csv(json_url=json_url)
	def test_connection(A):0