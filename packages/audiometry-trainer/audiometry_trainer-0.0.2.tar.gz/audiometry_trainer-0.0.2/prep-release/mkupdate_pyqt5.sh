#!/bin/sh

pyrcc5 -o ../audiometry_trainer/qrc_resources.py ../resources.qrc
pylupdate5 -verbose audiometry_trainer.pro
lrelease -verbose audiometry_trainer.pro

mv *.qm ../translations/
