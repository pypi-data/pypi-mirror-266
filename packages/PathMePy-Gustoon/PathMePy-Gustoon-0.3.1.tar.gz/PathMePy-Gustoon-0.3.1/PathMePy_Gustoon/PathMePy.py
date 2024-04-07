import os
import platform
import site
import sys

Current_Path = os.environ.get("PATH")

if platform.system() != "Windows" and platform.system() != "Linux" :
    Current_Path_Formated = Current_Path.replace(":", "\n")
if platform.system() == "Windows" :
    Current_Path_Formated = Current_Path.replace(";", "\n")
elif platform.system() == "Linux":
    Current_Path_Formated = Current_Path.replace(":", "\n")

class PathNotFoundError(Exception):
    def __init__(self, message):
        self.message = message

def IsAlreadyOnPath(path):
    if path in Current_Path_Formated:
        return True
    else:
        return False

def PathMePyDir(path):
    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise PathNotFoundError("The path " + path + " doesn't exist.")
    elif platform.system() != "Windows" and platform.system() != "Linux" :
        os.system('export PATH=$PATH:' + path)
    elif platform.system() == "Windows" :
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