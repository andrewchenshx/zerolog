import datetime
import logging
import multiprocessing
import time

from zerolog import Logger

if __name__ == '__main__':
    """写入10万条日志
    zerolog00:0.29200005531311035
    zerolog01:0.4070000648498535
    zerolog10:28.51200008392334
    zerolog11:26.667999982833862
    pythonlog:3.698000192642212
    """
    # multiprocessing.log_to_stderr(logging.DEBUG)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'main start')
    # Step 1: start_log with dict
    Logger.start_log({'log_file': r'log\log.txt', 'flush_before_exit': 'Y', 'time_out': 5})
    # Step 2: use log
    message = 'message ' * 20
    log_cnt = 100000

    start_time = time.time()
    for i in range(log_cnt):
        Logger.log('level', message, log_func=False, log_thread=False)
    end_time = time.time()
    run_time_zerolog = end_time - start_time
    print(f'zerolog00:{run_time_zerolog}')

    start_time = time.time()
    for i in range(log_cnt):
        Logger.log('level', message, log_func=False, log_thread=True)
    end_time = time.time()
    run_time_zerolog = end_time - start_time
    print(f'zerolog01:{run_time_zerolog}')

    start_time = time.time()
    for i in range(log_cnt):
        Logger.log('level', message, log_func=True, log_thread=False)
    end_time = time.time()
    run_time_zerolog = end_time - start_time
    print(f'zerolog10:{run_time_zerolog}')

    start_time = time.time()
    for i in range(log_cnt):
        Logger.log('level', message, log_func=True, log_thread=True)
    end_time = time.time()
    run_time_zerolog = end_time - start_time
    print(f'zerolog11:{run_time_zerolog}')

    logger = logging.getLogger('python')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(r'log\log2.txt')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    start_time = time.time()
    for i in range(log_cnt):
        logger.info(message)
    end_time = time.time()
    run_time_pythonlog = end_time - start_time

    print(f'pythonlog:{run_time_pythonlog}')
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'), 'main end')
