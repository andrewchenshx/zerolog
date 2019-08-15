title build and install zerolog
set path=C:\Users\hp\Anaconda3\Scripts;%path%
call activate
python setup.py sdist
python setup.py bdist_wheel
pause
