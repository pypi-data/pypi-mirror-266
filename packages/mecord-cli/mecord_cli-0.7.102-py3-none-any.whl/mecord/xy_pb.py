import json, os
import datetime
import uuid

import mecord.pb.user_ext_pb2 as user_ext_pb2
import mecord.pb.common_ext_pb2 as common_ext_pb2
import mecord.pb.aigc_ext_pb2 as aigc_ext_pb2
import mecord.pb.rpcinput_pb2 as rpcinput_pb2
from mecord import store 
from mecord import utils 
from mecord import taskUtils 
from mecord import constant 
from mecord import xy_network 

OFFICIAL_PRODUCT_TOKEN = "NDl8NWU5OGI1ODk4N2ExNTZmZWE1MmI4YzM3MTNjNjI0MDd8ZjI2MzYwZTA2ZWVkODg0Y2ZlNjZlZTBlNzVhZDM1OWY="
NORMAL_TOKEN = "NzB8OGMzYzZkYzVhMTQzNWRmOWEyODliMGMzMDMwYjIwYWN8MWFiNzE4ODA1YzczMjhmZTgxNzdlMmU4MTA3MmJjYjE="
COUNTRY_DOMAIN =  {
    "us" : "https://api.mecordai.com/proxymsg",
    "sg" : "https://api-sg.mecordai.com/proxymsg",
    "test" : "https://mecord-beta.2tianxin.com/proxymsg"
}

def supportCountrys():
    return ["US", "SG", "test"]
    
def real_token(country):
    if country != "test":
        return OFFICIAL_PRODUCT_TOKEN
    else:
        return NORMAL_TOKEN

def _aigc_post(country, request, function, objStr="mecord.aigc.AigcExtObj"):
    return _post(url=COUNTRY_DOMAIN[country.lower()], 
                 objStr=objStr, 
                 request=request, 
                 function=function,
                 token=real_token(country))

def _post(url, objStr, request, function, token):
    req = request.SerializeToString()
    opt = {
        "lang": "zh-Hans",
        "region": "CN",
        "appid": "80",
        "application": "mecord",
        "version": "1.0",
        "X-Token": token,
        "uid": "1",
    }
    input_req = rpcinput_pb2.RPCInput(obj=objStr, func=function, req=req, opt=opt)
    try:
        res_content = xy_network.post(url, input_req.SerializeToString())
        pb_rsp = rpcinput_pb2.RPCOutput()
        pb_rsp.ParseFromString(res_content)
        if pb_rsp.ret == 0:
            return 0, "", pb_rsp.rsp
        else:
            taskUtils.taskPrint(None, f'''=============== request {url} err_code={pb_rsp.ret} err_desc={pb_rsp.desc} {datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')} ===============
url={url}
func={function}
token={token}

req=
{request}
respose=
{res_content}
===============
''')
            return pb_rsp.ret, pb_rsp.desc, "" 
    except Exception as e:
        taskUtils.taskPrint(None, f'''=============== mecord {url} server error {datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')} ===============
url={url}
func={function}
token={token}

req=
{request}
exception={e}
===============
''')
        return -99, str(e), ""
    
#======================================== Task Function ==============================
def _extend():
    extInfo = store.readDeviceInfo()
    extInfo["app_version"] = constant.app_version
    extInfo["app_bulld_number"] = constant.app_bulld_number
    extInfo["app_name"] = constant.app_name
    extInfo["dts"] = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')
    extInfo["trace_id"] = ''.join(str(uuid.uuid4()).split('-'))
    extInfo["host_name"] = utils.get_hostname()
    return json.dumps(extInfo)

