_A='utf-8'
import os,json,base64,hashlib,random
from cryptography.fernet import Fernet
def sparta_2f643d01f2():A='__API_AUTH__';A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_a41ef7c1a0(objectToCrypt):A=objectToCrypt;C=sparta_2f643d01f2();D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_14615afdac(apiAuth):A=apiAuth;B=sparta_2f643d01f2();C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_0aa48927c9(kCrypt):A='__SQ_AUTH__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_7196e439c4(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_0aa48927c9(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_414367da9d(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_0aa48927c9(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_c658ae42f2(kCrypt):A='__SQ_EMAIL__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_26c147bbf5(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_c658ae42f2(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_4408985351(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_c658ae42f2(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)
def sparta_14e69ac661(kCrypt):A='__SQ_KEY_SSO_CRYPT__'+str(kCrypt);A=A.encode(_A);A=hashlib.md5(A).hexdigest();A=base64.b64encode(A.encode(_A));return A
def sparta_4106b706ef(objectToCrypt,kCrypt):A=objectToCrypt;C=sparta_14e69ac661(kCrypt);D=Fernet(C);A=A.encode(_A);B=D.encrypt(A).decode(_A);B=base64.b64encode(B.encode(_A)).decode(_A);return B
def sparta_9d3535eed2(objectToDecrypt,kCrypt):A=objectToDecrypt;B=sparta_14e69ac661(kCrypt);C=Fernet(B);A=base64.b64decode(A);return C.decrypt(A).decode(_A)