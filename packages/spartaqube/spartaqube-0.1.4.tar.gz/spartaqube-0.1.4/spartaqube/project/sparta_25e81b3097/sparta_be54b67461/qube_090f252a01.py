_A='utf-8'
import base64,hashlib
from cryptography.fernet import Fernet
def sparta_c048a5c96c():B='widget-plot-db';A=B.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A.decode(_A)
def sparta_fd2ae7f85e(password_to_encrypt):A=password_to_encrypt;A=A.encode(_A);C=Fernet(sparta_c048a5c96c().encode(_A));B=C.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_c22799f995(password_e):B=Fernet(sparta_c048a5c96c().encode(_A));A=base64.b64decode(password_e);A=B.decrypt(A).decode(_A);return A