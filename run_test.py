import json
from logging.config import dictConfig
import time
import os

from testrun.testengine import RulesEngineTester
from git_api.misc import update_files

__PATHS = {'temp_folder': os.path.join(os.getcwd(), "temp"),
            'diagnostic_files': os.path.join(os.getcwd(), "temp", "diagnostic_files"),
            'excel_files': os.path.join(os.getcwd(), "temp", "excel_files"),
            'jsons': os.path.join(os.getcwd(), "temp", "excel_files", "jsons")}

if __name__ == "__main__":
    with open("logging_config.json") as f:
        log_config = json.load(f)
    dictConfig(log_config)

    with open("JsonCommands2.json") as f:
        json_commands = json.load(f)
    
    for key in __PATHS.keys():
        if not os.path.exists(__PATHS[key]):
            os.mkdir(__PATHS[key])

    try:
        test_RE = RulesEngineTester(__PATHS['excel_files'])
    except Exception as e:
        raise "Unable to instantiate the RulesEngineTester class."
    try:
        test_RE.run(tests_to_run=json_commands)
    except Exception as e:
        raise f"Error during testrun. \n\t {e}"

    print("Tests Complete... \n Shutting down...")
    time.sleep(5)
