# Macal tests

There are tests available in the form of example code in the examples folder.
This assumes that the library is installed (in the active (venv) environment).

To execute the example code:

=> Go to the folder src/macal
=> Edit the file macal.py
=> On the class Macal set the value of self.debug to True

This will ensure that any exceptions that occur will show the entire exception trace.
When debug is False the execution is wrapped in a try-except block.

=> Save macal.py
=> Go to the interpreter folder.

In this folder is an executiable called mi
This is the interpreter for the language.
It can be used to execute the .mcl source files that are in the examples folder.

To execute for example helloworld.mcl issue the following command:

```bash
$ ./mi ../examples/helloworld
```

There is no need to add the .mcl extension to the filename, the interpreter assumes it implicitly.
This will show the "Hello World!" text and the exit code.
If ran with the -s switch it won't show the exit code.
Use the -v switch to show the version number of the language.

Any cli switches that are given after the filename will be available from within the application as an array in the sysargv variable.
The initial -v and -s will be popped off, so the application will only see the cli switches intended for it.