def GetTask(country):
    req = aigc_ext_pb2.GetTaskReq()
    req.version = constant.app_version
    req.DeviceKey = utils.generate_unique_id()
    map = store.widgetMap()
    for it in map:
        if isinstance(map[it], (dict)):
            if map[it]["isBlock"] == False:
                req.widgets.append(it)
        else:
            req.widgets.append(it)
    req.token = real_token(country)
    req.limit = 1
    req.extend = _extend()
    req.apply = False
    
    rsp = aigc_ext_pb2.GetTaskRes()
    r1, r2, r3 = _aigc_post(country, req, "GetTask")
    if r1 != 0:
        return [], 10
    rsp.ParseFromString(r3)
    datas = []
    for it in rsp.list:
        datas.append({
            "taskUUID": it.taskUUID,
            "pending_count": rsp.count - rsp.limit,
            "config": it.config,
            "data": it.data,
        })
    #Previous tasks may have failed due to network problems, so collect and resend
    retryLastTaskNotify()
    return datas, rsp.timeout

TASK_NOTIFY_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"task_notify_data.json")
def saveTaskNotifyData(country, taskUUID, status, msg, dataStr):
    taskUtils.taskPrint(taskUUID, f"save {taskUUID} to next notify")
    data = []
    try:
        if not os.path.exists(TASK_NOTIFY_DATA):
            with open(TASK_NOTIFY_DATA, 'w') as f:
                json.dump([], f)
        with open(TASK_NOTIFY_DATA, 'r') as f:
            data = json.load(f)
    except:
        pass
    try:
        data.append({
            "taskUUID":taskUUID,
            "status":status,
            "country":country,
            "msg":msg,
            "dataStr":dataStr
        })
        with open(TASK_NOTIFY_DATA, 'w') as f:
            json.dump(data, f)
    except:
        pass
def resetLastTaskNotify(taskUUID):
    data = []
    try:
        if os.path.exists(TASK_NOTIFY_DATA):
            with open(TASK_NOTIFY_DATA, 'r') as f:
                data = json.load(f)
    except:
        pass
    try:
        newData = []
        for it in data:
            if it["taskUUID"] != taskUUID:
                newData.append(it)
        with open(TASK_NOTIFY_DATA, 'w') as f:
            json.dump(newData, f)
    except:
        pass
def retryLastTaskNotify():
    data = []
    try:
        if os.path.exists(TASK_NOTIFY_DATA):
            with open(TASK_NOTIFY_DATA, 'r') as f:
                data = json.load(f)
    except:
        pass
    try:
        newData = []
        for it in data:
            msg = it["msg"]
            counrty = "US"
            if "country" in it:
                counrty = it["country"]
            fail_count = 0
            if "fail_count" in it:
                fail_count = it["fail_count"]
            else:
                it["fail_count"] = 0
            if fail_count < 10:
                if TaskNotify(counrty, it["taskUUID"], it["status"], f"{msg} *", it["dataStr"], False) == False:
                    it["fail_count"] += 1
                    newData.append(it)
        with open(TASK_NOTIFY_DATA, 'w') as f:
            json.dump(newData, f)
    except:
        pass

def TaskNotify(country, taskUUID, status, msg, dataStr, failSaveNotify=True):
    req = aigc_ext_pb2.TaskNotifyReq()
    req.version = constant.app_version
    req.taskUUID = taskUUID
    if status:
        req.taskStatus = common_ext_pb2.TaskStatus.TS_Success
    else:
        req.taskStatus = common_ext_pb2.TaskStatus.TS_Failure
    req.failReason = msg
    req.data = dataStr
    req.extend = _extend()
    
    rsp = aigc_ext_pb2.TaskNotifyRes()
    r1, r2, r3 = _aigc_post(country, req, "TaskNotify")
    if r1 != 0:
        if failSaveNotify:
            #tasks may have failed due to network problems, so collect and resend
            saveTaskNotifyData(country, taskUUID, status, msg, dataStr)
        return False
    rsp.ParseFromString(r3)
    taskUtils.taskPrint(taskUUID, f"receive server {rsp.ok} notify_id = {rsp.notify_id}")
    if len(rsp.notify_id) == 0:
        if failSaveNotify:
            #tasks may have failed due to network problems, so collect and resend
            saveTaskNotifyData(country, taskUUID, status, msg, dataStr)
    ok = rsp.ok == True
    if ok:
        taskUtils.taskPrint(taskUUID, f" task : {taskUUID} notify server success")
    else:
        taskUtils.taskPrint(taskUUID, f" task : {taskUUID} server fail~~")
        taskUtils.notifyServerError(taskUUID, country)
    return ok

    
