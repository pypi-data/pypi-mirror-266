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

from .pyqtver import*

import matplotlib, os, platform, random, time
matplotlib.rcParams['path.simplify'] = False
import matplotlib.ticker as ticker

if pyqtversion == 5:
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtCore import Qt, QEvent
    from PyQt5.QtGui import QDesktopServices, QDoubleValidator, QIcon, QIntValidator, QPainter
    from PyQt5.QtWidgets import QAction, QApplication, QCheckBox, QColorDialog, QComboBox, QDesktopWidget, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLayout, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QSplitter, QTextEdit, QVBoxLayout, QWidget
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    matplotlib.rcParams['backend'] = "Qt5Agg"
elif pyqtversion == 6:
    from PyQt6 import QtGui, QtCore
    from PyQt6.QtCore import Qt, QEvent
    from PyQt6.QtGui import QAction, QDesktopServices, QDoubleValidator, QIcon, QIntValidator, QPainter
    from PyQt6.QtWidgets import QApplication, QCheckBox, QColorDialog, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLayout, QLineEdit, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QSpacerItem, QSpinBox, QSplitter, QTextEdit, QVBoxLayout, QWidget
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    matplotlib.rcParams['backend'] = "Qt5Agg"
    
# Matplotlib Figure object
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from matplotlib import font_manager
from .hughson_westlake import*
from .utility_functions import*
from .audio_markers import*
from .pysdt import*
import numpy as np
import pandas as pd
import numpy.random as nprand
from .dialog_edit_preferences import*
from .window_generate_case import*

from ._version_info import*
__version__ = audiometry_trainer_version

