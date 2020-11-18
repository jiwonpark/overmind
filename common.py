import sys
import logging
import time

logging.basicConfig(
    filename='vulture.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p'
)

def log(*args):
    print("%s %s: %s" % (time.strftime('%x %X %Z'), sys._getframe(1).f_code.co_name, " ".join(map(str, list(args)))))
    logging.info("%s: %s" % (sys._getframe(1).f_code.co_name, " ".join(map(str, list(args)))))

def running_in_notebook():
    try:
        get_ipython()
        return True
    except:
        return False
