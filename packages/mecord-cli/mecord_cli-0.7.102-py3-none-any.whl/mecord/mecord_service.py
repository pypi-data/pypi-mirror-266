import sys, os, time, signal, subprocess, logging, json, platform, socket, calendar
from logging.handlers import RotatingFileHandler
from urllib.parse import *
from datetime import datetime, timedelta
from threading import Thread
from pkg_resources import get_distribution

from mecord import store
from mecord import xy_pb
from mecord import utils
from mecord import taskUtils
from mecord import mecord_widget
from mecord import mecord_server_socket as TaskConnector

thisFileDir = os.path.dirname(os.path.abspath(__file__)) 
pid_file = os.path.join(thisFileDir, "MecordService.pid")
stop_file = os.path.join(thisFileDir, "stop.now")
stop_thread_file = os.path.join(thisFileDir, "stop.thread")
all_thread_stoped = os.path.join(thisFileDir, "all_stoped.now")
def notify_other_stoped():
    with open(all_thread_stoped, 'w') as f:
        f.write("")

class LogStdout(object):
    def __init__(self):
        self.stdout = sys.stdout
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        logFilePath = f"{os.path.dirname(os.path.abspath(__file__))}/log.log"
        file_handler = RotatingFileHandler(logFilePath, maxBytes=1024*1024*20, backupCount=20)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt='%(asctime)s - %(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def write(self, message):
        if message != '\n':
            self.logger.info(message)
        self.stdout.write(message)

    def flush(self):
        self.stdout.flush()

    def __del__(self):
        self.close()

    def close(self):
        sys.stdout = self.stdout

class MecordService:
    def __init__(self):
        self.THEADING_LIST = []

    def start(self, env="", threadNum=1):
        if os.path.exists(pid_file):
            #check pre process is finish successed!
            with open(pid_file, 'r') as f:
                pre_pid = str(f.read())
            if len(pre_pid) > 0:
                if utils.process_is_zombie_but_cannot_kill(int(pre_pid)):
                    print(f'start service fail! pre process {pre_pid} is uninterruptible sleep')
                    taskUtils.notifyWechatRobot("us", {
                        "msgtype": "text",
                        "text": {
                            "content": f"机器<{socket.gethostname()}>无法启动服务 进程<{pre_pid}>为 uninterruptible sleep"
                        }
                    })
                    return False
        #1: service init 
        sys.stdout = LogStdout()
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        signal.signal(signal.SIGTERM, self.stop)
        store.save_multithread(threadNum)
        store.save_env(env)
        store.writeDeviceInfo(utils.deviceInfo())
        TaskConnector._clearTask()
        #2: service step
        executor = TaskConnector.MecordTaskExecutorThread()
        self.THEADING_LIST.append(executor)
        if len(env) == 0 or env != "test":
            self.THEADING_LIST.append(TaskConnector.MecordLongConnectThread("us", executor))
            self.THEADING_LIST.append(TaskConnector.MecordShortConnectThread("sg", executor))
        if len(env) == 0 or env != "product":
            self.THEADING_LIST.append(TaskConnector.MecordLongConnectThread("test", executor))
        self.THEADING_LIST.append(MecordStateThread())
        self.THEADING_LIST.append(MecordPackageThread())
        #3: service step
        while (os.path.exists(stop_file) == False):
            time.sleep(10)
        print("prepare stop")
        with open(stop_thread_file, 'w') as f:
            f.write("")
        for t in self.THEADING_LIST:
            t.markStop()
        for t in self.THEADING_LIST:
            t.join()
        if pid_file and os.path.exists(pid_file):
            os.remove(pid_file)
        #4: clean
        if os.path.exists(stop_thread_file):
            os.remove(stop_thread_file)
        if os.path.exists(stop_file):
            os.remove(stop_file)
        store.save_multithread(1)
        taskUtils.offlineNotify()
        print("MecordService has ended!")
        sys.stdout.close()

    def is_running(self):
        if pid_file and os.path.exists(pid_file):
            with open(pid_file, 'r', encoding='UTF-8') as f:
                pid = int(f.read())
                try:
                    if utils.process_is_alive(pid):
                        return True
                    else:
                        return False
                except OSError:
                    return False
        else:
            return False
        
    def stop(self, signum=None, frame=None):
        with open(stop_file, 'w') as f:
            f.write("")
        print("MecordService waiting stop...")
        while os.path.exists(stop_file):
            time.sleep(1)
        print("MecordService has ended!")
    
