import os, time, calendar
import json
from urllib.parse import *
import sys
import signal
import subprocess, multiprocessing
from threading import Thread, current_thread, Lock

from mecord import xy_pb
from mecord import store
from mecord import taskUtils
from mecord import utils
from pathlib import Path

def runTask(it, timeout, service_country):
    start_time = calendar.timegm(time.gmtime())
    taskUUID = it["taskUUID"]
    pending_count = it["pending_count"]
    config = json.loads(it["config"])
    params = json.loads(it["data"])
    widget_id = config["widget_id"]
    group_id = config["group_id"]
    #cmd
    local_cmd = cmdWithWidget(widget_id)
    cmd = ""
    if local_cmd:
        cmd = local_cmd
    else:
        cmd = str(Path(config["cmd"]))
    #params
    params["task_id"] = taskUUID
    params["pending_count"] = pending_count
    #run
    taskUtils.taskPrint(taskUUID, f"{current_thread().name}=== start execute {service_country} task : {taskUUID}")
    executeSuccess, result_obj = executeLocalPython(taskUUID, cmd, params, timeout, service_country)
    #result
    is_ok = executeSuccess and result_obj["status"] == 0
    msg = "Unknow Error"
    if len(result_obj["message"]) > 0:
        msg = str(result_obj["message"])
    if is_ok:
        checkResult(taskUUID, result_obj)
    taskUtils.taskPrint(taskUUID, f"{current_thread().name}=== task {taskUUID} is_ok={is_ok} ")
    taskUtils.saveCounter(taskUUID, service_country, (calendar.timegm(time.gmtime()) - start_time), is_ok)
    return is_ok, msg, json.dumps(result_obj["result"], separators=(',', ':'))

def cmdWithWidget(widget_id):
    map = store.widgetMap()
    if widget_id in map:
        path = ""
        is_block = False
        if isinstance(map[widget_id], (dict)):
            is_block = map[widget_id]["isBlock"]
            path = map[widget_id]["path"]
        else:
            is_block = False
            path = map[widget_id]
        if len(path) > 0 and is_block == False:
            return path
    return None
 
def executeLocalPython(taskUUID, cmd, param, timeout, service_country):
    inputArgs = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{taskUUID}.in")
    if os.path.exists(inputArgs):
        os.remove(inputArgs)
    with open(inputArgs, 'w') as f:
        json.dump(param, f)
    outArgs = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"{taskUUID}.out")
    if os.path.exists(outArgs):
        os.remove(outArgs)
        
    outData = {
        "result" : [ 
        ],
        "status" : -1,
        "message" : "script error"
    }
    executeSuccess = False
    command = [sys.executable, cmd, "--run", inputArgs, "--out", outArgs]
    taskUtils.taskPrint(taskUUID, f"{current_thread().name}=== exec => {command}")
    process = None
    try:
        if timeout == 0:
            timeout = 60*60 #max 1 hour expire time
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        output, error = process.stdout, process.stderr
        if process.returncode == 0:
            taskUtils.taskPrint(taskUUID, output.decode(encoding="utf8", errors="ignore"))
            if os.path.exists(outArgs):
                with open(outArgs, 'r', encoding='UTF-8') as f:
                    outData = json.load(f)
                executeSuccess = True
                taskUtils.taskPrint(taskUUID, f"exec success result => {outData}")
            else:
                taskUtils.taskPrint(taskUUID, f"task {taskUUID} result is empty!, please check {cmd}")
        else:
            taskUtils.taskPrint(taskUUID, f"====================== script error [{taskUUID}]======================")
            o1 = output.decode(encoding="utf8", errors="ignore")
            o2 = error.decode(encoding="utf8", errors="ignore")
            error_msg = f"{o1}\n{o2}"
            short_error_msg = ""
            if len(error_msg) > 310:
                short_error_msg = f"{error_msg[0:99]}\n...\n{error_msg[len(error_msg)-200:]}"
            else:
                short_error_msg = error_msg
            outData["message"] = short_error_msg
            taskUtils.taskPrint(taskUUID, error_msg)
            taskUtils.taskPrint(taskUUID, "======================     end      ======================")
            taskUtils.notifyScriptError(taskUUID, service_country)
    except Exception as e:
        time.sleep(1) 
        taskUtils.taskPrint(taskUUID, "f====================== process error [{taskUUID}]======================")
        taskUtils.taskPrint(taskUUID, e)
        taskUtils.taskPrint(taskUUID, "======================      end      ======================")
        if process:
            os.kill(process.pid, signal.SIGTERM) 
            if process.poll() is None:
                os.kill(process.pid, signal.SIGKILL)  
        taskUtils.notifyScriptError(taskUUID, service_country)
        outData["message"] = str(e)
    finally:
        if process and process.returncode is None:
            try:
                print("kill -9 " + str(process.pid))
                os.system("kill -9 " + str(process.pid))
            except ProcessLookupError:
                pass
        if os.path.exists(inputArgs):
            os.remove(inputArgs)
        if os.path.exists(outArgs):
            os.remove(outArgs)
    return executeSuccess, outData