class applicationWindow(QMainWindow):
    def __init__(self, parent=None, prm=None):
        QMainWindow.__init__(self, parent)
        #self.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
        self.prm = prm
        self.prm['version'] = __version__
        self.prm['builddate'] = audiometry_trainer_builddate
        self.currLocale = self.prm['appData']['currentLocale']
        self.currLocale.setNumberOptions(self.currLocale.NumberOption.OmitGroupSeparator | self.currLocale.NumberOption.RejectGroupSeparator)

        if pyqtversion == 5:
            screen = QDesktopWidget().screenGeometry()
        elif pyqtversion == 6:
            screen = self.screen().geometry()

        #define some parameters before axes creation
        self.canvasColor = scaleRGBTo01(self.prm['pref']['canvasColor'])
        self.backgroundColor = scaleRGBTo01(self.prm['pref']['backgroundColor'])
        self.axesColor = scaleRGBTo01(self.prm['pref']['axes_color'])
        self.tickLabelColor = scaleRGBTo01(self.prm['pref']['tick_label_color'])
        self.gridColor = scaleRGBTo01(self.prm['pref']['grid_color'])
        self.axesLabelColor = scaleRGBTo01(self.prm['pref']['axes_label_color'])
        self.labelFontFamily = self.prm['pref']['label_font_family']
        self.labelFontWeight = self.prm['pref']['label_font_weight']
        self.labelFontStyle = self.prm['pref']['label_font_style']
        self.labelFontSize = self.prm['pref']['label_font_size']
        self.labelFont = font_manager.FontProperties(family=self.labelFontFamily,
                                                     weight=self.labelFontWeight,
                                                     style= self.labelFontStyle,
                                                     size=self.labelFontSize)
        
        self.majorTickLength = self.prm['pref']['major_tick_length']
        self.majorTickWidth = self.prm['pref']['major_tick_width']
        self.minorTickLength = self.prm['pref']['minor_tick_length']
        self.minorTickWidth = self.prm['pref']['minor_tick_width']
        self.tickLabelFontFamily = self.prm['pref']['tick_label_font_family']
        self.tickLabelFontWeight = self.prm['pref']['tick_label_font_weight']
        self.tickLabelFontStyle = self.prm['pref']['tick_label_font_style']
        self.tickLabelFontSize = self.prm['pref']['tick_label_font_size']
        self.tickLabelFont = font_manager.FontProperties(family=self.tickLabelFontFamily,
                                                         weight=self.tickLabelFontWeight,
                                                         style= self.tickLabelFontStyle,
                                                         size=self.tickLabelFontSize)
        self.xAxisLabel = self.tr('Frequency (kHz)')
        self.yAxisLabel = self.tr('Level (dB HL)')
        self.dpi = self.prm['pref']['dpi']
        self.spinesLineWidth = self.prm['pref']['spines_line_width']
        self.gridLineWidth = self.prm['pref']['grid_line_width']

        self.plotMarkerSize = self.prm['pref']['marker_size']
        self.plotMarkerSizeNR = self.plotMarkerSize*1.35
        self.trackerMarkerSize = self.prm['pref']['tracker_size']

        self.transducerCh1 = self.tr("Supra-aural")
        self.transducerCh2 = self.tr("Supra-aural")
        self.testEarCoverType = self.tr("Supra-aural")
        self.testFreq = 1000
        self.testEar = self.tr("Right")
        self.testLev = 35
        self.ch2Lev = 0
        self.ch2On = False
        self.chansLocked=False
        self.showRespEar=False
        self.showRespCounts=True
        if self.testEar == self.tr("Right"):
            self.currCh1Color = "red"
            self.currCh2Color = "blue"
        else:
            self.currCh1Color = "blue"
            self.currCh2Color = "red"
        self.ch1Marker = "$S$"
        self.ch2Marker = "$M$"

        allFls = os.listdir(prm['rootDirectory'] + '/case_files/')
        self.caseFls = list(filter(lambda x:x.endswith('.csv'), allFls))
        self.fCaseName = prm['rootDirectory'] + '/case_files/' + random.choice(self.caseFls)
        self.lis = pd.read_csv(self.fCaseName, delimiter = ',')
        self.loadCaseInfo()
        self.testFreqs = np.array(self.lis['freq'])
        self.testMode = 'manual'
        self.curr_dir = "down"
        self.thresh_obt = False
        self.thresh = np.nan

        self.min_n_resp = 3
        self.step_up = 5
        self.step_down = 10
        
        self.asce_levs = np.empty(shape=0)
        self.asce_n = np.empty(shape=0)
        self.asce_yes = np.empty(shape=0)
        self.asce_yes_prop = np.empty(shape=0)
        self.prevStimLev = np.inf

        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.f1=QFrame()
        self.f1.setFrameStyle(QFrame.Shape.StyledPanel|QFrame.Shadow.Sunken)
        self.f2=QFrame()
        self.f2.setFrameStyle(QFrame.Shape.StyledPanel|QFrame.Shadow.Sunken)
        self.f3=QFrame()
        self.f3.setFrameStyle(QFrame.Shape.StyledPanel|QFrame.Shadow.Sunken)
        self.mw = QWidget(self)
        #self.hbl = QHBoxLayout(self.mw)
        self.grid_L = QGridLayout()
        self.grid_L.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.grid_R = QGridLayout()
        self.grid_R.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vbl_mid = QVBoxLayout()
        self.fig = Figure(facecolor=self.canvasColor, dpi=self.dpi, figsize=(20, 15), constrained_layout=True)
        self.ylims = (-25, 125)
        self.xlims = (80, 10000)
        self.setupBaseFigure()

        ## MENU BAR
        self.menubar = self.menuBar()
        exitAction = QAction(QIcon(':/exit'), self.tr('Exit'), self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip(self.tr('Exit application'))
        exitAction.triggered.connect(self.close)
        self.statusBar()
        loadCaseAction = QAction(QIcon(':/folder-open-regular'), self.tr('Load case'), self)
        loadCaseAction.setShortcut('Ctrl+L')
        loadCaseAction.setStatusTip(self.tr('Load case file'))
        loadCaseAction.triggered.connect(self.loadCaseDialog)
        loadRandomCaseAction = QAction(QIcon(':/dice-solid'), self.tr('Load random case'), self) #QIcon(':/dice-solid'), self.tr('Exit'), self.tr('Load random case'), self)
        #loadCaseAction.setShortcut('Ctrl+L')
        loadRandomCaseAction.setStatusTip(self.tr('Load random case file'))
        loadRandomCaseAction.triggered.connect(self.loadRandomCase)
        generateCaseAction = QAction(self.tr('Generate case'), self)
        generateCaseAction.triggered.connect(self.onClickGenerateCase)
        #FILE MENU
        self.fileMenu = self.menubar.addMenu(self.tr('&File'))
        self.fileMenu.addAction(loadCaseAction)
        self.fileMenu.addAction(loadRandomCaseAction)
        self.fileMenu.addAction(generateCaseAction)
        self.fileMenu.addAction(exitAction)

        #EDIT MENU
        self.editMenu = self.menubar.addMenu(self.tr('&Edit'))
        self.editPrefAction = QAction(self.tr('Preferences'), self)
        self.editMenu.addAction(self.editPrefAction)
        self.editPrefAction.triggered.connect(self.onEditPref)
        #HELP MENU
        self.helpMenu = self.menubar.addMenu(self.tr('&Help'))

        self.onShowManualHtmlAction = QAction(self.tr('Manual (html)'), self)
        self.helpMenu.addAction(self.onShowManualHtmlAction)
        self.onShowManualHtmlAction.triggered.connect(self.onShowManualHtml)

        self.onShowManualPdfAction = QAction(self.tr('Manual (pdf)'), self)
        self.helpMenu.addAction(self.onShowManualPdfAction)
        self.onShowManualPdfAction.triggered.connect(self.onShowManualPdf)

        self.onAboutAction = QAction(QIcon.fromTheme("help-about", QIcon(":/help-about")), self.tr('About audiometry_trainer'), self)
        self.helpMenu.addAction(self.onAboutAction)
        self.onAboutAction.triggered.connect(self.onAbout)

        ## control grid left side
        n = 0
        self.ch1Label = QLabel(self.tr('Chan. 1:'), self)
        self.transducerChooserCh1 = QComboBox()
        if self.prm['experimental_features'] == True:
            self.transducerChooserCh1.addItems([self.tr("Supra-aural"), self.tr("Insert"), self.tr("Bone"), self.tr("Sound field")]) #self.tr("Circum-aural"),
        else:
            self.transducerChooserCh1.addItems([self.tr("Supra-aural"), self.tr("Insert"), self.tr("Bone")]) #self.tr("Circum-aural"),
        self.transducerChooserCh1.setCurrentIndex(0)
        self.transducerChooserCh1.textActivated[str].connect(self.onTransducerChooserCh1Change)
        self.transducerChooserCh1.setItemIcon(0, QtGui.QIcon(":/headphones-solid"))
        self.transducerChooserCh1.setItemIcon(1, QtGui.QIcon(":/insert")) 
        self.transducerChooserCh1.setItemIcon(2, QtGui.QIcon(":/skull-solid")) 
        self.grid_L.addWidget(self.ch1Label, n, 0)
        self.grid_L.addWidget(self.transducerChooserCh1, n, 1)
        n = n+1
        self.ch1EarLabel = QLabel(self.tr('Test ear:'), self)
        self.ch1EarChooser = QComboBox()
        self.ch1EarChooser.addItems([self.tr("Right"), self.tr("Left")])
        self.ch1EarChooser.textActivated[str].connect(self.onTestEarChange)
        self.grid_L.addWidget(self.ch1EarLabel, n, 0)
        self.grid_L.addWidget(self.ch1EarChooser, n, 1)
        n = n+1
        self.TESFStatusLabel = QLabel(self.tr('Test ear status:'), self)
        self.TESFStatusChooser = QComboBox()
        self.TESFStatusChooser.addItems([self.tr("Unaided"), self.tr("Aided")])
        self.TESFStatusChooser.textActivated[str].connect(self.onTESFStatusChooserChange)
        self.grid_L.addWidget(self.TESFStatusLabel, n, 0)
        self.grid_L.addWidget(self.TESFStatusChooser, n, 1)
        self.TESFStatusLabel.hide()
        self.TESFStatusChooser.hide()
        n = n+1
        self.TESFCouplingLabel = QLabel(self.tr('Test ear coupling:'), self)
        self.TESFCouplingChooser = QComboBox()
        self.TESFCouplingChooser.addItems([self.tr("Dome (open)"), self.tr("Dome (tulip)"), self.tr("Dome (single vent)"), self.tr("Dome (double vent)"), self.tr("Double dome (power)"), self.tr("Earmold")])
        self.TESFCouplingChooser.textActivated[str].connect(self.onTESFCouplingChooserChange)
        self.grid_L.addWidget(self.TESFCouplingLabel, n, 0)
        self.grid_L.addWidget(self.TESFCouplingChooser, n, 1)
        self.TESFCouplingLabel.hide()
        self.TESFCouplingChooser.hide()
        n = n+1
        self.lockChansCheckBox = QCheckBox(self.tr('Lock channels'))
        self.lockChansCheckBox.stateChanged[int].connect(self.toggleLockChans)
        self.lockChansCheckBox.setIcon(QtGui.QIcon(":/lock-open-solid")) 
        self.grid_L.addWidget(self.lockChansCheckBox, n, 0, 1, 1)

        self.autoSearchButton = QPushButton(self.tr("Auto. thresh. search"), self)
        self.autoSearchButton.clicked.connect(self.onClickAutoButton)
        self.grid_L.addWidget(self.autoSearchButton, n, 1)
        
        n = n+1
        self.showRespEarCheckBox = QCheckBox(self.tr('Show response ear'))
        self.showRespEarCheckBox.stateChanged[int].connect(self.toggleShowRespEar)
        self.grid_L.addWidget(self.showRespEarCheckBox, n, 0, 1, 2)
        n = n+1
        self.showRespCountsCheckBox = QCheckBox(self.tr('Show response counts'))
        self.showRespCountsCheckBox.setChecked(self.showRespCounts)
        self.showRespCountsCheckBox.stateChanged[int].connect(self.toggleShowRespCounts)
        self.grid_L.addWidget(self.showRespCountsCheckBox, n, 0, 1, 2)
        n = n+1
        self.respLightLabel = QLabel(self.tr("Response light"))
        self.respLightLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.respLightLabel.setStyleSheet("font-weight: bold")
        self.grid_L.addWidget(self.respLightLabel, n, 0, 1, 2)
        n = n+1
        self.respLight = indicatorLight(self)
        self.grid_L.addWidget(self.respLight, n, 0, 1, 2)
        n=n+1
        self.markThreshButton = QPushButton(self.tr("Mark threshold"), self)
        self.grid_L.addWidget(self.markThreshButton, n, 0, 1, 2)
        self.markThreshButton.clicked.connect(self.onClickMarkThreshButton)
        n=n+1
        self.markNoResponseButton = QPushButton(self.tr("No response"), self)
        self.grid_L.addWidget(self.markNoResponseButton, n, 0)
        self.markNoResponseButton.clicked.connect(self.onClickMarkNoResponseButton)
        self.markMaskingDilemmaButton = QPushButton(self.tr("Masking dilemma"), self)
        self.grid_L.addWidget(self.markMaskingDilemmaButton, n, 1)
        self.markMaskingDilemmaButton.clicked.connect(self.onClickMarkMaskingDilemmaButton)
        n = n+1
        self.showEstThreshLbl = QLabel(self.tr('Show estimated thresholds:'), self)
        self.grid_L.addWidget(self.showEstThreshLbl, n, 0, 1, 2)
        n = n+1
      
        self.showEstUnmAirRCheckBox = QCheckBox(self.tr('Thresh. unm. air R'))
        self.showEstUnmAirRCheckBox.setChecked(True)
        self.showEstUnmAirRCheckBox.stateChanged[int].connect(self.toggleShowEstUnmAirR)
        self.grid_L.addWidget(self.showEstUnmAirRCheckBox, n, 0)

    
        n = n+1
        self.showEstUnmAirLCheckBox = QCheckBox(self.tr('Thresh. unm. air L'))
        self.showEstUnmAirLCheckBox.setChecked(True)
        self.showEstUnmAirLCheckBox.stateChanged[int].connect(self.toggleShowEstUnmAirL)
        self.grid_L.addWidget(self.showEstUnmAirLCheckBox, n, 0)
        n = n+1
        self.showEstUnmBoneRCheckBox = QCheckBox(self.tr('Thresh. unm. bone R'))
        self.showEstUnmBoneRCheckBox.setChecked(True)
        self.showEstUnmBoneRCheckBox.stateChanged[int].connect(self.toggleShowEstUnmBoneR)
        self.grid_L.addWidget(self.showEstUnmBoneRCheckBox, n, 0)
        n = n+1
        self.showEstUnmBoneLCheckBox = QCheckBox(self.tr('Thresh. unm. bone L'))
        self.showEstUnmBoneLCheckBox.setChecked(True)
        self.showEstUnmBoneLCheckBox.stateChanged[int].connect(self.toggleShowEstUnmBoneL)
        self.grid_L.addWidget(self.showEstUnmBoneLCheckBox, n, 0)
        n = n+1
        self.showEstMskAirRCheckBox = QCheckBox(self.tr('Thresh. msk. air R'))
        self.showEstMskAirRCheckBox.setChecked(True)
        self.showEstMskAirRCheckBox.stateChanged[int].connect(self.toggleShowEstMskAirR)
        self.grid_L.addWidget(self.showEstMskAirRCheckBox, n, 0)
        n = n+1
        self.showEstMskAirLCheckBox = QCheckBox(self.tr('Thresh. msk. air L'))
        self.showEstMskAirLCheckBox.setChecked(True)
        self.showEstMskAirLCheckBox.stateChanged[int].connect(self.toggleShowEstMskAirL)
        self.grid_L.addWidget(self.showEstMskAirLCheckBox, n, 0)
        n = n+1
        self.showEstMskBoneRCheckBox = QCheckBox(self.tr('Thresh. msk. bone R'))
        self.showEstMskBoneRCheckBox.setChecked(True)
        self.showEstMskBoneRCheckBox.stateChanged[int].connect(self.toggleShowEstMskBoneR)
        self.grid_L.addWidget(self.showEstMskBoneRCheckBox, n, 0)
        n = n+1
        self.showEstMskBoneLCheckBox = QCheckBox(self.tr('Thresh. msk. bone L'))
        self.showEstMskBoneLCheckBox.setChecked(True)
        self.showEstMskBoneLCheckBox.stateChanged[int].connect(self.toggleShowEstMskBoneL)
        self.grid_L.addWidget(self.showEstMskBoneLCheckBox, n, 0)
        n = n+1 
       
        self.showRealThreshLbl = QLabel(self.tr('Show actual thresholds:'), self)
        self.grid_L.addWidget(self.showRealThreshLbl, n, 0, 1, 2)
        n = n+1
        self.showAirRCheckBox = QCheckBox(self.tr('Thresh. air R'))
        self.showAirRCheckBox.stateChanged[int].connect(self.toggleShowAirR)
        self.grid_L.addWidget(self.showAirRCheckBox, n, 0)

        self.showCIAirRCheckBox = QCheckBox(self.tr('CI'))
        self.showCIAirRCheckBox.stateChanged[int].connect(self.toggleShowCIAirR)
        self.grid_L.addWidget(self.showCIAirRCheckBox, n, 1)
        n = n+1
        self.showAirLCheckBox = QCheckBox(self.tr('Thresh. air L'))
        self.showAirLCheckBox.stateChanged[int].connect(self.toggleShowAirL)
        self.grid_L.addWidget(self.showAirLCheckBox, n, 0)

        self.showCIAirLCheckBox = QCheckBox(self.tr('CI'))
        self.showCIAirLCheckBox.stateChanged[int].connect(self.toggleShowCIAirL)
        self.grid_L.addWidget(self.showCIAirLCheckBox, n, 1)
        n = n+1
        self.showBoneRCheckBox = QCheckBox(self.tr('Thresh. bone R'))
        self.showBoneRCheckBox.stateChanged[int].connect(self.toggleShowBoneR)
        self.grid_L.addWidget(self.showBoneRCheckBox, n, 0)
        self.showCIBoneRCheckBox = QCheckBox(self.tr('CI'))
        self.showCIBoneRCheckBox.stateChanged[int].connect(self.toggleShowCIBoneR)
        self.grid_L.addWidget(self.showCIBoneRCheckBox, n, 1)
        n = n+1
        self.showBoneLCheckBox = QCheckBox(self.tr('Thresh. bone L'))
        self.showBoneLCheckBox.stateChanged[int].connect(self.toggleShowBoneL)
        self.grid_L.addWidget(self.showBoneLCheckBox, n, 0)
        self.showCIBoneLCheckBox = QCheckBox(self.tr('CI'))
        self.showCIBoneLCheckBox.stateChanged[int].connect(self.toggleShowCIBoneL)
        self.grid_L.addWidget(self.showCIBoneLCheckBox, n, 1)
        
        ## control grid right side
        n = 0
        self.NTEStatusLabel = QLabel(self.tr('Non-test ear status:'), self)
        self.NTEStatusChooser = QComboBox()
        self.NTEStatusChooser.addItems([self.tr("Uncovered"), self.tr("Earphone on")])
        self.NTEStatusChooser.textActivated[str].connect(self.onNTEStatusChooserChange)
        self.grid_R.addWidget(self.NTEStatusLabel, n, 0)
        self.grid_R.addWidget(self.NTEStatusChooser, n, 1)
        self.NTEStatusLabel.hide()
        self.NTEStatusChooser.hide()
        n = n+1
        self.NTESFStatusLabel = QLabel(self.tr('Non-test ear status:'), self)
        self.NTESFStatusChooser = QComboBox()
        self.NTESFStatusChooser.addItems([self.tr("Unaided"), self.tr("Chan. 2"), self.tr("Earplug"), self.tr("Dome (open)"), self.tr("Dome (tulip)"), self.tr("Dome (single vent)"), self.tr("Dome (double vent)"), self.tr("Double dome (power)"), self.tr("Earmold")])
        self.NTESFStatusChooser.textActivated[str].connect(self.onNTESFStatusChooserChange)
        self.grid_R.addWidget(self.NTESFStatusLabel, n, 0)
        self.grid_R.addWidget(self.NTESFStatusChooser, n, 1)
        self.NTESFStatusLabel.hide()
        self.NTESFStatusChooser.hide()
        n = n+1
        self.ch2Label = QLabel(self.tr('Chan. 2:'), self)
        self.transducerChooserCh2 = QComboBox()
        self.transducerChooserCh2.addItems([self.tr("Supra-aural"), self.tr("Insert")])
        self.transducerChooserCh2.setCurrentIndex(0)
        self.transducerChooserCh2.textActivated[str].connect(self.onTransducerChooserCh2Change)
        self.transducerChooserCh2.setItemIcon(0, QtGui.QIcon(":/headphones-solid"))
        self.transducerChooserCh2.setItemIcon(1, QtGui.QIcon(":/insert")) 
        self.transducerChooserCh2.setItemIcon(2, QtGui.QIcon(":/skull-solid")) 
        self.grid_R.addWidget(self.ch2Label, n, 0)
        self.grid_R.addWidget(self.transducerChooserCh2, n, 1)
        n = n+1
        self.ch2LevLabel = QLabel(self.tr("Chan. 2 level"))
        self.ch2LevTF = QLineEdit("0") #QSpinBox("0") #QLineEdit("0")
        self.ch2LevTF.setValidator(QIntValidator(self))
        self.ch2Lev = self.currLocale.toInt(self.ch2LevTF.text())[0]
        self.ch2LevTF.editingFinished.connect(self.onCh2LevChange)
        self.grid_R.addWidget(self.ch2LevLabel, n, 0, 2, 1)
        self.grid_R.addWidget(self.ch2LevTF, n, 1, 2, 1)

        self.ch2UpButton = QPushButton("+", self)
        self.ch2UpButton.setIcon(QtGui.QIcon(":/arrow-up-solid"))
        self.grid_R.addWidget(self.ch2UpButton, n, 2)
        self.ch2UpButton.clicked.connect(self.onClickCh2UpButton)
        n = n+1
        self.ch2DownButton = QPushButton(self.tr("-"), self)
        self.ch2DownButton.setIcon(QtGui.QIcon(":/arrow-down-solid"))
        self.grid_R.addWidget(self.ch2DownButton, n, 2)
        self.ch2DownButton.clicked.connect(self.onClickCh2DownButton)
        
        n = n+1
        self.ch2OnCheckBox = QCheckBox(self.tr('Chan. 2 ON'))
        #self.gridOn.setChecked(self.prm['pref']['grid'])
        self.ch2OnCheckBox.stateChanged[int].connect(self.toggleCh2)
        self.grid_R.addWidget(self.ch2OnCheckBox, n, 0)

        n = n+1
        self.showCaseFileNameCheckBox = QCheckBox(self.tr('Show case filename'))
        self.showCaseFileNameCheckBox.setChecked(False)
        self.showCaseFileNameCheckBox.stateChanged[int].connect(self.toggleShowCaseFileName)
        self.grid_R.addWidget(self.showCaseFileNameCheckBox, n, 0)
        
        self.showCaseInfoCheckBox = QCheckBox(self.tr('Show case info'))
        self.showCaseInfoCheckBox.setChecked(False)
        self.showCaseInfoCheckBox.stateChanged[int].connect(self.toggleShowCaseInfo)
        self.grid_R.addWidget(self.showCaseInfoCheckBox, n, 1)

        n = n+1
        self.caseFileNameLabel = QLabel(self.tr("Case file: ") + self.fCaseName)
        self.caseFileNameLabel.setWordWrap(True)
        self.grid_R.addWidget(self.caseFileNameLabel, n, 0, 1, 3)
        self.caseFileNameLabel.hide()

        n = n+1
        self.caseInfoBox = QTextEdit(self.caseInfo)
        self.caseInfoBox.setMarkdown(self.caseInfo)
        self.caseInfoBox.setReadOnly(True)
        self.caseInfoBox.hide()
        self.grid_R.addWidget(self.caseInfoBox, n, 0, 1, 3)
        
        self.canvas = FigureCanvas(self.fig)

        #self.canvas.setParent(self.mw)
       
        self.ntb = NavigationToolbar(self.canvas, self.mw)
        self.gridOn = QCheckBox(self.tr('Grid'))
        self.gridOn.setChecked(self.prm['pref']['grid'])
        self.gridOn.stateChanged[int].connect(self.toggleGrid)
        self.setBaseFigureProperties()

        self.ntbBox = QHBoxLayout()
        self.ntbBox.addWidget(self.ntb)
        self.ntbBox.addWidget(self.gridOn)

        self.stimLight = indicatorLight(self)
        self.stimLightLabel = QLabel(self.tr("Stimulus light"))
        self.stimLightLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.stimLightLabel.setStyleSheet("font-weight: bold")
        self.playStimButton = QPushButton(self.tr("Play stimulus"), self)
        self.playStimButton.pressed.connect(self.onPlayStim)
        self.playStimButton.released.connect(self.onStopStim)

        self.vbl_mid.addWidget(self.canvas, stretch=1)
        self.vbl_mid.addLayout(self.ntbBox)
        self.vbl_mid.addWidget(self.stimLightLabel)
        self.vbl_mid.addWidget(self.stimLight)
        self.vbl_mid.addWidget(self.playStimButton)
        self.f1.setLayout(self.grid_L)
        self.f2.setLayout(self.vbl_mid)
        self.f3.setLayout(self.grid_R)
        self.splitter.addWidget(self.f1)
        self.splitter.addWidget(self.f2)
        self.splitter.addWidget(self.f3)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.splitter)
        self.mw.setFocus()
        self.show()
        self.canvas.draw()
        self.setupStructs()

        self.symbs = {}
        self.symbs['masked'] = {}
        self.symbs['unmasked'] = {}
        self.symbs['masked']['air'] = {}
        self.symbs['masked']['bone'] = {}
        self.symbs['unmasked']['air'] = {}
        self.symbs['unmasked']['bone'] = {}
        self.symbs['masked']['air']['left'] = {}
        self.symbs['masked']['bone']['left'] = {}
        self.symbs['masked']['air']['right'] = {}
        self.symbs['masked']['bone']['right'] = {}

        self.symbs['unmasked']['air']['left'] = {}
        self.symbs['unmasked']['bone']['left'] = {}
        self.symbs['unmasked']['air']['right'] = {}
        self.symbs['unmasked']['bone']['right'] = {}

        self.symbs['masked']['air']['left']['found'] = air_L_msk #'s'
        self.symbs['masked']['bone']['left']['found'] = bone_L_msk #'$]$'
        self.symbs['masked']['air']['right']['found'] = air_R_msk #'$Δ$'
        self.symbs['masked']['bone']['right']['found'] = bone_R_msk #'$[$'

        self.symbs['unmasked']['air']['left']['found'] = air_L_unm #'x'
        self.symbs['unmasked']['bone']['left']['found'] = bone_L_unm #'$>$'
        self.symbs['unmasked']['air']['right']['found'] = air_R_unm #'o'
        self.symbs['unmasked']['bone']['right']['found'] = bone_R_unm #'$<$'

        self.symbs['masked']['air']['left']['NR'] = air_L_msk_NR #'s'
        self.symbs['masked']['bone']['left']['NR'] = bone_L_msk_NR #'$]$'
        self.symbs['masked']['air']['right']['NR'] = air_R_msk_NR #'$Δ$'
        self.symbs['masked']['bone']['right']['NR'] = bone_R_msk_NR #'$[$'

        self.symbs['unmasked']['air']['left']['NR'] = air_L_unm_NR #'x'
        self.symbs['unmasked']['bone']['left']['NR'] = bone_L_unm_NR #'$>$'
        self.symbs['unmasked']['air']['right']['NR'] = air_R_unm_NR #'o'
        self.symbs['unmasked']['bone']['right']['NR'] = bone_R_unm_NR #'$<$'

        self.symbs['masked']['air']['left']['MD'] = '$\\frac{?}{AL}$' #'$ALM-nMD$'
        self.symbs['masked']['bone']['left']['MD'] = '$\\frac{?}{BL}$'
        self.symbs['masked']['air']['right']['MD'] = '$\\frac{?}{AR}$'
        self.symbs['masked']['bone']['right']['MD'] = '$\\frac{?}{BR}$'

        self.symbs['unmasked']['air']['left']['MD'] = '$\\frac{?}{ALU}$'
        self.symbs['unmasked']['bone']['left']['MD'] = '$\\frac{?}{BLU}$'
        self.symbs['unmasked']['air']['right']['MD'] = '$\\frac{?}{ARU}$'
        self.symbs['unmasked']['bone']['right']['MD'] = '$\\frac{?}{BRU}$'

        self.trans_min = {}
        self.trans_min[self.tr("Bone")] = {}
        self.trans_min[self.tr("Bone")][125] = -20
        self.trans_min[self.tr("Bone")][250] = -20
        self.trans_min[self.tr("Bone")][500] = -20
        self.trans_min[self.tr("Bone")][750] = -20
        self.trans_min[self.tr("Bone")][1000] = -20
        self.trans_min[self.tr("Bone")][1500] = -20
        self.trans_min[self.tr("Bone")][2000] = -20
        self.trans_min[self.tr("Bone")][3000] = -20
        self.trans_min[self.tr("Bone")][4000] = -20
        self.trans_min[self.tr("Bone")][6000] = -20
        self.trans_min[self.tr("Bone")][8000] = -20

        self.trans_min[self.tr("Supra-aural")] = {}
        self.trans_min[self.tr("Supra-aural")][125] = -20
        self.trans_min[self.tr("Supra-aural")][250] = -20
        self.trans_min[self.tr("Supra-aural")][500] = -20
        self.trans_min[self.tr("Supra-aural")][750] = -20
        self.trans_min[self.tr("Supra-aural")][1000] = -20
        self.trans_min[self.tr("Supra-aural")][1500] = -20
        self.trans_min[self.tr("Supra-aural")][2000] = -20
        self.trans_min[self.tr("Supra-aural")][3000] = -20
        self.trans_min[self.tr("Supra-aural")][4000] = -20
        self.trans_min[self.tr("Supra-aural")][6000] = -20
        self.trans_min[self.tr("Supra-aural")][8000] = -20

        self.trans_min[self.tr("Insert")] = {}
        self.trans_min[self.tr("Insert")][125] = -20
        self.trans_min[self.tr("Insert")][250] = -20
        self.trans_min[self.tr("Insert")][500] = -20
        self.trans_min[self.tr("Insert")][750] = -20
        self.trans_min[self.tr("Insert")][1000] = -20
        self.trans_min[self.tr("Insert")][1500] = -20
        self.trans_min[self.tr("Insert")][2000] = -20
        self.trans_min[self.tr("Insert")][3000] = -20
        self.trans_min[self.tr("Insert")][4000] = -20
        self.trans_min[self.tr("Insert")][6000] = -20
        self.trans_min[self.tr("Insert")][8000] = -20

        self.trans_min[self.tr("Sound field")] = {}
        self.trans_min[self.tr("Sound field")][125] = 0
        self.trans_min[self.tr("Sound field")][250] = 0
        self.trans_min[self.tr("Sound field")][500] = 0
        self.trans_min[self.tr("Sound field")][750] = 0
        self.trans_min[self.tr("Sound field")][1000] = 0
        self.trans_min[self.tr("Sound field")][1500] = 0
        self.trans_min[self.tr("Sound field")][2000] = 0
        self.trans_min[self.tr("Sound field")][3000] = 0
        self.trans_min[self.tr("Sound field")][4000] = 0
        self.trans_min[self.tr("Sound field")][6000] = 0
        self.trans_min[self.tr("Sound field")][8000] = 0

        self.trans_max = {}
        self.trans_max[self.tr("Bone")] = {}
        self.trans_max[self.tr("Bone")][125] = 30
        self.trans_max[self.tr("Bone")][250] = 35
        self.trans_max[self.tr("Bone")][500] = 50
        self.trans_max[self.tr("Bone")][750] = 60
        self.trans_max[self.tr("Bone")][1000] = 70
        self.trans_max[self.tr("Bone")][1500] = 70
        self.trans_max[self.tr("Bone")][2000] = 70
        self.trans_max[self.tr("Bone")][3000] = 70
        self.trans_max[self.tr("Bone")][4000] = 70
        self.trans_max[self.tr("Bone")][6000] = 70
        self.trans_max[self.tr("Bone")][8000] = 70

        self.trans_max[self.tr("Supra-aural")] = {}
        self.trans_max[self.tr("Supra-aural")][125] = 105
        self.trans_max[self.tr("Supra-aural")][250] = 105
        self.trans_max[self.tr("Supra-aural")][500] = 110
        self.trans_max[self.tr("Supra-aural")][750] = 115
        self.trans_max[self.tr("Supra-aural")][1000] = 120
        self.trans_max[self.tr("Supra-aural")][1500] = 120
        self.trans_max[self.tr("Supra-aural")][2000] = 120
        self.trans_max[self.tr("Supra-aural")][3000] = 120
        self.trans_max[self.tr("Supra-aural")][4000] = 115
        self.trans_max[self.tr("Supra-aural")][6000] = 115
        self.trans_max[self.tr("Supra-aural")][8000] = 115


        self.trans_max[self.tr("Insert")] = {}
        self.trans_max[self.tr("Insert")][125] = 105
        self.trans_max[self.tr("Insert")][250] = 105
        self.trans_max[self.tr("Insert")][500] = 110
        self.trans_max[self.tr("Insert")][750] = 115
        self.trans_max[self.tr("Insert")][1000] = 120
        self.trans_max[self.tr("Insert")][1500] = 120
        self.trans_max[self.tr("Insert")][2000] = 120
        self.trans_max[self.tr("Insert")][3000] = 120
        self.trans_max[self.tr("Insert")][4000] = 115
        self.trans_max[self.tr("Insert")][6000] = 115
        self.trans_max[self.tr("Insert")][8000] = 115

        self.trans_max[self.tr("Sound field")] = {}
        self.trans_max[self.tr("Sound field")][125] = 105
        self.trans_max[self.tr("Sound field")][250] = 105
        self.trans_max[self.tr("Sound field")][500] = 110
        self.trans_max[self.tr("Sound field")][750] = 110
        self.trans_max[self.tr("Sound field")][1000] = 110
        self.trans_max[self.tr("Sound field")][1500] = 110
        self.trans_max[self.tr("Sound field")][2000] = 110
        self.trans_max[self.tr("Sound field")][3000] = 110
        self.trans_max[self.tr("Sound field")][4000] = 110
        self.trans_max[self.tr("Sound field")][6000] = 110
        self.trans_max[self.tr("Sound field")][8000] = 110


    def setupBaseFigure(self):
        self.axes = self.fig.add_subplot(111, facecolor=self.backgroundColor, xlim=self.xlims, ylim=self.ylims)
        self.axes.format_coord = lambda x, y: ''
        self.axes.invert_yaxis()
        self.axes.set_xscale('log')
        self.axes.xaxis.set_major_locator(ticker.NullLocator())
        self.axes.xaxis.set_minor_locator(ticker.NullLocator())
        self.axes.set_xticks([125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000])
        self.axes.set_xticklabels(['.125', '.25', '.5', '.75','1','1.5','2','3','4','6','8'])
        self.axes.set_yticks([-20, -10, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120])
        self.axes.set_yticklabels(['-20', '-10', '0', '10', '20', '30', '40', '50', '60', '70', '80', '90', '100', '110', '120'])
        self.ch1Tracker, = self.axes.plot(self.testFreq, self.testLev, marker=self.ch1Marker, color=self.currCh1Color, markersize=self.trackerMarkerSize)
        self.ch2Tracker, = self.axes.plot(self.testFreq, self.ch2Lev, marker=self.ch2Marker, color=self.currCh2Color, markersize=self.trackerMarkerSize)
        self.threshTracker = {}
        if self.ch2On == False:
            self.ch2Tracker.remove()

    def setupStructs(self):
        self.pnts = {}
        self.pnts['unmasked'] = {}
        self.pnts['unmasked']['air'] = {}
        self.pnts['unmasked']['air']['left'] = {}
        self.pnts['unmasked']['air']['right'] = {}
        self.pnts['unmasked']['bone'] = {}
        self.pnts['unmasked']['bone']['left'] = {}
        self.pnts['unmasked']['bone']['right'] = {}
        self.pnts['masked'] = {}
        self.pnts['masked']['air'] = {}
        self.pnts['masked']['air']['left'] = {}
        self.pnts['masked']['air']['right'] = {}
        self.pnts['masked']['bone'] = {}
        self.pnts['masked']['bone']['left'] = {}
        self.pnts['masked']['bone']['right'] = {}

        n_freqs = len(self.testFreqs)
        self.est_aud = {}
        self.est_aud['unmasked'] = {}
        self.est_aud['unmasked']['air'] = {}
        self.est_aud['unmasked']['air']['left'] = np.full(n_freqs, np.nan)
        self.est_aud['unmasked']['air']['right'] = np.full(n_freqs, np.nan)
        self.est_aud['unmasked']['bone'] = {}
        self.est_aud['unmasked']['bone']['left'] = np.full(n_freqs, np.nan)
        self.est_aud['unmasked']['bone']['right'] = np.full(n_freqs, np.nan)

        self.est_aud['masked'] = {}
        self.est_aud['masked']['air'] = {}
        self.est_aud['masked']['air']['left'] = np.full(n_freqs, np.nan)
        self.est_aud['masked']['air']['right'] = np.full(n_freqs, np.nan)
        self.est_aud['masked']['bone'] = {}
        self.est_aud['masked']['bone']['left'] = np.full(n_freqs, np.nan)
        self.est_aud['masked']['bone']['right'] = np.full(n_freqs, np.nan)

        self.plot_prms = {}
        self.plot_prms['unmasked'] = {}
        self.plot_prms['unmasked']['air'] = {}
        self.plot_prms['unmasked']['air']['left'] = {}
        self.plot_prms['unmasked']['air']['right'] = {}
        self.plot_prms['unmasked']['air']['left']['visible'] = np.full(n_freqs, False)
        self.plot_prms['unmasked']['air']['right']['visible'] = np.full(n_freqs, False)
        self.plot_prms['unmasked']['air']['left']['thresh_status'] = ['' for i in range(n_freqs)]
        self.plot_prms['unmasked']['air']['right']['thresh_status'] = ['' for i in range(n_freqs)]
        self.plot_prms['unmasked']['bone'] = {}
        self.plot_prms['unmasked']['bone']['left'] = {}
        self.plot_prms['unmasked']['bone']['right'] = {}
        self.plot_prms['unmasked']['bone']['left']['visible'] = np.full(n_freqs, False)
        self.plot_prms['unmasked']['bone']['right']['visible'] = np.full(n_freqs, False)
        self.plot_prms['unmasked']['bone']['left']['thresh_status'] = ['' for i in range(n_freqs)]
        self.plot_prms['unmasked']['bone']['right']['thresh_status'] = ['' for i in range(n_freqs)]

        self.plot_prms['masked'] = {}
        self.plot_prms['masked']['air'] = {}
        self.plot_prms['masked']['air']['left'] = {}
        self.plot_prms['masked']['air']['right'] = {}
        self.plot_prms['masked']['air']['left']['visible'] = np.full(n_freqs, False)
        self.plot_prms['masked']['air']['right']['visible'] = np.full(n_freqs, False)
        self.plot_prms['masked']['air']['left']['thresh_status'] = ['' for i in range(n_freqs)]
        self.plot_prms['masked']['air']['right']['thresh_status'] = ['' for i in range(n_freqs)]
        self.plot_prms['masked']['bone'] = {}
        self.plot_prms['masked']['bone']['left'] = {}
        self.plot_prms['masked']['bone']['right'] = {}
        self.plot_prms['masked']['bone']['left']['visible'] = np.full(n_freqs, False)
        self.plot_prms['masked']['bone']['right']['visible'] = np.full(n_freqs, False)
        self.plot_prms['masked']['bone']['left']['thresh_status'] = ['' for i in range(n_freqs)]
        self.plot_prms['masked']['bone']['right']['thresh_status'] = ['' for i in range(n_freqs)]

        self.est_msk_need = {}
        self.est_msk_need['air'] = {}
        self.est_msk_need['air']['left'] = np.full(n_freqs, np.nan)
        self.est_msk_need['air']['right'] = np.full(n_freqs, np.nan)
        self.est_msk_need['bone'] = {}
        self.est_msk_need['bone']['left'] = np.full(n_freqs, np.nan)
        self.est_msk_need['bone']['right'] = np.full(n_freqs, np.nan)

        self.est_msk_min = {}
        self.est_msk_min['air'] = {}
        self.est_msk_min['air']['left'] = np.full(n_freqs, np.nan)
        self.est_msk_min['air']['right'] = np.full(n_freqs, np.nan)
        self.est_msk_min['bone'] = {}
        self.est_msk_min['bone']['left'] = np.full(n_freqs, np.nan)
        self.est_msk_min['bone']['right'] = np.full(n_freqs, np.nan)

        self.est_msk_max = {}
        self.est_msk_max['air'] = {}
        self.est_msk_max['air']['left'] = np.full(n_freqs, np.nan)
        self.est_msk_max['air']['right'] = np.full(n_freqs, np.nan)
        self.est_msk_max['bone'] = {}
        self.est_msk_max['bone']['left'] = np.full(n_freqs, np.nan)
        self.est_msk_max['bone']['right'] = np.full(n_freqs, np.nan)


    def loadCase(self):
        self.lis = pd.read_csv(self.fCaseName, delimiter = ',')
        self.caseFileNameLabel.setText(self.fCaseName)
        self.loadCaseInfo()
        self.setupNewCase()
        self.curr_dir = "down"
        self.thresh_obt = False
        self.thresh = np.nan
        self.asce_levs = np.empty(shape=0)
        self.asce_n = np.empty(shape=0)
        self.asce_yes = np.empty(shape=0)
        self.asce_yes_prop = np.empty(shape=0)
        self.prevStimLev = np.inf

        for key in list(self.threshTracker.keys()):
            self.threshTracker[key].remove()
        self.threshTracker = {}

    def loadCaseInfo(self):
        lang = self.prm['locale_string'].split('_')[0]
        if os.path.exists(self.fCaseName[0:-4]+'_info_'+self.prm['locale_string']+'.md'):
            fHnl = open(self.fCaseName[0:-4]+'_info_'+self.prm['locale_string']+'.md', 'r')
            self.caseInfo = fHnl.read()
            fHnl.close()
        elif os.path.exists(self.fCaseName[0:-4]+'_info_'+ lang +'.md'):
            fHnl = open(self.fCaseName[0:-4]+'_info_'+ lang +'.md', 'r')
            self.caseInfo = fHnl.read()
            fHnl.close()
        elif os.path.exists(self.fCaseName[0:-4]+'_info.md'):
            fHnl = open(self.fCaseName[0:-4]+'_info.md', 'r')
            self.caseInfo = fHnl.read()
            fHnl.close()
        else:
            self.caseInfo = self.tr("No case info available")
        
    def loadCaseDialog(self):
        self.fCaseName = QFileDialog.getOpenFileName(self, self.tr("Choose case file to load"), self.prm['rootDirectory']+'/case_files/', self.tr("CSV files (*.csv *CSV *Csv);;All Files (*)"))[0]
        if len(self.fCaseName) > 0: #if the user didn't press cancel
            self.loadCase()

    def loadRandomCase(self):
        self.fCaseName = self.prm['rootDirectory'] + '/case_files/' + random.choice(self.caseFls)
        self.loadCase()

    def setupNewCase(self):
        self.showEstUnmAirRCheckBox.setChecked(True)
        self.showEstUnmAirLCheckBox.setChecked(True)
        self.showEstUnmBoneRCheckBox.setChecked(True)
        self.showEstUnmBoneLCheckBox.setChecked(True)
        self.showEstMskAirRCheckBox.setChecked(True)
        self.showEstMskAirLCheckBox.setChecked(True)
        self.showEstMskBoneRCheckBox.setChecked(True)
        self.showEstMskBoneLCheckBox.setChecked(True)
        self.showAirRCheckBox.setChecked(False)
        self.showAirLCheckBox.setChecked(False)
        self.showBoneRCheckBox.setChecked(False)
        self.showBoneLCheckBox.setChecked(False)
        self.showCIAirRCheckBox.setChecked(False)
        self.showCIAirLCheckBox.setChecked(False)
        self.showCIBoneRCheckBox.setChecked(False)
        self.showCIBoneLCheckBox.setChecked(False)
        self.testFreqs = np.array(self.lis['freq'])
        self.setupStructs()
        self.fig.clf()
        self.setupBaseFigure()
        self.setBaseFigureProperties()
        if self.gridOn.isChecked():
            self.axes.grid(True, color=self.gridColor, linewidth=self.gridLineWidth, which="both")
        else:
            self.axes.grid(False)
        self.canvas.draw()
       

        self.caseInfoBox.setMarkdown(self.caseInfo)

    def onClickGenerateCase(self):
        dialog = generateCaseWindow(self)

    def toggleShowCaseInfo(self):
        if self.showCaseInfoCheckBox.isChecked():
            self.caseInfoBox.show()
        else:
            self.caseInfoBox.hide()
        self.mw.setFocus()
            
    def toggleShowCaseFileName(self):
        if self.showCaseFileNameCheckBox.isChecked():
            self.caseFileNameLabel.show()
        else:
            self.caseFileNameLabel.hide()
        self.mw.setFocus()

    def toggleGrid(self, state):
        if self.gridOn.isChecked():
            self.axes.grid(True, color=self.gridColor, linewidth=self.gridLineWidth, which="both")
        else:
            self.axes.grid(False)
        self.canvas.draw()

    def toggleCh2(self, state):
        if self.ch2OnCheckBox.isChecked():
            self.ch2On = True
            self.ch2Tracker, = self.axes.plot(self.testFreq, self.ch2Lev, marker=self.ch2Marker, color=self.currCh2Color, markersize=self.trackerMarkerSize)
            self.NTEStatusChooser.setCurrentIndex(self.NTEStatusChooser.findText(self.tr("Earphone on")))
        else:
            self.ch2On = False
            self.ch2Tracker.remove()
        self.canvas.draw()
        self.mw.setFocus()

    def toggleLockChans(self, state):
        if self.lockChansCheckBox.isChecked():
            self.chansLocked = True
            self.lockChansCheckBox.setText(self.tr("Unlock channels"))
            self.lockChansCheckBox.setIcon(QtGui.QIcon(":/lock-solid")) 
        else:
            self.chansLocked = False
            self.lockChansCheckBox.setText(self.tr("Lock channels"))
            self.lockChansCheckBox.setIcon(QtGui.QIcon(":/lock-open-solid")) 
        self.mw.setFocus()

    def toggleShowRespEar(self, state):
        if self.showRespEarCheckBox.isChecked():
            self.showRespEar = True
        else:
            self.showRespEar = False
        self.mw.setFocus()

    def toggleShowRespCounts(self, state):
        if self.showRespCountsCheckBox.isChecked():
            self.showRespCounts = True
            self.plotResponseCounts()
        else:
            self.showRespCounts = False
            for key in list(self.threshTracker.keys()):
                self.threshTracker[key].remove()
            self.threshTracker = {}
            self.canvas.draw()
        self.mw.setFocus()

    def toggleShowEstUnmAirR(self, state):
        if self.showEstUnmAirRCheckBox.isChecked():
            self.plotPoints('unmasked', 'air', 'right')
        else:
            self.removePoints('unmasked', 'air', 'right')
        self.mw.setFocus()

    def toggleShowEstUnmAirL(self, state):
        if self.showEstUnmAirLCheckBox.isChecked():
            self.plotPoints('unmasked', 'air', 'left')
        else:
            self.removePoints('unmasked', 'air', 'left')
        self.mw.setFocus()

    def toggleShowEstUnmBoneR(self, state):
        if self.showEstUnmBoneRCheckBox.isChecked():
            self.plotPoints('unmasked', 'bone', 'right')
        else:
            self.removePoints('unmasked', 'bone', 'right')
        self.mw.setFocus()

    def toggleShowEstUnmBoneL(self, state):
        if self.showEstUnmBoneLCheckBox.isChecked():
            self.plotPoints('unmasked', 'bone', 'left')
        else:
            self.removePoints('unmasked', 'bone', 'left')
        self.mw.setFocus()

    def toggleShowEstMskAirR(self, state):
        if self.showEstMskAirRCheckBox.isChecked():
            self.plotPoints('masked', 'air', 'right')
        else:
            self.removePoints('masked', 'air', 'right')
        self.mw.setFocus()

    def toggleShowEstMskAirL(self, state):
        if self.showEstMskAirLCheckBox.isChecked():
            self.plotPoints('masked', 'air', 'left')
        else:
            self.removePoints('masked', 'air', 'left')
        self.mw.setFocus()

    def toggleShowEstMskBoneR(self, state):
        if self.showEstMskBoneRCheckBox.isChecked():
            self.plotPoints('masked', 'bone', 'right')
        else:
            self.removePoints('masked', 'bone', 'right')
        self.mw.setFocus()

    def toggleShowEstMskBoneL(self, state):
        if self.showEstMskBoneLCheckBox.isChecked():
            self.plotPoints('masked', 'bone', 'left')
        else:
            self.removePoints('masked', 'bone', 'left')
        self.mw.setFocus()

    def toggleShowAirR(self, state):
        if self.showAirRCheckBox.isChecked():
            n_freqs = len(self.testFreqs)
            self.air_r_p50_trace = {}
            for pn in range(n_freqs):
                if np.isinf(self.lis['air_R_perc50'][pn]):
                    vl = self.ylims[1] -5
                    ps = "$?$"
                else:
                    vl = self.lis['air_R_perc50'][pn]
                    ps = "$/$"
                self.air_r_p50_trace[self.testFreqs[pn]], = self.axes.plot(self.testFreqs[pn], vl, marker=ps, color='red', markersize=self.plotMarkerSize, markerfacecolor='none', linestyle='none')
        else:
            n_freqs = len(self.testFreqs)
            for pn in range(n_freqs):
                self.air_r_p50_trace[self.testFreqs[pn]].remove()            
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowCIAirR(self, state):
        if self.showCIAirRCheckBox.isChecked():
            lo = np.array(self.lis['air_R_perc2.5'])
            hi = np.array(self.lis['air_R_perc97.5'])
            lo[np.where(np.isinf(lo))] = self.ylims[1]
            hi[np.where(np.isinf(hi))] = self.ylims[1]
            self.air_r_CI_trace = self.axes.fill_between(self.testFreqs, lo, hi, alpha=0.5, edgecolor='red', facecolor='red')
        else:
            self.air_r_CI_trace.remove()
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowAirL(self, state):
        if self.showAirLCheckBox.isChecked():
            n_freqs = len(self.testFreqs)
            self.air_l_p50_trace = {}
            for pn in range(n_freqs):
                if np.isinf(self.lis['air_L_perc50'][pn]):
                    vl = self.ylims[1] -5
                    ps = "$?$"
                else:
                    vl = self.lis['air_L_perc50'][pn]
                    ps = "$/$"
                self.air_l_p50_trace[self.testFreqs[pn]], = self.axes.plot(self.testFreqs[pn], vl, marker=ps, color='blue', markersize=self.plotMarkerSize, markerfacecolor='none', linestyle='none')
        else:
            n_freqs = len(self.testFreqs)
            for pn in range(n_freqs):
                self.air_l_p50_trace[self.testFreqs[pn]].remove()            
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowCIAirL(self, state):
        if self.showCIAirLCheckBox.isChecked():
            lo = np.array(self.lis['air_L_perc2.5'])
            hi = np.array(self.lis['air_L_perc97.5'])
            lo[np.where(np.isinf(lo))] = self.ylims[1]
            hi[np.where(np.isinf(hi))] = self.ylims[1]
            self.air_l_CI_trace = self.axes.fill_between(self.testFreqs, lo, hi, alpha=0.5, edgecolor='blue', facecolor='blue')
        else:
            self.air_l_CI_trace.remove()
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowBoneR(self, state):
        if self.showBoneRCheckBox.isChecked():
            n_freqs = len(self.testFreqs)
            self.bone_r_p50_trace = {}
            for pn in range(n_freqs):
                if np.isinf(self.lis['bone_R_perc50'][pn]):
                    vl = self.ylims[1] -5
                    ps = "$¿$"
                else:
                    vl = self.lis['bone_R_perc50'][pn]
                    ps = "$-$"
                self.bone_r_p50_trace[self.testFreqs[pn]], = self.axes.plot(self.testFreqs[pn], vl, marker=ps, color='red', markersize=self.plotMarkerSize, markerfacecolor='none', linestyle='none')
        else:
            n_freqs = len(self.testFreqs)
            for pn in range(n_freqs):
                self.bone_r_p50_trace[self.testFreqs[pn]].remove()
                
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowCIBoneR(self, state):
        if self.showCIBoneRCheckBox.isChecked():
            lo = np.array(self.lis['bone_R_perc2.5'])
            hi = np.array(self.lis['bone_R_perc97.5'])
            lo[np.where(np.isinf(lo))] = self.ylims[1]
            hi[np.where(np.isinf(hi))] = self.ylims[1]
            self.bone_r_CI_trace = self.axes.fill_between(self.testFreqs, lo, hi, alpha=0.5, edgecolor='red', facecolor='red')
        else:
            self.bone_r_CI_trace.remove()
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowBoneL(self, state):
        if self.showBoneLCheckBox.isChecked():
            n_freqs = len(self.testFreqs)
            self.bone_l_p50_trace = {}
            for pn in range(n_freqs):
                if np.isinf(self.lis['bone_L_perc50'][pn]):
                    vl = self.ylims[1] -5
                    ps = "$¿$"
                else:
                    vl = self.lis['bone_L_perc50'][pn]
                    ps = "$-$"
                self.bone_l_p50_trace[self.testFreqs[pn]], = self.axes.plot(self.testFreqs[pn], vl, marker=ps, color='blue', markersize=self.plotMarkerSize, markerfacecolor='none', linestyle='none')
        else:
            n_freqs = len(self.testFreqs)
            for pn in range(n_freqs):
                self.bone_l_p50_trace[self.testFreqs[pn]].remove()
                
        self.canvas.draw()
        self.mw.setFocus()

    def toggleShowCIBoneL(self, state):
        if self.showCIBoneLCheckBox.isChecked():
            lo = np.array(self.lis['bone_L_perc2.5'])
            hi = np.array(self.lis['bone_L_perc97.5'])
            lo[np.where(np.isinf(lo))] = self.ylims[1]
            hi[np.where(np.isinf(hi))] = self.ylims[1]
            self.bone_l_CI_trace = self.axes.fill_between(self.testFreqs, lo, hi, alpha=0.5, edgecolor='blue', facecolor='blue')
        else:
            self.bone_l_CI_trace.remove()
        self.canvas.draw()
        self.mw.setFocus()

    def onTransducerChooserCh1Change(self, transducerSelected):
        if self.transducerCh1 != transducerSelected:
            self.curr_dir = "down"
            self.thresh_obt = False
            self.thresh = np.nan
            self.asce_levs = np.empty(shape=0)
            self.asce_n = np.empty(shape=0)
            self.asce_yes = np.empty(shape=0)
            self.asce_yes_prop = np.empty(shape=0)
            self.prevStimLev = np.inf
            self.transducerCh1 = transducerSelected
            if self.transducerCh1 == self.tr("Sound field"):
                self.TESFStatusLabel.show()
                self.TESFStatusChooser.show()
                self.NTESFStatusLabel.show()
                self.NTESFStatusChooser.show()
                self.NTEStatusLabel.hide()
                self.NTEStatusChooser.hide()
            elif self.transducerCh1 == self.tr("Bone"):
                self.NTEStatusLabel.show()
                self.NTEStatusChooser.show()
                self.TESFStatusLabel.hide()
                self.TESFStatusChooser.hide()
                self.NTESFStatusLabel.hide()
                self.NTESFStatusChooser.hide()
            else:
                self.NTEStatusLabel.hide()
                self.NTEStatusChooser.hide()
                self.TESFStatusLabel.hide()
                self.TESFStatusChooser.hide()
                self.NTESFStatusLabel.hide()
                self.NTESFStatusChooser.hide()

            self.testLev = 35
            self.ch1Tracker.set_data((self.testFreq, self.testLev))

            for key in list(self.threshTracker.keys()):
                self.threshTracker[key].remove()
            self.threshTracker = {}
            
            self.canvas.draw()
        self.mw.setFocus()

    def onTransducerChooserCh2Change(self, transducerSelected):
        self.transducerCh2 = transducerSelected
        self.ch2Lev = 0
        self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
        self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
        self.canvas.draw()
        self.mw.setFocus()

    def onTestEarChange(self, testEarSelected):
        if self.testEar != testEarSelected:
            self.curr_dir = "down"
            self.thresh_obt = False
            self.thresh = np.nan
            self.asce_levs = np.empty(shape=0)
            self.asce_n = np.empty(shape=0)
            self.asce_yes = np.empty(shape=0)
            self.asce_yes_prop = np.empty(shape=0)
            self.prevStimLev = np.inf
            self.testEar = testEarSelected
            if self.testEar == self.tr("Right"):
                self.currCh1Color = "red"
                self.currCh2Color = "blue"
            elif self.testEar == self.tr("Left"):
                self.currCh1Color = "blue"
                self.currCh2Color = "red"

            self.ch1Tracker.remove()
            self.ch1Tracker, = self.axes.plot(self.testFreq, self.testLev, marker=self.ch1Marker, color=self.currCh1Color, markersize=self.trackerMarkerSize)
            if self.ch2OnCheckBox.isChecked():
                self.ch2Tracker.remove()
                self.ch2Tracker, = self.axes.plot(self.testFreq, self.ch2Lev, marker=self.ch2Marker, color=self.currCh2Color, markersize=self.trackerMarkerSize)

            for key in list(self.threshTracker.keys()):
                self.threshTracker[key].remove()
            self.threshTracker = {}
            
            self.canvas.draw()
        self.mw.setFocus()

    def onTESFStatusChooserChange(self, status):
        if status == self.tr("Aided"):
            self.TESFCouplingLabel.show()
            self.TESFCouplingChooser.show()
        elif status == self.tr("Unaided"):
            self.TESFCouplingLabel.hide()
            self.TESFCouplingChooser.hide()
        self.mw.setFocus()

    def onTESFCouplingChooserChange(self):
        self.mw.setFocus()

    def onNTESFStatusChooserChange(self):
        self.mw.setFocus()
        
    def onNTEStatusChooserChange(self):
        self.mw.setFocus()

    def onCh2LevChange(self):
        if self.currLocale.toInt(self.ch2LevTF.text())[0] > self.trans_max[self.transducerCh2][self.testFreq]:
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("Requested channel 2 value out of limits for the current transducers"),
                                      QMessageBox.StandardButton.Ok)
            self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            return
        elif self.currLocale.toInt(self.ch2LevTF.text())[0] < self.trans_min[self.transducerCh2][self.testFreq]:
            self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("Requested channel 2 value out of limits for the current transducers"),
                                      QMessageBox.StandardButton.Ok)
            return
        else:
            self.ch2Lev = self.currLocale.toInt(self.ch2LevTF.text())[0]
            
        self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
        self.canvas.draw()
        self.mw.setFocus()
        
    def onClickCh2UpButton(self):
        currLev = self.currLocale.toInt(self.ch2LevTF.text())[0]
        if currLev+5 > self.trans_max[self.transducerCh2][self.testFreq]:
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("Channel 2 has reached its maximum level for the current transducers"),
                                      QMessageBox.StandardButton.Ok)
            return
        else:
            self.ch2Lev = currLev + 5
            self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
            self.canvas.draw()
            self.mw.setFocus()
        
    def onClickCh2DownButton(self):
        currLev = self.currLocale.toInt(self.ch2LevTF.text())[0]
        if currLev-5 < self.trans_min[self.transducerCh2][self.testFreq]:
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("Channel 2 has reached its minimum level for the current transducers"),
                                      QMessageBox.StandardButton.Ok)
            return
        else:
            self.ch2Lev = currLev - 5
            self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
            self.canvas.draw()
            self.mw.setFocus()
        
    def keyPressEvent(self, event):
        if (event.type() == QEvent.Type.KeyPress):
            if event.key()==Qt.Key.Key_Up:
                self.onShiftLev("up")
            elif event.key()==Qt.Key.Key_Down:
                self.onShiftLev("down")
            elif event.key()==Qt.Key.Key_Left:
                self.onShiftFreq("left")
            elif event.key()==Qt.Key.Key_Right:
                self.onShiftFreq("right")
            elif event.key() == Qt.Key.Key_Space:
                self.onPlayStim()
            elif event.key() == Qt.Key.Key_T:
                self.onMarkThresh('found')
            elif event.key() == Qt.Key.Key_N:
                self.onMarkThresh('NR')
            elif event.key() == Qt.Key.Key_X:
                self.onMarkThresh('MD')
            elif event.key() == Qt.Key.Key_D or event.key() == Qt.Key.Key_Delete:
                self.onDeleteThresh()
                
    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if (event.type() == QEvent.Type.KeyRelease):
            if event.key() == Qt.Key.Key_Space:
                self.onStopStim()
                
    def onShiftLev(self, direction):
        if direction == "up":
            if (self.testLev - 5) < self.trans_min[self.transducerCh1][self.testFreq]:
                ret = QMessageBox.warning(self, self.tr("Warning"),
                                          self.tr("Channel 1 has reached the minimum level for the current transducers"),
                                          QMessageBox.StandardButton.Ok)
                return
            else:
                if self.chansLocked == True and (self.ch2Lev-5) < self.trans_min[self.transducerCh2][self.testFreq]:
                    ret = QMessageBox.warning(self, self.tr("Warning"),
                                              self.tr("Channel 2 is locked to channel 1 and has reached its minimum level for the current transducers"),
                                              QMessageBox.StandardButton.Ok)
                    return
                else:
                    self.testLev = self.testLev-5
                    if self.chansLocked == True:
                        self.ch2Lev = self.ch2Lev-5
                        self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
        elif direction == "down":
            if (self.testLev + 5) > self.trans_max[self.transducerCh1][self.testFreq]:
                ret = QMessageBox.warning(self, self.tr("Warning"),
                                          self.tr("Channel 1 has reached the maximum level for the current transducers"),
                                          QMessageBox.StandardButton.Ok)
                return
            else:
                if self.chansLocked == True and (self.ch2Lev+5) > self.trans_max[self.transducerCh2][self.testFreq]:
                    ret = QMessageBox.warning(self, self.tr("Warning"),
                                              self.tr("Channel 2 is locked to channel 1 and has reached its maximum level for the current transducers"),
                                              QMessageBox.StandardButton.Ok)
                    return
                else:
                    self.testLev = self.testLev+5
                    if self.chansLocked == True:
                        self.ch2Lev = self.ch2Lev+5
                        self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            
        self.ch1Tracker.set_data((self.testFreq, self.testLev))
        self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
        self.canvas.draw()

        #msk_needed = 
        
    def onShiftFreq(self, direction):
        idx = np.where(self.testFreqs == self.testFreq)[0][0]
        if direction == "left":
            if idx == 0:
                #self.testFreq = self.testFreqs[-1]
                self.testFreq = 1000
            else:
                self.testFreq = self.testFreqs[idx-1]
        elif direction == "right":
            if idx == len(self.testFreqs)-1:
                #self.testFreq = self.testFreqs[0]
                self.testFreq = 1000
            else:
                self.testFreq = self.testFreqs[idx+1]
        self.curr_dir = "down"
        self.thresh_obt = False
        self.thresh = np.nan
        self.asce_levs = np.empty(shape=0)
        self.asce_n = np.empty(shape=0)
        self.asce_yes = np.empty(shape=0)
        self.asce_yes_prop = np.empty(shape=0)
        self.prevStimLev = np.inf

        for key in list(self.threshTracker.keys()):
            self.threshTracker[key].remove()
        self.threshTracker = {}
        
        self.ch1Tracker.set_data((self.testFreq, self.testLev))
        self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
        self.canvas.draw()

    def onClickAutoButton(self):
        if self.ch2On:
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("Automatic threshold search does not work when channel 2 is ON"),
                                      QMessageBox.StandardButton.Ok)
            return
        self.testMode = 'auto'
        for f in self.testFreqs:
            self.testFreq = f
            self.curr_dir = "down"
            self.thresh_obt = False
            self.thresh = np.nan
            self.asce_levs = np.empty(shape=0)
            self.asce_n = np.empty(shape=0)
            self.asce_yes = np.empty(shape=0)
            self.asce_yes_prop = np.empty(shape=0)
            self.prevStimLev = np.inf
        
            self.ch1Tracker.set_data((self.testFreq, self.testLev))
            self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))

            for key in list(self.threshTracker.keys()):
                self.threshTracker[key].remove()
            self.threshTracker = {}
            
            self.canvas.draw()

            while self.thresh_obt == False:
                self.autoSearch()
        self.testMode = 'manual'

    def autoSearch(self):
        self.onPlayStim()
        self.onStopStim()
        if self.thresh_obt == True:
            if self.thresh == np.inf:
                self.onMarkThresh('NR')
            else:
                self.onMarkThresh('found')
        else:
            if self.resp == True:
                self.autoLevShift('up')
            else:
                self.autoLevShift('down')

    def autoLevShift(self, direction):
        if direction == "up":
            if (self.testLev - 10) >= self.trans_min[self.transducerCh1][self.testFreq]:
                self.testLev = self.testLev-10
                if self.chansLocked == True:
                    self.ch2Lev = self.ch2Lev-10
                    self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            elif (self.testLev - 5) >= self.trans_min[self.transducerCh1][self.testFreq]:
                self.testLev = self.testLev-10
                if self.chansLocked == True:
                    self.ch2Lev = self.ch2Lev-10
                    self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            else:
                self.testLev = self.testLev+5
                if self.chansLocked == True:
                    self.ch2Lev = self.ch2Lev+5
                    self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
        elif direction == "down":
            if (self.testLev + 5) <= self.trans_max[self.transducerCh1][self.testFreq]:
                self.testLev = self.testLev+5
                if self.chansLocked == True:
                    self.ch2Lev = self.ch2Lev+5
                    self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            else:
                self.testLev = self.testLev-5
                if self.chansLocked == True:
                    self.ch2Lev = self.ch2Lev-5
                    self.ch2LevTF.setText(self.currLocale.toString(self.ch2Lev))
            
        self.ch1Tracker.set_data((self.testFreq, self.testLev))
        self.ch2Tracker.set_data((self.testFreq, self.ch2Lev))
        self.canvas.draw()
        
    def onPlayStim(self):
        self.stimLight.setStatus("on")
        
    def onStopStim(self):
        self.stimLight.setStatus("off")

        if self.testEar == self.tr("Right"):
            ipsiSide = 'R'
            contraSide = 'L'
        else:
            ipsiSide = 'L'
            contraSide = 'R'

        if self.transducerCh1 == self.tr("Supra-aural"):
            transCh1 = 'supra'
        elif self.transducerCh1 == self.tr("Circum-aural"):
            transCh1 = 'circum'
        elif self.transducerCh1 == self.tr("Insert"):
            transCh1 = 'insert'
        elif self.transducerCh1 == self.tr("Bone"):
            transCh1 = 'bone'

        if self.transducerCh2 == self.tr("Supra-aural"):
            transCh2 = 'supra'
        elif self.transducerCh2 == self.tr("Circum-aural"):
            transCh2 = 'circum'
        elif self.transducerCh2 == self.tr("Insert"):
            transCh2 = 'insert'
        elif self.transducerCh2 == self.tr("Bone"):
            transCh2 = 'bone'

        v = {}
        v['IA_supra'] = self.lis.loc[self.lis['freq']==self.testFreq]['IA_supra'].values[0]
        v['IA_circum'] = self.lis.loc[self.lis['freq']==self.testFreq]['IA_circum'].values[0]
        v['IA_insert'] = self.lis.loc[self.lis['freq']==self.testFreq]['IA_insert'].values[0]
        v['IA_bone'] = self.lis.loc[self.lis['freq']==self.testFreq]['IA_bone'].values[0]
        v['OE_R_supra'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_supra'].values[0]
        v['OE_R_circum'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_circum'].values[0]
        v['OE_R_insert'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_insert'].values[0]
        v['OE_R_earplug'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_earplug'].values[0]
        v['OE_R_earmold'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_earmold'].values[0]
        v['OE_R_dome_open'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_dome_open'].values[0]
        v['OE_R_dome_tulip'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_dome_tulip'].values[0]
        v['OE_R_dome_2_vents'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_dome_2_vents'].values[0]
        v['OE_R_dome_1_vent'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_dome_1_vent'].values[0]
        v['OE_R_double_dome'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_R_double_dome'].values[0]
        v['OE_L_supra'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_supra'].values[0]
        v['OE_L_circum'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_circum'].values[0]
        v['OE_L_insert'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_insert'].values[0]
        v['OE_L_earplug'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_earplug'].values[0]
        v['OE_L_earmold'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_earmold'].values[0]
        v['OE_L_dome_open'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_dome_open'].values[0]
        v['OE_L_dome_tulip'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_dome_tulip'].values[0]
        v['OE_L_dome_2_vents'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_dome_2_vents'].values[0]
        v['OE_L_dome_1_vent'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_dome_1_vent'].values[0]
        v['OE_L_double_dome'] = self.lis.loc[self.lis['freq']==self.testFreq]['OE_L_double_dome'].values[0]
        msk_diff = self.lis.loc[self.lis['freq']==self.testFreq]['msk_diff'].values[0]

        if self.transducerCh1 != self.tr("Sound field"):
            IA = v['IA_'+transCh1]
            NTEStatus = self.NTEStatusChooser.currentText()

        if self.transducerCh2 != self.tr("Sound field"):
            IA_ch2 = v['IA_'+transCh2]
            if self.transducerCh2 != self.tr("Bone"):
                OE = v['OE_'+contraSide+'_'+transCh2]
        
        v['mdp_bone_R'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_R_mdp'].values[0]
        v['mdp_bone_L'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_L_mdp'].values[0]
        v['wdt_bone_R'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_R_wdt'].values[0]
        v['wdt_bone_L'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_L_wdt'].values[0]
        v['bone_R_FA_rate'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_R_FA_rate'].values[0]
        v['bone_R_lapse_rate'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_R_lapse_rate'].values[0]
        v['bone_L_FA_rate'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_L_FA_rate'].values[0]
        v['bone_L_lapse_rate'] = self.lis.loc[self.lis['freq']==self.testFreq]['bone_L_lapse_rate'].values[0]

        mdp_bone_ipsi = v['mdp_bone_'+ipsiSide]
        wdt_bone_ipsi = v['wdt_bone_'+ipsiSide]
        bone_ipsi_FA_rate = v['bone_'+ipsiSide+'_FA_rate']
        bone_ipsi_lapse_rate = v['bone_'+ipsiSide+'_lapse_rate']
        mdp_bone_contra = v['mdp_bone_'+contraSide]
        wdt_bone_contra = v['wdt_bone_'+contraSide]
        bone_contra_FA_rate = v['bone_'+contraSide+'_FA_rate']
        bone_contra_lapse_rate = v['bone_'+contraSide+'_lapse_rate']


        ## AIR-BONE GAP
        abg_ipsi = self.lis.loc[self.lis['freq']==self.testFreq]['abg_'+ipsiSide].values[0] 
        abg_contra   = self.lis.loc[self.lis['freq']==self.testFreq]['abg_'+contraSide].values[0] 
            
        if abg_ipsi < 0:
            abg_ipsi = 0
        if abg_contra < 0:
            abg_contra = 0

        #bone conduction attenuation limit
        BCAL = self.lis.loc[self.lis['freq']==self.testFreq]['BCAL'].values[0]


        if self.ch2On == True and NTEStatus == self.tr("Earphone on"): ##AIR-BONE GAP!
            noise_contra_cochl = self.ch2Lev - abg_contra
            noise_ipsi_cochl = self.ch2Lev - IA_ch2

        ## BONE CONDUCTION
        if self.transducerCh1 == self.tr("Bone"):
            if self.ch2On == True and NTEStatus == self.tr("Earphone on") and (noise_ipsi_cochl+msk_diff) > mdp_bone_ipsi:
                print('noise_ipsi_cochl: ' + str(noise_ipsi_cochl))
                print('noise_contra_cochl: '+ str(noise_contra_cochl))
                mdp_ipsi = noise_ipsi_cochl+msk_diff
            else:
                mdp_ipsi = mdp_bone_ipsi

            if self.ch2On == True and NTEStatus == self.tr("Earphone on") and (noise_contra_cochl+msk_diff) > mdp_bone_contra:
                print('noise_ipsi_cochl: ' + str(noise_ipsi_cochl))
                print('noise_contra_cochl: '+ str(noise_contra_cochl))
                mdp_contra = noise_contra_cochl+msk_diff
            else:
                mdp_contra = mdp_bone_contra
            
            if NTEStatus == self.tr("Uncovered"): #self.ch2On == False:
                pyes_ipsi = logisticPsyWd(self.testLev, mdp_ipsi, wdt_bone_ipsi, bone_ipsi_FA_rate, bone_ipsi_lapse_rate)
                resp_ipsi = nprand.choice([True, False], p=[pyes_ipsi, 1-pyes_ipsi])
                pyes_contra = logisticPsyWd(self.testLev-IA, mdp_contra, wdt_bone_contra, bone_contra_FA_rate, bone_contra_lapse_rate)
                resp_contra = nprand.choice([True, False], p=[pyes_contra, 1-pyes_contra])
            elif NTEStatus == self.tr("Earphone on"): #self.ch2On == True:
                pyes_ipsi = logisticPsyWd(self.testLev, mdp_ipsi, wdt_bone_ipsi, bone_ipsi_FA_rate, bone_ipsi_lapse_rate)
                resp_ipsi = nprand.choice([True, False], p=[pyes_ipsi, 1-pyes_ipsi])
                pyes_contra = logisticPsyWd(self.testLev-IA+OE, mdp_contra, wdt_bone_contra, bone_contra_FA_rate, bone_contra_lapse_rate)
                resp_contra = nprand.choice([True, False], p=[pyes_contra, 1-pyes_contra])

            print('OE: ', OE)
            print('mdp_bone_ipsi: ' + str(mdp_bone_ipsi))
            print('mdp_ipsi: ' + str(mdp_ipsi))
            print('mdp_bone_contra: ' + str(mdp_bone_contra))
            print('mdp_contra: ' + str(mdp_contra))
            print('pyes_ipsi: '+ str(pyes_ipsi))
            print('pyes_contra: '+ str(pyes_contra))
                    
        ## AIR CONDUCTION
        elif self.transducerCh1 in [self.tr("Supra-aural"), self.tr("Insert"), self.tr("Circum-aural")]:
            if self.ch2On == True and NTEStatus == self.tr("Earphone on") and (noise_ipsi_cochl+msk_diff) > mdp_bone_ipsi:
                print('noise_ipsi_cochl: ' + str(noise_ipsi_cochl))
                print('noise_contra_cochl: '+ str(noise_contra_cochl))
                mdp_ipsi = noise_ipsi_cochl+msk_diff
            else:
                mdp_ipsi = mdp_bone_ipsi

            if self.ch2On == True and NTEStatus == self.tr("Earphone on") and (noise_contra_cochl+msk_diff) > mdp_bone_contra:
                print('noise_ipsi_cochl: ' + str(noise_ipsi_cochl))
                print('noise_contra_cochl: '+ str(noise_contra_cochl))
                mdp_contra = noise_contra_cochl+msk_diff
            else:
                mdp_contra = mdp_bone_contra
                
            pyes_ipsi = logisticPsyWd(self.testLev-abg_ipsi, mdp_ipsi, wdt_bone_ipsi, bone_ipsi_FA_rate, bone_ipsi_lapse_rate)
            resp_ipsi = nprand.choice([True, False], p=[pyes_ipsi, 1-pyes_ipsi])
            pyes_contra = logisticPsyWd(self.testLev-IA, mdp_contra, wdt_bone_contra, bone_contra_FA_rate, bone_contra_lapse_rate)
            resp_contra = nprand.choice([True, False], p=[pyes_contra, 1-pyes_contra])

         
            print('mdp_bone_ipsi: ' + str(mdp_bone_ipsi))
            print('mdp_ipsi: ' + str(mdp_ipsi))
            print('mdp_bone_contra: ' + str(mdp_bone_contra))
            print('mdp_contra: ' + str(mdp_contra))
            print('pyes_ipsi: ' + str(pyes_ipsi))
            print('pyes_contra: '+ str(pyes_contra))
                    
        ## SOUND FIELD
        elif self.transducerCh1 == self.tr("Sound field"):
            gain = self.lis.loc[self.lis['freq']==self.testFreq]['gain_'+ipsiSide].values[0]
            if self.ch2On == True and NTEStatus == self.tr("Earphone on") and (noise_ipsi_cochl+msk_diff) > mdp_bone_ipsi:
                mdp_ipsi = noise_ipsi_cochl+msk_diff
            else:
                mdp_ipsi = mdp_bone_ipsi

            if self.ch2On == True and NTEStatus == self.tr("Earphone on") and (noise_contra_cochl+msk_diff) > mdp_bone_contra:
                mdp_contra = noise_contra_cochl+msk_diff
            else:
                mdp_contra = mdp_bone_contra
            
            if self.NTESFStatusChooser.currentText() == self.tr("Earplug"):
                #earplug attenuation values from Berger et al 2003, measured using thresholds,
                #not SPL in the ear canal, hence this is the maximal attenuation achievable through
                #both air and body paths, attenuation through the air path on its own may be higher
                #attenuation through the air path on its own would be the appropriate value here
                #but I don't have it
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['earplug_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_earplug']
            elif self.NTESFStatusChooser.currentText() == self.tr("Dome (open)"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['dome_open_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_dome_open']
            elif self.NTESFStatusChooser.currentText() == self.tr("Dome (tulip)"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['dome_tulip_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_dome_tulip']
            elif self.NTESFStatusChooser.currentText() == self.tr("Dome (single vent)"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['dome_1_vent_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_1_vent']
            elif self.NTESFStatusChooser.currentText() == self.tr("Dome (double vent)"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['dome_2_vents_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_dome_2_vents']
            elif self.NTESFStatusChooser.currentText() == self.tr("Double dome (power)"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['double_dome_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_double_dome']
            elif self.NTESFStatusChooser.currentText() == self.tr("Earmold"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq]['earmold_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_earmold']
            elif self.NTESFStatusChooser.currentText() == self.tr("Chan. 2"):
                amb_att = self.lis.loc[self.lis['freq']==self.testFreq][transCh2+'_amb_att'].values[0]
                OE_contra = v['OE_'+contraSide+'_'+transCh2]
            elif self.NTESFStatusChooser.currentText() == self.tr("Unaided"):
                amb_att = 0
                OE_contra = 0

            if self.TESFCouplingChooser.currentText() == self.tr("Dome (open)"):
                OE_ipsi = v['OE_'+ipsiSide+'_dome_open']
            elif self.TESFCouplingChooser.currentText() == self.tr("Dome (tulip)"):
                OE_ipsi = v['OE_'+ipsiSide+'_dome_tulip']
            elif self.TESFCouplingChooser.currentText() == self.tr("Dome (single vent)"):
                OE_ipsi = v['OE_'+ipsiSide+'_dome_1_vent']
            elif self.TESFCouplingChooser.currentText() == self.tr("Dome (double vent)"):
                OE_ipsi = v['OE_'+ipsiSide+'_dome_2_vents']
            elif self.TESFCouplingChooser.currentText() == self.tr("Double dome (power)"):
                OE_ipsi = v['OE_'+ipsiSide+'_double_dome']
            elif self.TESFCouplingChooser.currentText() == self.tr("Earmold"):
                OE_ipsi = v['OE_'+ipsiSide+'_earmold']

            if self.TESFStatusChooser.currentText() == self.tr("Unaided"):
                lev_ipsi_path_air = self.testLev - abg_ipsi
                lev_ipsi_path_body = self.testLev - BCAL
                lev_ipsi = np.max([lev_ipsi_path_air, lev_ipsi_path_body])
            elif self.TESFStatusChooser.currentText() == self.tr("Aided"):
                lev_ipsi_path_air = self.testLev + gain - abg_ipsi
                lev_ipsi_path_body = self.testLev - BCAL + OE_ipsi
                lev_ipsi = np.max([lev_ipsi_path_air, lev_ipsi_path_body])

            lev_contra_path_air = self.testLev - abg_contra - amb_att
            lev_contra_path_body = self.testLev - BCAL + OE_contra
            if self.TESFStatusChooser.currentText() == self.tr("Unaided"):
                lev_contra = np.max([lev_contra_path_air, lev_contra_path_body])
            elif self.TESFStatusChooser.currentText() == self.tr("Aided"):
                #include occl eff or consider it's already included in IA_insert value??
                lev_contra_cross = self.testLev + gain - v['IA_insert'] 
                lev_contra = np.max([lev_contra_path_air, lev_contra_path_body, lev_contra_cross])

            pyes_ipsi = logisticPsyWd(lev_ipsi, mdp_ipsi, wdt_bone_ipsi, bone_ipsi_FA_rate, bone_ipsi_lapse_rate)
            resp_ipsi = nprand.choice([True, False], p=[pyes_ipsi, 1-pyes_ipsi])
            pyes_contra = logisticPsyWd(lev_contra, mdp_contra, wdt_bone_contra, bone_contra_FA_rate, bone_contra_lapse_rate)
            resp_contra = nprand.choice([True, False], p=[pyes_contra, 1-pyes_contra])

        if self.testLev > self.prevStimLev:
            self.curr_dir = 'up'
        elif self.testLev < self.prevStimLev:
            if (resp_ipsi or resp_contra) == True:
                self.curr_dir = 'down'
            else:
                self.curr_dir = 'up'
        else:
            self.curr_dir = 'same'
        self.prevStimLev = copy.copy(self.testLev)
        st_min = self.trans_min[self.transducerCh1][self.testFreq]
        st_max = self.trans_max[self.transducerCh1][self.testFreq]
        if (resp_ipsi or resp_contra) == True:
            self.resp = True
            if self.showRespEar == False:
                self.respLight.setStatus('on')
            elif self.showRespEar == True:
                if resp_ipsi == resp_contra:
                    self.respLight.setStatus('on')
                else:
                    if self.testEar == self.tr("Right") and resp_ipsi == True:
                        self.respLight.setStatus('right')
                    elif self.testEar == self.tr("Right") and resp_contra == True:
                        self.respLight.setStatus('left')
                    elif self.testEar == self.tr("Left") and resp_ipsi == True:
                        self.respLight.setStatus('left')
                    elif self.testEar == self.tr("Left") and resp_contra == True:
                        self.respLight.setStatus('right')
                        
            if (self.curr_dir == "up") or (self.testLev==st_min):
                if (self.testLev in self.asce_levs) == False:
                    self.asce_levs = np.append(self.asce_levs, self.testLev)
                    self.asce_n = np.append(self.asce_n, 1)
                    self.asce_yes = np.append(self.asce_yes, 1)
                else:
                    idx = np.where(self.asce_levs==self.testLev)[0][0]
                    self.asce_n[idx] = self.asce_n[idx]+1
                    self.asce_yes[idx] = self.asce_yes[idx]+1
            if self.testMode == 'manual':
                time.sleep(1)
            self.respLight.setStatus('off')
            QApplication.processEvents()
        else: #no response
            self.resp = False
            if (self.curr_dir == "up") or (self.testLev==st_min):
                if (self.testLev in self.asce_levs) == False:
                    self.asce_levs = np.append(self.asce_levs, self.testLev)
                    self.asce_n = np.append(self.asce_n, 1)
                    self.asce_yes = np.append(self.asce_yes, 0)
                else:
                    idx = np.where(self.asce_levs==self.testLev)[0][0]
                    self.asce_n[idx] = self.asce_n[idx]+1

        sortidx = np.argsort(self.asce_levs)
        self.asce_levs = self.asce_levs[sortidx]
        self.asce_n = self.asce_n[sortidx]
        self.asce_yes = self.asce_yes[sortidx]
        self.asce_yes_prop = self.asce_yes/self.asce_n

        for idx in range(len(self.asce_levs)):
            if ((self.asce_n[idx] >= self.min_n_resp) and (self.asce_yes_prop[idx] >= 0.5)) or ((self.asce_n[idx] < self.min_n_resp) and (self.asce_yes[idx]/self.min_n_resp >= 0.5)):
                if self.asce_levs[idx] <= st_min:
                    self.thresh = self.asce_levs[idx]
                    self.thresh_obt = True
                if (self.asce_levs[idx]-self.step_up in self.asce_levs):
                    if ((self.asce_n[idx-1] >= self.min_n_resp) & (self.asce_yes_prop[idx-1] < 0.5)) or ((self.asce_n[idx-1] < self.min_n_resp) & ((self.asce_n[idx-1]-self.asce_yes[idx-1])/self.min_n_resp > 0.5)):
                        self.thresh = self.asce_levs[idx]
                        self.thresh_obt = True

        if (st_max in self.asce_levs):
            idx = np.where(self.asce_levs==st_max)[0][0]
            if (self.asce_n[idx] >=10) and (self.asce_yes_prop[idx] < 0.5):
                self.thresh = np.inf
                self.thresh_obt = True
        print("------------")
        print(self.asce_levs)
        print(self.asce_n)
        print(self.asce_yes_prop)
        print(self.thresh_obt)

        if self.showRespCounts == True:
            self.plotResponseCounts()
        QApplication.processEvents()
        # if self.testMode == 'manual':
        #     time.sleep(1)
        # self.respLight.setStatus('off')
        # QApplication.processEvents()
        self.mw.setFocus()

    def plotResponseCounts(self):
        for key in list(self.threshTracker.keys()):
            self.threshTracker[key].remove()
        for ln in range(len(self.asce_levs)):
            smb = '$'+str(int(self.asce_yes[ln]))+'/'+str(int(self.asce_n[ln]))+'$'
            if self.thresh_obt == True and self.thresh == self.asce_levs[ln]:
                cl = 'green'
            else:
                cl = 'black'
            self.threshTracker[self.asce_levs[ln]], = self.axes.plot(100, self.asce_levs[ln], marker=smb, color=cl, markersize=self.plotMarkerSize)#, markerfacecolor='none')
        self.canvas.draw()

    def onMarkThresh(self, thresh_status):
        if self.ch2On == True:
            msk_status = 'masked'
        else:
            msk_status = 'unmasked'

        if self.testEar == self.tr("Right"):
            ear_status = 'right'
        else:
            ear_status = 'left'

        if self.transducerCh1 == self.tr("Bone"):
            transd_status = 'bone'
        else:
            transd_status = 'air'

        idx = np.where(self.testFreqs==self.testFreq)[0][0]
        if thresh_status == "found":
            self.est_aud[msk_status][transd_status][ear_status][idx] = copy.copy(self.testLev)
        elif thresh_status == "NR":
            self.est_aud[msk_status][transd_status][ear_status][idx] = copy.copy(self.testLev)
        elif thresh_status == "MD":
            self.est_aud[msk_status][transd_status][ear_status][idx] = copy.copy(self.testLev)

        this_symb = self.symbs[msk_status][transd_status][ear_status][thresh_status]
        if thresh_status == "found":
            this_marker_size = self.plotMarkerSize
        elif thresh_status == "NR":
            this_marker_size = self.plotMarkerSizeNR
        if thresh_status == "MD":
            this_marker_size = self.plotMarkerSize
        
        if self.plot_prms[msk_status][transd_status][ear_status]['visible'][idx] == True:
            self.pnts[msk_status][transd_status][ear_status][self.testFreq].remove()
       
        self.pnts[msk_status][transd_status][ear_status][self.testFreq], = self.axes.plot(self.testFreq, self.testLev, marker=this_symb, color=self.currCh1Color, markersize=this_marker_size, markerfacecolor='none')

        self.plot_prms[msk_status][transd_status][ear_status]['visible'][idx] = True
        self.plot_prms[msk_status][transd_status][ear_status]['thresh_status'][idx] = thresh_status

        self.canvas.draw()
        self.setEstCheckBoxes(msk_status, transd_status, ear_status)

    def setEstCheckBoxes(self, msk_status, transd_status, ear_status):
        if msk_status == 'unmasked':
            if transd_status == 'air':
                if ear_status == 'right':
                    self.showEstUnmAirRCheckBox.setChecked(True)
                elif ear_status == 'left':
                    self.showEstUnmAirLCheckBox.setChecked(True)
            elif transd_status == 'bone':
                if ear_status == 'right':
                    self.showEstUnmBoneRCheckBox.setChecked(True)
                elif ear_status == 'left':
                    self.showEstUnmBoneLCheckBox.setChecked(True)
        elif msk_status == 'masked':
            if transd_status == 'air':
                if ear_status == 'right':
                    self.showEstMskAirRCheckBox.setChecked(True)
                elif ear_status == 'left':
                    self.showEstMskAirLCheckBox.setChecked(True)
            elif transd_status == 'bone':
                if ear_status == 'right':
                    self.showEstMskBoneRCheckBox.setChecked(True)
                elif ear_status == 'left':
                    self.showEstMskBoneLCheckBox.setChecked(True)

    def onClickMarkThreshButton(self):
        self.onMarkThresh("found")
        self.mw.setFocus()
        
    def onClickMarkNoResponseButton(self):
        self.onMarkThresh("NR")
        self.mw.setFocus()
        
    def onClickMarkMaskingDilemmaButton(self):
        self.onMarkThresh("MD")
        self.mw.setFocus()
        
    def plotPoints(self, msk_status, transd_status, ear_status):
        if ear_status == "right":
            currCol = "red"
        else:
            currCol = "blue"
        for i in range(len(self.est_aud[msk_status][transd_status][ear_status])):
            if np.isnan(self.est_aud[msk_status][transd_status][ear_status][i]) == False:
                this_symb = self.symbs[msk_status][transd_status][ear_status][self.plot_prms[msk_status][transd_status][ear_status]['thresh_status'][i]]
                if self.plot_prms[msk_status][transd_status][ear_status]['visible'][i] == False:
                    self.pnts[msk_status][transd_status][ear_status][self.testFreqs[i]], = self.axes.plot(self.testFreqs[i], self.est_aud[msk_status][transd_status][ear_status][i], marker=this_symb, color=currCol, markersize=self.plotMarkerSize, markerfacecolor='none')
                    self.plot_prms[msk_status][transd_status][ear_status]['visible'][i] = True

        self.canvas.draw()

    def removePoints(self, msk_status, transd_status, ear_status):
        for i in range(len(self.est_aud[msk_status][transd_status][ear_status])):
            if self.plot_prms[msk_status][transd_status][ear_status]['visible'][i] == True:
                self.pnts[msk_status][transd_status][ear_status][self.testFreqs[i]].remove()
                self.plot_prms[msk_status][transd_status][ear_status]['visible'][i] = False
        self.canvas.draw()
        
    def onDeleteThresh(self):
        if self.ch2On == True:
            msk_status = 'masked'
        else:
            msk_status = 'unmasked'

        if self.testEar == self.tr("Right"):
            ear_status = 'right'
        else:
            ear_status = 'left'

        if self.transducerCh1 == self.tr("Bone"):
            transd_status = 'bone'
        else:
            transd_status = 'air'

        if self.testFreq in self.pnts[msk_status][transd_status][ear_status]:
            self.pnts[msk_status][transd_status][ear_status][self.testFreq].remove()
            self.pnts[msk_status][transd_status][ear_status].pop(self.testFreq) #remove key from dict
            idx = np.where(self.testFreqs==self.testFreq)[0][0]
            self.est_aud[msk_status][transd_status][ear_status][idx] = np.nan
            self.plot_prms[msk_status][transd_status][ear_status]['visible'][idx] = False

            self.canvas.draw()
      
    def setBaseFigureProperties(self):
        self.fig.set_facecolor(self.canvasColor)
        self.axes.set_facecolor(self.backgroundColor)
        self.toggleGrid(None)
        self.axes.spines['bottom'].set_color(self.axesColor)
        self.axes.spines['left'].set_color(self.axesColor)
        self.axes.spines['top'].set_color(self.axesColor)
        self.axes.spines['right'].set_color(self.axesColor)
        self.axes.spines['bottom'].set_linewidth(self.spinesLineWidth)
        self.axes.spines['left'].set_linewidth(self.spinesLineWidth)
        self.axes.spines['top'].set_linewidth(self.spinesLineWidth)
        self.axes.spines['right'].set_linewidth(self.spinesLineWidth)
        for line in self.axes.yaxis.get_ticklines():
            line.set_color(self.axesColor)
            line.set_markersize(self.majorTickLength)
            line.set_markeredgewidth(self.majorTickWidth)
        for line in self.axes.xaxis.get_ticklines():
            line.set_color(self.axesColor)
            line.set_markersize(self.majorTickLength)
            line.set_markeredgewidth(self.majorTickWidth)
        for line in self.axes.yaxis.get_ticklines(minor=True):
            line.set_color(self.axesColor)
            line.set_markersize(self.minorTickLength)
            line.set_markeredgewidth(self.minorTickWidth)
        for line in self.axes.xaxis.get_ticklines(minor=True):
            line.set_color(self.axesColor)
            line.set_markersize(self.minorTickLength)
            line.set_markeredgewidth(self.minorTickWidth)
        for tick in self.axes.xaxis.get_major_ticks():
            tick.label1.set_color(self.tickLabelColor)
        for tick in self.axes.yaxis.get_major_ticks():
            tick.label1.set_color(self.tickLabelColor)
       

        for tick in self.axes.xaxis.get_major_ticks():
            tick.label1.set_family(self.tickLabelFont.get_family())
            tick.label1.set_size(self.tickLabelFont.get_size())
            tick.label1.set_weight(self.tickLabelFont.get_weight())
            tick.label1.set_style(self.tickLabelFont.get_style())
        for tick in self.axes.yaxis.get_major_ticks():
            tick.label1.set_family(self.tickLabelFont.get_family())
            tick.label1.set_size(self.tickLabelFont.get_size())
            tick.label1.set_weight(self.tickLabelFont.get_weight())
            tick.label1.set_style(self.tickLabelFont.get_style())

        self.axes.set_xlabel(self.xAxisLabel, color=self.axesLabelColor, fontproperties = self.labelFont)
        self.axes.set_ylabel(self.yAxisLabel, color=self.axesLabelColor, fontproperties = self.labelFont)
        self.canvas.draw()

    def onEditPref(self):
        dialog = preferencesDialog(self)
        if dialog.exec():
            dialog.permanentApply()
            #self.audioManager.initializeAudio()
            if dialog.markerSizeChanged:
                self.plotMarkerSize = self.prm['pref']['marker_size']
                self.plotMarkerSizeNR = self.plotMarkerSize*1.35
                if self.showEstUnmAirRCheckBox.isChecked():
                    self.removePoints('unmasked', 'air', 'right')
                    self.plotPoints('unmasked', 'air', 'right')
                if self.showEstUnmAirLCheckBox.isChecked():
                    self.removePoints('unmasked', 'air', 'left')
                    self.plotPoints('unmasked', 'air', 'left')
                if self.showEstUnmBoneRCheckBox.isChecked():
                    self.removePoints('unmasked', 'bone', 'right')
                    self.plotPoints('unmasked', 'bone', 'right')
                if self.showEstUnmBoneLCheckBox.isChecked():
                    self.removePoints('unmasked', 'bone', 'left')
                    self.plotPoints('unmasked', 'bone', 'left')

                if self.showEstMskAirRCheckBox.isChecked():
                    self.removePoints('masked', 'air', 'right')
                    self.plotPoints('masked', 'air', 'right')
                if self.showEstMskAirLCheckBox.isChecked():
                    self.removePoints('masked', 'air', 'left')
                    self.plotPoints('masked', 'air', 'left')
                if self.showEstMskBoneRCheckBox.isChecked():
                    self.removePoints('masked', 'bone', 'right')
                    self.plotPoints('masked', 'bone', 'right')
                if self.showEstMskBoneLCheckBox.isChecked():
                    self.removePoints('masked', 'bone', 'left')
                    self.plotPoints('masked', 'bone', 'left')

            if dialog.trackerSizeChanged:
                self.trackerMarkerSize = self.prm['pref']['tracker_size']
                self.ch1Tracker.remove()
                self.ch1Tracker, = self.axes.plot(self.testFreq, self.testLev, marker=self.ch1Marker, color=self.currCh1Color, markersize=self.trackerMarkerSize)
                if self.ch2OnCheckBox.isChecked():
                    self.ch2Tracker.remove()
                    self.ch2Tracker, = self.axes.plot(self.testFreq, self.ch2Lev, marker=self.ch2Marker, color=self.currCh2Color, markersize=self.trackerMarkerSize)
            self.canvas.draw()

    def onShowManualPdf(self):
        
        localized_pdf_path = os.path.abspath(self.prm['rootDirectory']) + '/doc/_build/latex_'+self.prm['locale_string'][0:2]+'/audiometry_trainer.pdf'
        if os.path.isfile(localized_pdf_path):
            fileToOpen = localized_pdf_path
        else:
            fileToOpen = os.path.abspath(self.prm['rootDirectory']) + '/doc/_build/latex/audiometry_trainer.pdf'

        QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(fileToOpen))
        
    def onShowManualHtml(self):
        localized_html_path = os.path.abspath(self.prm['rootDirectory']) + '/doc/_build/html_'+self.prm['locale_string'][0:2]+'/index.html'
        if os.path.isfile(localized_html_path):
            fileToOpen = localized_html_path
        else:
            fileToOpen = os.path.abspath(self.prm['rootDirectory']) + '/doc/_build/html/index.html'
        QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(fileToOpen))

    def onAbout(self):
        if pyqtversion in [5,6]:
            qt_compiled_ver = QtCore.QT_VERSION_STR
            qt_runtime_ver = QtCore.qVersion()
            qt_pybackend_ver = QtCore.PYQT_VERSION_STR
            qt_pybackend = "PyQt"
        QMessageBox.about(self, self.tr("About audiometry_trainer"),
                                self.tr("""<b>audiometry_trainer</b> <br>
                                - version: {0}; <br>
                                - build date: {1} <br>
                                <p> Copyright &copy; 2023-2024 Samuele Carcagno. <a href="mailto:sam.carcagno@gmail.com">sam.carcagno@gmail.com</a> 
                                All rights reserved. <p>
                This program is free software: you can redistribute it and/or modify
                it under the terms of the GNU General Public License as published by
                the Free Software Foundation, either version 3 of the License, or
                (at your option) any later version.
                <p>
                This program is distributed in the hope that it will be useful,
                but WITHOUT ANY WARRANTY; without even the implied warranty of
                MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                GNU General Public License for more details.
                <p>
                You should have received a copy of the GNU General Public License
                along with this program.  If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>
                <p>Python {2} - {3} {4} compiled against Qt {5}, and running with Qt {6} on {7}""").format(__version__, self.prm['builddate'], platform.python_version(), qt_pybackend, qt_pybackend_ver, qt_compiled_ver, qt_runtime_ver, platform.system()))


class indicatorLight(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred))
        self.borderColor = Qt.GlobalColor.red
        self.lightColor = Qt.GlobalColor.black
    def minimumSizeHint(self):
        return QtCore.QSize(25, 25)
    def setStatus(self, status):
        if status == 'left':
            self.lightColor = Qt.GlobalColor.blue
        elif status == 'right':
            self.lightColor = Qt.GlobalColor.red
        elif status == "both":
            self.lightColor = Qt.GlobalColor.white
        elif status == "on":
            self.lightColor = Qt.GlobalColor.white
        elif status == "off":
            self.lightColor = Qt.GlobalColor.black
        self.parent().repaint()
        QApplication.processEvents()
    def paintEvent(self, event=None):
        painter = QPainter(self)
        painter.setViewport(0, 0, self.width(),self.height())
        painter.setPen(self.borderColor)
        painter.setBrush(self.lightColor)
        painter.fillRect(int(self.width()/60), int(self.height()/60), self.width()-int(self.width()/30), self.height(), self.lightColor)


    # def onAxesChange(self):
    #     xmin = 0#self.currLocale.toDouble(self.xminWidget.text())[0]
    #     xmax = 8000#self.currLocale.toDouble(self.xmaxWidget.text())[0]
    #     ymin = -20 #self.currLocale.toDouble(self.yminWidget.text())[0]
    #     ymax = 140 #self.currLocale.toDouble(self.ymaxWidget.text())[0]
    #     self.axes.set_xlim((xmin, xmax))
    #     self.axes.set_ylim((ymin, ymax))
    #     self.canvas.draw()
