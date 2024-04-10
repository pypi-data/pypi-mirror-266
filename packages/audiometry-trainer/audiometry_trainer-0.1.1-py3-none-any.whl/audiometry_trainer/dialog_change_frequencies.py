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
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QGridLayout, QLabel
elif pyqtversion == 6:
    from PyQt6 import QtGui, QtCore
    from PyQt6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QGridLayout, QLabel

import numpy as np
    
class changeFrequenciesDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        
        self.currLocale = self.parent().currLocale
        grid = QGridLayout()
        n = 0
        self.standardFreqs = np.array([125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000])
        currFreqs = self.parent().freqs
        nFreqs = len(self.standardFreqs)
        self.ckb = []
        for i in range(nFreqs):
            self.ckb.append(QCheckBox(self.currLocale.toString(self.standardFreqs[i])))
            if self.standardFreqs[i] in currFreqs:
                self.ckb[i].setChecked(True)
            if self.standardFreqs[i] == 1000:
                self.ckb[i].setEnabled(False)
            grid.addWidget(self.ckb[i], n, 0)
            n = n+1
     
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|
                                     QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        grid.addWidget(buttonBox, n, 1)
        self.setLayout(grid)
        self.setWindowTitle(self.tr("Edit frequencies"))

   
