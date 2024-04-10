_A='utf-8'
import base64,hashlib
from cryptography.fernet import Fernet
def sparta_c048a5c96c():B='db-conn';A=B.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A.decode(_A)
def sparta_e594220c6d(password_to_encrypt):A=password_to_encrypt;A=A.encode(_A);C=Fernet(sparta_c048a5c96c().encode(_A));B=C.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_35b35865b9(password_e):B=Fernet(sparta_c048a5c96c().encode(_A));A=base64.b64decode(password_e);A=B.decrypt(A).decode(_A);return A
def sparta_f61f16b553():return sorted(['arctic','cassandra','csv','duckdb','json_api','mongo','mssql','mysql','oracle','postgres','questdb','redis','sqlite','wss'])