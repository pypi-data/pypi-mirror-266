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
if pyqtversion == 5:
    from PyQt5 import QtGui, QtCore, QtWidgets
    from PyQt5.QtCore import pyqtSignal, QItemSelectionModel, QLocale, Qt, QThread
    from PyQt5.QtGui import QColor, QDoubleValidator, QIntValidator
    from PyQt5.QtWidgets import QAction, QApplication, QCheckBox, QColorDialog, QComboBox, QDesktopWidget, QDialog, QDialogButtonBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSplitter, QTableView, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget
elif pyqtversion == 6:
    from PyQt6 import QtGui, QtCore, QtWidgets
    from PyQt6.QtCore import pyqtSignal, QItemSelectionModel, QLocale, Qt, QThread
    from PyQt6.QtGui import QAction, QColor, QDoubleValidator, QIntValidator
    from PyQt6.QtWidgets import QApplication, QCheckBox, QColorDialog, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMenu, QMessageBox, QProgressBar, QProgressDialog, QPushButton, QSizePolicy, QSplitter, QTableView, QTableWidget, QTableWidgetItem, QTextEdit, QVBoxLayout, QWidget

import fnmatch, os, scipy
import numpy as np
import pandas as pd
#from .utility_audiogram import*
from .hughson_westlake import*
from .acoust_values import*
from .dialog_set_value import*
from .dialog_change_frequencies import*

