import json
import logging
from logging.config import dictConfig
import time
import os
import sys

from testrun.testengine import RulesEngineTester
from git_api.misc import update_files

__PATHS = {'temp_folder': os.path.join(os.getcwd(), "temp"),
            'diagnostic_files': os.path.join(os.getcwd(), "temp", "diagnostic_files"),
            'excel_files': os.path.join(os.getcwd(), "temp", "excel_files"),
            'jsons': os.path.join(os.getcwd(), "temp", "excel_files", "jsons")}


def make_folders():
    for key in __PATHS.keys():
        if not os.path.exists(__PATHS[key]):
            os.mkdir(__PATHS[key])


def filter_args(args):
    filtered_args = {}
    try:
        json_file_name = args[0]
        filtered_args["json_file_name"] = json_file_name
    except IndexError:
        filtered_args["json_file_name"] = None
    
    return filtered_args


def load_json_commands(json_file_name=None):
    if json_file_name:
        try:
            with open(json_file_name) as f:
                json_commands = json.load(f)
        except FileNotFoundError:
            print("""
                    SELECTED file does not exist. Please use add a useable
                    filename as an arg. """)
    else:
        try:
            with open("JsonCommands2.json") as f:
                json_commands = json.load(f)
        except FileNotFoundError:
            print("""
                DEFAULT file does not exist. Please use add a useable
                filename as an arg. """)

    return json_commands


if __name__ == "__main__":
    with open("logging_config.json") as f:
        log_config = json.load(f)
    dictConfig(log_config)

    __log = logging.getLogger("TestRun")

    __log.info("Checking/Creating folder directory... ")
    make_folders()

    filtered_args = filter_args(sys.argv[1:])
    json_file_name = filtered_args["json_file_name"]

    __log.info(f"Using file {json_file_name}")
    
    try:
        json_commands = load_json_commands(json_file_name)

        try:
            test_RE = RulesEngineTester(__PATHS['excel_files'])
            test_RE.run(tests_to_run=json_commands)
            print("Tests Complete... \n Shutting down...")
        except Exception as e:
            raise "Unable to instantiate the RulesEngineTester class."

    except Exception as e:
        __log.info(f"Error during process. Shutting down ...")
    
    time.sleep(5)
