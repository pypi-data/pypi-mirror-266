#
# -*- coding: utf-8  -*-
#=================================================================
# Created by: Jieming Ye
# Created on: Nov 2023
# Last Modified: Feb 2024
#=================================================================
"""
Pre-requisite: 
N/A
Used Input:
N/A
Expected Output:
Start GUI
Description:
This module is the package entry.
This module is the only module to be called from User End script directly.

"""
#=================================================================
# VERSION CONTROL
# V1.0 (Jieming Ye) - Initial Version
#=================================================================
# Set Information Variable
# N/A
#=================================================================

# Default
# print('loading...')
# import sys
# import os
# import math
# import csv
# import copy

# Third Party
# print('loading externel library...')
# import matplotlib.pyplot as plt
# import tkinter as tk
# from tkinter import font as tkfont
# #from tkinter import messagebox
# #from PIL import Image
# #import numpy as np 
# #from subprocess import check_output 
# import pandas as pd

# Loading subfunctions
# from main_page_frame import PageOne, PageTwo, PageThree, PageFour
# from extraction_frame import F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14
# from shared_variables import SharedVariables
print('loading....')
# try:
#     #from . import gui_start # relative import
#     import gui_start # relative import
# except ModuleNotFoundError:
#     from vision_oslo_extension import gui_start
# import os
# import sys
# define base bath

# import gui_start # relative import
from vision_oslo_extension import gui_start
# GUI start up

def main():
    print("Loading completed. GUI starts up...")
    # # for PyInstaller Excutable process. So that move file location will not cause issue.
    # if getattr(sys, 'frozen', False):
    #     # PyInstaller creates a temp folder and stores path in _MEIPASS
    #     application_path = sys._MEIPASS
    # else:
    #     # Regular Python execution
    #     application_path = os.path.dirname(os.path.abspath(__file__))

    # print(application_path)
    # define root
    # root = tk.Tk()
    # Start GUI
    # print('loading externel library...')
    app = gui_start.SampleApp()

    app.mainloop()
    # main_window()

# programme running
if __name__ == '__main__':
    main()    