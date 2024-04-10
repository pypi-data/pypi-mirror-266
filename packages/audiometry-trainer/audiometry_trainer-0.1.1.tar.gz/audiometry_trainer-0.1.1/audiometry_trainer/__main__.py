#!/usr/bin/env python
# -*- coding: utf-8 -*-
#   Copyright (C) 2023-2024 Samuele Carcagno <sam.carcagno@gmail.com>
#   This file is part of audiometry_trainer

#    audiometry_trainer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    audiometry_trainer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with audiometry_trainer.  If not, see <http://www.gnu.org/licenses/>.

import argparse, sys, platform, os, copy, logging, pickle, signal, scipy, time, traceback
from audiometry_trainer.pyqtver import*
if pyqtversion == 5:
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtGui import QIcon
    from PyQt5.QtWidgets import QAbstractItemView, QAction, QApplication, QDialog, QDialogButtonBox, QGridLayout, QFileDialog, QInputDialog, QLabel, QMainWindow, QMessageBox, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
elif pyqtversion == 6:
    from PyQt6 import QtGui, QtCore
    from PyQt6.QtGui import QAction, QIcon
    from PyQt6.QtWidgets import QAbstractItemView, QApplication, QDialog, QDialogButtonBox, QGridLayout, QFileDialog, QInputDialog, QLabel, QMainWindow, QMessageBox, QPushButton, QScrollArea, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from numpy import sin, cos, pi, sqrt, abs, arange, zeros, mean, concatenate, convolve, angle, real, log2, log10, int_, linspace, repeat, ceil, unique, hamming, hanning, blackman, bartlett, round, transpose
from numpy.fft import rfft, irfft, fft, ifft
from tempfile import mkstemp

from audiometry_trainer import qrc_resources
from audiometry_trainer.global_parameters import*
from audiometry_trainer._version_info import*
from audiometry_trainer.main_window import*
#from audiometry_trainer.utilities_open_manual import*
#from audiometry_trainer.threaded_plotters import*
#from audiometry_trainer.audio_manager import*

__version__ = audiometry_trainer_version
signal.signal(signal.SIGINT, signal.SIG_DFL)

local_dir = os.path.expanduser("~") +'/.local/share/data/audiometry_trainer/'
if os.path.exists(local_dir) == False:
    os.makedirs(local_dir)
stderrFile = os.path.expanduser("~") +'/.local/share/data/audiometry_trainer/audiometry_trainer_stderr_log.txt'

logging.basicConfig(filename=stderrFile,level=logging.DEBUG,)


def excepthook(except_type, except_val, tbck):
    """ Show errors in message box"""
    # recover traceback
    tb = traceback.format_exception(except_type, except_val, tbck)
    def onClickSaveTbButton():
        ftow = QFileDialog.getSaveFileName(None, 'Choose where to save the traceback', "traceback.txt", 'All Files (*)')[0]
        if len(ftow) > 0:
            if fnmatch.fnmatch(ftow, '*.txt') == False:
                ftow = ftow + '.txt'
            fName = open(ftow, 'w')
            fName.write("".join(tb))
            fName.close()
    
    diag = QDialog(None, Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
    diag.window().setWindowTitle("Critical Error!")
    siz = QVBoxLayout()
    lay = QVBoxLayout()
    saveTbButton = QPushButton("Save Traceback", diag)
    saveTbButton.clicked.connect(onClickSaveTbButton)
    lab = QLabel("Sorry, something went wrong. The attached traceback can help you troubleshoot the problem: \n\n" + "".join(tb))
    lab.setMargin(10)
    lab.setWordWrap(True)
    lab.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    lab.setStyleSheet("QLabel { background-color: white }");
    lay.addWidget(lab)

    sc = QScrollArea()
    sc.setWidget(lab)
    siz.addWidget(sc) #SCROLLAREA IS A WIDGET SO IT NEEDS TO BE ADDED TO A LAYOUT

    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)

    buttonBox.accepted.connect(diag.accept)
    buttonBox.rejected.connect(diag.reject)
    siz.addWidget(saveTbButton)
    siz.addWidget(buttonBox)
    diag.setLayout(siz)
    diag.exec()

    timeStamp = ''+ time.strftime("%d/%m/%y %H:%M:%S", time.localtime()) + ' ' + '\n'
    logMsg = timeStamp + ''.join(tb)
    logging.debug(logMsg)