class generateCaseWindow(QMainWindow):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.currLocale = self.parent().prm['appData']['currentLocale']
        self.currLocale.setNumberOptions(self.currLocale.NumberOption.OmitGroupSeparator | self.currLocale.NumberOption.RejectGroupSeparator)
        
        if pyqtversion == 5:
            screen = QDesktopWidget().screenGeometry()
        elif pyqtversion == 6:
            screen = self.screen().geometry()

        self.setGeometry(0, 0, int((8/10)*screen.width()), int((6/10)*screen.height())) 
        
        self.freqs = np.array([125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000])
        self.nFreqs = len(self.freqs)
        self.seed = None

        self.menubar = self.menuBar()

        self.fileMenu = self.menubar.addMenu(self.tr('&File'))
        loadPrmAction = QAction(self.tr('Load parameters'), self)
        loadPrmAction.setStatusTip(self.tr('Load audiogram parameters'))
        loadPrmAction.triggered.connect(self.onLoadPrmFile)
        self.fileMenu.addAction(loadPrmAction)
        savePrmAction = QAction(self.tr('Save parameters'), self)
        savePrmAction.setStatusTip(self.tr('Save audiogram parameters'))
        savePrmAction.triggered.connect(self.onSavePrmFile)
        self.fileMenu.addAction(savePrmAction)
        
        self.editMenu = self.menubar.addMenu(self.tr('&Edit'))
        editFreqsAction = QAction(self.tr('Frequencies'), self)
        editFreqsAction.setStatusTip(self.tr('Add/remove audiogram frequencies'))
        editFreqsAction.triggered.connect(self.onEditFrequencies)
        self.editMenu.addAction(editFreqsAction)

        self.splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.f1=QFrame()
        self.f1.setFrameStyle(QFrame.Shape.StyledPanel|QFrame.Shadow.Sunken)
        self.f2=QFrame()
        self.f2.setFrameStyle(QFrame.Shape.StyledPanel|QFrame.Shadow.Sunken)
        
        #self.valsTableWidget = SpreadsheetWidget(freqs, self.currLocale)
        self.valsTableWidget = SpreadsheetWidget(self)


            #self.valsTableWidget.itemChanged.connect(self.validateTable)

        self.vBox_L = QVBoxLayout()
        self.grid_R = QGridLayout()
        self.grid_R.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBox_L.addWidget(self.valsTableWidget)

        n = 0
        self.runSimulationButton = QPushButton(self.tr("Run simulation"), self)
        self.grid_R.addWidget(self.runSimulationButton, n, 0, 1, 2)
        self.runSimulationButton.clicked.connect(self.onClickRunSimulationButton)
        n = n+1
        self.nSimLabel = QLabel(self.tr("No. simulations"))
        self.nSimTF = QLineEdit("1000")
        self.nSimTF.setValidator(QIntValidator(self))
        self.nSim = self.currLocale.toInt(self.nSimTF.text())[0]
        self.nSimTF.editingFinished.connect(self.onNSimChange)
        self.grid_R.addWidget(self.nSimLabel, n, 0)
        self.grid_R.addWidget(self.nSimTF, n, 1)
        n = n+1
        self.seedLabel = QLabel(self.tr("Random seed"))
        self.seedTF = QLineEdit("")
        self.seedTF.setValidator(QIntValidator(self))
        self.seed = self.currLocale.toInt(self.seedTF.text())[0]
        self.seedTF.editingFinished.connect(self.onSeedChange)
        self.grid_R.addWidget(self.seedLabel, n, 0)
        self.grid_R.addWidget(self.seedTF, n, 1)

        n = n+1
        self.caseInfoLabel = QLabel(self.tr("Case info:"))
        self.grid_R.addWidget(self.caseInfoLabel, n, 0, 1, 2)
        n = n+1
        self.caseInfoBox = QTextEdit('')
        #self.caseInfoBox.setMarkdown('')
        self.grid_R.addWidget(self.caseInfoBox, n, 0, 1, 2)

        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)
        self.progressBar.hide()
        self.progressBar.setFormat(self.tr("Simulation running. This may take a while..."))
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progressBar.setTextVisible(True)
        self.vBox_L.addWidget(self.progressBar)
        
        self.f1.setLayout(self.vBox_L)
        self.f2.setLayout(self.grid_R)
        self.splitter.addWidget(self.f1)
        self.splitter.addWidget(self.f2)
        self.splitter.setSizes([int((7/10)*screen.width()), int((1/10)*screen.width())])
        self.setCentralWidget(self.splitter)
        self.valsTableWidget.setFocus()
        self.show()

    def onClickRunSimulationButton(self):
        if self.validateTable() == True:
            ftow = QFileDialog.getSaveFileName(self, self.tr('Choose file to write results'), "", self.tr('CSV (*.csv *CSV *Csv);;All Files (*)'), "")[0]
            if len(ftow) > 0:
                if fnmatch.fnmatch(ftow, '*.csv') == False:
                    ftow = ftow + '.csv'

                if os.path.isfile(ftow[0:-4]+'_info.md'):
                    ret = QMessageBox.warning(self, self.tr("Warning"),
                                              self.tr("Case info file ") + ftow[0:-4]+"_info.md" + self.tr(" already exists, overwrite?"),
                                              QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
                    if ret == QMessageBox.StandardButton.Yes:
                        infoFileName = ftow[0:-4]+'_info.md'
                    else:
                        infoFileName = QFileDialog.getSaveFileName(self, self.tr('Choose file write case info'), "", self.tr('markdown (*.md);;All Files (*)'), "")[0]
                else:
                    infoFileName = ftow[0:-4]+'_info.md'
               

                self.progressBar.show()
                base_prm = self.cnvToDataframe()

                QApplication.processEvents()
                df = self.generateCase(base_prm, n_sim=self.nSim, seed=self.seed)
                df.to_csv(ftow, sep=',', index=False, na_rep="NA")
                if len(infoFileName)>0:
                    if fnmatch.fnmatch(infoFileName, '*.md') == False:
                        infoFileName = infoFileName + '.md'
                    self.caseInfo = self.caseInfoBox.toPlainText()
                    hnl = open(infoFileName, 'w')
                    hnl.write(self.caseInfo)
                    hnl.close()
                
                self.progressBar.hide()
                self.progressBar.setValue(0)
                
    def validateTable(self):
        nRows = self.valsTableWidget.rowCount()
        nCols = self.valsTableWidget.columnCount()
        tableValid = True
        v = QDoubleValidator(); pos = 0
        for col in range(nCols):
            for row in range(nRows):
                val = self.currLocale.toDouble(self.valsTableWidget.item(row, col).text())[0]
                if pyqtversion == 5:
                    if v.validate(self.valsTableWidget.item(row, col).text(), pos)[0] != 2:
                        tableValid = False
                        index = self.valsTableWidget.model().index(row, col)
                        self.valsTableWidget.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Current)

                        QMessageBox.warning(self, self.tr('Warning'), self.tr('Invalid entry in cell['+ str(row+1)+','+str(col+1)+']'))
                        return tableValid
                elif pyqtversion == 6:
                    if v.validate(self.valsTableWidget.item(row, col).text(), pos)[0].value != 2:
                        tableValid = False
                        index = self.valsTableWidget.model().index(row, col)
                        self.valsTableWidget.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Current)

                        QMessageBox.warning(self, self.tr('Warning'), self.tr('Invalid entry in cell[')+ str(row+1)+','+str(col+1)+']')
                        return tableValid
                if col in [1, 7]:
                    if val <= 0:
                        QMessageBox.warning(self, self.tr('Warning'), self.tr('Invalid entry in cell[')+ str(row+1)+','+str(col+1)+self.tr(']. Psychometric function width must be positive!'))
                        tableValid = False
                        return tableValid
                if col in [2, 8]:
                    if val < 0:
                        QMessageBox.warning(self, self.tr('Warning'), self.tr('Invalid entry in cell[')+ str(row+1)+','+str(col+1)+self.tr(']. Air-bone gap must be >= 0!'))
                        tableValid = False
                        return tableValid
                if col in [3, 9]:
                    if val < 0 or val > 1:
                        QMessageBox.warning(self, self.tr('Warning'), self.tr('Invalid entry in cell[')+ str(row+1)+','+str(col+1)+self.tr(']. False alarm rate must be between 0 and 1!'))
                        tableValid = False
                        return tableValid
                if col in [4, 10]:
                    if val < 0 or val > 1:
                        QMessageBox.warning(self, self.tr('Warning'), self.tr('Invalid entry in cell[')+ str(row+1)+','+str(col+1)+self.tr(']. Lapse rate must be between 0 and 1!'))
                        tableValid = False
                        return tableValid

        return tableValid

    def cnvToDataframe(self):
        nFreqs = self.nFreqs
        bone_R_mdp = np.zeros(nFreqs)
        bone_R_wdt = np.zeros(nFreqs)
        abg_R = np.zeros(nFreqs)
        FA_rate_R = np.zeros(nFreqs)
        lapse_rate_R = np.zeros(nFreqs)
        gain_R = np.zeros(nFreqs)
        bone_L_mdp = np.zeros(nFreqs)
        bone_L_wdt = np.zeros(nFreqs)
        abg_L = np.zeros(nFreqs)
        FA_rate_L = np.zeros(nFreqs)
        lapse_rate_L = np.zeros(nFreqs)
        gain_L = np.zeros(nFreqs)

        for r in range(nFreqs):
            bone_R_mdp[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 0).text())[0]
            bone_R_wdt[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 1).text())[0]
            abg_R[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 2).text())[0]
            FA_rate_R[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 3).text())[0]
            lapse_rate_R[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 4).text())[0]
            gain_R[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 5).text())[0]
            bone_L_mdp[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 6).text())[0]
            bone_L_wdt[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 7).text())[0]
            abg_L[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 8).text())[0]
            FA_rate_L[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 9).text())[0]
            lapse_rate_L[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 10).text())[0]
            gain_L[r] = self.currLocale.toDouble(self.valsTableWidget.item(r, 11).text())[0]
        
        df = pd.DataFrame()
        df['freq'] = self.freqs
        df['bone_R_mdp'] = bone_R_mdp
        df['bone_R_wdt'] = bone_R_wdt
        df['abg_R'] = abg_R
        df['FA_rate_R'] = FA_rate_R
        df['lapse_rate_R'] = lapse_rate_R
        df['gain_R'] = gain_R
        df['bone_L_mdp'] = bone_L_mdp
        df['bone_L_wdt'] = bone_L_wdt
        df['abg_L'] = abg_L
        df['FA_rate_L'] = FA_rate_L
        df['lapse_rate_L'] = lapse_rate_L
        df['gain_L'] = gain_L

        return df

    def onLoadPrmFile(self):
        fName = QFileDialog.getOpenFileName(self, self.tr("Choose parameters file to load"), '~/', self.tr("All Files (*)"))[0]
        if len(fName) > 0: #if the user didn't press cancel
            df = pd.read_csv(fName, delimiter = ',')
            prmFreqs = np.array(df['freq'])
            for f in self.freqs:
                if f not in prmFreqs:
                    self.valsTableWidget.removeFrequency(f)
            for f in prmFreqs:
                if f not in self.freqs:
                    self.valsTableWidget.addFrequency(f)
            self.freqs = self.valsTableWidget.freqs = np.array(df['freq'])
            self.nFreqs = self.valsTableWidget.nFreqs = len(self.freqs)
            for r in range(len(self.freqs)):
                self.valsTableWidget.item(r, 0).setText(self.currLocale.toString(df['bone_R_mdp'][r]))
                self.valsTableWidget.item(r, 1).setText(self.currLocale.toString(df['bone_R_wdt'][r]))
                self.valsTableWidget.item(r, 2).setText(self.currLocale.toString(df['abg_R'][r]))
                self.valsTableWidget.item(r, 3).setText(self.currLocale.toString(df['FA_rate_R'][r]))
                self.valsTableWidget.item(r, 4).setText(self.currLocale.toString(df['lapse_rate_R'][r]))
                self.valsTableWidget.item(r, 5).setText(self.currLocale.toString(df['gain_R'][r]))
                self.valsTableWidget.item(r, 6).setText(self.currLocale.toString(df['bone_L_mdp'][r]))
                self.valsTableWidget.item(r, 7).setText(self.currLocale.toString(df['bone_L_wdt'][r]))
                self.valsTableWidget.item(r, 8).setText(self.currLocale.toString(df['abg_L'][r]))
                self.valsTableWidget.item(r, 9).setText(self.currLocale.toString(df['FA_rate_L'][r]))
                self.valsTableWidget.item(r, 10).setText(self.currLocale.toString(df['lapse_rate_L'][r]))
                self.valsTableWidget.item(r, 11).setText(self.currLocale.toString(df['gain_L'][r]))

            if os.path.isfile(fName[0:-4]+'_info'+'.md'):
                fHnl = open(fName[0:-4]+'_info'+'.md', 'r')
                caseInfo = fHnl.read()
                fHnl.close()
                self.caseInfoBox.setText(caseInfo)

    def onSavePrmFile(self):
        if self.validateTable() == True:
            ftow = QFileDialog.getSaveFileName(self, self.tr('Choose file to write parameters'), "", self.tr('CSV (*.csv *CSV *Csv);;All Files (*)'), "")[0]
            if len(ftow) > 0:
                if fnmatch.fnmatch(ftow, '*.csv') == False:
                    ftow = ftow + '.csv'
                df = self.cnvToDataframe()
                df.to_csv(ftow, sep=',', index=False)

                self.caseInfo = self.caseInfoBox.toPlainText()
                infoFileName = ''
                if os.path.isfile(ftow[0:-4]+'_info.md'):
                    ret = QMessageBox.warning(self, self.tr("Warning"),
                                              self.tr("Case info file " + ftow[0:-4]+"_info.md" + " already exists, overwrite?"),
                                              QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No)
                    if ret == QMessageBox.StandardButton.Yes:
                        infoFileName = ftow[0:-4]+'_info.md'
                    else:
                        infoFileName = QFileDialog.getSaveFileName(self, self.tr('Choose file write case info'), "", self.tr('markdown (*.md);;All Files (*)'), "")[0]
                else:
                    infoFileName = ftow[0:-4]+'_info.md'
                if len(infoFileName)>0:
                    if fnmatch.fnmatch(infoFileName, '*.md') == False:
                        infoFileName = infoFileName + '.md'
                    hnl = open(infoFileName, 'w')
                    hnl.write(self.caseInfo)
                    hnl.close()

    def onNSimChange(self):
        if self.nSim <=0:
            ret = QMessageBox.warning(self, self.tr("Warning"),
                                      self.tr("The number of simulations must be > 0"),
                                      QMessageBox.StandardButton.Ok)
            self.nSimTF.setText(self.currLocale.toString(1000))
            self.nSim = 1000
        else:
            self.nSim = self.currLocale.toInt(self.nSimTF.text())[0]
            
        return

    def onSeedChange(self):
        if self.seedTF.text() == "":
            self.seed = None
        else:
            self.seed = self.currLocale.toInt(self.seedTF.text())[0]

    def onEditFrequencies(self):
        diag = changeFrequenciesDialog(self)
        if diag.exec():
            for i in range(len(diag.standardFreqs)):
                if diag.ckb[i].isChecked() == False and diag.standardFreqs[i] in self.freqs:
                    self.valsTableWidget.removeFrequency(diag.standardFreqs[i])
                elif diag.ckb[i].isChecked() == True and diag.standardFreqs[i] not in self.freqs:
                    self.valsTableWidget.addFrequency(diag.standardFreqs[i])
            self.freqs = self.valsTableWidget.freqs; self.nFreqs = self.valsTableWidget.nFreqs


    def generateCase(self, base_prm, n_sim=1000, st_min=-20, st_max=120, step_up=5, step_down=10,
                     min_n_resp=3, seed=None):

        rng = np.random.default_rng(seed=seed)
        
        freqs = base_prm['freq']
        lbls = ['bone_R', 'bone_L', 'air_R', 'air_L']
        lsprm = {}
        for lbl in lbls:
            lsprm[lbl] = {}
            lsprm[lbl]['freq'] = np.array(freqs)
            lsprm[lbl]['FA_rate_R'] = np.array(base_prm['FA_rate_R'])
            lsprm[lbl]['lapse_rate_R'] = np.array(base_prm['lapse_rate_R'])
            lsprm[lbl]['FA_rate_L'] = np.array(base_prm['FA_rate_L'])
            lsprm[lbl]['lapse_rate_L'] = np.array(base_prm['lapse_rate_L'])

        lsprm['air_R']['mdp'] = np.array(base_prm['bone_R_mdp'] + base_prm['abg_R'])
        lsprm['air_L']['mdp'] = np.array(base_prm['bone_L_mdp'] + base_prm['abg_L'])
        lsprm['bone_R']['mdp'] = np.array(base_prm['bone_R_mdp'])
        lsprm['bone_L']['mdp'] = np.array(base_prm['bone_L_mdp'])
        lsprm['air_R']['wdt'] = np.array(base_prm['bone_R_wdt'])
        lsprm['air_L']['wdt'] = np.array(base_prm['bone_L_wdt'])
        lsprm['bone_R']['wdt'] = np.array(base_prm['bone_R_wdt'])
        lsprm['bone_L']['wdt'] = np.array(base_prm['bone_L_wdt'])
   

        lsres = {}
        cnt = 1
        for lbl in lbls:
            cnt = cnt+1
            lsres[lbl] = {}

            if lbl in ['air_R', 'bone_R']:
                this_FA_rate = base_prm['FA_rate_R']
                this_lapse_rate = base_prm['lapse_rate_R']
            else:
                this_FA_rate = base_prm['FA_rate_L']
                this_lapse_rate = base_prm['lapse_rate_L']

            resmat = simulate_audiogram(lsprm[lbl]['freq'], lsprm[lbl]['mdp'], lsprm[lbl]['wdt'],
                                        this_FA_rate, this_lapse_rate, st_min=st_min,
                                        st_max=st_max, step_up=step_up, step_down=step_down, 
                                        min_n_resp=min_n_resp, n_sim=n_sim)

            self.progressBar.setValue(int(cnt/len(lbls)*100))
            QApplication.processEvents()

            p_mid=np.zeros(len(lsprm[lbl]['freq']))
            p_lo=np.zeros(len(lsprm[lbl]['freq']))
            p_hi=np.zeros(len(lsprm[lbl]['freq']))
            for i in range(len(lsprm[lbl]['freq'])):
                p_mid[i] = scipy.stats.scoreatpercentile(resmat[:,i], 50)
                p_lo[i] = scipy.stats.scoreatpercentile(resmat[:,i], 2.5)
                p_hi[i] = scipy.stats.scoreatpercentile(resmat[:,i], 97.5)
                lsres[lbl]['perc50'] = p_mid
                lsres[lbl]['perc2.5'] = p_lo
                lsres[lbl]['perc97.5'] = p_hi

        OE_supra, OE_circum, OE_insert, OE_earplug, OE_earmold, OE_dome_open, OE_dome_tulip, OE_dome_2_vents, OE_dome_1_vent, OE_double_dome, supra_amb_att, circum_amb_att, insert_amb_att, earplug_att, earmold_att, dome_open_att, dome_tulip_att, dome_2_vents_att, dome_1_vent_att, double_dome_att, IA_supra, IA_insert, IA_circum, IA_bone, BCAL = acoust_values(seed=seed)

        df = pd.DataFrame()
        df['freq'] = lsprm['air_R']['freq']
        
        for lbl in ['bone_R', 'bone_L']:
            df[lbl+'_mdp']=lsprm[lbl]['mdp']
            df[lbl+'_wdt']=lsprm[lbl]['wdt']
            if lbl == 'bone_R':
                df[lbl+'_FA_rate']=lsprm[lbl]['FA_rate_R']
                df[lbl+'_lapse_rate']=lsprm[lbl]['lapse_rate_R']
            else:
                df[lbl+'_FA_rate']=lsprm[lbl]['FA_rate_L']
                df[lbl+'_lapse_rate']=lsprm[lbl]['lapse_rate_L']
        
        for lbl in lbls:
            df[lbl+'_perc50']=lsres[lbl]['perc50']
            df[lbl+'_perc2.5']=lsres[lbl]['perc2.5']
            df[lbl+'_perc97.5']=lsres[lbl]['perc97.5']

        df['gain_R'] = base_prm['gain_R']
        df['gain_L'] = base_prm['gain_L']
        df['abg_R'] = base_prm['abg_R']
        df['abg_L'] = base_prm['abg_L']

        OE_R_supra_arr = np.zeros(len(freqs))
        OE_R_circum_arr = np.zeros(len(freqs))
        OE_R_insert_arr = np.zeros(len(freqs))
        OE_R_earplug_arr = np.zeros(len(freqs))
        OE_R_earmold_arr = np.zeros(len(freqs))
        OE_R_dome_open_arr = np.zeros(len(freqs))
        OE_R_dome_tulip_arr = np.zeros(len(freqs))
        OE_R_dome_2_vents_arr = np.zeros(len(freqs))
        OE_R_dome_1_vent_arr = np.zeros(len(freqs))
        OE_R_double_dome_arr = np.zeros(len(freqs))
        
        OE_L_supra_arr = np.zeros(len(freqs))
        OE_L_circum_arr = np.zeros(len(freqs))
        OE_L_insert_arr = np.zeros(len(freqs))
        OE_L_earplug_arr = np.zeros(len(freqs))
        OE_L_earmold_arr = np.zeros(len(freqs))
        OE_L_dome_open_arr = np.zeros(len(freqs))
        OE_L_dome_tulip_arr = np.zeros(len(freqs))
        OE_L_dome_2_vents_arr = np.zeros(len(freqs))
        OE_L_dome_1_vent_arr = np.zeros(len(freqs))
        OE_L_double_dome_arr = np.zeros(len(freqs))
        
        IA_supra_arr = np.zeros(len(freqs))
        IA_circum_arr = np.zeros(len(freqs))
        IA_insert_arr = np.zeros(len(freqs))
        IA_bone_arr = np.zeros(len(freqs))
        BCAL_arr = np.zeros(len(freqs))
        earplug_att_arr = np.zeros(len(freqs))
        supra_amb_att_arr = np.zeros(len(freqs))
        circum_amb_att_arr = np.zeros(len(freqs))
        insert_amb_att_arr = np.zeros(len(freqs))
        dome_open_att_arr = np.zeros(len(freqs))
        dome_tulip_att_arr = np.zeros(len(freqs))
        dome_2_vents_att_arr = np.zeros(len(freqs))
        dome_1_vent_att_arr = np.zeros(len(freqs))
        double_dome_att_arr = np.zeros(len(freqs))
        earmold_att_arr = np.zeros(len(freqs))

        for i in range(len(freqs)):
            abg_R = df['abg_R'][i] 
            abg_L = df['abg_L'][i] 
            if abg_R >=20:
                OE_R_supra_arr[i] = 0
                OE_R_circum_arr[i] = 0
                OE_R_insert_arr[i] = 0
                OE_R_earplug_arr[i] = 0
                OE_R_earmold_arr[i] = 0
                OE_R_dome_open_arr[i] = 0 
                OE_R_dome_tulip_arr[i] = 0
                OE_R_dome_2_vents_arr[i] = 0
                OE_R_dome_1_vent_arr[i] = 0
                OE_R_double_dome_arr[i] = 0
            else:
                OE_R_supra_arr[i] = OE_supra[freqs[i]] - OE_supra[freqs[i]] * (abg_R/20)
                OE_R_circum_arr[i] = OE_circum[freqs[i]] - OE_circum[freqs[i]] * (abg_R/20)
                OE_R_insert_arr[i] = OE_insert[freqs[i]] - OE_insert[freqs[i]] * (abg_R/20)
                OE_R_earplug_arr[i] = OE_earplug[freqs[i]] - OE_earplug[freqs[i]] * (abg_R/20)
                OE_R_earmold_arr[i] = OE_earmold[freqs[i]] - OE_earmold[freqs[i]] * (abg_R/20)
                OE_R_dome_open_arr[i] = OE_dome_open[freqs[i]] - OE_dome_open[freqs[i]] * (abg_R/20)
                OE_R_dome_tulip_arr[i] = OE_dome_tulip[freqs[i]] - OE_dome_tulip[freqs[i]] * (abg_R/20)
                OE_R_dome_2_vents_arr[i] = OE_dome_2_vents[freqs[i]] - OE_dome_2_vents[freqs[i]] * (abg_R/20)
                OE_R_dome_1_vent_arr[i] = OE_dome_1_vent[freqs[i]] - OE_dome_1_vent[freqs[i]] * (abg_R/20)
                OE_R_double_dome_arr[i] = OE_double_dome[freqs[i]] - OE_double_dome[freqs[i]] * (abg_R/20)

            if abg_L >=20:
                OE_L_supra_arr[i] = 0
                OE_L_circum_arr[i] = 0
                OE_L_insert_arr[i] = 0
                OE_L_earplug_arr[i] = 0
                OE_L_earmold_arr[i] = 0
                OE_L_dome_open_arr[i] = 0 
                OE_L_dome_tulip_arr[i] = 0
                OE_L_dome_2_vents_arr[i] = 0 
                OE_L_dome_1_vent_arr[i] = 0
                OE_L_double_dome_arr[i] = 0
            else:
                OE_L_supra_arr[i] = OE_supra[freqs[i]] - OE_supra[freqs[i]] * (abg_L/20)
                OE_L_circum_arr[i] = OE_circum[freqs[i]] - OE_circum[freqs[i]] * (abg_L/20)
                OE_L_insert_arr[i] = OE_insert[freqs[i]] - OE_insert[freqs[i]] * (abg_L/20)
                OE_L_earplug_arr[i] = OE_earplug[freqs[i]] - OE_earplug[freqs[i]] * (abg_R/20)
                OE_L_earmold_arr[i] = OE_earmold[freqs[i]] - OE_earmold[freqs[i]] * (abg_R/20)
                OE_L_dome_open_arr[i] = OE_dome_open[freqs[i]] - OE_dome_open[freqs[i]] * (abg_R/20)
                OE_L_dome_tulip_arr[i] = OE_dome_tulip[freqs[i]] - OE_dome_tulip[freqs[i]] * (abg_R/20)
                OE_L_dome_2_vents_arr[i] = OE_dome_2_vents[freqs[i]] - OE_dome_2_vents[freqs[i]] * (abg_R/20)
                OE_L_dome_1_vent_arr[i] = OE_dome_1_vent[freqs[i]] - OE_dome_1_vent[freqs[i]] * (abg_R/20)
                OE_L_double_dome_arr[i] = OE_double_dome[freqs[i]] - OE_double_dome[freqs[i]] * (abg_R/20)

            IA_supra_arr[i] = IA_supra[freqs[i]]
            IA_circum_arr[i] = IA_circum[freqs[i]]
            IA_insert_arr[i] = IA_insert[freqs[i]]
            IA_bone_arr[i] = IA_bone[freqs[i]]
            BCAL_arr[i] = BCAL[freqs[i]]
            earplug_att_arr[i] = earplug_att[freqs[i]]
            supra_amb_att_arr[i] = supra_amb_att[freqs[i]]
            circum_amb_att_arr[i] = circum_amb_att[freqs[i]]
            insert_amb_att_arr[i] = insert_amb_att[freqs[i]]
            dome_open_att_arr[i] = dome_open_att[freqs[i]]
            dome_tulip_att_arr[i] = dome_tulip_att[freqs[i]]
            dome_2_vents_att_arr[i] = dome_2_vents_att[freqs[i]]
            dome_1_vent_att_arr[i] = dome_1_vent_att[freqs[i]]
            double_dome_att_arr[i] = double_dome_att[freqs[i]]
            earmold_att_arr[i] = earmold_att[freqs[i]]

        df['OE_R_supra'] = OE_R_supra_arr
        df['OE_R_circum'] = OE_R_circum_arr
        df['OE_R_insert'] = OE_R_insert_arr
        df['OE_R_earplug'] = OE_R_earplug_arr
        df['OE_R_earmold'] = OE_R_earmold_arr
        df['OE_R_dome_open'] = OE_R_dome_open_arr
        df['OE_R_dome_tulip'] = OE_R_dome_tulip_arr
        df['OE_R_dome_2_vents'] = OE_R_dome_2_vents_arr
        df['OE_R_dome_1_vent'] = OE_R_dome_1_vent_arr
        df['OE_R_double_dome'] = OE_R_double_dome_arr
        df['OE_L_supra'] = OE_L_supra_arr
        df['OE_L_circum'] = OE_L_circum_arr
        df['OE_L_insert'] = OE_L_insert_arr
        df['OE_L_earplug'] = OE_L_earplug_arr
        df['OE_L_earmold'] = OE_L_earmold_arr
        df['OE_L_dome_open'] = OE_L_dome_open_arr
        df['OE_L_dome_tulip'] = OE_L_dome_tulip_arr
        df['OE_L_dome_2_vents'] = OE_L_dome_2_vents_arr
        df['OE_L_dome_1_vent'] = OE_L_dome_1_vent_arr
        df['OE_L_double_dome'] = OE_L_double_dome_arr
        
        df['IA_supra'] = IA_supra_arr
        df['IA_circum'] = IA_circum_arr
        df['IA_insert'] = IA_insert_arr
        df['IA_bone'] = IA_bone_arr
        df['msk_diff'] = rng.normal(loc=0.0, scale=3, size=len(freqs))
        df['cnt_msk'] = rng.uniform(low=0.0, high=12, size=len(freqs))
        df['BCAL'] = BCAL_arr
        df['earplug_att'] = earplug_att_arr
        df['supra_amb_att'] = supra_amb_att_arr
        df['circum_amb_att'] = circum_amb_att_arr
        df['insert_amb_att'] = insert_amb_att_arr
        df['dome_open_att'] = dome_open_att_arr
        df['dome_tulip_att'] = dome_tulip_att_arr
        df['dome_2_vents_att'] = dome_2_vents_att_arr
        df['dome_1_vent_att'] = dome_1_vent_att_arr
        df['double_dome_att'] = double_dome_att_arr
        df['earmold_att'] = earmold_att_arr

        return df         
        
