import logging
import logging.handlers
from logging.handlers import WatchedFileHandler
import os
import multiprocessing
bind = '127.0.0.1:8000' 
backlog = 512               
timeout = 30   
worker_class = 'eventlet'
reload = True
#workers = multiprocessing.cpu_count() * 2 + 1     
workers = 1
loglevel = 'info' 
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
accesslog = "-"      
errorlog = "-"    
