import sys, os, urllib3, curses, time, platform, json

from mecord import utils
from mecord import mecord_service
from mecord import mecord_widget
from mecord import store
from mecord import utils
from mecord import taskUtils

ll = 42
def scr_str(s):
    return "| " + s + " |"
def scr_str1(s):
    return "| " + s
def scr_line(s):
    return "|" + s + "|"

def service_status(stdscr, idx):
    def real_stdsrc(*args):
        if platform.system() == 'Windows':
            print(args[2])
        else:
            stdscr.addstr(*args)
    if platform.system() != 'Windows':
        real_stdsrc(idx, 0, scr_str("test".ljust(ll)))
        real_stdsrc(idx, ll*1-1, scr_str("us".ljust(ll)))
        real_stdsrc(idx, ll*2-2, scr_str("sg".ljust(ll)))
        idx+=1
    def running_task_uuids():
        test_lst = []
        us_lst = []
        sg_lst = []
        if os.path.exists(taskUtils.task_config_file):
            with open(taskUtils.task_config_file, 'r') as f:
                data = json.load(f)
            infos = ""
            for it in data:
                if it not in ["last_task_pts"]:
                    c = data[it]["country"].lower()
                    if c == "test":
                        test_lst.append(it)
                    elif c == "us":
                        us_lst.append(it)
                    elif c == "sg":
                        sg_lst.append(it)
        return test_lst, us_lst, sg_lst
    test_lst, us_lst, sg_lst = running_task_uuids()
    for d in range(0, max([len(test_lst),len(us_lst),len(sg_lst)])):
        def widget_stdscr(this_d, this_lst, row_idx, col_idx, append_str):
            if this_d < len(this_lst):
                real_s = this_lst[this_d]
                if len(append_str) > 0:
                    real_s += f" [{append_str}]"
                real_stdsrc(row_idx, col_idx, scr_str(" " + real_s.ljust(ll-1)))
            else:
                real_stdsrc(row_idx, col_idx, scr_str(" " + " ".ljust(ll-1)))
        widget_stdscr(d, test_lst, idx, 0, "test" if platform.system() == 'Windows' else "")
        widget_stdscr(d, us_lst, idx, ll*1-1, "us" if platform.system() == 'Windows' else "")
        widget_stdscr(d, sg_lst, idx, ll*2-2, "sg" if platform.system() == 'Windows' else "")
        idx+=1
    return idx

def device_status(stdscr, idx):
    def real_stdsrc(*args):
        if platform.system() == 'Windows':
            print(args[2])
        else:
            stdscr.addstr(*args)
    import psutil
    import GPUtil
    cpu_load = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_load = mem.percent
    gpu_list = GPUtil.getGPUs()
    if len(gpu_list) > 0:
        gpu_load = gpu_list[0].load * 100  # 只考虑第一块显卡
    else:
        gpu_load = 0
    real_stdsrc(idx, 0, scr_str(f"Device Usage                  CPU : {cpu_load}%                  Memory : {mem_load}%                  GPU : {gpu_load}%".ljust(ll*3-2)))
    idx+=1
    return idx

def widget_status(stdscr, idx):
    def real_stdsrc(*args):
        if platform.system() == 'Windows':
            print(args[2])
        else:
            stdscr.addstr(*args)
    real_stdsrc(idx, 0, scr_str("Widget List".ljust(ll*3-2)))
    idx+=1
    widget_map = store.widgetMap()
    if len(widget_map) == 0:
        real_stdsrc(idx, 0, scr_str("empty"))
        idx+=1
        return idx
    maxJust = 10
    for it in widget_map:
        if len(it) > maxJust:
            maxJust = len(it)
    maxJust += 5
    for it in widget_map:
        path = ""
        is_block = False
        if isinstance(widget_map[it], (dict)):
            path = widget_map[it]["path"]
            is_block = widget_map[it]["isBlock"]
        else:
            path = map[it]
        end_args = ""
        if is_block:
            end_args = " [X]"
        real_stdsrc(idx, 0, scr_str(f'{f"{it}{end_args}".ljust(maxJust)} {path}'.ljust(ll*3-2)))
        idx+=1
    return idx

