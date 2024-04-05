#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Feb 2024
# Last Modified: Feb 2024
#=================================================================
"""
Pre-requisite: 
N/A
Used Input:
Various
Expected Output:
Various
Description:
This script defines two shared classes of default values to be shared among various scripts.
This script also defines a SharedMethods class containing common functions to be used for various scripts such as checking the existence of files, time manipulation, etc. 

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
#=================================================================
# Set Information Variable
# N/A
#=================================================================


#import tkinter as tk
import os
import shutil
import importlib
import importlib.resources
import csv
import time
import subprocess

class SharedVariables:
    # this class will store all shared varibles
    sim_variable = None
    main_option = None
    
    # varible to be updated following version upgrade:
    # Replace 'your_package_name' with the actual name of your package
    package_name = 'vision_oslo_extension'
    support_name = 'support'

    tiploc_name = 'tiploc_library.csv'
    
    lastupdate = 'April / 2024'
    copyright = 'CopyRight @ 2024'
    
class Local_Shared:
    # this class will store all local shared varibles
    option_select = None
    time_start = None
    time_end = None
    text_input = None
    low_threshold = None
    high_threshold = None
    time_step = None

class SharedMethods:
    # copy files from source folder to active entry
    def copy_example_files(filename):
        distribution = importlib.resources.files(SharedVariables.package_name)
        # Get the path to the package
        #package_path = distribution.location + "\\" + SharedVariables.package_name
        package_path = os.path.join(str(distribution), SharedVariables.support_name)

        # Get the absolute path of the file in the package location
        file_in_package = os.path.join(package_path, filename)
        current_path = os.getcwd() # get current path

        check_file = os.path.join(current_path, filename)

        if os.path.exists(check_file):
            print(f"File '{filename}' already exists in the current working directory. Skipping copy...")
        else:
            # Copy the file to the current working directory
            shutil.copy(file_in_package,current_path)
            print(f"File '{filename}' copied to the current working directory. Config as required...")

    #check existin file
    def check_existing_file(filename):
        print("Checking File {}...".format(filename))

        first = filename.split('.')[0]
        if first == "":
            SharedMethods.print_message("ERROR: Select the simulation or required file to continue...","31")
            return False

        current_path = os.getcwd() # get current path
        file_path = os.path.join(current_path,filename) # join the file path
        if not os.path.isfile(file_path): # if the oof file does not exist
            SharedMethods.print_message(f"ERROR: Required file {filename} does not exist. Checking required...","31")
            return False
        return True

    # check the folder and file for summary
    def folder_file_check(subfolder,filename):
        print("Checking File {} in {}...".format(filename,subfolder))
        current_path = os.getcwd() # get current path

        # Create the complete folder path
        folder_path = os.path.join(current_path, subfolder)
        
        # Check if the folder exists
        if not os.path.exists(folder_path):
            SharedMethods.print_message(f"ERROR: Required folder {subfolder} does not exist. Check your Input. Exiting...","31")
            return False
        
        # file path
        file_path = os.path.join(folder_path,filename) # join the file path
        # print(file_path)
        if not os.path.isfile(file_path):
            SharedMethods.print_message(f"ERROR: Required file {filename} does not exist at {subfolder}. Check your Input. Exiting...","31")
            return False
        return True

    # check oof file
    def check_oofresult_file(simname):

        resultfile = simname + ".oof"
        if simname == "":
            SharedMethods.print_message("ERROR: Please select the simulation to Continue...","31")
            return False

        if not SharedMethods.check_existing_file(resultfile):
            return False

        return True

    # osop running       
    def osop_running(cmdline):
        # package_name = 'vision_oslo_extension'
        # Get the distribution object for your package
        distribution = importlib.resources.files(SharedVariables.package_name)
        # Get the path to the package
        package_path = str(distribution)

        with open("batch_run.bat","w") as fba:
            fba.writelines("@echo off\n")
            fba.writelines("set PATH=%PATH%;" + package_path + "\n")
            fba.writelines("@echo on\n")
            fba.writelines(cmdline)
        os.system("batch_run.bat")

    # rename files
    def file_rename(old_name,new_name):
        try:
            os.rename(old_name,new_name)
            print("File {} successfully created. Processing Continue...".format(new_name))
        except FileExistsError:
            os.remove(new_name)
            os.rename(old_name,new_name)
            print("File {} successfully replaced. Processing Continue...".format(new_name))
        except FileNotFoundError:
            SharedMethods.print_message(f"ERROR: File {new_name} FAILED as the OSOP extraction fail. Check Input...","31")

    # module to check 7 digit user input time
    def time_input_process(time_string,option_back):
        #option_back = 1: return string
        #option_back = 2: return seconds

        if not len(time_string) == 7:
            SharedMethods.print_message("ERROR: Invalid time format input. Press reenter the 7 digit time.","31")
            return False

        seconds_int = 0        
        day = int(time_string[:1])
        hour = int(time_string[1:3])
        minute = int(time_string[3:5])
        second = int(time_string[5:7])

        if not 0 <= day <= 9:
            SharedMethods.print_message("ERROR: Invalid DAY input (0-9). Press reenter the 7 digit time.","31")
            return False
                
        if 0 <= hour <= 24:
            seconds_int += hour*60*60
        else:
            SharedMethods.print_message("ERROR: Invalid HOUR input (0-24). Press reenter the 7 digit time.","31")
            return False
                
        if 0 <= minute <= 60:
            seconds_int += minute*60
        else:
            SharedMethods.print_message("ERROR: Invalid MINUTE input (0-60). Press reenter the 7 digit time.","31")
            return False
                
        if 0 <= second <= 60:
            seconds_int += second
        else:
            SharedMethods.print_message("ERROR: Invalid SECOND input (0-60). Press reenter the 7 digit time.","31")
            return False

        if option_back == 1:
            return time_string
        else:
            return seconds_int

    # check the propoer life file of the model
    def check_lst_file(simname):
        cmdline = "osop " + simname
        filename = simname + ".osop.lst"
        opcname = simname + ".opc"

        # Create batch file for list command and run the batch file
        # and define the lst file name to process the information
        # generate List file
        if not os.path.isfile(filename):
            with open(opcname,"w") as fopc:
                fopc.writelines("LIST INPUT FILE\n")
            SharedMethods.osop_running(cmdline)
            
        lst_file_size = os.path.getsize(filename)
        
        if lst_file_size < 10000: # a random size (bytes) to check if lst should be redone (10000 bytes = 10 kb)
            with open(opcname,"w") as fopc:
                fopc.writelines("LIST INPUT FILE\n")
            SharedMethods.osop_running(cmdline)
    
    # module to read the text file input    
    def file_read_import(filename,simname):
        
        if not os.path.isfile(filename): # if the file exist
            SharedMethods.print_message(f"ERROR: Required input file {filename} does not exist. Please select another option.","31")
            return False

        # reading the train list file
        text_input = []
        with open(filename) as fbrlist:
            for index, line in enumerate(fbrlist):
                text_input.append(line[:50].strip())

        return text_input
    
    # write to text file (not used)
    def file_write(header,creatname,listname):
        with open(creatname, 'w') as fw:
            fw.write(header)
            for items in listname:
                string_line = map(str,items) # string all item
                result_line = ",".join(string_line) # join item removing brackets/quotes
                fw.write("%s\n" % result_line) # print out
    
    # module to convert 7 digits time to time format 
    def time_convert(time_string):
        
        #time_string = input()          
        day = int(time_string[:1])
        hour = int(time_string[1:3])
        minute = int(time_string[3:5])
        second = int(time_string[5:7])

        if not day == 0:
            day = day # to be updated to process info at a later stage
        time = str(hour) + ":" + str(minute) + ":" + str(second)        
        #debug purpose
        #print(seconds_int)
        # Return the second integer number as same used in the list file           
        return time

    # read tiploc information
    def get_tiploc_library():
        tiploc = {} # create a empty tiploc
        
        filename = SharedVariables.tiploc_name
        distribution = importlib.resources.files(SharedVariables.package_name)
        package_path = os.path.join(str(distribution), SharedVariables.support_name)

        # Get the absolute path of the file in the package location
        filepath = os.path.join(package_path, filename)

        last_modified_timestamp = os.path.getmtime(filepath)
        # Convert timestamp to a readable format
        last_time = time.strftime('%Y-%m-%d', time.localtime(last_modified_timestamp))

        print("\nTIPLOC Libray Last Update: {}".format(last_time))

        SharedMethods.print_message("ATTENTION: Please contact support if a TIPLOC library update is needed!","33")

        with open(filepath,'r') as file:
            csv_reader = csv.reader(file)
            # next(csv_reader)  # Skip the first row
            for row in csv_reader:
                key = row[0]
                value = row[1]
                tiploc[key] = value
        
        return tiploc

    # open a file in support folder
    def open_support_file(filename):
        distribution = importlib.resources.files(SharedVariables.package_name)
        package_path = os.path.join(str(distribution), SharedVariables.support_name)
        # Get the absolute path of the file in the package location
        file_in_package = os.path.join(package_path, filename)
        try:
            subprocess.Popen(['start', '', file_in_package], shell=True,close_fds=True)
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error opening file with default app: {e}","31")

        return

    # define the running in thread mechanism    
    def common_thread_run(import_option, sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step):
        # Define a dictionary mapping import_option to module names
        module_mapping = {
            "cif_prepare.py": "cif_prepare",
            "model_check.py": "model_check",
            "oslo_extraction.py": "oslo_extraction",
            "post_processing.py": "post_processing",
            "average_load.py": "average_load",
            "protection_if.py": "protection_if",
            "grid_connection.py": "grid_connection",
            "ole_processing.py": "ole_processing",
            "batch_processing.py": "batch_processing",
            "dc_summary.py": "dc_summary"
        }

        # Get the module name corresponding to import_option
        module_name = module_mapping.get(import_option)

        # Import the module
        if module_name:
            fc = importlib.import_module(f"vision_oslo_extension.{module_name}")
            #from vision_oslo_extension import module_name as fc
        else:
            # Handle the case when import_option doesn't match any module
            print("Invalid import_option:", import_option)
        
        try:    
            continue_process = fc.main(sim_name, main_option, time_start, time_end, option_select, text_input, low_v, high_v, time_step)
            if not continue_process:
                # Do something if the process should not continue
                # Print error message in red
                SharedMethods.print_message("ERROR: Process terminated unexpectedly. "
                                            "Please check the error history above or contact support. "
                                            "You can continue using other options...", '31')
            else:
                # Do something if the process should continue
                # Print success message in green
                SharedMethods.print_message("Action successfully completed. "
                                            "Check monitor history above and result files in your folder.", '32')
        
        except Exception as e:
            print(f"Error in {import_option}:", e)
    
    def print_message(message, color_code):
        os.system("")
        color_start = f'\033[1;{color_code}m'   # Start color
        color_reset = '\033[1;0m'               # Reset color
        print(color_start + message + color_reset)
