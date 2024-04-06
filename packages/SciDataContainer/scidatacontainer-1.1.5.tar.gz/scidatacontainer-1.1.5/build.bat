@echo off
call clean.bat
python setup.py sdist bdist_wheel
pip install .
rem python -m twine upload dist/*
