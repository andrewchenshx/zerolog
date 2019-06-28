# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='zerolog',
    version='0.0.1',
    description='Sample package for Python-Guide.org',
    long_description=readme,
    author='Andrew',
    author_email='chenshx@live.cn',
    url='https://github.com/andrewchenshx/zerolog',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)