def TaskUpdateProgress(country, taskUUID, progress, dataStr):
    req = aigc_ext_pb2.TaskUpdateReq()
    req.taskUUID = taskUUID
    req.progress = progress
    req.data = dataStr
    
    rsp = aigc_ext_pb2.TaskUpdateRes()
    r1, r2, r3 = _aigc_post(country, req, "TaskUpdate")
    if r1 != 0:
        return False
    rsp.ParseFromString(r3)
    return True

def GetOssUrl(country, ext):
    req = aigc_ext_pb2.UploadFileUrlReq()
    req.token = real_token(country)
    req.version = constant.app_version
    req.fileExt = ext

    rsp = aigc_ext_pb2.UploadFileUrlRes()
    r1, r2, r3 = _aigc_post(country, req, "UploadFileUrl")
    if r1 != 0:
        return "", r2
    rsp.ParseFromString(r3)
    return rsp.url, rsp.contentType

def UploadMarketModel(country, name, cover, model_url, type, taskuuid):
    req = aigc_ext_pb2.MarketModelCreateWithTaskReq()
    req.name = name
    req.cover = cover
    req.url = model_url
    req.type = type
    req.TaskUUID = taskuuid

    rsp = aigc_ext_pb2.MarketModelCreateWithTaskRes()
    r1, r2, r3 = _aigc_post(country, req, "MarketModelCreateWithTask")
    if r1 != 0:
        return 0
    rsp.ParseFromString(r3)
    return True

def GetSystemConfig(country, k):
    req = user_ext_pb2.SystemConfigReq()
    req.key = k

    rsp = user_ext_pb2.SystemConfigRes()
    r1, r2, r3 = _aigc_post(country, req, "GetSystemConfig", "mecord.user.UserExtObj")
    if r1 != 0:
        return None
    rsp.ParseFromString(r3)
    
    if rsp.key == k:
        return rsp.value
    else:
        return None
#======================================== Other Function ==============================
def CreateWidgetUUID():
    req = aigc_ext_pb2.ApplyWidgetReq()
    rsp = aigc_ext_pb2.ApplyWidgetRes()
    r1, r2, r3 = _aigc_post("test", req, "ApplyWidget")
    if r1 != 0:
        return ""
    rsp.ParseFromString(r3)
    return rsp.widgetUUID

def DeleteWidget(widgetid):
    req = aigc_ext_pb2.DeleteAigcWidgetReq()
    req.widgetUUID = widgetid
    req.deviceToken = real_token("test")
    rsp = aigc_ext_pb2.DeleteAigcWidgetRes()
    r1, r2, r3 = _aigc_post("test", req, "DeleteWidget")
    if r1 != 0:
        return False
    rsp.ParseFromString(r3)
    return True

def GetTaskCount(widgetid):
    req = aigc_ext_pb2.TaskCountReq()
    req.deviceToken = real_token("test")
    rsp = aigc_ext_pb2.TaskCountRes()
    r1, r2, r3 = _aigc_post("test", req, "TaskCount")
    if r1 != 0:
        return []
    rsp.ParseFromString(r3)
    datas = []
    for it in rsp.items:
        datas.append({
            "widgetUUID": it.widgetUUID,
            "taskCount": it.taskCount
        })
    return datas

