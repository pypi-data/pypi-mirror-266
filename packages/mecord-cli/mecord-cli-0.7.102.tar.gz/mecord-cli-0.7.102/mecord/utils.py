import uuid
import platform
import subprocess
import os
import sys
import requests
from io import BytesIO
import psutil
import pynvml
import datetime
import http
import json
from pathlib import Path
import zipfile
import socket
from PIL import Image

def get_mac_from_nettools():
    try:
        cmd = "ifconfig"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode(encoding='UTF-8')
        mac = output_str[output_str.index('ether') + 6:output_str.index('ether') + 23].replace(':', '')
        return True, mac
    except Exception as e:
        return False, None
    
def get_mac_from_system():
    try:
        root_path = '/sys/class/net/'
        dbtype_list = os.listdir(root_path)
        for dbtype in dbtype_list:
            if os.path.isfile(os.path.join(root_path, dbtype)):
                dbtype_list.remove(dbtype)

        if len(dbtype_list) == 0:
            return False, None
        mac = ''
        for dbtype in dbtype_list:
          cmd = f"cat {root_path}{dbtype}/address"
          output = subprocess.check_output(cmd, shell=True)
          mac += output.decode(encoding='UTF-8')
        return True, mac
    except Exception as e:
        return False, None

mac_value = ""
def get_mac_address():
    global mac_value
    if mac_value and len(mac_value) > 0:
        return mac_value
    
    if platform.system() == 'Windows':
        cmd = "ipconfig /all"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode('gbk')
        pos = output_str.find('Physical Address')
        if pos == -1:
            pos = output_str.find('物理地址')
        mac_value = (output_str[pos:pos+100].split(':')[1]).strip().replace('-', '')
    elif platform.system() == 'Linux' or platform.system() == 'Darwin':
        ok, mac_value = get_mac_from_nettools()
        if ok:
            return mac_value
        ok, mac_value = get_mac_from_system()
        if ok:
            return mac_value
        return None
    else:
        mac_value = None
    return mac_value

cpu_serial = ""
def get_cpu_serial():
    global cpu_serial
    if cpu_serial and len(cpu_serial) > 0:
        return cpu_serial
    
    if platform.system() == 'Windows':
        cmd = "wmic cpu get ProcessorId"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode('gbk')
        pos = output_str.index("\n")
        cpu_serial = output_str[pos:].strip()
    elif platform.system() == 'Linux':
        with open('/proc/cpuinfo') as f:
            
            for line in f:
                if line[0:6] == 'Serial':
                    return "1"
                if line.strip().startswith('serial'):
                    cpu_serial = line.split(":")[1].strip()
                    break
        if not cpu_serial:
            cpu_serial = None
    elif platform.system() == 'Darwin':
        cmd = "/usr/sbin/system_profiler SPHardwareDataType"
        output = subprocess.check_output(cmd, shell=True)
        output_str = output.decode(encoding='UTF-8')
        cpu_serial = output_str[output_str.index('Hardware UUID:') + 14:output_str.index('Hardware UUID:') + 51].replace('-', '')
    else:
        cpu_serial = None
    return cpu_serial

def get_hostname():
    return socket.gethostname()

def generate_unique_id():
    mac = get_mac_address()
    cpu_serial = get_cpu_serial()
    hostname = get_hostname()
    if mac and cpu_serial:
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, mac + cpu_serial + hostname)
        return str(unique_id).replace('-', '')
    if mac :
        unique_id = uuid.uuid5(uuid.NAMESPACE_DNS, mac + hostname)
        return str(unique_id).replace('-', '')

def getOssImageSize(p):
    try:
        s = requests.session()
        s.keep_alive = False
        res = s.get(p, timeout=60)
        image = Image.open(BytesIO(res.content), "r")
        s.close()
        return image.size
    except:
        return 0, 0
    
