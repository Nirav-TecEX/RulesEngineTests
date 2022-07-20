import logging
import os
import subprocess

class RulesEngineTester:
    def __init__(self) -> None:
        self.__log = logging.getLogger("TestRun").getChild("RulesEngineTester")
        self.__env = os.environ.copy()
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

    def __run(self, filename):          
        excel_file_path = os.path.join("temp", "excel_files", filename)
        postman_cmd = ['python', f"{self.test_path}", "-r", excel_file_path, "-u", 
                       "https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c"]
        
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

    def run(self):
        excel_file_dir_items = os.listdir(os.path.join("temp", "excel_files"))
        # remove "jsons" folder from list
        try:
            excel_file_dir_items.pop(0)
        except IndexError as e:
            self.__log.info("Folder is empty. ")
        
        try:
            for filename in excel_file_dir_items:
                self.__run(filename)
        except Exception as e:
            self.__log.info(f"An error occured during testing.\n\t {e}")