import os,openpyxl,pandas as pd
from project.sparta_25e81b3097.sparta_3007b0e958.qube_7aef8eaed3 import EngineBuilder
class CsvConnector(EngineBuilder):
	def __init__(A,csv_path,csv_delimiter=None):B=csv_path;super().__init__(host=None,port=None);A.connector=A.build_csv(file_path=B);A.is_csv=os.path.splitext(B)[1].lower()=='.csv';A.csv_path=B;A.csv_delimiter=csv_delimiter
	def test_connection(B):
		A=False
		try:
			if os.path.isfile(B.connector.file_path):return True
			else:return A
		except Exception as C:print(f"Error: {C}");return A
	def get_available_tables(A):
		if A.is_csv:return A.get_available_tables_csv()
		else:return A.get_available_tables_xls()
	def get_available_tables_csv(A):return['sheet1']
	def get_available_tables_xls(A):
		try:B=openpyxl.load_workbook(A.csv_path);C=B.sheetnames;return sorted(C)
		except Exception as D:print('Exception get available tables metadata');print(D);return[]
	def get_data_table(A,table_name):
		if A.is_csv:return A.get_data_table_csv()
		else:return A.get_data_table_xls(table_name)
	def get_data_table_csv(A):return pd.read_csv(A.csv_path)
	def get_data_table_xls(A,table_name):return pd.read_excel(A.csv_path,sheet_name=table_name)