#! /bin/sh


##export PYTHONPATH=$PYTHONPATH:../../:../:../default_experiments/
make html
make latexpdf
make gettext
sphinx-intl update -p _build/gettext -l fr
sphinx-build -b html -D language=fr . _build/html_fr
sphinx-build -b latex -D language=fr . _build/latex_fr #. _build/latex/fr
cd _build/latex_fr
pdflatex audiometry_trainer.tex
cd ..