def _needChangeValue(taskUUID, data, type, key):
    if "type" not in data:
        taskUtils.taskPrint(taskUUID, "result is not avalid")
        return False
    if data["type"] != type:
        return False
    if "extension" not in data or key not in data["extension"] or len(data["extension"][key]) == 0:
        return True
    return False
            
def checkResult(taskUUID, data):
    try:
        for it in data["result"]:
            if "extension" not in it:
                continue
            if _needChangeValue(taskUUID, it, "text", "cover_url"):
                it["extension"]["cover_url"] = ""
            if _needChangeValue(taskUUID, it, "audio", "cover_url"):
                it["extension"]["cover_url"] = ""
            if _needChangeValue(taskUUID, it, "image", "cover_url"):
                it["extension"]["cover_url"] = ""
            if _needChangeValue(taskUUID, it, "video", "cover_url"):
                it["extension"]["cover_url"] = ""
                
            if "cover_url" in it["extension"] and len(it["extension"]["cover_url"]) > 0:
                cover_url = str(it["extension"]["cover_url"])
                parsed_url = urlparse(cover_url)
                params = parse_qs(parsed_url.query)
                #add width & height if need
                if "width" not in params and "height" not in params:
                    w, h = utils.getOssImageSize(cover_url)
                    if w > 0 and h > 0:
                        params["width"] = w
                        params["height"] = h
                        it["extension"]["width"] = w
                        it["extension"]["height"] = h
                #remove optional parameters
                for k in ["Expires","OSSAccessKeyId","Signature","security-token"]:
                    params.pop(k, None)
                if "width" in it["extension"]:
                    if isinstance(it["extension"]["width"], str):
                        it["extension"]["width"] = int(it["extension"]["width"])
                if "height" in it["extension"]:
                    if isinstance(it["extension"]["height"], str):
                        it["extension"]["height"] = int(it["extension"]["height"])
                updated_query_string = urlencode(params, doseq=True)
                final_url = parsed_url._replace(query=updated_query_string).geturl()
                it["extension"]["cover_url"] = final_url
    except Exception as ex:
        taskUtils.taskPrint(taskUUID, f"result: {data} status is not valid, exception is {ex} ")
        pass

def updateProgress(data, progress=0.5, taskUUID=None):
    realTaskUUID = taskUUID
    country = None
    if store.is_multithread() or taskUUID != None:
        country = taskUtils.taskCountryWithUUID(taskUUID)
    else:
        firstTaskUUID, country = taskUtils.taskInfoWithFirstTask()
        if realTaskUUID == None:
            realTaskUUID = firstTaskUUID
    if country == None:
        country = "test"
    if progress < 0:
        progress = 0
    if progress > 1:
        progress = progress / 100.0
    return xy_pb.TaskUpdateProgress(country, realTaskUUID, progress, json.dumps(data["result"]))

    