def deviceInfo():
    mac = get_mac_address()
    mac = "" if mac == None else mac
    cpu_serial = get_cpu_serial()
    cpu_serial = "" if cpu_serial == None else cpu_serial
    hostname = get_hostname()
    M=1024*1024
    data = {
        "cpu": {
            "logical_count" : psutil.cpu_count(),
            "count" : psutil.cpu_count(logical=False),
            "max_freq" : f"{psutil.cpu_freq().max / 1000} GHz",
        },
        "memory": {
            "total" : f"{psutil.virtual_memory().total/M} M",
            "free" : f"{psutil.virtual_memory().free/M} M"
        },
        "gpu": {
            "count" : 0,
            "list" : [],
            "mem" : []
        },
        "device_id": generate_unique_id(),
        "host_name": hostname
    }
    try:
        pynvml.nvmlInit()
        gpuCount = pynvml.nvmlDeviceGetCount()
        data["gpu"]["count"] = gpuCount
        for i in range(gpuCount):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            data["gpu"]["list"].append(f"GPU{i}: {pynvml.nvmlDeviceGetName(handle)}")
            memInfo = pynvml.nvmlDeviceGetMemoryInfo(handle)
            data["gpu"]["mem"].append(f"GPU{i}: total:{memInfo.total/M} M free:{memInfo.free/M} M")
            
        pynvml.nvmlShutdown()
    except Exception as e:
        data["gpu"]["count"] = 1
        data["gpu"]["list"].append(f"GPU0: Normal")
    return data

def reportLog():
    reason = ""
    if len(sys.argv) >= 2:
        reason = sys.argv[2].strip().replace("\n","").replace(",","").replace(" ","").replace(";","")
    d = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    uid = generate_unique_id()

    thisFileDir = os.path.dirname(os.path.abspath(__file__))
    dist = os.path.join(thisFileDir, f"{uid}_{reason}_{d}.zip")
    zip = zipfile.ZipFile(dist, "w", zipfile.ZIP_DEFLATED) 

    for root,dirs,files in os.walk(thisFileDir):
        for file in files:
            if str(file).startswith("~$"):
                continue
            ext = file[file.rindex("."):]
            if ext == ".log" or ext == ".json" or ".log." in file:
                filepath = os.path.join(root, file)
                zip.write(filepath, file)
        if root != files:
            break
    zip.close()
    ossurl = uploadOSS(dist)
    os.remove(dist)
    return ossurl

def uploadOSS(file):
    conn = http.client.HTTPSConnection("api.mecordai.com")
    payload = json.dumps({
        "sign": "f0463f490eb84133c0aab3a8576ed2fc"
    })
    headers = {
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/proxymsg/get_oss_config", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    if data["code"] == 0:
        AccessKeyId = data["data"]["AccessKeyId"]
        AccessKeySecret = data["data"]["AccessKeySecret"]
        SecurityToken = data["data"]["SecurityToken"]
        BucketName = data["data"]["BucketName"]
        Expiration = data["data"]["Expiration"]
        Endpoint = data["data"]["Endpoint"]
        CallbackUrl = data["data"]["CallbackUrl"]
        cdn = data["data"]["cdn"]
        
        if len(AccessKeyId) > 0:  
            import oss2
            auth = oss2.StsAuth(AccessKeyId, AccessKeySecret, SecurityToken)
            bucket = oss2.Bucket(auth, Endpoint, BucketName, connect_timeout=600)
            with open(file, "rb") as f:
                byte_data = f.read()
            file_name = Path(file).name
            publish_name = f"mecord/report/{file_name}" 
            bucket.put_object(publish_name, byte_data)
            return f"{cdn}{publish_name}" 
    else:
        print(f"get_oss_config fail: response={data}")

def process_is_alive(pid: int) -> bool:
    try:
        process = psutil.Process(pid)
        pstatus = process.status()
        if pstatus == psutil.STATUS_RUNNING or pstatus == psutil.STATUS_SLEEPING:
            return True
        else:
            return False
    except (FileNotFoundError, psutil.NoSuchProcess):
        return False
    except Exception as e:
        return False
    
def process_is_zombie_but_cannot_kill(pid: int) -> bool:
    try:
        process = psutil.Process(pid)
        pstatus = process.status()
        if pstatus == psutil.STATUS_DISK_SLEEP:
            return True
    except Exception as e:
        return False
    return False
    
def firstExitWithDir(root, suffix):
    for root,dirs,files in os.walk(root):
        for file in files:
            if file.find(".") <= 0:
                continue
            ext = file[file.rindex("."):]
            if ext == f".{suffix}":
                return os.path.join(root, file)
        if root != files:
            break
    return None