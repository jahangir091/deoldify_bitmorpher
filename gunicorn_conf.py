# gunicorn_conf.py
from multiprocessing import cpu_count

# Socket path
bind = 'unix:/run/deoldify/gunicorn.sock'

# Worker Options
# workers = cpu_count() + 1
workers = 2
worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options
loglevel = 'debug'
accesslog = '/var/log/deoldify/access.log'
errorlog = '/var/log/deoldify/error.log'