def RemoteWidgetList(widgetid):
    req = aigc_ext_pb2.AigcWidgetListReq()
    req.deviceToken = real_token("test")
    rsp = aigc_ext_pb2.AigcWidgetListRes()
    r1, r2, r3 = _aigc_post("test", req, "WidgetList")
    if r1 != 0:
        return []
    rsp.ParseFromString(r3)
    datas = []
    for it in rsp.items:
        datas.append({
            "uuid": it.uuid,
            "name": it.name,
            "updated_at": it.updated_at,
        })
    return datas
   
def GetWidgetOssUrl(widgetid):
    req = aigc_ext_pb2.UploadWidgetUrlReq()
    req.version = constant.app_version
    req.widgetUUID = widgetid

    rsp = aigc_ext_pb2.UploadWidgetUrlRes()
    r1, r2, r3 = _aigc_post("test", req, "UploadWidgetUrl")
    if r1 != 0:
        return "", ""
    rsp.ParseFromString(r3)
    return rsp.url, rsp.contentType

def WidgetUploadEnd(url):
    req = aigc_ext_pb2.UploadWidgetReq()
    req.version = constant.app_version
    req.fileUrl = url
    
    rsp = aigc_ext_pb2.UploadWidgetRes()
    r1, r2, r3 = _aigc_post("test", req, "UploadWidget")
    if r1 != 0:
        return 0
    rsp.ParseFromString(r3)
    return rsp.checkId
    
def UploadWidgetCheck(checkId):
    req = aigc_ext_pb2.UploadWidgetCheckReq()
    req.version = constant.app_version
    req.checkId = checkId

    rsp = aigc_ext_pb2.UploadWidgetCheckRes()
    r1, r2, r3 = _aigc_post("test", req, "UploadWidgetCheck")
    if r1 != 0:
        return 0
    rsp.ParseFromString(r3)
    if rsp.status == aigc_ext_pb2.UploadWidgetStatus.UWS_SUCCESS:
        return 1
    elif rsp.status == aigc_ext_pb2.UploadWidgetStatus.UWS_FAILURE:
        print(f"widget pulish fail msg => {rsp.failReason}")
        return 0
    else:
        return -1
    
#======================================== Task Function ==============================
def createTask(country, widget_id, params):
    req = aigc_ext_pb2.CreateTaskReq()
    req.taskType = 0
    req.labelType = common_ext_pb2.LT_Public#LT_NONE
    req.labelValue = 1
    req.user_id = 1
    req.widget_id = widget_id
    req.widget_data = json.dumps(params)
    req.parentTaskId = 0

    rsp = aigc_ext_pb2.CreateTaskRes()
    r1, r2, r3 = _aigc_post(country, req, "CreateTask")
    if r1 != 0:
        raise Exception(f"create task fail!, reason={r2}")
    rsp.ParseFromString(r3)
    return rsp.taskUUID

def findWidget(country, name):
    req = aigc_ext_pb2.WidgetOptionReq()
    rsp = aigc_ext_pb2.WidgetOptionRes()
    r1, r2, r3 = _aigc_post(country, req, "WidgetOption")
    if r1 != 0:
        return 0
    rsp.ParseFromString(r3)
    for it in rsp.items:
        widget_id = it.id
        widget_name = it.name
        if widget_name.strip().lower() == name.strip().lower():
            return widget_id
    return 0

def checkTask(country, checkUUID):
    req = aigc_ext_pb2.TaskInfoReq()
    req.taskUUID = checkUUID
    req.findTaskResult = True

    rsp = aigc_ext_pb2.TaskInfoRes()
    r1, r2, r3 = _aigc_post(country, req, "TaskInfo")
    if r1 != 0:
        return False, False, "server fail"
    rsp.ParseFromString(r3)
    if rsp.taskStatus < 3:
        return False, False, ""
    elif rsp.taskStatus == 3:
        return True, True, json.loads(rsp.taskResult)
    elif rsp.taskStatus == 4:
        return True, False, rsp.failReason