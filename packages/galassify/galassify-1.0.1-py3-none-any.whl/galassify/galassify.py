#! /usr/bin/python3
#######################################################
# GALAssify: Tool to manually classify void galaxies. #
# Written by MrManlu                                  #
#######################################################

import sys
import os
from PyQt5 import QtWidgets
from . import utils
from . import gui

VERSION = '1.0.1'

def main():
    args = utils.getOptions(VERSION)
    if not len(sys.argv) > 1:
        if utils.exist_basic_files():
            run_gui(args)
        else:    
            selec = utils.load_menu()
            if selec == 0:
                utils.init_flag()            
            elif selec == 10:
                utils.example_flag('basic')
            elif selec == 11:
                utils.example_flag('fits')
    else:
        if args.init:
            utils.init_flag()
        elif args.example != '':
            print(f"INFO:\t Create the {args.example} example files")
            utils.example_flag(args.example)
        else:
            run_gui(args)


def run_gui(args):
    selectedFiles, selectedGroups = utils.getFiles()
    if len(selectedFiles) > 0:
        if args.list:
            print(selectedFiles.filename)
        else:
            print(f"INFO:\t {str(len(selectedFiles))} galaxies found in selected group(s).")
            df = selectedFiles # utils.expand_df(selectedFiles)
            app = QtWidgets.QApplication(sys.argv)
            window = gui.Ui(df, selectedGroups)
            app.exec_()
    else:
        print('ERROR:\tNo files found with the arguments given.')
        print('HINT:\tDid you populate your .csv file?')


if __name__ == '__main__':
    sys.exit(main())