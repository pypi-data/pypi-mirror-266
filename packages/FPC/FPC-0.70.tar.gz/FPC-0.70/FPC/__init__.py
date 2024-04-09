import datetime,builtins,platform,time,math,os,urllib,sys,hashlib
from urllib import request
dicts={}
IS_WIN=False if platform.system().find('Linux')>-1 else True
NOW=datetime.datetime.now()
NOW_TS=math.floor(NOW.timestamp())
NOW=NOW.strftime('%Y-%m-%d %H:%M:%S')
start_time=0
proxies='http://127.0.0.1:10809';proxies={'http':proxies,'https':proxies}
def is_numeric(x):
	try:float(x);return True
	except:return False
def now(x=None):#x=micro return microsecond;x='str' return string;x is int means convert timestamp to string;x is sting means convert string to timestamp
	if not x:return int(datetime.datetime.now().timestamp())
	elif x=='micro':return datetime.datetime.now().timestamp()
	elif x=='str':return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	elif isinstance(x,int):return datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S')
	else:
		try: import dateutil.parser;return int(dateutil.parser.parse(x).timestamp())
		except Exception: return int(datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').timestamp())
class interval_exec(object):
	def __init__(self,interval,now=True):
		self.interval=interval
		self.count=-1 if now else 0
	def __call__(self):
		self.count+=1
		return self.count%self.interval==0
def print(*a,func=None,time='%m/%d %H:%M:%S',pretty=False,**s):
	a=list(a)
	if func:
		for i,x in enumerate(a):
			a[i]=func(x)
	if time:
		a.insert(0,datetime.datetime.now().strftime(time)+' :')
	if pretty:
		import pprint
		for x in a:
			pprint.pprint(x)
	else:
		builtins.print(*a,**s)
def split_str(strs,num=1):
	_=[]
	for x in range(math.ceil(len(strs)/num)):
		_.append(strs[x*num:x*num+num])
	return _
def diff(a,b):
	diff={}
	for x in a:
		if b.get(x)!=a[x]: diff[x]=[a[x],b.get(x)]
	return diff
def notice(x,c='default',silent=None):
	if silent:
		red=redis()
		if red.exists(x):return
		else:
			red.set(x,'1',silent)
	try:request.urlopen(r'http://call.ff2.pw/?%s=%s&passwd=frank'%(c,urllib.parse.quote_plus(x)))
	except:pass
def rand_sleep(i=0.4,a=0.8):import random;time.sleep(random.randint(i*1000,a*1000)/1000);
def rand(i=9,a=None):import random;return random.randint(int(i),int(a)) if a else random.randint(0,int(i-1));
def md5(x):hl = hashlib.md5();hl.update(x.encode('utf-8') if isinstance(x,str) else x);return hl.hexdigest();
def bin2hex(x):import binascii;return binascii.hexlify(x.encode('utf-8') if isinstance(x,str) else x);
def base64_encode(x):import base64;return base64.b64encode(x) if isinstance(x,bytes) else base64.b64encode(x.encode('utf-8'))
def base64_decode(x):import base64;return base64.b64decode(x+(b'===' if isinstance(x,bytes) else '==='))
def log(*x,path=None):#已经带有时间
	if path is None:
		path='/tmp/frank.log' if os.path.exists('/tmp') else './FPC.log'
	with open(path,'a',encoding='utf-8') as f:
		print(*x,file=f)
def parse(o):#print class/obj's attr beatiful
	method=[];attr=[]
	for x in dir(o):
		if x[:2]=='__':continue
		method.append(x) if callable(getattr(o,x)) else attr.append(x)
	builtins.print('method',method)
	builtins.print('attr',attr)
#save or open a python varible,name and expire just for local
def obj(obj=None,remote=False,name:str =None,expire:(str,int)=None,is_json=False):
	if is_json:import json as pickle
	else:import pickle
	if remote:
		return pickle.loads(request.urlopen(r'http://a.ff2.pw/obj.php').read()) if obj is None else request.urlopen(r'http://a.ff2.pw/obj.php',pickle.dumps(obj))
	else:
		os.path.exists('/tmp') or os.makedirs('/tmp')
		if name is None:
			path='/tmp/'+(sys.argv[0][sys.argv[0].replace('\\','/').rindex('/')+1:] if '/' in sys.argv[0] or '\\' in sys.argv[0] else sys.argv[0])+'.obj'
		else: path=f'/tmp/_named_{name}.obj'
		if obj is None: return pickle.load(open(path,'rb')) if os.path.exists(path) else None
		else:
			if expire:
				_={'s':1,'m':60,'h':3600,'d':86400}
				if isinstance(expire,str): expire=int(expire[:-1])*_[expire[-1]]
				if NOW_TS-os.path.getmtime(path)>expire:
					os.remove(path)
					return None
			return pickle.dump(obj,open(path,'wb'))
def encrypt(string,password=None):
	if isinstance(string,bytes): string=string.decode('latin')
	first_letter=string[0]
	hl = hashlib.sha512()
	hl.update(first_letter.encode('utf-8')if password is None else password.encode('utf-8'))
	sha512=hl.digest()
	_= sha512[0]%64
	sha512=(sha512[_:]+sha512[:_])*math.ceil(len(string)/64)
	encrypted=''
	for i,x in enumerate(string):
		encrypted+=chr((ord(x)+sha512[i])%94+33)
	if password is None:
		encrypted=chr((ord(first_letter)+ord(encrypted[-1]))%94+33)+encrypted[1:]
	return encrypted
def decrypt(string,password=None):
	hl = hashlib.sha512()
	if not password:
		for i in range(6):
			_=94*i+ord(string[0])-(ord(string[-1])+33)
			if _ >=33 and _<127:break
		first_letter=chr(_)
	hl.update(first_letter.encode('utf-8')if password is None else password.encode('utf-8'))
	sha512=hl.digest()
	_= sha512[0]%64
	sha512=(sha512[_:]+sha512[:_])*math.ceil(len(string)/64)
	decrypted=''
	for i,x in enumerate(string):
		for ii in range(6):
			_=94*ii+ord(x)-(sha512[i]+33)
			if _ >=33 and _<127:break
		decrypted+=chr(_)
	if password is None:
		decrypted=first_letter+decrypted[1:]
	return decrypted
def start():
	global start_time
	start_time=now('micro')
def end(_type=True):#True:print False:return number:sleep(number)
	if _type is True : print(now('micro')-start_time)
	elif _type is False:return now('micro')-start_time
	elif isinstance(_type,(int,float)):
		_=_type-(now('micro')-start_time)
		_>0 and time.sleep(_)
class mysql(object):
	conn=None
	def __init__(self, host=None,port=3306,threadsafe=False,**args):
		import pymysql
		self.pymysql=pymysql
		if threadsafe:
			self.lock=threading.Lock()
		else:self.lock=None
		if host=='sqlite':
			import sqlite3
			self.conn=sqlite3.connect('/tmp/sqlite.db',isolation_level=None)
			if 'table' in args : self.table=args['table']
			return
		if args.get('ssh_host'):
			import sshtunnel
			sshtunnel.DAEMON=True
			sshtunnel.SSHTunnelForwarder.daemon_forward_servers=True
			sshtunnel.SSHTunnelForwarder.daemon_transport=True
			self.server = sshtunnel.SSHTunnelForwarder(ssh_address_or_host=args.pop('ssh_host'),ssh_username=args.pop('ssh_username'),ssh_password=args.pop('ssh_password'),remote_bind_address=('127.0.0.1' if host is None else host,port))
			self.server.start()
			port=self.server.local_bind_port
		connect_config={'host':'127.0.0.1' if host is None else host,'port':port,'user':'root','password':'','db':'localhost','cursorclass':pymysql.cursors.DictCursor,'autocommit':None}
		if 'table' in args:
			self.table=args['table']
			del args['table']
		if not args:
			args=obj(name='mysql' if host is None else f'mysql_{host}')
		for x in args:
			connect_config[x]=args[x]
		self.connect_config = connect_config
	def __init_connect__(self):
		self.conn = self.pymysql.connect(**self.connect_config)
	def __getattr__(self,attr):
		return getattr(self.conn,attr)
	def _decide_type(self,value):
		if isinstance(value,(int,float)):
			pass
		elif isinstance(value,bytes):
			value=value.decode('utf-8')
		elif value is None:
			value='NULL'
		else:
			value='"'+self.pymysql.converters.escape_string(value)+'"'
		return value
	def _split_dict(self,dicts,splitor=','):
		string=''
		for field in dicts:
			if isinstance(dicts[field],(list,tuple)):
				operator= dicts[field][0].upper()
				if 'IN' in operator:
					value=''
					for in_value in dicts[field][1]:
						value+=f'{self._decide_type(in_value)},'
					value=value[:-1]
					string+=f' `{field}` {operator} ({value}) {splitor}'
				elif 'BETWEEN' in operator:
					value=[self._decide_type(dicts[field][1][0]),self._decide_type(dicts[field][1][1])]
					string+=f' `{field}` {operator} {value[0]} and {value[1]} {splitor}'
				else:
					value=self._decide_type(dicts[field][1])
					string+=f' `{field}` {operator} {value} {splitor}'
			else:
				value=self._decide_type(dicts[field])
				string+=f' `{field}`={value} {splitor}'
		return string[:-len(splitor)]
	def _split_add_dict(self,dicts):
		key=value=''
		for x in dicts:
			key+=r'`%s`,'%x
			if dicts[x] is None:value+='null,'
			else:value+=r'%s,'%(dicts[x]) if is_numeric(dicts[x]) else r'"%s",'%(self.pymysql.converters.escape_string(dicts[x]))
		return key[:-1],value[:-1]
	def execute(self,strs):
		if not self.conn:self.__init_connect__()
		strs=strs.strip()
		op_type=strs[:4].lower()
		is_query = True if op_type in ['sele','show','desc'] else False
		for x in range(3):
			try:
				cur=None
				if self.lock:self.lock.acquire(10)
				cur=self.conn.cursor()
				cur.execute(strs)
				if is_query:
					data=cur.fetchall()
				elif op_type in ['upda','dele']:
					data=cur.rowcount
				else:
					data=cur.lastrowid
				return data
			except Exception as e:
				if '2006' in str(e) or '2013' in str(e) or isinstance(e,self.pymysql.err.InterfaceError):
					if self.conn:
						self.conn.close();self.conn=None;
						self.__init_connect__()
				else:
					e.args=e.args+(f' FPC_SQL:{strs}',)
					raise e
			finally:
				if cur:cur.close()
				if self.lock:self.lock.release()
		# is_query or self.conn.commit()
		raise Exception('MYSQL:try 3 times connect,but error')
	def add(self,dicts,table=None,ignore=False,duplicate=[]):
		'''table is optional,dicts can be list or dict,duplicate should be list'''
		if not isinstance(table,str):
			if table is None:
				table=self.table
			else:#table is not none and reverse two args
				table_=dicts
				dicts=table
				table=table_
		if not dicts:return
		if isinstance(dicts,dict): dicts=[dicts]
		values=''#values like (1,2),(2,3) 
		for x in dicts:
			key,value=self._split_add_dict(x)
			values+=r'(%s),'%(value)
		ignore='' if not ignore else 'ignore'
		duplicate_str=''
		if duplicate:
			duplicate_str='as a on duplicate key update '
			for x in duplicate:
				duplicate_str+=f' `{x}`=a.`{x}`,'
			duplicate_str=duplicate_str[:-1]
		return self.execute(f''' insert {ignore} into `{table}`({key}) values {values[:-1]} {duplicate_str}''')
	def update(self,data,where,table=None):
		'''where can be str or dict'''
		table=self.table if table is None else table
		where=self._split_dict(where,'and') if isinstance(where,dict) else where
		data=self._split_dict(data)
		return self.execute(r' update `%s` set %s where %s'%(table,data,where))
	def delete(self,where,table=None,where_splitor='and'):
		where=self._split_dict(where,where_splitor) if isinstance(where,dict) else where
		return self.execute(r' delete from `%s` where %s'%(table,where))
	def select(self,where=None,table=None,where_splitor='and',field='*',order=None,limit=None):
		table=self.table if table is None else table
		query_str=f'select {field} from {table} '
		if where:
			where=self._split_dict(where,where_splitor) if isinstance(where,dict) else where
			query_str+=f'where {where} '
		if order:
			query_str+=f'order by {order} '
		if limit:
			query_str+=f'limit {limit} '
		return self.execute(query_str)
	def find(self,*args,**argv):
		if 'order' not in argv : argv['order']='id desc'
		res=self.select(*args,**argv,limit=1)
		return res and (res[0][list(res[0].keys())[0]] if len(res[0])==1 else res[0])
class redis(object):
	server=False
	def __init__(self,host='127.0.0.1',db=0,port=6379,ssh_host=None,ssh_username='root',ssh_password=None):
		import redis
		if ssh_host:
			import sshtunnel
			sshtunnel.DAEMON=True
			sshtunnel.SSHTunnelForwarder.daemon_forward_servers=True
			sshtunnel.SSHTunnelForwarder.daemon_transport=True
			self.server = sshtunnel.SSHTunnelForwarder(ssh_address_or_host=ssh_host,ssh_username=ssh_username,ssh_password=ssh_password,remote_bind_address=(host,port))
			self.server.start()
			port=self.server.local_bind_port
		self.redis=redis.StrictRedis(host=host, port=port, db=db,decode_responses=True)
	def __getattr__(self,attr):
		return getattr(self.redis,attr)
def process_arg_construct(urls:list,args):#args must be iterable
	proc_args=[]
	every_proc_count=math.ceil(len(args)/len(urls))
	for i,url in enumerate(urls):
		proc_args.append((url,args[i*every_proc_count:i*every_proc_count+every_proc_count]))
	return proc_args
def process(target,is_thread=True,join=False,num=1,sleep=None,daemon=False,**args):
	if isinstance(target,(str,list)):#args:target,[sync=True]
		import subprocess
		proc=subprocess.Popen(target,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True if isinstance(target,str) else False);
		return proc.communicate() if args.get('sync',True) else proc
	pros=[]
	if 'args' in args:#args can be list or tuple : [('',),('',)]
		assert isinstance(args['args'],(tuple,list))
		args_list=args['args']
		num=len(args_list)
	if is_thread: from threading import Thread as proc
	else: from multiprocessing import Process as proc
	for x in range(num):
		if 'args' in args:
			args['args']=args_list[x] if isinstance(args_list[x],(tuple,list)) else [args_list[x]]
		pros.append(proc(target=target,**args))
		if daemon : pros[-1].daemon=True
		pros[-1].start()
		if sleep:time.sleep(sleep)
	if join:
		for x in range(num):
			pros[x].join(None if join is True else join)
	return pros[0] if len(pros)==1 else pros
class ErrorCounter:
	def __init__(self,time_interval=60):
		from collections import deque
		self.error_timestamps = deque()
		self.time_interval=time_interval
	def add(self):
		current_time = time.time()
		self.error_timestamps.append(current_time)
	def count(self):
		current_time = time.time()
		while self.error_timestamps and self.error_timestamps[0] < current_time - self.time_interval:
			self.error_timestamps.popleft()
		return len(self.error_timestamps)
	def clear(self):
		self.error_timestamps.clear()