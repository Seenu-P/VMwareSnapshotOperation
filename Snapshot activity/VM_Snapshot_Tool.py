#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import ssl
import subprocess
import configparser
import io
import getpass
import urllib
import urllib3
import base64
import json
import logging
import logging.handlers
import traceback
import socket
from collections import OrderedDict
from html.parser import HTMLParser
from http.cookiejar import CookieJar
sys.path.append("/usr/lib/vmware-marvin/marvind/webapps/ROOT/WEB-INF/classes/scripts/lib/python2.7/site-packages")
from pyVmomi import vim, vmodl
from pyVim import connect
from datetime import datetime
from Snapshot_Operation.snap_test import take_snap
from Snapshot_Operation.Delete_Snapshot import delete_snap
from Snapshot_Operation.Revert_Snapshot import revert_snap
from Snapshot_Operation.Delete_All_Snapshot import delete_all_snap
from Snapshot_Operation.Snapshot_Report import snap_report


def setup_logger(level=logging.DEBUG, print_screen=True):
    """Setup logging to print all log messages with the different level"""
    global log  # pylint: disable=invalid-name
    log = logging.getLogger(__name__)
    # Debug if needed
    if print_screen:
        sysout_handler = logging.StreamHandler(sys.stdout)
        sysout_handler.setFormatter(logging.Formatter("%(message)s"))
        sysout_handler.setLevel(level)
        log.addHandler(sysout_handler)
    log.setLevel(level)


def show_menu():
    print('''
+========================= What do you want to do? ==============================+
|  1)  All VM's snapshot report           2) Take snapshot of a VM               |
|  3)  Revert snapshot of a VM            4) Delete snapshot of a VM             |
|  5)  Delete All snapshots of a VM       q) Exit                                |
+================================================================================+''')
    
def print_menu():
    """ menu1"""
    choice = {}
    choice["1"] = "Snapshot Report"
    choice["2"] = "Take Snapshot"
    choice["3"] = "Revert"
    choice["4"] = "Delete a Snapshot"
    choice["5"] = "Delete All Snapshot"
    choice["q"] = "exit"
    choice["m"] = "menu"
    while True:
        print("|================================================================================|")
        x = input("Select an option[1-5,q(quit),m(show menu)]:")
        print("|================================================================================|")
        if x in ("1", "2", "3", "4", "5", "q", "m"):
            break
    if choice[x] == "exit":
        exit(1)
    return choice[x]

def main():
    """ main for 4.x"""
    argv_para = "menu"
    argv_value = "menu"
    menu_flag = True
    show_menu()
    while menu_flag is True:
        # menu and advancemenu logic
        if argv_para == "menu":
            argv_value = print_menu()
        else:
            menu_flag = False
        # menu menu logic end

        # for check all
        if argv_value == "menu":
            show_menu()
        if argv_value == "Snapshot Report":
            """This block of code will help in gathering the snapshot report of all the VMs in the provided VC"""
            print("Let's take snapshot report for all the VMs in a given vCenter")
            snap_report()
            
        if argv_value == "Take Snapshot":
            """This block of code will help in taking a snapshot for the given VM if its residing in the provided VC"""
            print("Let's take snapshot for a VM")
            take_snap()
            
        if argv_value == "Revert":
            """This block of code will help in reverting a snapshot for the given VM if its residing in the provided VC"""
            print("Let's revert snapshot for a VM")
            revert_snap()
            
        if argv_value == "Delete a Snapshot":
            """This block of code will help in deleting a snapshot for the given VM if its residing in the provided VC"""
            print("Let's delete unwanted snapshot for a VM")
            delete_snap()
            
        if argv_value == "Delete All Snapshot":
            """This block of code will help in deleting all the snapshots for the given VM if its residing in the provided VC"""
            print("Let's delete all snapshots for a VM")
            delete_all_snap()
            
    return 0

# Start program
if __name__ == "__main__":
    setup_logger()
    log.info("[Start Snapshot tool...]")
    main()
