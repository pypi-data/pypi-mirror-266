import os
import platform
import site
import sys

def PathMePyDir(path):
    path = os.path.abspath(path)
    if platform.system() != "Windows" and platform.system() != "Linux" :
        os.system('export PATH=$PATH:' + path)
    if platform.system() == "Windows" :
        os.system('set Path="%Path%;' + path + '"')
    elif platform.system() == "Linux":
        os.system('export PATH=$PATH:' + path)

def PathMePyUserScriptFolder():
    path = site.getusersitepackages()
    if platform.system() != "Windows" and platform.system() != "Linux" :
        os.system('export PATH=$PATH:' + path)
    if platform.system() == "Windows" :
        os.system('set Path="%Path%;' + path + '"')
    elif platform.system() == "Linux":
        os.system('export PATH=$PATH:' + path)

Current_Path = os.environ.get("PATH")

if platform.system() != "Windows" and platform.system() != "Linux" :
    Current_Path_Formated = Current_Path.replace(":", "\n")
if platform.system() == "Windows" :
    Current_Path_Formated = Current_Path.replace(";", "\n")
elif platform.system() == "Linux":
    Current_Path_Formated = Current_Path.replace(":", "\n")