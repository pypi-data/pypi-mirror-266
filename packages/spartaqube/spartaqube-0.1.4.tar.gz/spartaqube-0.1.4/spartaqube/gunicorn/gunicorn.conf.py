import logging
bind = '0.0.0.0:8000'
workers = 3
accesslog = '/app/logs/gunicorn.access.log'
errorlog = '/app/logs/gunicorn.error.log'
capture_output = True
loglevel = 'debug'

#END OF QUBE
