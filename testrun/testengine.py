import logging
import os
import subprocess

class RulesEngineTester:
    def __init__(self) -> None:
        self.__log = logging.getLogger("TestRun").getChild("RulesEngineTester")
        self.__subproc_out_txt = ""

    @property
    def subproc_out_txt(self):
        return self.__subproc_out_txt

    @subproc_out_txt.setter
    def subproc_out_txt(self, name):
        self.__subproc_out_txt = os.path.join("temp", "diagnostic_files", f"{name}.txt")
    
    @property
    def test_path(self):
        return os.path.join("postman", "testfromexcel.py")

    def __run(self, filename=None, personal_cmd=None):
               
        if not personal_cmd:
            excel_file_path = os.path.join("temp", "excel_files", filename)   
            postman_cmd = ['python', f"{self.test_path}", "-r", excel_file_path, "-u", 
                           "https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c"]
        else:
            postman_cmd = ['python', f"{self.test_path}"] + personal_cmd
            for i in range(0, len(personal_cmd)):
                if personal_cmd[i] in ["-g", "-r", "--generate", "--run"]:
                    try:
                        filename = os.path.split(personal_cmd[i+1])[-1]
                        break
                    except IndexError as e:
                        pass
            
        if not filename:
            self.__log.info("No file or commands given. ")
            return

        self.subproc_out_txt = filename.replace(".xlsx","") 

        with open(self.subproc_out_txt, 'w+') as f:
            f.write(f"Command executed:\n{postman_cmd}\n\n")

        subproc = subprocess.Popen(postman_cmd, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)

        self.__log.info(f"Subprocess Test for {filename} started.")
        with open(self.subproc_out_txt, 'a', encoding='utf-8') as out_file:
            attempts = 0
            while attempts < 3:
                try:
                    outs, errs = subproc.communicate()
                except subprocess.TimeoutExpired:
                    subproc.kill()
                    attempts = attempts + 1
                    out_file.write(f"Attempt {attempts} complete.")
                    continue

                out_file.write(f"Attempt {attempts} Out:\n")
                out_file.write(outs.decode('utf-8'))
                out_file.write(f"Attempt {attempts} Error:\n")
                out_file.write(errs.decode('utf-8'))
                break
        self.__log.info(f"Subprocess Test for {filename} complete.")   

    def run(self, tests_to_run=None):
        """ Performs the test by calling postman/testfromexcel.py and starting 
            in a subprocess. Takes a json with a filename and flags in a string.
            
            Defaults to the xlsx files in temp/excel_files, flag -r. 
            Defaults -u to: 
            https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c
    
            :param tests_to_run    ::  json
                {"test1": "-r SO_Tests.xlsx -u abc"}
                Make sure the commands are space seperated because the process
                performs a .split(" ").
            
            Be careful when providing -g and -r in the same command. May produce
            unexpceted results- preferably don't. 
        """
        
        excel_file_path = os.path.join("temp", "excel_files")
        excel_file_dir_items = os.listdir(excel_file_path)

        if not tests_to_run:
            # remove "jsons" folder from list
            try:
                excel_file_dir_items.pop(0)
            except IndexError as e:
                self.__log.info("Folder is empty. ")
            
            try:
                for filename in excel_file_dir_items:
                    self.__run(filename=filename)
            except Exception as e:
                self.__log.info(f"An error occured during testing.\n\t {e}")
        else:
            for key in tests_to_run:
                self.__log.info(f"Test from JSON payload: {key}")
                test_str = tests_to_run[key]
                try:
                    self.__run(personal_cmd=test_str.split(" "))
                except Exception as e:
                    self.__log.info(f"An error occured during testing.\n\t {e}")

        self.__log.info("All tests complete")