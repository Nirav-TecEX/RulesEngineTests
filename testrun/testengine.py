import logging
import os
import subprocess
import multiprocessing
from multiprocessing import RLock
from time import sleep

class RulesEngineTester:
    def __init__(self) -> None:
        self.__log = logging.getLogger("TestRun").getChild("RulesEngineTester")
        self.__subproc_out_txt = ""
        self.__lock = RLock

    @property
    def subproc_out_txt(self):
        return self.__subproc_out_txt

    @subproc_out_txt.setter
    def subproc_out_txt(self, name):
        self.__subproc_out_txt = os.path.join("temp", "diagnostic_files", f"{name}.txt")
    
    @property
    def test_path(self):
        return os.path.join("postman", "testfromexcel.py")

    def execute(self, personal_cmd, filename=None):     
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
            print("No file or commands given. ")
            return

        self.subproc_out_txt = filename.replace(".xlsx","") 

        with open(self.subproc_out_txt, 'w+') as f:
            f.write(f"Command executed:\n{postman_cmd}\n\n")

        subproc = subprocess.Popen(postman_cmd, 
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   shell=True)

        print(f"Subprocess Test for {filename} started.")
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
                outs = outs.decode('utf-8')
                try:
                    outs = "┌"+outs.split("┌")[1]
                except IndexError as e:
                    pass
                out_file.write(outs)
                out_file.write(f"Attempt {attempts} Error:\n")
                out_file.write(errs.decode('utf-8'))
                
                # out_file.write(f"Attempt {attempts} Out:\n")
                # out_file.write(outs.decode('utf-8'))
                # out_file.write(f"Attempt {attempts} Error:\n")
                # out_file.write(errs.decode('utf-8'))
                break
        
        # attempts = 0
        # while attempts < 3:
        #     try:
        #         outs, errs = subproc.communicate()
        #     except subprocess.TimeoutExpired:
        #         subproc.kill()
        #         attempts = attempts + 1
        #         continue        
        #     break

        print(f"Subprocess Test for {filename} complete.")   

        return {self.subproc_out_txt: (outs, errs)}

    def run(self, tests_to_run=None):
        """ Performs the test by calling postman/testfromexcel.py. Can be performed on a
            single test or multiple: takes a json with a filename and flags in a string,
            otherwise defaults to using the xlsx files in temp/excel_files.
            
            Defualts:
            Defaults to the xlsx files in temp/excel_files, flag -r. 
            Defaults -u to: 
            https://t06m5fii71.execute-api.eu-central-1.amazonaws.com/dev/sync/Shipment_Order__c

            Be careful when providing -g and -r in the same command. May produce
            unexpceted results- preferably don't. 

            :param tests_to_run    ::  json
                {"test1": "-r,SO_Tests.xlsx,-u,abc", ...}
                Make sure the commands are COMMA seperated 
                and that no file is accessed more than once.            
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
                    self.execute(None, filename=filename)
            except Exception as e:
                self.__log.info(f"An error occured during testing.\n\t {e}")
        else:
            all_commands = []
            for key in tests_to_run:
                single_cmd_str = tests_to_run[key].replace(", ", ",")
                test_cmnds_list = single_cmd_str.split(",")
                all_commands.append(test_cmnds_list)
            try:
                if len(all_commands) > 1:
                    results = self.multiple_tests_run(all_commands)
                else:
                    results = self.execute(all_commands[0])
            except Exception as e:
                self.__log.info(f"An error occured during testing.\n\t {e}")
        
        self.__log.info("All tests complete. Writing outputs.")
        
        # for result in results:
        #     for key in result:  # should only be 1 key
        #         with open(key, 'a', encoding='utf-8') as out_file:
        #             outs = result[key][0].decode('utf-8')
        #             errs = result[key][1].decode('utf-8')
        #             try:
        #                 outs = "┌"+outs.split("┌")[1]
        #             except IndexError as e:
        #                 pass
        #             out_file.write(outs)
        #             out_file.write(errs)
        #             sleep(2)

        self.__log.info("All test outputs parsed. ")
    
    def multiple_tests_run(self, all_commands):
        """ Allows parallel execution of newman processes.
            Sends a set of commands to self.__run that calls the newman process.

            :param all_commands ::  list of lists
                [[], [], [] ...] 
        """
        with multiprocessing.Pool(3) as pool:
            try:
                processes = [pool.apply_async(self.execute, args=(personal_cmd,)) for personal_cmd in all_commands]
                results = [proc.get() for proc in processes]
            except Exception as e:
                self.__log.debug(f"{e}")
        
        return results