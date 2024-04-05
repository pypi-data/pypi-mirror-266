# macal

[![PyPI - Version](https://img.shields.io/pypi/v/macal.svg)](https://pypi.org/project/macal)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/macal.svg)](https://pypi.org/project/macal)

-----

**Table of Contents**

- [Whats new](#Whats-new)
- [Installation](#Installation)
- [License](#License)
- [About](#About)
- [Howto](#Howto)
- [Variables](#Variables)
- [Strings](#Strings)
- [Const](#Const)
- [Libraries](#Libraries)
- [Creating variables](#Creating)
- [If, elif, else](#If)
- [Functions](#Functions)
- [Foreach](#Foreach)
- [Select](#Select)
- [Break](#Break)
- [Halt](#Halt)
- [Continue](#Continue)
- [Csv Library](#CsvLibrary)
- [Io Library](#IoLibrary)
- [Math Library](#MathLibrary)
- [Strings library](#strings-library)
- [Syslog Library](#Syslog-library)
- [System Library](#System-library)
- [Time Library](#Time-library)
- [Creating an addon library](#Creating-an-addon-library)

## Whats new


In version 5.0.0 RC 34 the lexer, parser and the interpreter have been updated. A compiler stage was introduced.
** 
   This version is still being tested, i tacked RC on too soon, it's more beta testing, there's still bugs.
   The features that i wanted for sure are in. Not everything from previous versions has been implemented.
   The feature that was left out wasn't used by us, so it should not impact existing code. 
   But test before you begin. Use virtual environments for certain!
   You may find that you are able to create invalid code constructs without the parser or the compiler
   complaining. If you encounter this, please report it.
**

- The lexer is simplified
- Recursion is reduced in the parser
- The compiler compiles the AST to a "bytecode" representation that can be saved to a binary file.
- The interpreter now interprets the "bytecode" from the compiler rather than the AST directly.

- Creating libraries with external functions is improved.
- Added switch statement to the language
- Added print statement to the language, depricating the Console and Print functions from the system library,
  although they still exist.
- The Type and Is<Type> functions have been removed from the system library, they are now always available.

- mc program added -> Macal compiler
- mi program now does lex, parse, compile, run, can save binary with -o
- mr program added -> Macal runtime loads only the bytecode

- mc and mi can reserve variables on the stack with the -r option. -r --reserved_vars takes a string with a csv
  list with the names of the variables to reserve. 
  Please note that you need to set the values for these variables before executing the script.
  Typically you do this only if you use Macal integrated in your own project and not when running scripts with mi/mr.

- system library has new functions for cli arguments and environment variables
  Args() -> gets the cli arguments as a list
  ArcCount() -> gets the length of the cli arguments list, although you can also use Len from the string library for this.
  Arg(index: int) -> get cli argument [index]
  Env(varname: str) -> get the value from environment variable varname
  SetEnv(varname: str, value: any) -> set the value of the environment variable varname.

- New keyring library
- Meraki_v1 library now included in this distribution, it contains a limited subset of the Meraki Dashboard API.
  
- requirements.txt now includes all Python library dependancies.
- Makefile to clean/build/publish

TODO:
 - better type checking
 - reworking compiler error messages
 - reworking interpreter error messages
 - rework verbose mode for compiler
 - rework verbose mode for interpreter
 - decompiler (md)
 - re-implement first class treatment of functions.
   Currently you can't assign functions to variables.
   

## Installation


```bash
python3 -m pip install macal
```


## License


`macal` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.



## About


Macal is a Domain specific language (DSL) implemented in Python.
It's main function is to read, transform and output data using an SQL like SELECT statement.
The instructionset of Macal is limited so it's easy to learn. 
It's possible to extend the language by using libraries.

Macal is about controlling the flow of "the river of data".
Hence the name Macal, it's a river in Belize.

The following chapters will contain code examples.

Macal comes with an interpreter called 'mi' which can run both source code (.mcl) as well as 
binary (.mcb) files. When running from source code you can save the binary output with -o.

```bash
./mi <path/filename>
```


## Howto


Below is a minimal code example on how to use Macal in your own Python project.

```python
from macal.macal_vm import MacalVm
from macal.macal_binary_file_io import LoadBinary

vm = MacalVm()
try:
	code = LoadBinary("test.mcb")
	vm.Execute(code)	
except Exception as ex:
	print(ex)
```


## Libraries


There are several libraries included in the macal package.

- csv
- io
- keyring
- math
- meraki_v1
- strings
- syslog
- system
- time

To use a library it needs to be included in the source:

```c
include system;

Console("Hello World!");
```

Include can have multiple libraries separated by comma's.

*Note: The Console has been depricated. 
 The language has a built in print command now.
 The reason for implementing it directly instead of through an external library is the performance.


## Variables


A variable is a 'container' for data.
Macal is a loosely typed language.
This means that you don't explicitly declare a variable to be of a specific type, the type is inferred from the value that has been assigned.

The following data types are recognized:

- array     (Comparable to a list in Python)
- boolean   (true/false lower case)
- float     (a double if you are used to languages as C#)
- integer
- nil       (None in Python, null in C#, nil in Pascal)
- record    (a dict in Python)
- string

A variable consists of a name and a value. 
Before you can use a variable you have to assign a value to it.

```c

var1 = 42;
var2 = 3.14;
var3 = "Hello World!";
var4 = true;
var5 = nil;
var6 = array;
var7 = record;

print($"{var1}, {var2}, {var3}, {var4}, {var5}, {var6}, {var7}");
```

This will show the value of each variable on a single line, where variables 6 and 7 an 
empty array and record depicted by [] and {} respectively.

In Macal 5 you can alternatively assign the values of var6 and var7 also as:

```c
var6 = [];
var7 = {};

```

nil is special here because it is both a type and a value, or more precisely, the absense of a value.
array and record are special because they are types as well as initializers.


## Strings


A string is a literal value containing text.
When assigning a string it can span over multiple lines.
New lines in the code, will also be in the string.

Example:

```c

str = "This is a string
Multi line
string.";

print(str);
```

This example will show 3 lines of text:
```console
This is a string
Multi line
string.
```

Concatenation of strings is handled by the + operator.

Example:
```c
include system;

str_a = "string a ";
str_b = "string b";

var = str_a + str_b;
console(var)
```

This will display a single string.

While variables of various types can be converted to a string with the to_string(var) function 
from the strings library, there is a more powerfull way to put values of variables into strings.

This is string interpolation.

An example is:

```c
a=1;
b=2;

str= $"{b} = {a} * 2";
```

The value of the variables a and b will be put into string str.
Macal also supports function calls and expressions inside the curley brackets of string interpolation ({}).



## Const


Const is a special instruction that will create a readonly "variable".
This means that the value of a const can be set at creation time, but can't be changed afterwards.

As an example, the following code will cause a runtime error*.

(* the intention is to catch this in the compiler at some time.)

```c

const THEANSWERTOLIFETHEUNIVERSYANDEVERYTHING = 42;

THEANSWERTOLIFETHEUNIVERSYANDEVERYTHING = "Forty Two";

```

Other than the fact that a const is readonly it can be used like a variable.


## Creating Variables


There is no specific command to declare a variable.
A variable is created when a value is assigned to it.

```c

x = 42;
y = 1.1;
hello = "Hello World";
test = true;
undefined = nil;
data = array;
data[] = 10;
data[] = 1.1;
moredata = record;
moredata["test"] = 1;
moredata["hitchhikers"] = "guidetothegalaxy";

// Display the values:
print(x, " ", y);
print(hello);
print(test);
print(undefined);
print(data[0], " : ", data[1]);
print(moredata["test"]);
print(moredata["hitchhikers"]);
```



## If, elif, else


If and elif are conditional branching statements.
Else is the final branch taken if previous conditions are not met.

The if statement can be used on it's own, or followed by one or more elif statements, 
and finally followed by an optional else statement.

The conditions can be made from logical mathematical equasions like == for equals, != for not equal, > for greater than etc.

It is not required to enclose the condition with brackets ().
If you are mixing mathematical equasions and boolean equasons then you should use brackets.
For example with "(a == 1) and (b == 2)". 
If you don't supply brackets there, the equivalent of this gets processed: "a == (1 and b) == 2", which is something completely different.

```c
a = 1;

if a == 1 {
	print("Hello World!");	
}
elif a == 2 {
	print("Change a = 1 to 2 to be able to see this message.");
}
else {
	print("This should show up only if a is not 1 or 2.");
}
```



## Functions


Functions are "first class" in Macal. Which means you can assign functions to variables, and functions can be returned from functions.
Functions can also be passed in as arguments to other functions.

Function arguments are of "type" any, which means you can pass anything you want into a function parameter.
If your code relies on parameters being a certain type, you should test that.
The System library has several "isXXX" functions that you can use to determine the type of the variable/parameter that you pass in.

The resulting value that is returned by the function using the return statement will have the type specific to the value that is provided after the return statement.


```c
print => (arg) {
    c = arg();
    return c; 
}

fourty_two => () {
  return 42;
}

result = print(fourty_two());
print(result);
```

Above example shows a two functions being defined (print and forty_two) and then one function is passed as a parameter to the other function.
Finally the result is displayed: 42.

It is not required to provide a value in the return statement.

```c
def => (){
	a = 1;
	if a == 1 {
		print("a is 1.");
		return;
	}
	print("a was not 1");
}

def();
```

The result of return in the above example is that the function will stop execution.
The print statement after return is never reached.



## Foreach


Foreach is an iterative statement, which means it will iterate over a record, an array or even a string and it will 
repeat it's block of statements as many times as there are "items".

It's only parameter is the object that it will iterate over. Within it's scope there is a variable called 'it' that contains the current 'item' value.

The following code will populate a variable in a array/record structure and is used as the base for other examples in this chapter and the next.

```c

var  = array;
var[] = record;
var[] = record;
var[] = record;
var[] = record;
var[0]["id"] = 1;
var[1]["id"] = 2;
var[2]["id"] = 3;
var[3]["id"] = 4;
var[0]["title"] = "The Hobbit";
var[1]["title"] = "Foundation";
var[2]["title"] = "The Hitch Hikers Guide to the Galaxy";
var[3]["title"] = "The Lord of The Rings";
var[0]["author"] = "J.R.R. Tolkien";
var[1]["author"] = "Isaac Asimov";
var[2]["author"] = "Douglas Adams";
var[3]["author"] = "J.R.R. Tolkien";
```

Using the above code to populate the variable, lets see some examples of foreach:

```c

foreach var {
	print(it)
}

```
This will iterate over the records in var and output them on the print.

When iterating over a record, the 'it' variable will contain the key index of the record.
This is much like Python's for .. in dict construction.


```c

foreach var[1] {
	print($"'{it}' : {var[1][it]}");
}
```

The following example is testing to iterate over a string.
```c
foreach "Runtime" {
	print(it);
}
```
As you can see you can pass the string as a literal instead of having it in a variable.


The next example shows you that you can also use functions that return a value as an operand for foreach:

```c
test => () {
	return "test";
}

foreach test() {
	print(it);
}
```


## Select


The select statement lies at the core of the Macal language.
It can be used to retrieve data from a data source much like an SQL statement would in a database.
The difference with SQL is that Macal's select statement has variables and functions as data source 
instead of just the database.


It is possible to write a function/library that allows retrieving data from a database and use that function in this select statement as a data source.
An example of how to write a simple library is provided in another chapter.

The output of the select statement is either a record, an array of records or a single value.
It depends on how the select statement is structured.

The way to ensure that the output is always a record is to use the distinct keyword after select.
Where a normal select statement would return an array of records, with distinct only the fist record is returned.
The distinct feature works similar to distinct in SQL, however, as it is implemented now in Macal 5.0, distinct 
will enforce the output to be a single record or a single value.
This is more a backwards compatibility descision than anything else. The actual implementation works very similar
to SQL's equivalent.

To select all fields the * symbol is used.
To select individual fields (keys in a record), use the name of that field.
For multiple fields use a comma to separate them.
The name of the field in the resulting record can be changed by using the as keyword.

To filter data based on a specific condition use the where keyword.

The variable name after the into keyword indicates into which variable the result of the select statement is stored.

Below are the examples of using the select statement.
The examples all use the same starting template as mentioned in the previous chapter.

```c
select * from var into y;

foreach y {
	print(it);
}
```

The above is the most simple form of the select statement and would be equivalent to: y = var.

A more advanced and interresting form is the following:

```c
select author as Author, title as Title from var where author == 'J.R.R. Tolkien' into y;

foreach y {
	print(it);
}
```

The above select statement selects the author and title fields of the record and renames them with a capital letter first.
It will also filter the result to only contain those records for which the value of the author field is J.R.R. Tolkien.


```c
select distinct author as Author, title as Title from var where author == 'J.R.R. Tolkien' into y;
print(y);
```

With the distinct method the output is limited to just a record.
In the previous example you see that the output of the query without distinct is a list of 2 records.
In this example only the first record will be returned.

It is possible to combine the results of multiple select statements together by using the merge keyword.

```c
select author as Author, title as Title from var where author == 'J.R.R. Tolkien' into y;
select author as Author, title as Title from var where author == 'Douglas Adams' merge into y;

foreach y {
	print(it);
}
```

This will result in y containing an array of 3 records, two from the first select statement, and one from the second.



## Break


Break is used to stop the execution of a foreach or while loop.

The following example uses the same setup code as the ones in the foreach chapter.

```c
foreach var {
	print(it["title"]);
	break;
	print("this doesn’t show");
}

```

The text "this doesn't show" is not displayed. Also only 1 title is shown.

The break statement is usually combined with a condition.

```c
foreach var {
	print(it["title"]);
	if it["title"] == "Foundation" {
		break;
	}
	print("this only shows once");
}
print("This line will show.")
```

The above example would result in two book titles being displayed, separated by the line "this only shows once."
The line "This line will show" will be displayed because break doesn't stop the application from running, it only stops the loop.



## Halt


The halt statement is used to stop execution of the application.
Unlike the break statement that only stops a loop, halt stops everything.
Also halt may also be used with an integer value as an argument.
This is to set the 'exitcode' value of the application.

```c
var = "a";
if var == "a" {
	print("This is shown.");
	halt 1;
	print("This does not show.");
}
print("This also is not shown.");
```

In above example the only text that is displayed is "This is shown."
The rest is not shown as the application is terminated at the halt instruction, setting the 
value of the exitcode property of the VM.


## Continue


The continue statement is used in a loop to skip the rest of the loop block and continue with the next iteration.

An example:

```c
lst = list('item 1', 'item 2', 'item 3', false, 'item 4', 'item 5');

foreach lst {
	if it == false { continue; }
	print(it);
}
```

The above example will show all elements in the array, with the exception of the element that has false as value.




## Csv library


HeadersToCsv(record)

Returns the keys of the record (records are key/value pairs) as a CSV string.

ValueToCsv(record)

Returns the values of the record as a CSV string.

ArrayToCsv(array)

Returns the element values of the array as a CSV string.



## Io library


Load(filename)

Loads a text file returns it as a string.


ReadJSON(filename)

Reads a JSON file and returns it as the apropriate type (record/array).


Exists(filename)

Returns true if the file/path exists, otherwise false.


Save(filename, content)

Saves the content into the file.
Returns true if successfull, otherwise raises RuntimeError.


WriteJSON(filename, content)

Write the content into a json file.
Returns true if successfull, otherwise raises RuntimeError.


GetLastRun(org_name, iso_now)

Checks the /temp for a file (org_name) and loads it, returns the iso timestamp in that file.
If the file doesn't exist returns iso_now
This is handy when you deal with data that collects over time (a log file for example) so you 
know from which point on you have to start processing.


SetLastRun(org_name, iso_now)

Stores the iso_now timestamp into a file (org_name) in /temp


## Math library


The math library contains functions and constants that are mathematical in origin.

constant: E 	
constant: PI
constant: TAU

Round(arg, digits)

If no digits are supplied:
returns arg rounded to the nearest integer (<.5 rounds down, >= .5 rounds up).
If digits are supplied:
returns arg rounded to the nearest float with digits number of digits.

Please note that the number of digits should fall within the range that a double can represent. Giving a larger number can give undesirable effects.

Ceil(arg)

returns arg rounded up to the next whole number.

Floor(arg)

returns arg rounded down to the next whole number.

Cos(x)

returns cosinus of x where x is a numberic value between between -PI/2 and PI/2  radians.

Sin(x)

returns sinus of x where x is a numberic value between between -PI/2 and PI/2  radians.

Tan(x)

returns tangent of x where x is a numberic value between between -PI/2 and PI/2  radians.

Acos(x)

returns arc cosinus of x where x is a numberic value between between -PI/2 and PI/2  radians.

Asin(x)

returns arc sinus of x where x is a numberic value between between -PI/2 and PI/2  radians.

Atan(x)

returns arc tangent of x where x is a numberic value between between -PI/2 and PI/2  radians.

Pow(x, y)

returns x to the power of y.

Sqrt(x)

returns the square root of x.

Log(x)

returns the natural logarithm of x.

Log2(x)

returns the base 2 logarithm of x.

Log10(x)

returns the base 10 logarithm of x.

Exp(x)

returns E raised to the power of x.

Expm1(x)

returns E raised to the power of x minus 1.
This function is more accurate than calling exp(x) and subtracting 1.



## Strings library


Len(x)

Returns the length of x, where x can be an array, a record or a string.
For an array it returns the number of elements. For a record it returns the number of key/value pairs.
For a string it returns the number of characters.


Left(str, length)

Returns the left length characters of the string.


Mid(str, start, length)

Returns length characters from starting character start of the string.


ToString(arg)

Converts an integer or a float to a string.


Format(format, arg)

Like Python's format but unlike that it can only have a single arg value not multiple.

Contains(needle, haystack)

Returns true if needle is in haystack, otherwise false.


Replace(var, from, with)

Returns a string from the original with from replaced by with.


StartsWith(str, first)

Returns true if the string starts with first, false if not.


RemoveNonAscii(str)

Removes all non-ascii characters from the string, but tries to replace these with ascii characters where possible.


ReplaceEx(var, repl, by)

The same as replace, but repl is an array of strings.

PadLeft(string, char, amount)

returns string padded on the left side with amount number of char.

PadRight(string, char, amount)

returns string padded on the right side with amount number of char.



## Syslog library



SyslogInit(remote)

Initializes the syslog functionality. Remote indicates if the syslog server is supposed to be running on localhost or elsewhere.

SyslogSetAddress(address, port)

Set the IP address/Host name and Port number for the syslog server if it is a remote server.


Syslog(level, message)

Sends the message to the syslog server with the given level (debug, info, warn, error, critical)



## System library

*Depricated*
Console(params)

Outputs given argument(s) to the console.

*Depricated*
Array(params)

Alternate way to define an array. Returns an array of elements made of the arguments given to this function.

```c
include system;

lst = Array('item1'. 2, 'item3', 'the fourth item');

Console(lst);

```

RecordHasField(record, fieldname)

Returns true if the record has a key fieldname, otherwise returns false.

platform()

Returns the current platform the application is running on (Linux, Windows).

ShowVersion()

Prints the version info, author and credits to the console.

Items(record)

Returns the items of the record as an array of key/value pairs.
Is to be used in conjunction with key and value functions.

Key(keyvalueitem)

returns the key of a key/value pair. Key/value pair aray is generated with the items function.

Value(keyvalueitem)

returns the value of a key/value pair. Key/value pair array is generated with the items function.

Keys(record)

returns all the keys in the record as an array.

Values(record)

returns all the values in the record as an array.

Env(variable)

Returns the value of the environment variable in the operating system.

SetEnv(variable, value)

Sets the value of the environment variable in the operating system.

Args()

Returns an array with the command line arguments in the operating system.

Arg(index)

Returns the value of the command line argument at index (integer) in the operating system.

ArgCount()

Returns the total number of command line arguments in the operating system.


## Time library


UtcNow()

Returns the current utc date/time.

UtcIsoNow()

Returns the current utc date/time in iso format.

IsoNow()

Returns the current local date/time in iso format.


Now()

Returns the current local date/time.


DateToUnix(date_str)

Returns the unix representation (# of seconds) of the given date string.


IsoToUnix(isodate_str)

Returns the unix representation of the given iso formatted date string.


DateFromUnix(seconds)

Returns a date string from the given unix representation.

IsoFromUnix(secods)

Returns an iso formatted date string from the given unix representation.


PerfCounter()

Returns the value of the system performance counter.
Can be used for a simple stopwatch.



## Creating an addon Library


Creating a new "library" is pretty much the same as creating a normal .mcl file.
In the below example a library test is implemented.
It consists of 2 files: demolib.mcl and demolib.py.

demolib.mcl contains the definition of the function print.
The external keyword is used to indicate that this function is implemented in an external (Python) file, specifically in the function Print.

The actual implementation of the function is in the demolib.py Python file in the function Print.


File: demolib.mcl
```c

/*
 Author: Marco Caspers
 
 The Demo library is a demonstration on how to create a library for macal.
*/

const DEMOCONST = 'The Demo constant.';

print => (text) external "demolib", "Print";

```

File: demolib.py
```python

# demolib
# Author: Marco Caspers
# Demo Library implementation

def Print(text: str) -> None:
	"""Implementation of print function for demolib."""
	print(f"The value of the argument is: {text}")

```

Any function that is callable from a macal library via external has to conform to the interface as defined in
the .mcl library file.

If you have seen the implementations required for versions prior to Macal 5 you will immediately notice the
lack of any dependance on Macal itself for the implementation in Python.

You can use any Python application and any function from Macal as long as you describe the interface to Macal
as shown in demolib.mcl.

In order to return a value back to the Macal interpreter you use the Python return statement as if you were
interacting with a normal Python application.

If you do not return any value, Macal will automatically insert nil as the return value.
In Python this would be None.

The following demo shows how to use the demo library in code:

```c
/*

Author: Marco Caspers
This demo shows how to use the demolib library.

*/

include demolib;

var = print(DEMOCONST);
print("A literal string.");
print(var);

```

This will output the following on the console:

```console

A literal string.
The Demo constant.

```

