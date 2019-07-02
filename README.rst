Zerolog
========================

用于记录日志的python库，日志消息先写入队列，以尽量减少记录日志的方法对性能的影响，再由独立的日志进程写入日志文件。



示例代码
---------------
::

  from zerolog import Logger
  # Step 1: start_log with dict
  Logger.start_log({'log_file': r'log\log.txt'})

  # Step 2: use log
  Logger.log('INFO', message)


性能对比
---------------

写入10万条日志，不记录调用方法和线程，则zerolog耗时0.29秒，python自带的logging库耗时3.70秒。具体见test/performance.py.
