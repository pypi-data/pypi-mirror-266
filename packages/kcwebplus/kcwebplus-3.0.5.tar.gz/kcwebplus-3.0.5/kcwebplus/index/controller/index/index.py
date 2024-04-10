from .common import *
def before_request():
    pass
def index():
    return "默认模块"
def outlogin():
    account_token=request.args.get("account_token")
    if account_token:
        del_cache(account_token)
    else:
        del_session('userinfo')
    return successjson()
def get_account_token(username,sign,timestamp,random,types="get_account_token"):
    "获取用户token"
    status,code,msg,account_token=serlogin(username,sign,timestamp,random,types)
    if status:
        return successjson(data={"account_token":account_token},msg=msg)
    else:
        return errorjson(code=-1,msg=msg)
def login(username,sign,timestamp,random,types="session"):
    "登录"
    G.setadminlog=username+",登录系统"
    status,code,msg,account_token=serlogin(username,sign,timestamp,random,types)
    if status:
        return successjson(data=account_token,msg=msg)
    else:
        return errorjson(code=code,msg=msg)
def addr():
    return successjson(request.HEADER.Physical_IP())

def getkcweb():
    config.kcweb['path']=get_folder()
    return successjson(config.kcweb)
def aa(taskid):
    while True:
        time.sleep(1)
        if not Queues.setstart(taskid,1):
            break
def test():
    taskid=md5(randoms())
    return successjson(Queues.insert(target=aa,args=(taskid,),taskid=taskid,start=1,updtime=times()+1))
    