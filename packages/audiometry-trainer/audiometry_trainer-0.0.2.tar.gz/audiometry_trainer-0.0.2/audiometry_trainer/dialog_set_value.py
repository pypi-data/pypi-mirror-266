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
    from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit
elif pyqtversion == 6:
    from PyQt6 import QtGui, QtCore
    from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QGridLayout, QLabel, QLineEdit
    
class setValueDialog(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)

        grid = QGridLayout()
        n = 0
        self.TFLabel = QLabel(self.tr('Value: '))
        self.TF = QLineEdit('')
        grid.addWidget(self.TFLabel, n, 0)
        grid.addWidget(self.TF, n, 1)
        n = n+1
     
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|
                                     QDialogButtonBox.StandardButton.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        grid.addWidget(buttonBox, n, 1)
        self.setLayout(grid)
        self.setWindowTitle(self.tr("Set Value"))

   
