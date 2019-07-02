# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst', encoding='utf8') as f:
    readme = f.read()

with open('LICENSE', encoding='utf8') as f:
    license = f.read()

setup(
    name='zerolog',
    version='0.0.1',
    description='Zero Log',
    long_description=readme,
    author='Andrew',
    author_email='chenshx@live.cn',
    url='https://github.com/andrewchenshx/zerolog',
    license=license,
    # packages=find_packages(exclude=('tests', 'docs'))
    py_modules=['zerolog']
)

