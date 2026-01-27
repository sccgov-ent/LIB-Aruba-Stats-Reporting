from .central import Central
from .dataprocessing import *
from .error_report import *
from datetime import *
import traceback
import sys

#api = Central()
with open("/home/yam/dev1/WhoFi/logs/" + datetime.now().strftime("%y-%m-%d-%H:%M") + ".log", "a") as log:
    sys.stdout = log
    if len(sys.argv) > 1 and sys.argv[1] == "error":
        print("error report")
        error_report()
    else:
        
        try:
            #api.gather_data()
            gather_test_data()
        except Exception as error:
            log.write(repr(error))
            log.write(traceback.format_exc())
