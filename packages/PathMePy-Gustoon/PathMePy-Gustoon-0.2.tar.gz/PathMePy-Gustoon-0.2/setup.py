from setuptools import setup, find_packages

setup(
name='PathMePy-Gustoon',
version='0.2',
author='Gustoon',
author_email='',
description='A tool to add scripts to Path',
long_description='''
# PathMePy

A tool to add scripts to Path

## Installation
You have to install the package using pip : `pip install PathMePy-Gustoon`

## usage
You need to import this package with `import PathMePy_Gustoon`
This packages add two function : 
`PathMePyDir(path)` and 
`PathMePyUserScriptFolder()` .
`PathMePyDir(path)` is for add to Path temporaly a direrctory and `PathMePyUserScriptFolder()` is for add the User Script folder to Path temporaly.''',
long_description_content_type='text/markdown',
packages=find_packages(),
classifiers=[
'Programming Language :: Python :: 3',
'License :: OSI Approved :: MIT License',
'Operating System :: OS Independent',
],
python_requires='>=3.6',
)