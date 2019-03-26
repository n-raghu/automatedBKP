try:
	import yaml as y
	from collections import OrderedDict as odict
	from pandas import read_sql_query as rsq,DataFrame as pdf
	from sqlalchemy import create_engine as pgcnx
	from psycopg2 import connect as pgconnect
	from datetime import datetime as dtm
	from sqlalchemy.orm import sessionmaker
	from io import StringIO
	from mysql.connector import connect as mysqlCNX
except ImportError:
	raise ImportError('Module(s) not installed...')

with open('dimConfig.yml') as ymlFile:
	cfg=y.load(ymlFile)

def dwCNX(tinyset=False):
	uri='postgresql://' +cfg['eaedb']['uid']+ ':' +cfg['eaedb']['pwd']+ '@' +cfg['eaedb']['host']+ ':' +str(int(cfg['eaedb']['port']))+ '/' +cfg['eaedb']['db']
	eaeSchema=cfg['eaedb']['schema']
	if tinyset:
		csize=cfg['pandas']['tinyset']
	else:
		csize=cfg['pandas']['bigset']
	return csize,eaeSchema,uri

def objects_mysql(urx):
	insList_io=[]
	cnxPGX=pgcnx(urx)
	insData=cnxPGX.execute("SELECT * FROM framework.instanceconfig WHERE isactive=true AND instancetype='mysql' ")
	colFrame_io=rsq("SELECT icode,instancetype,collection,s_table,rower,stg_cols,pkitab,pki_cols FROM framework.live_instancecollections() WHERE instancetype='mysql' ",cnxPGX)
	for cnx in insData:
		dat=odict(cnx)
		insDict=odict()
		insDict['icode']=dat['instancecode']
		insDict['hport']=dat['hport']
		insDict['hostip']=dat['hostip']
		insDict['dbname']=dat['dbname']
		insDict['uid']=dat['uid']
		insDict['pwd']=dat['pwd']
		insList_io.append(insDict)
	return odict([('frame',colFrame_io),('insList',insList_io)])

csize,eaeSchema,uri=dwCNX()
pgx=pgcnx(uri)
colFrame=objects_mysql(uri)['frame']
cnx=mysqlCNX(user='phish',password='Super@Phish1',database='phishproof',host='172.16.1.253')
ccr=cnx.cursor(buffered=True)
trk=pdf([],columns=['collection','chunkstart','chunkfinish','rowversion','status','timestarted','timefinished'])
tracker=pdf([],columns=['status','instancecode','collection','timestarted','timefinished','rowversion'])

for idx,rowdata in colFrame.iterrows():
	rco=rowdata['collection']
	s_table=rowdata['s_table']
	rower=str(int(rowdata['rower']))
	icode=rowdata['icode']
	sql="SELECT '" +icode+ "' AS instancecode,*,UNIX_TIMESTAMP(sys_ROWVERSION) AS rower FROM " +rco+ " WHERE CAST(sys_ROWVERSION AS BIGINT)>" +rower
	print(sql)
	ccr.execute(sql)
	list(ccr)
