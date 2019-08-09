import os
import psutil
import multiprocessing
import threading
import datetime
import queue
import inspect
from atexit import register
import sys


default_except_hook = sys.excepthook


class Logger(object):
    instance = None
    lock = threading.Lock()
    log_queue = None
    run_stop = multiprocessing.Value('i', 0)
    __log_proc = None

    def __init__(self):
        pass

    @staticmethod
    def start_log(log_conf):
        """
        :param log_conf:
        log_file:文本日志文件名
        log_db:sqlite数据库名
        time_out:读queue超时时间（秒）
        flush_before_exit:是否需要读完所有queue消息才退出，N为不需要
        :return:
        """
        if Logger.instance is None:
            Logger.lock.acquire()
            if Logger.instance is None:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '开始初始化单例')
                Logger.instance = Logger()

                Logger.log_queue = multiprocessing.Queue()
                Logger.__log_proc = multiprocessing.Process(target=write_log, args=(Logger.run_stop, Logger.log_queue, log_conf))
                Logger.__log_proc.start()
                # 主进程结束的时候会调用子进程的join()，因此需要通知并等待日志子进程先退出。
                register(Logger.instance.__stop_log)

                def custom_except_hook(exc_type, exc_value, exc_traceback):
                    print('custom except hook called')
                    Logger.instance.__stop_log()
                    default_except_hook(exc_type, exc_value, exc_traceback)

                sys.excepthook = custom_except_hook
            else:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '单例已经初始化')
            Logger.lock.release()
        else:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + '单例已经初始化')
        return Logger.instance

    @staticmethod
    def log(level, message, log_func=True, log_thread=True, name=''):
        log_time = datetime.datetime.now()
        if log_thread:
            cur_thread = threading.current_thread()
            thread_name = '{name}[{id}]'.format(name=cur_thread.getName(), id=cur_thread.ident)
        else:
            thread_name = ''
        if log_func:
            caller_frame_record = inspect.stack()[1]
            file_name = caller_frame_record[1]
            line_num = caller_frame_record[2]
            func_name = caller_frame_record[3]
        else:
            file_name = ''
            line_num = ''
            func_name = ''
        Logger.log_queue.put((log_time, thread_name, file_name, line_num, func_name, level, message, name))

    @staticmethod
    def __stop_log():
        Logger.run_stop.value = 1
        Logger.__log_proc.join()
        Logger.log_queue.cancel_join_thread()


def write_log(status, log_queue, log_conf):
    pid = os.getpid()
    ppid = os.getppid()
    proc = psutil.Process(pid)
    parent_proc_hash = hash(psutil.Process(ppid))

    proc_name = '{name}[{pid}<=P{ppid}]'.format(name=psutil.Process(pid).name(), pid=pid, ppid=ppid)
    message = '{log_time} {proc_name} {msg}'.format(log_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                                                    proc_name=proc_name,
                                                    msg='开始记录日志')
    print(message)
    write_file = None
    write_db = False
    if log_conf.get('log_file'):
        __log_file = log_conf.get('log_file')
        log_dir = os.path.dirname(os.path.abspath(__log_file))
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        write_file = open(file=__log_file, mode='a', encoding='utf8')

    if log_conf.get('log_db'):
        __log_db = log_conf.get('log_db')
        write_db = True

    # todo: 检查log_db中是否存在表结构

    if log_conf.get('time_out'):
        time_out = float(log_conf.get('time_out'))
    else:
        time_out = 1

    flush_before_exit = True
    if log_conf.get('flush_before_exit') == 'N':
        flush_before_exit = False

    if status.value == 0:
        while True:
            try:
                (log_time, thread_name, file_name, line_num, func_name, level, message, name) = log_queue.get(
                    block=True, timeout=time_out)
                if write_file:
                    line = '{log_time},{thread_name},{file_name},{func_name},{line_num},{level},{name},{message}\n'.format(
                        log_time=log_time.strftime('%Y-%m-%d %H:%M:%S.%f'),
                        thread_name=thread_name,
                        file_name=file_name,
                        func_name=func_name,
                        line_num=line_num,
                        name=name,
                        level=level,
                        message=message)
                    try:
                        write_file.write(line)
                    except Exception as e:
                        print(e)
                if write_db:
                    pass
            except queue.Empty:
                print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + " queue no data")
                # TODO: 主进程不会先于子进程结束，这里的检测代码无用？
                if psutil.pid_exists(ppid):
                    parent_proc = psutil.Process(ppid)
                    if not parent_proc or hash(parent_proc) != parent_proc_hash:
                        log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                        message = f'{log_time} {proc_name} 主进程[{ppid}]不存在(已重新分配)'
                        print(message)
                        break
                else:
                    log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    message = f'{log_time} {proc_name} 主进程[{ppid}]不存在'
                    print(message)
                    break
            if status.value != 0:
                if not flush_before_exit or log_queue.empty():
                    log_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                    message = f'{log_time} {proc_name} 状态变更为停止'
                    print(message)
                    break

    if write_file:
        write_file.close()
    message = '{log_time} {proc_name} {msg}'.format(log_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                                                    proc_name=proc_name,
                                                    msg='退出记录日志')
    print(message)


def str_code_point(s):
    return ''.join(['\\u{:0>4x}'.format(ord(c)) for c in s])


def env_to_str(env):
    key_list = [key for key in env.keys()]
    key_list.sort()
    return '\n'.join(['[{key}]:[{value}]'.format(key=key, value=env.get(key)) for key in key_list])


