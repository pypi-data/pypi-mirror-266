#!/bin/sh

. /home/sam/bin/ppyenv/bin/activate
read -p 'pyqtver: ' pyqtver
python3 switch_pyqt$pyqtver.py
#./mkupdate_pyqt$pyqtver.sh
cd ../audiometry_trainer/doc
./mkdoc.sh
cd ../../prep-release
cd ..
python3 -m build