if platform.system() == 'Windows':
    import winsound





tmpprm = {}; tmpprm['appData'] = {}
tmpprm = set_global_parameters(tmpprm)
tmpprm = get_prefs(tmpprm)
# if tmpprm['pref']['sound']['wavmanager'] == 'soundfile':
#     from audiometry_trainer.wavpy_sndf import wavread, wavwrite
# elif tmpprm['pref']['sound']['wavmanager'] == 'scipy':
#     #from audiometry_trainer.scipy_wav import scipy_wavwrite, scipy_wavread
#     from audiometry_trainer.wavpy import wavread, wavwrite
     

def main():
    
    prm = {}
    prm['appData'] = {}
    #prm['appData'] = {}; prm['prefs'] = {}
    # create the GUI application
    qApp = QApplication(sys.argv)
    sys.excepthook = excepthook

    #prm['calledWithWAVFiles'] = False
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--experimental", help="experimental features",
                        action="store_true")
    args = parser.parse_args()
    if args.experimental:
        prm['experimental_features'] = True
    else:
        prm['experimental_features'] = False
    #parser.add_argument("-e", "--experimental", help="Load WAV file", nargs='*', default='')
    # args = parser.parse_args()
    # if len(args.file) > 0:
    #     prm['calledWithWAVFiles'] = True
    #     prm['WAVFilesToLoad'] = args.file
    
    #first read the locale settings
    locale = QtCore.QLocale().system().name() #returns a string such as en_US
    qtTranslator = QtCore.QTranslator()
    if qtTranslator.load("qt_" + locale, ":/translations/"):
        qApp.installTranslator(qtTranslator)
    appTranslator = QtCore.QTranslator()
    if appTranslator.load("audiometry_trainer_" + locale, ":/translations/"):
        qApp.installTranslator(appTranslator)
    prm['appData']['currentLocale'] = QtCore.QLocale(locale)
    QtCore.QLocale.setDefault(prm['appData']['currentLocale'])

    if getattr(sys, "frozen", False):
         # The application is frozen
         prm['rootDirectory'] = os.path.dirname(sys.executable)
    else:
        prm['rootDirectory'] = os.path.dirname(__file__)
    
    prm = get_prefs(prm)
    prm = set_global_parameters(prm)
    
    #then load the preferred language
    if prm['pref']['country'] != "System Settings":
        locale =  prm['pref']['language']  + '_' + prm['pref']['country']#returns a string such as en_US
        qtTranslator = QtCore.QTranslator()
        if qtTranslator.load("qt_" + locale, ":/translations/"):
            qApp.installTranslator(qtTranslator)
        appTranslator = QtCore.QTranslator()
        if appTranslator.load("audiometry_trainer_" + locale, ":/translations/") or locale == "en_US":
            qApp.installTranslator(appTranslator)
            prm['appData']['currentLocale'] = QtCore.QLocale(locale)
            QtCore.QLocale.setDefault(prm['appData']['currentLocale'])
            prm['appData']['currentLocale'].setNumberOptions(prm['appData']['currentLocale'].NumberOption.OmitGroupSeparator | prm['appData']['currentLocale'].NumberOption.RejectGroupSeparator)

    prm['locale_string'] = locale
    qApp.setWindowIcon(QIcon(":/audiometry_trainer_icon"))
  
    qApp.setApplicationName('audiometry_trainer')
    aw = applicationWindow(prm=prm)


    # show the widget
    aw.show()
    # start the Qt main loop execution, exiting from this script
    # with the same return code of Qt application
    sys.exit(qApp.exec())
    
if __name__ == "__main__":
    main()
   
