import os
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_ed47cb6371 import qube_ed47cb6371
from project.sparta_0ed9d00fc8.sparta_68e3f7ddcb.qube_afce30863b import qube_afce30863b
class db_custom_connection:
	def __init__(A):A.dbCon=None;A.dbIdManager='';A.spartAppId=''
	def setSettingsSqlite(B,dbId,dbLocalPath,dbFileNameWithExtension):E='spartApp';F=dbLocalPath;C=dbId;from bqm import settings as G,settingsLocalDesktop as H;B.dbType=0;B.spartAppId=C;A={};A['id']=C;A['ENGINE']='django.db.backends.sqlite3';A['NAME']=str(F)+'/'+str(dbFileNameWithExtension);A['USER']='';A['PASSWORD']='2change';A['HOST']='';A['PORT']='';G.DATABASES[C]=A;H.DATABASES[C]=A;D=qube_afce30863b();D.setPath(F);D.setDbName(E);B.dbCon=D;B.dbIdManager=E;print(G.DATABASES)
	def getConnection(A):return A.dbCon
	def setAuthDB(A,authDB):A.dbType=authDB.dbType