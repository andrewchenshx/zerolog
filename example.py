import datetime
import logging
import multiprocessing
import time

from zerolog import Logger

if __name__ == '__main__':
    multiprocessing.log_to_stderr(logging.DEBUG)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'main start')
    # Step 1: start_log with dict
    Logger.start_log({'log_file': r'log\log.txt', 'flush_before_exit': 'Y', 'time_out': 5})
    # Step 2: use log
    Logger.log('level', 'message')
    Logger.log('level', 'message')
    Logger.log('level', 'message')
    for i in range(10000):
        Logger.log('level', i)

    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'main end')
