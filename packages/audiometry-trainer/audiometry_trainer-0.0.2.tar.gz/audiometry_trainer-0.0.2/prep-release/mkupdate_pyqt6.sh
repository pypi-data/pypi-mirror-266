#!/usr/bin/env bash

pylupdate6 --verbose --ts audiometry_trainer_en_GB.ts --ts audiometry_trainer_es.ts --ts audiometry_trainer_fr.ts --ts audiometry_trainer_it.ts \
	   ../audiometry_trainer/__main__.py \
	   ../audiometry_trainer/dialog_change_frequencies.py \
	   ../audiometry_trainer/dialog_edit_preferences.py \
	   ../audiometry_trainer/dialog_set_value.py \
	   ../audiometry_trainer/global_parameters.py \
	   ../audiometry_trainer/main_window.py \
	   ../audiometry_trainer/window_generate_case.py



lrelease -verbose audiometry_trainer.pro

mv *.qm ../translations/

rcc -g python ../resources.qrc | sed '0,/PySide2/s//PyQt6/' > ../audiometry_trainer/qrc_resources.py