def status():
    from pkg_resources import parse_version, get_distribution
    ver = get_distribution("mecord-cli").version
    deviceid = utils.generate_unique_id()
    import socket
    machine_name = socket.gethostname()
    service = mecord_service.MecordService()
    thread_num = store.get_multithread()

    if platform.system() == 'Windows':
        service_is_running = service.is_running()
        print(scr_line("-" * ll*3))
        print(scr_str(f"Mecord".ljust(ll*3-2)))
        print(scr_str(f"版本: {ver}".ljust(ll*3-4)))
        print(scr_str(f"设备号: {deviceid}".ljust(ll*3-5)))
        print(scr_str(f"容器HostName: {machine_name}".ljust(ll*3-4)))
        print(scr_line("-" * ll*3))
        if service_is_running:
            print(scr_str1(f"运行中 ({thread_num} 线程)".ljust(ll*3-2)))
        else:
            print(scr_str1("未运行".ljust(ll*3-2)))
        print(scr_line("-" * ll*3))
        service_status(None, 0)
        print(scr_line("-" * ll*3))
        device_status(None, 0)
        print(scr_line("-" * ll*3))
        widget_status(None, 0)
        print(scr_line("-" * ll*3))
    else:
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        stdscr.keypad(True)
        try:
            tiktak = 0
            while True:
                stdscr.clear()
                height, width = stdscr.getmaxyx()
                service_is_running = service.is_running()
                idx=0
                stdscr.addstr(idx, 0, scr_line("-" * ll*3))
                idx+=1
                stdscr.addstr(idx, 0, scr_str(f"Mecord".ljust(ll*3-2)))
                idx+=1
                stdscr.addstr(idx, 0, scr_str(f"版本: {ver}".ljust(ll*3-4)))
                idx+=1
                stdscr.addstr(idx, 0, scr_str(f"设备号: {deviceid}".ljust(ll*3-5)))
                idx+=1
                stdscr.addstr(idx, 0, scr_str(f"容器HostName: {machine_name}".ljust(ll*3-4)))
                idx+=1
                stdscr.addstr(idx, 0, scr_line("-" * ll*3))
                idx+=1
                if service_is_running:
                    if tiktak > 3:
                        tiktak = 0
                    stdscr.addstr(idx, 0, scr_str1("运行中"+"."*tiktak+f" ({thread_num} 线程)".ljust(ll*3-2)), curses.color_pair(1))
                    tiktak+=1
                else:
                    stdscr.addstr(idx, 0, scr_str1("未运行".ljust(ll*3-2)), curses.color_pair(2))
                idx+=1
                stdscr.addstr(idx, 0, scr_line("-" * ll*3))
                idx+=1
                idx = service_status(stdscr, idx)
                stdscr.addstr(idx, 0, scr_line("-" * ll*3))
                idx+=1
                idx = device_status(stdscr, idx)
                stdscr.addstr(idx, 0, scr_line("-" * ll*3))
                idx+=1
                idx = widget_status(stdscr, idx)
                stdscr.addstr(idx, 0, scr_line("-" * ll*3))
                stdscr.refresh()
                time.sleep(1)
        except:
            pass
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()

def service():
    if len(sys.argv) <= 2:
        print('please set command!')
        utils.show_help()
        return

    command = sys.argv[2]
    service = mecord_service.MecordService()
    if command == 'start':
        wid_map = store.widgetMap()
        if len(wid_map) == 0:
            print("please add widget first!")
            utils.show_help()
            return
        if service.is_running():
            print('Service is already running.')
        else:
            print(f'Starting service...[args = {" ".join(sys.argv)}]')
            threadNum = 1
            idx = 2      
            env = ""
            while idx < len(sys.argv):
                if sys.argv[idx] == "-thread":
                    threadNum = int(sys.argv[idx+1])
                    if threadNum < 1 or threadNum > 500:
                        print('multi thread number must be 1~500')
                        return
                if sys.argv[idx] in ["prod","product"]:
                    env = "product"
                if sys.argv[idx] in ["test"]:
                    env = "test"
                idx+=1
            service.start(env, threadNum)
    elif command == 'stop':
        if not service.is_running():
            print('Service is not running.')
        else:
            print('Stopping service...')
            service.stop()
    elif command == 'status': 
        status()
    else:
        print("Unknown command:", command)

def widget():
    if len(sys.argv) <= 2:
        print('please set command! Usage: mecord widget [init|publish]')
        return

    command = sys.argv[2]
    work_path = os.getcwd()
    if len(sys.argv) > 3:
        work_path = sys.argv[3]
    if command == 'init':
        mecord_widget.createWidget(work_path)
    elif command == 'publish':
        mecord_widget.publishWidget(work_path)
    elif command == 'list':
        map = store.widgetMap()
        if len(map) == 0:
            print("local widget is empty")
        maxJust = 20
        for it in map:
            if len(it) > maxJust:
                maxJust = len(it)
        maxJust += 10
        showStatus = ""
        if len(sys.argv) > 3:
            showStatus = sys.argv[3]
        for it in map:
            path = ""
            is_block = False
            if isinstance(map[it], (dict)):
                path = map[it]["path"]
                is_block = map[it]["isBlock"]
            else:
                path = map[it]
            end_args = ""
            if is_block:
                end_args = " [X]"
            ss = f"{it}{end_args}"
            if showStatus in ["disable", "enable"]:
                if is_block and showStatus == "disable":
                    print(f'{ss.ljust(maxJust + 4)} {path}')
                elif is_block == False and showStatus == "enable":
                    print(f'{ss.ljust(maxJust + 4)} {path}')
            else:
                print(f'{ss.ljust(maxJust + 4)} {path}')
    elif command == 'add':
        mecord_widget.addWidgetToEnv(work_path)
    elif command == 'remove':
        mecord_widget.remove(work_path)
    elif command == 'enable':
        mecord_widget.enable(work_path)
    elif command == 'disable':
        mecord_widget.disable(work_path)
    elif command == 'pending_task':
        mecord_widget.getTaskCount(work_path)
    else:
        print("Unknown command:", command)

def main():
    urllib3.disable_warnings()

    if len(sys.argv) >= 2:
        module = sys.argv[1]
        if module == "widget":
            widget()
        elif module == "service":
            service()
        elif module == "status":
            status()
        elif module == "report":
            utils.reportLog()
            print(f"report success")
        else:
            print(f"Unknown command:{module}")
            sys.exit(0)
    else:
        status()

if __name__ == '__main__':
    main()
