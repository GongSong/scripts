#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import datetime, time
import logging
from optparse import OptionParser
import math
import string, codecs
import subprocess

def isdate(s):
  try:
    time.strptime(str(s).replace('-',''),"%Y%m%d")
    return True
  except:
    return False

def mklogfile(s):
  if not os.path.exists(s):
    f=open(s,'w')
    f.write('.log\n')
    f.close()
    os.chmod(s, 0664)

def list2str(l):
  return "'" + "','".join(l) + "'"

def delCtrlChar(s, cc = "\n\t\r"):
  return str(s).translate(string.maketrans(cc," "*len(cc)))

def sqlEscape(s):
  try:
    ret = str(s).replace('\\','\\\\')
    ret = ret.replace('`','\\`')
    return ret
  except:
    return None

def runHiveQL(s):
  logger.debug("sql# %s" % s)
  cmd = 'hive -S -e "%(sql)s"' % {'sql':sqlEscape(s)}
  proc = subprocess.Popen(cmd, shell=True, env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
  hiveout, errmsg = proc.communicate()
  retval = proc.wait()
  if retval!=0:
    logger.error("HiveError!!!(%d)" % retval)
    logger.error("Debug Info: %s" % str(errmsg))
    sys.exit(retval)
  return hiveout

def runShell(cmd):
  logger.debug("shell# %s" % str(cmd))
  proc = subprocess.Popen(str(cmd), shell=True, env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  
  shellout, errmsg = proc.communicate()
  retval = proc.wait()
  if retval!=0:
    logger.error("ShellError!!!(%d) %s" % (retval, str(cmd)))
    logger.error("Debug Info: %s" % str(errmsg))
    sys.exit(retval)
  return shellout

def getJsonValString(jsontext,key):
  key = '"%(keyword)s":"' % {'keyword':key}
  p0 = jsontext.find(key)
  if p0==-1:
    return ""
  p0 += len(key)
  p1 = jsontext.find('"',p0)
  if p1==-1:
    return ""
  return jsontext[p0:p1]

reload(sys)
sys.setdefaultencoding("utf8")

retval = 0

##runtime variable
pid = os.getpid()
rundate = datetime.date.today().strftime("%Y%m%d")
rundir = os.path.dirname(os.path.abspath(__file__))
runfilename = os.path.splitext(os.path.split(os.path.abspath(__file__))[1])[0]
logdir = rundir + "/log"
tmpdir =  rundir + "/tmp"
if not os.path.exists(logdir):
  os.mkdir(logdir,0774)
if not os.path.exists(tmpdir):
  os.mkdir(tmpdir,0774)
logfile = '%(dir)s/%(filename)s.log' % {'dir':logdir,'filename':runfilename,'rundate':rundate,'pid':pid}
if not os.path.exists(logfile):
  mklogfile(logfile)

##logger
logger = logging.getLogger("sp")
logger.setLevel(logging.DEBUG)
fileHandler = logging.FileHandler(logfile)
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(logging.Formatter("%(asctime)s\tpid#%(process)d\t%(levelname)s - %(message)s"))
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(logging.Formatter("%(asctime)s\tpid#%(process)d\t%(filename)s\n%(message)s"))
logger.addHandler(consoleHandler)

logger.info("begin execute... %s" % str(sys.argv))

##option parse
usageinfo = "%prog [--date=statisdate] [--timeout=xxx][-v]"
parser = OptionParser(usage=usageinfo, version="%prog v0.0.1")
parser.set_defaults(statisdate=(datetime.datetime.strptime(rundate,"%Y%m%d")+datetime.timedelta(days=-1)).strftime("%Y%m%d"))
parser.set_defaults(session_timeout="300")
parser.add_option("-d", "--date", dest="statisdate", help="statis date, yyyy-mm-dd or yyyymmdd", metavar="DATE")
parser.add_option("-t", "--timeout", dest="session_timeout", help="session timeout. default 300.", metavar="VALUE")
parser.add_option("-v", "--verbose", action="store_true", dest="verbosemode", default=False, help="verbose mode", metavar="MODE")

(options, args) = parser.parse_args()
opt_statisdate = options.statisdate.replace('-','')
opt_session_timeout = options.session_timeout
verbosemode = options.verbosemode

if isdate(opt_statisdate)==False:
  logger.error("unconverted date %s" % opt_statisdate)
  sys.exit(-101)
statisdate = opt_statisdate

if not opt_session_timeout.isdigit():
  logger.error("unconverted int %s" % opt_session_timeout)
  sys.exit(-102)
session_timeout = int(opt_session_timeout)

if session_timeout < 60:
  logger.error("session timeout is too small.(%s)" % opt_session_timeout)
  sys.exit(-103)

if verbosemode==True:
  consoleHandler.setLevel(logging.DEBUG)

##tmp file
tmpfilename = 'dw_app_requestlog_session_dm_%(statisdate)s.dat' % {'statisdate':statisdate}
tmpfile = '%(dir)s/%(tmpfilename)s' % {'dir':tmpdir, 'tmpfilename':tmpfilename}
tmpwriter = open(tmpfile,'w+')
##register file
regfilename = 'dw_app_requestlog_reg_dm_%(statisdate)s.dat' % {'statisdate':statisdate}
regfile = '%(dir)s/%(regfilename)s' % {'dir':tmpdir, 'regfilename':regfilename}
regwriter = open(regfile,'w+')

dt_statisdate = datetime.datetime.strptime(statisdate,"%Y%m%d")
statis_date = dt_statisdate.strftime("%Y-%m-%d")
statisdate = dt_statisdate.strftime("%Y%m%d")
curdate = rundate
cur_date = "%s-%s-%s" % (curdate[0:4],curdate[4:6],curdate[6:8])
nullstring = ''

jobname = "%(script)s@%(statisdate)s" % {'script':os.path.split(os.path.abspath(__file__))[1], 'statisdate':statisdate}
hiveconf = {'mapred.job.name':jobname, 'mapred.job.queue.name':'default'}
conf = ''
for item in hiveconf:
  conf += '--hiveconf %(key)s=%(value)s ' % {'key':item, 'value':hiveconf[item]}
bin = "hive -S %(hiveconf)s -e" % {'rundir':rundir, 'hiveconf':conf}

logger.debug("reading requestlog (%s)..." % statis_date)

##非用户行为请求列表
invalid_functionlist = ['ad.getad_imocha','common.gettime','mobiledevice.initandroiddevice','mobiledevice.initiphonedevice','notice.getpullnotice','recipe.getfindrecipe','fix.getimagehostdnslist']
##用户注册行为请求列表
register_functionlist = ['common.sendcode','passport.bindconnectstatus','passport.connectbindreg','passport.loginbyconnect','passport.reg']

outfieldnum=12
c_request_time_ts, \
c_request_time   , \
c_device_id      , \
c_channel_id     , \
c_userip         , \
c_app_id         , \
c_version_id     , \
c_userid         , \
c_function_id    , \
c_parameter_info , \
c_parameter_desc , \
c_uuid = range(outfieldnum)

##应与目的表bing.dw_app_requestlog_session_dm 的定义格式一致
fieldsdelimiter, rowsdelimiter = "\t", "\n"
resultrowformat = \
"%(request_time)s" + fieldsdelimiter + \
"%(device_id)s" + fieldsdelimiter + \
"%(channel_id)s" + fieldsdelimiter + \
"%(userip)s" + fieldsdelimiter + \
"%(app_id)s" + fieldsdelimiter + \
"%(version_id)s" + fieldsdelimiter + \
"%(userid)s" + fieldsdelimiter + \
"%(function_id)s" + fieldsdelimiter + \
"%(parameter_info)s" + fieldsdelimiter + \
"%(parameter_desc)s" + fieldsdelimiter + \
"%(uuid)s" + fieldsdelimiter + \
"%(session_id)d" + fieldsdelimiter + \
"%(session_seq)d" + rowsdelimiter

sqlstmt = R"""
set hive.cli.print.header=false;
set mapreduce.map.memory.mb=8192;
set mapreduce.reduce.memory.mb=8192;
set mapreduce.reduce.tasks=15;

select
unix_timestamp(request_time) as request_time_ts,
request_time  ,
device_id     ,
channel_id    ,
userip        ,
app_id        ,
coalesce(version_id,'') as version_id,
coalesce(userid,'') as userid,
function_id   ,
parameter_info,
'' as parameter_desc,
coalesce(uuid,'') as uuid
from bing.ods_app_requestlog_dm
where statis_date='${statis_date}'
and function_id not in (${invalid_function})
distribute by app_id, device_id
sort by app_id, device_id, uuid, channel_id, request_time
;
"""
sql = delCtrlChar(sqlstmt,'\t\r')
sql = sql.replace('${statis_date}',statis_date)
sql = sql.replace('${invalid_function}',list2str(invalid_functionlist))
logger.debug("sql# %s" % sql)
cmd = '%(bin)s "%(sql)s"' % {'bin':bin, 'sql':sqlEscape(sql)}
hive = subprocess.Popen(cmd, shell=True, env=os.environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE)  

logger.debug("splitting session ...")
pos, errnum, chunksize, resultchunk = 0, 0, 200000, []
##init session variable 
prekey, curkey, cur_request_time_ts, cur_session_id, cur_session_seq = '', '', 0, 0, 0
##init register session
preregkey, curregkey, regchunk = '', '', []
for outline in hive.stdout:
  pos += 1
  outrow = outline.strip('\n').split("\t")
  if len(outrow)< outfieldnum:
    errnum += 1
    continue
  prekey, pre_request_time_ts = curkey, cur_request_time_ts
  ##assemle session key
  curkey = '$' + str(outrow[c_app_id]) + '$' + str(outrow[c_device_id]) + '$' + str(outrow[c_uuid]) + '$' + str(outrow[c_channel_id])
  if outrow[c_request_time_ts].isdigit():
    cur_request_time_ts = int(outrow[c_request_time_ts])
  else:
    cur_request_time_ts = 0
  if curkey!=prekey:
    ##session key
    cur_app_id         = outrow[c_app_id        ]
    cur_device_id      = outrow[c_device_id     ]
    cur_uuid           = outrow[c_uuid          ]
    cur_channel_id     = outrow[c_channel_id    ]
    ##session info
    cur_request_time   = outrow[c_request_time  ]
    cur_userip         = outrow[c_userip        ]
    cur_version_id     = outrow[c_version_id    ]
    cur_userid         = outrow[c_userid        ]
    cur_function_id    = outrow[c_function_id   ]
    cur_parameter_info = outrow[c_parameter_info]
    cur_parameter_desc = outrow[c_parameter_desc]
    cur_session_id     = 1
    cur_session_seq    = 1
  else:
    ##session info
    cur_request_time   = outrow[c_request_time  ]
    cur_userip         = outrow[c_userip        ]
    cur_version_id     = outrow[c_version_id    ]
    cur_userid         = outrow[c_userid        ]
    cur_function_id    = outrow[c_function_id   ]
    cur_parameter_info = outrow[c_parameter_info]
    cur_parameter_desc = outrow[c_parameter_desc]
    if cur_request_time_ts - pre_request_time_ts<=session_timeout:
      cur_session_seq += 1
    else:
      cur_session_id += 1
      cur_session_seq = 1
  resultline = resultrowformat % { \
    'request_time':cur_request_time, \
    'device_id':cur_device_id, \
    'channel_id':cur_channel_id, \
    'userip':cur_userip, \
    'app_id':cur_app_id, \
    'version_id':cur_version_id, \
    'userid':cur_userid, \
    'function_id':cur_function_id, \
    'parameter_info':cur_parameter_info, \
    'parameter_desc':cur_parameter_desc, \
    'uuid':cur_uuid, \
    'session_id':cur_session_id, \
    'session_seq':cur_session_seq \
    }
  resultchunk.append(resultline)
  if pos % chunksize == 0:
    logger.debug("%d" % pos)
    try:
      tmpwriter.writelines(resultchunk)
      resultchunk = []
    except:
      tmpwriter.close()
  ##register window <<<
  preregkey = curregkey
  curregkey = curkey + '$' + str(cur_session_id)
  if curregkey!=preregkey:
    is_reg = 0
  if is_reg==0 and cur_function_id in register_functionlist and cur_userid=='':
    is_reg = 1
  if is_reg==1:
    regchunk.append(resultline)
  if cur_userid!='':
    is_reg = 0
hive.terminate()

logger.debug("%d" % pos)
tmpwriter.writelines(resultchunk)
tmpwriter.close()
logger.debug("error number: %d" % errnum)

logger.debug("zipping file ...")
if os.path.exists(tmpfile+".lzo"):
  runShell("rm %s.lzo" % tmpfile)
runShell("cd %(tmpdir)s && lzop %(tmpfilename)s" % {'tmpdir':tmpdir, 'tmpfilename':tmpfilename})

logger.debug("loading data ...")
runHiveQL("load data local inpath '%(tmpfile)s.lzo' overwrite into table bing.dw_app_requestlog_session_dm partition (statis_date='%(statis_date)s');" % {'tmpfile':tmpfile, 'statis_date':statis_date})

logger.debug("deleting tmpfile ...")
runShell("cd %(tmpdir)s && ls -l %(tmpfilename)s* | grep -v .lst > %(tmpfilename)s.lst" % {'tmpdir':tmpdir, 'tmpfilename':tmpfilename})
runShell("rm %s" % tmpfile)
runShell("rm %s.lzo" % tmpfile)

##load register file
regwriter.writelines(regchunk)
regwriter.close()
if os.path.exists(regfile+".lzo"):
  runShell("rm %s.lzo" % regfile)
runShell("cd %(tmpdir)s && lzop %(regfilename)s" % {'tmpdir':tmpdir, 'regfilename':regfilename})
runHiveQL("load data local inpath '%(regfile)s.lzo' overwrite into table bing.dw_app_requestlog_reg_dm partition (statis_date='%(statis_date)s');" % {'regfile':regfile, 'statis_date':statis_date})
runShell("cd %(tmpdir)s && ls -l %(regfilename)s* | grep -v .lst > %(regfilename)s.lst" % {'tmpdir':tmpdir, 'regfilename':regfilename})
runShell("rm %s" % regfile)
runShell("rm %s.lzo" % regfile)

logger.info("end.(%d)" % retval)
sys.exit(retval)