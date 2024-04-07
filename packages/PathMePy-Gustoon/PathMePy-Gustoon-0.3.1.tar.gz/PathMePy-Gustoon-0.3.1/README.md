# PathMePy
A tool to add scripts to Path

## Installation
You have to install the package using pip : `pip install PathMePy-Gustoon`

## Content
You need to import this package with `import PathMePy_Gustoon`
This packages add three functions : 
`PathMePyDir(path)`,
`PathMePyUserScriptFolder()`,
`IsAlreadyOnPath(path)`,
two variables `Current_Path` and `Current_Path_Formated`

## Explanation
`PathMePyDir(path)` function is for temporaly add a directory in your user PATH variable,
`PathMePyUserScriptFolder()` function is for add the Python User Script Folder to the user PATH variable,
`IsAlreadyOnPath(path)` function return if an element is on the PATH or not,
`Current_Path` is a variable with the current path,
`Current_Path_Formated` is a formatted version of `Current_Path` that changes each PATH separator with a newline.