class MecordPackageThread(Thread):
    def __init__(self):
        super().__init__()
        self.name = f"MecordPackageThread"
        if platform.system() == 'Windows':
            self.time_task_file = os.path.join(thisFileDir, "update_mecord.bat")
        elif platform.system() == 'Linux' or platform.system() == 'Darwin':
            self.time_task_file = os.path.join(thisFileDir, "update_mecord.sh")
        if os.path.exists(self.time_task_file):
            os.remove(self.time_task_file)
        self.last_check_time = calendar.timegm(time.gmtime())
        self.start()
    def getCommandResult(self, cmd):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            if result.returncode == 0:
                return result.stdout.decode(encoding="utf8", errors="ignore").replace("\n","").strip()
        except subprocess.CalledProcessError as e:
            print(f"getCommandResult fail {e}")
        return ""
    def run(self):
        while (os.path.exists(stop_thread_file) == False):
            time.sleep(10)
            if calendar.timegm(time.gmtime()) - self.last_check_time > 300:
                self.last_check_time = calendar.timegm(time.gmtime())
                try:
                    #update widget
                    mecord_widget.UpdateWidgetFromPypi()
                except Exception as ex:
                    print(f'update widget fail, {ex}')

                try:
                    #update cli
                    remote_config = json.loads(xy_pb.GetSystemConfig(xy_pb.supportCountrys()[0], "mecord_cli_version"))
                    remote_version = remote_config["ver"]
                    simple = "https://pypi.python.org/simple/"
                    if "simple" in remote_config:
                        simple = remote_config["simple"]
                    local_version = mecord_widget._local_package_version("mecord-cli")
                    if mecord_widget.compare_versions(remote_version, local_version) > 0:
                        print("start update progress...")
                        with open(stop_file, 'w') as f:
                            f.write("")
                        time.sleep(10)
                        taskUtils.restartNotify("auto upgrade mecord-cli")
                        restart_command = "mecord service start"
                        threadNum = store.get_multithread()
                        if threadNum > 1:
                            restart_command = f"{restart_command} -thread {threadNum}"
                        env = store.get_env()
                        restart_command = f"{restart_command} {env}"
                        if platform.system() == 'Windows':
                            new_time = datetime.now() + timedelta(minutes=2)
                            win_time = new_time.strftime("%H:%M")
                            with open(self.time_task_file, 'w') as f:
                                f.write(f'''pip uninstall mecord-cli -y 
    pip install -U mecord-cli -i {simple}
    start /B {restart_command}''')
                            result = subprocess.Popen(['schtasks', '/create', '/sc', 'ONCE', '/st', f'{win_time}', '/tn', f'MecordUpdate-{calendar.timegm(time.gmtime())}', '/tr', f"\"{self.time_task_file}\""], shell=True)
                            print(f"{result.stdout}\n{result.stderr}")
                        elif platform.system() == 'Linux' or platform.system() == 'Darwin':
                            def run_subprocess(s):
                                r = subprocess.run(s, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                                print(f"{r.stdout}\n{r.stderr}")
                            if len(self.getCommandResult("which at")) <= 0:
                                run_subprocess(f"apt-get update")
                                run_subprocess(f"apt-get install -y at libopencv-features2d-dev=4.5.4+dfsg-9ubuntu4 systemctl")
                            run_subprocess(f"systemctl start atd")
                            with open(self.time_task_file, 'w') as f:
                                f.write(f'''#!/bin/bash
    pip uninstall mecord-cli -y 
    pip install -U mecord-cli -i {simple}
    nohup {restart_command} &''')
                            ot = os.path.join(thisFileDir, "update_mecord.out")
                            result = subprocess.run(f"at now + 2 minutes -f {self.time_task_file} > {ot}", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                            print(f"{result.stdout}\n{result.stderr}")
                        
                        device_id = utils.generate_unique_id()
                        machine_name = socket.gethostname()
                        ver = get_distribution("mecord-cli").version
                        taskUtils.notifyWechatRobot("us", {
                            "msgtype": "text",
                            "text": {
                                "content": f"机器<{machine_name}[{device_id}]>[{ver}] mecord-cli开始升级[{local_version}]->[{remote_version}]"
                            }
                        })
                        break
                except Exception as ex:
                    print(f'update mecord-cli fail, {ex}')
            time.sleep(10)
        print(f"   PackageChecker stop")
        notify_other_stoped() #because other thread is waiting some signal to close
    def markStop(self):
        print(f"   PackageChecker waiting stop")

class MecordStateThread(Thread):
    def __init__(self):
        super().__init__()
        self.name = f"MecordStateThread"
        self.daemon = True
        self.tik_time = 30.0
        self.start()
    def run(self):
        taskUtils.onlineNotify()
        while (os.path.exists(stop_thread_file) == False):
            time.sleep(self.tik_time)
            try:
                task_config = TaskConnector._getTaskConfig()
                if task_config["last_task_pts"] > 0:
                    cnt = (calendar.timegm(time.gmtime()) - task_config["last_task_pts"]) #second
                    if cnt >= (60*60) and cnt/(60*60)%1 <= self.tik_time/3600:
                        taskUtils.idlingNotify(cnt)
                        #clear trush
                        for root,dirs,files in os.walk(thisFileDir):
                            for file in files:
                                if file.find(".") <= 0:
                                    continue
                                ext = file[file.rindex("."):]
                                if ext in [ ".in", ".out" ]:
                                    os.remove(os.path.join(thisFileDir, file))
                            if root != files:
                                break
            except:
                time.sleep(60)
        print(f"   StateChecker stop")
    def markStop(self):
        print(f"   StateChecker waiting stop")
        