class SpreadsheetWidget(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        #QTableWidget.__init__(self, parent)
        self.freqs = self.parent().freqs
        self.nFreqs = len(self.parent().freqs)
        self.currLocale = self.parent().currLocale
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setColumnCount(12)
        self.setRowCount(self.nFreqs)
        self.setHorizontalHeaderLabels([self.tr('Bone R mdp'),
                                        self.tr('Bone R width'),
                                        self.tr('ABG R'),
                                        self.tr('F. A. rate R'),
                                        self.tr('Lapse rate R'),
                                        self.tr('Gain R'),
                                        self.tr('Bone L mdp'),
                                        self.tr('Bone L width'),
                                         self.tr('ABG L'),
                                        self.tr('F. A. rate L'),
                                        self.tr('Lapse rate L'),
                                        self.tr('Gain L')
                                        ])
        self.setVerticalHeaderLabels(['125 Hz',
                                      '250 Hz',
                                      '500 Hz',
                                      '750 Hz',
                                      '1000 Hz',
                                      '1500 Hz',
                                      '2000 Hz',
                                      '3000 Hz',
                                      '4000 Hz',
                                      '6000 Hz',
                                      '8000 Hz'
                                      ])


        for i in range(self.nFreqs):
            self.initializeRow(i)
         
    def initializeRow(self, rowN):
        newItem = QTableWidgetItem('0')
        self.setItem(rowN, 0, newItem)

        newItem = QTableWidgetItem('5')
        self.setItem(rowN, 1, newItem)

        newItem = QTableWidgetItem('0')
        self.setItem(rowN, 2, newItem)

        newItem = QTableWidgetItem(self.currLocale.toString(0.01))
        self.setItem(rowN, 3, newItem)

        newItem = QTableWidgetItem(self.currLocale.toString(0.01))
        self.setItem(rowN, 4, newItem)

        newItem = QTableWidgetItem('0')
        self.setItem(rowN, 5, newItem)

        newItem = QTableWidgetItem('0')
        self.setItem(rowN, 6, newItem)

        newItem = QTableWidgetItem('5')
        self.setItem(rowN, 7, newItem)

        newItem = QTableWidgetItem('0')
        self.setItem(rowN, 8, newItem)

        newItem = QTableWidgetItem(self.currLocale.toString(0.01))
        self.setItem(rowN, 9, newItem)

        newItem = QTableWidgetItem(self.currLocale.toString(0.01))
        self.setItem(rowN, 10, newItem)

        newItem = QTableWidgetItem('0')
        self.setItem(rowN, 11, newItem)
    
    def keyPressEvent(self, event: QtGui.QKeyEvent):
        # if event.key() == Qt.Key.Key_Return:
        #      col = self.currentColumn()
        #      row = self.currentRow()
        #      model = self.model()
        #      index = model.index(row+1, col)
        #      self.setCurrentIndex(index)
        #      self.setCurrentCell(row + 1, col)
        if event.matches(QtGui.QKeySequence.StandardKey.Copy):
            self.copyOrCutCells(cut=False)
        elif event.matches(QtGui.QKeySequence.StandardKey.Cut):
            self.copyOrCutCells(cut=True)
        elif event.matches(QtGui.QKeySequence.StandardKey.Paste):
            self.pasteCells()
        else:
            QTableWidget.keyPressEvent(self, event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        copyAction = menu.addAction(self.tr("Copy"))
        cutAction = menu.addAction(self.tr("Cut"))
        pasteAction = menu.addAction(self.tr("Paste"))
        setValueAction = menu.addAction(self.tr("Set value"))
        # removeRowAction = menu.addAction(self.tr("Remove row"))
        # addRowAction = menu.addAction(self.tr("Add row"))
        action = menu.exec(self.mapToGlobal(event.pos()))
        if action == copyAction:
            self.copyOrCutCells(cut=False)
        elif action == cutAction:
            self.copyOrCutCells(cut=True)
        elif action == pasteAction:
            self.pasteCells()
        elif action == setValueAction:
            diag = setValueDialog(self)
            if diag.exec():
                val = diag.TF.text()
                selRows = self.findSelectedItemRows()
                selCols = self.findSelectedItemColumns()
                for i in range(len(selRows)):
                    self.item(selRows[i], selCols[i]).setText(val)

    def addFrequency(self, freq):
        if len(np.where(self.freqs > freq)[0]) > 0:
            newRowIdx = np.where(self.freqs > freq)[0][0]
        else:
            newRowIdx = self.nFreqs
        self.insertRow(newRowIdx)
        self.initializeRow(newRowIdx)
        self.freqs = np.sort(np.append(self.freqs, freq))
        self.nFreqs = self.nFreqs + 1
        self.setVerticalHeaderLabels([str(f) + ' Hz' for f in self.freqs])

    def removeFrequency(self, freq):
        idx = np.where(self.freqs == freq)[0][0]
        self.removeRow(idx)
        self.freqs = np.delete(self.freqs, idx)
        self.nFreqs = self.nFreqs - 1
                    
    def findSelectedItemRows(self):
        selItems = self.selectedItems()
        selItemsRows = []
        for i in range(len(selItems)):
            selItemsRows.append(selItems[i].row())
        return selItemsRows

    def findSelectedItemColumns(self):
        selItems = self.selectedItems()
        selItemsColumns = []
        for i in range(len(selItems)):
            selItemsColumns.append(selItems[i].column())
        return selItemsColumns

    def copyOrCutCells(self, cut=False):
        clipboard = QApplication.clipboard()
        currCol = self.currentColumn()
        currRow = self.currentRow()
        selRows = self.findSelectedItemRows()
        selCols = self.findSelectedItemColumns()
        minRow = np.min(selRows); maxRow = np.max(selRows)
        minCol = np.min(selCols); maxCol = np.max(selCols)
        nRows = maxRow-minRow +1
        nCols = maxCol-minCol +1
        l = [['\t' for c in range(nCols)] for r in range(nRows)]
        for i in range(len(selRows)):
            r = selRows[i]
            c = selCols[i]
            l[r-minRow][c-minCol] = self.item(r, c).text() +'\t'

        for i in range(len(l)):
            for j in range(len(l[i])):
                if j == (len(l[i])-1):
                    l[i][j] = l[i][j].split('\t')[0]
        q = []
        for i in range(len(l)):
            q.append(''.join(l[i]))
        out = '\n'.join(q)+'\n'
        clipboard.setText(out)
        if cut==True:
            for i in range(len(selRows)):
                r = selRows[i]
                c = selCols[i]
                self.item(r, c).setText('')
    def pasteCells(self):
        clipboard = QApplication.clipboard()
        currCol = self.currentColumn()
        currRow = self.currentRow()
        txt = clipboard.text()
        if len(txt) > 0:
            lns = txt.split('\n')
            lns.pop()
            n_lines = len(lns)
            for i in range(n_lines):
                if currRow + i <= self.rowCount():
                    wrds = lns[i].split('\t')
                    for j in range(len(wrds)):
                        if currCol + j <= self.columnCount():
                            self.item(currRow+i, currCol+j).setText(wrds[j].strip())



class Worker(QThread):
    updateValueSignal = pyqtSignal(int)

    def __init__(self, base_prm, nSim, ftow):
        super().__init__()
        self.base_prm = base_prm
        self.nSim = nSim
        self.ftow = ftow

    def run(self):
        """
        The thread begins running from here. run() is only called after start().
        """
        df = generateCase(self.base_prm, n_sim=self.nSim, seed=self.seed)
        df.to_csv(self.ftow, sep=',', index=False, na_rep="NA")

        #self.updateValueSignal.emit(i + 1)

        
# class applyChanges(QDialog):
#     def __init__(self, parent):
#         QDialog.__init__(self, parent)
#         grid = QGridLayout()
#         n = 0
#         label = QLabel(self.tr('There are unsaved changes. Apply Changes?'))
#         grid.addWidget(label, n, 1)
#         n = n+1
#         buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|
#                                      QDialogButtonBox.StandardButton.Cancel)
#         buttonBox.accepted.connect(self.accept)
#         buttonBox.rejected.connect(self.reject)
#         grid.addWidget(buttonBox, n, 1)
#         self.setLayout(grid)
#         self.setWindowTitle(self.tr("Apply Changes"))
