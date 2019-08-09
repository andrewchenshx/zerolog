title build and install zerolog
set path=C:\Users\hp\Anaconda3\Scripts;%path%
call activate
python setup.py sdist
python setup.py bdist_wheel
cd E:\incubator\zerolog\dist
pip install -U zerolog-0.0.1-py3-none-any.whl
pause
