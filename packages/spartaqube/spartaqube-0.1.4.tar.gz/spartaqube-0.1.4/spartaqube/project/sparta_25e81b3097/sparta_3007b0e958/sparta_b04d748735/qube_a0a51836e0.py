import pandas as pd
from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class ArcticConnector(EngineBuilder):
	def __init__(A,host,port,user,password,library_arctic):B=library_arctic;A.library_arctic=B;super().__init__(host=host,port=port,user=user,password=password,engine_name='arctic');A.connector=A.build_arctic(B)
	def test_connection(A):0