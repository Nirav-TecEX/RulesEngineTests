import json
from logging.config import dictConfig
from testrun.testrun import RulesEngineTester
import time
import os

if __name__ == "__main__":
    with open("logging_config.json") as f:
        log_config = json.load(f)
    dictConfig(log_config)

    __PATHS = {'temp_folder': os.path.join(os.getcwd(), "temp"),
               'diagnostic_files': os.path.join(os.getcwd(), "temp", "diagnostic_files"),
               'excel_files': os.path.join(os.getcwd(), "temp", "excel_files"),
               'jsons': os.path.join(os.getcwd(), "temp", "excel_files", "jsons")}
    
    for key in __PATHS.keys():
        if not os.path.exists(__PATHS[key]):
            os.mkdir(__PATHS[key])
    
    test_RE = RulesEngineTester()
    test_RE.run()

    print("Tests Complete... \n Shutting down...")
    time.sleep(5)

    