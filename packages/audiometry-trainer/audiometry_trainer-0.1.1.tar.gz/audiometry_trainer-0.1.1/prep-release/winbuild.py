#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os

os.system("rm -r ../windows_installer/audiometry_trainer")

ver_to_build = input("Version to build: ")
os.system("tar -xvf ../dist/audiometry_trainer-"+ver_to_build+".tar.gz --directory ../windows_installer/")
os.system("mv ../windows_installer/audiometry_trainer-"+ver_to_build+ " ../windows_installer/audiometry_trainer")

os.chdir("../windows_installer/audiometry_trainer")

os.system("wine cmd /c python setup_cx.py build")

os.system("rsync -r ./build/exe.win-amd64-3.11/lib/audiometry_trainer/doc/ ./build/exe.win-amd64-3.11/doc/")
os.system("rsync -r ./build/exe.win-amd64-3.11/lib/audiometry_trainer/case_files/ ./build/exe.win-amd64-3.11/case_files/")


os.system("/usr/bin/bash ../../prep-release/win_launch_iss_compiler.sh")
