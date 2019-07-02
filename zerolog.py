import os
import psutil
import multiprocessing
import threading
import datetime
import queue
import inspect


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
    def stop_log():
        Logger.run_stop.value = 1
        Logger.__log_proc.join()
        Logger.log_queue.cancel_join_thread()


def write_log(status, log_queue, log_conf):
    pid = os.getpid()
    proc_name = '{name}[{pid}<=P{ppid}]'.format(name=psutil.Process(pid).name(), pid=pid, ppid=os.getppid())
    message = '{log_time} {proc_name} {msg}'.format(log_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'),
                                                    proc_name=proc_name,
                                                    msg='开始记录日志')
    print(message)
    write_file = None
    write_db = False
    if log_conf.get('log_file'):
        __log_file = log_conf.get('log_file')
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
            if status.value != 0:
                if not flush_before_exit or log_queue.empty():
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


