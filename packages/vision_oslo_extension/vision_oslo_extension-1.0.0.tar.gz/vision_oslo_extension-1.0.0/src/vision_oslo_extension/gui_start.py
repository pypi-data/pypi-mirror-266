#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Feb 2024
# Last Modified: Feb 2024
#=================================================================
"""
Pre-requisite: 
-supporting- folder with various templates. 
Used Input:
Calling from master.py
Expected Output:
Main GUI window and Menu Bar
Description:
This script defines main properties of GUI such as font, title, size, etc.
This script also defines the main frame of all GUI window and menu bar, including actions of each item listed in the menu.
Attention:
This script needs to be updated once a new frame / page is developed. This could be achieved by importing the new class and updating top-level frame list (def _init_)

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
#=================================================================
# Set Information Variable
# N/A
#=================================================================

# Third Party

import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog

import subprocess
import os
import importlib.metadata

from vision_oslo_extension.main_page_frame import PageOne, PageTwo, PageThree, PageFour
from vision_oslo_extension.extraction_frame import F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14
from vision_oslo_extension.processing_frame import P01, P02, P03, P04, P05, P06, P07, P08, P08, P09, P10, P11, P12
from vision_oslo_extension.check_frame import C01, C02, C03
from vision_oslo_extension.input_frame import S01, S02, S03, S04, S05
from vision_oslo_extension.shared_contents import SharedVariables,SharedMethods
from vision_oslo_extension.base_frame import BasePage

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold")
        self.sub_title_font = tkfont.Font(family='Helvetica', size=12, weight="bold")
        self.big_text_font = tkfont.Font(family='Helvetica', size=10, weight="bold")
        self.text_font = tkfont.Font(family='Helvetica', size=10)
        # root.geometry('300x200')
        self.title('Vision-Oslo Extension')

        # define the top bar menu  'variible called menu
        menu = tk.Menu(self)
        self.config(menu = menu)
        # sub-menu 1 = filemenu
        filemenu = tk.Menu(menu)
        menu.add_cascade(label='File', menu = filemenu)
        filemenu.add_command(label= 'Select Simulation', command = lambda: SampleApp.open_simulation(self))
        filemenu.add_command(label= 'Open Configuration File', command = lambda: SampleApp.open_file_dialog(self))
        filemenu.add_separator()
        filemenu.add_command(label= 'Exit', command = self.quit)

        # sub-menu 2 import template
        getmenu = tk.Menu(menu)
        menu.add_cascade(label='Import', menu = getmenu)
        getmenu.add_command(label= 'Text - FeederList.txt',command = lambda: SharedMethods.copy_example_files('FeederList.txt'))
        getmenu.add_command(label= 'Text - BranchList.txt',command = lambda: SharedMethods.copy_example_files('BranchList.txt'))
        getmenu.add_command(label= 'Text - BranchNodeList.txt',command = lambda: SharedMethods.copy_example_files('BranchNodeList.txt'))
        getmenu.add_command(label= 'Text - TransformerList.txt',command = lambda: SharedMethods.copy_example_files('TransformerList.txt'))
        getmenu.add_command(label= 'Text - TrainList.txt',command = lambda: SharedMethods.copy_example_files('TrainList.txt'))
        getmenu.add_command(label= 'CSV - GridAllocation.csv',command = lambda: SharedMethods.copy_example_files('GridAllocation.csv'))
        getmenu.add_command(label= 'CSV - CIF_Selection.csv',command = lambda: SharedMethods.copy_example_files('CIF_Selection.csv'))
        getmenu.add_command(label= 'Excel - (AC) For Average Power',command = lambda: SharedMethods.copy_example_files('power_template.xlsx'))
        getmenu.add_command(label= 'Excel - (AC) For IF Protection',command = lambda: SharedMethods.copy_example_files('protection_template.xlsx'))
        getmenu.add_command(label= 'Excel - (AC) For New SP Connect',command = lambda: SharedMethods.copy_example_files('new_connection_template.xlsx'))
        getmenu.add_command(label= 'Excel - (AC) For OLE Rating',command = lambda: SharedMethods.copy_example_files('ole_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For TRU Summary',command = lambda: SharedMethods.copy_example_files('TRU_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Main DCCB Summary',command = lambda: SharedMethods.copy_example_files('mainCB_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For DCBB Summary',command = lambda: SharedMethods.copy_example_files('DCBB_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Neg ETE Summary',command = lambda: SharedMethods.copy_example_files('NegETE_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Imp Bond Summary',command = lambda: SharedMethods.copy_example_files('ImpBond_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Track CB Summary',command = lambda: SharedMethods.copy_example_files('trackCB_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Pos ETE Summary',command = lambda: SharedMethods.copy_example_files('PosETE_rating_template.xlsx'))
        getmenu.add_command(label= 'Excel - (DC) For Train V Summary',command = lambda: SharedMethods.copy_example_files('trainV_template.xlsx'))
        # getmenu.add_command(label= 'Excel - For Data Input')

        # sub-menu 2 = helpmenu
        helpmenu = tk.Menu(menu)
        menu.add_cascade(label='Help', menu = helpmenu)

        helpmenu.add_command(label='Help Document',command =  lambda: SharedMethods.open_support_file('VISION-OSLO Extension User Guide.pdf'))
        helpmenu.add_command(label='About',command = self.show_about_popup)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree, PageFour, \
                  F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14, \
                    P01, P02, P03, P04, P05, P06, P07, P08, P09, P10, P11, P12, \
                        C01, C02, C03, \
                            S01, S02, S03, S04, S05):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    def show_about_popup(self):
        about_popup = tk.Toplevel(self)
        about_popup.title("About-Copyright")

        installed_version = importlib.metadata.version(SharedVariables.package_name)
        about_text = f"VISION-OSLO extension, version {installed_version}"
        about_font = tkfont.Font(family='Helvetica', size=11, weight="bold")
        about_label = tk.Label(about_popup, text=about_text, font = about_font, padx=10, pady=10)
        about_label.pack()

        info_text = "This is developed by Jieming Ye.\n"\
            "Copyright to Engineering Services, Network Rail Infrastructure Ltd.\n"\
            f"Last Update: {SharedVariables.lastupdate}.\n"\
            "License: OST Approved, MIT License.\n"\
            "For support please consult Jieming.Ye@networkrail.co.uk"
        #info_label = tk.Message(about_popup, text=info_text, aspect = 800, padx=10, pady=10)
        info_label = tk.Label(about_popup, text=info_text, padx=10, pady=10, justify="left")
        info_label.pack()

        # Center the popup window on the screen
        about_popup.geometry("+%d+%d" % (self.winfo_rootx() + self.winfo_width() // 2 - about_popup.winfo_reqwidth() // 2,
                                         self.winfo_rooty() + self.winfo_height() // 2 - about_popup.winfo_reqheight() // 2))
    
    
    def open_simulation(self):
        initial_dir = os.getcwd()
        file_path = filedialog.askopenfilename(title="Select Simulation",initialdir=initial_dir)
        if file_path:
            print(f"Selected file: {file_path}")
            file_name = os.path.basename(file_path)
            file_name_parts = file_name.split('.')
        
            # Only the first part of the file name (before the dot)
            simname = file_name_parts[0] if file_name_parts else file_name

            print(simname)

            SharedVariables.sim_variable.set(simname)
    
    # Create a function to be called when the "Open" menu option is clicked
    def open_file_dialog(self):
        initial_dir = os.getcwd()  # Get the current working directory
        file_path = filedialog.askopenfilename(title="Select a file",initialdir=initial_dir)
        if file_path:
            print(f"Selected file: {file_path}")

            SharedMethods.print_message("WARNING: DO NOT EXIT THE PROGRAME BEFORE SAVING THE OPENED FILE.","33")
            
            self.open_file(file_path)


    def open_file(self, file_path):
        try:
            subprocess.Popen(['start', '', file_path], shell=True,close_fds=True)
        except Exception as e:
            SharedMethods.print_message(f"ERROR: Error opening file with default app: {e}","31")

class StartPage(BasePage): # define another object of first page

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.headframe = self.create_frame(fill=tk.BOTH)
        self.nameframe = self.create_frame(fill=tk.BOTH, column_weights=(1, 6))
        self.optionframe = self.create_frame(fill=tk.BOTH, row_weights=(1, 1, 1, 1), column_weights=(4, 1))
        self.infoframe = self.create_frame(fill=tk.BOTH)

        # add widgets here
        head = tk.Label(master=self.headframe, text = 'Welcome to VISION-OSLO Add-In',font = controller.title_font)
        head.pack()
        
        text1 = tk.Label(master=self.nameframe, text = 'Simulation Name',font = controller.text_font)
        text1.grid(row = 0, column = 0) # sticky n alight to top center part

        SharedVariables.sim_variable = tk.StringVar()
        entry1 = tk.Entry(master=self.nameframe,width = 40,textvariable = SharedVariables.sim_variable)
        entry1.grid(row = 0,column = 1)

        explain1 = tk.Label(master=self.optionframe, text = 'Pre-Model Information Prepare: create VISION-OSLO ready information', font = controller.text_font)
        explain1.grid(row = 0, column = 0, sticky = "w", padx=5, pady=5)

        button1 = tk.Button(master=self.optionframe, text = 'Model Prepare', command=lambda: self.button_callback("PageOne"))
        button1.grid(row = 0, column = 1, sticky = "w", padx=5, pady=5)

        explain2 = tk.Label(master=self.optionframe, text = 'Model Check Report: check model report. A working VISION-OSLO model is required', font=controller.text_font)
        explain2.grid(row = 1, column = 0, sticky = "w", padx=5, pady=5)

        button2 = tk.Button(master=self.optionframe, text = 'Model Check', command=lambda: self.button_callback("PageTwo"))
        button2.grid(row = 1, column = 1, sticky = "w", padx=5, pady=5)

        explain3 = tk.Label(master=self.optionframe, text = 'Default OSLO Extraction: A VISION-OSLO simulation result (oof) file is required.',font = controller.text_font)
        explain3.grid(row = 2, column = 0, sticky = "w", padx=5, pady=5)  

        button3 = tk.Button(master=self.optionframe, text = 'Result Extraction', command=lambda: self.button_callback("PageThree"))
        button3.grid(row = 2, column = 1, sticky = "w", padx=5, pady=5)

        explain4 = tk.Label(master=self.optionframe, text = 'Custmised Post-Processing: A VISION-OSLO simulation result (oof) file is required.',font = controller.text_font)
        explain4.grid(row = 3, column = 0, sticky = "w", padx=5, pady=5)  

        button4 = tk.Button(master=self.optionframe, text = 'Result Process', command=lambda: self.button_callback("PageFour"))
        button4.grid(row = 3, column = 1, sticky = "w", padx=5, pady=5)

        installed_version = importlib.metadata.version(SharedVariables.package_name)
        diclaimer = tk.Label(master=self.infoframe, text = f'Version {installed_version} -- {SharedVariables.copyright}')
        diclaimer.pack()
    
    # # This is kept to not calling Basepage hence increase the start up speed.
    # def create_frame(self, fill=None, row_weights=None, column_weights=None):
    #     frame = tk.Frame(self)
    #     if fill:
    #         frame.pack(fill=fill)
    #     if row_weights:
    #         for i, weight in enumerate(row_weights):
    #             frame.rowconfigure(i, weight=weight)
    #     if column_weights:
    #         for i, weight in enumerate(column_weights):
    #             frame.columnconfigure(i, weight=weight)
    #     return frame

    # def get_entry_value(self):
    #     user_input = SharedVariables.sim_variable.get()
    #     print("User Input: ", user_input )
    #     #return user_input

    # def button_callback(self,target_page):
    #     self.get_entry_value()
    #     self.controller.show_frame(target_page)

# programme running
if __name__ == '__main__':
    app = SampleApp()
    app.mainloop() 