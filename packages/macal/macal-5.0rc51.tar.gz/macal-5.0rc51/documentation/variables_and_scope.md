# Python: Variables and Scope

## Table of Contents

- [Introduction](#introduction)
- [1. Variable Scope](#1-variable-scope)
  - [a) Local Scope](#a-local-scope)
  - [b) Enclosing Scope](#b-enclosing-scope)
  - [c) Global Scope](#c-global-scope)
  - [d) Differences with C: Enclosing Scope and Block-level Scope](#d-differences-with-c-enclosing-scope-and-block-level-scope)
- [2. Class Scope and Attributes](#2-class-scope-and-attributes)
  - [a) Class Variables](#a-class-variables)
  - [b) Instance Variables (Attributes)](#b-instance-variables-attributes)
  - [c) Danger of Using Mutable Class Variables](#c-danger-of-using-mutable-class-variables)
- [3. Immutable vs. Mutable Objects](#3-immutable-vs-mutable-objects)
  - [a) Immutable Objects](#a-immutable-objects)
  - [b) Mutable Objects](#b-mutable-objects)
- [Conclusion](#conclusion)

## Introduction

Welcome, everyone, to today's lecture on Python programming. In this session, we will explore the concepts of variable scope, class scope, and the distinction between immutable and mutable objects in Python. Understanding these concepts is crucial for writing efficient and bug-free code. So, let's dive in!

## 1. Variable Scope

In Python, variable scope refers to the portion of code where a particular variable is accessible. Python has three levels of variable scope:

### a) Local Scope

Variables defined within a function are considered local and can only be accessed within that function.

```python
def my_function():
    x = 10       # Local variable
    print(x)     # Accessible within the function

my_function()
# Output: 10
```

In this example, the variable `x` has local scope within the `my_function` function and is not accessible outside of it. When we call `my_function()`, it prints the value of `x`, which is 10.

### b) Enclosing Scope

If a function is defined within another function, variables from the outer function are accessible within the inner function.

```python
def outer_function():
    x = 10

    def inner_function():
        print(x)  # Accessible within the inner function

    inner_function()

outer_function()
# Output: 10
```

In this example, the variable `x` is defined in the outer function `outer_function`. The inner function `inner_function` can access `x` from the enclosing scope. When we call `outer_function()`, it invokes `inner_function()`, which then prints the value of `x`, resulting in the output 10.

### c) Global Scope

Variables defined outside any function or class have global scope and can be accessed from anywhere in the code.

```python
x = 10     # Global variable

def my_function():
    print(x)     # Accessible within the function

my_function()
# Output: 10
```

In this example, `x` is defined in the global scope. The function `my_function` can access the global variable `x` and print its value, resulting in the output 10.

### d) Differences with C: Enclosing Scope and Block-level Scope

In contrast to languages like C, Python allows variables defined within conditional statements or loops to be accessed outside of the block in which they were defined.

```python
if True:
    y = 20    # Block-level variable in Python

print(y)     # Output: 20


```

In this example, the variable `y` is defined within the if statement block. Despite being defined inside the if statement, we can still access it outside the block, and the output will be 20. This is different from languages like C, where variables defined inside blocks (such as if or for loops) are not accessible outside those blocks.

## 2. Class Scope and Attributes

In Python, classes allow us to define objects with specific characteristics and behaviors. When declaring a class, we can define class variables and instance variables, which are also known as attributes. Let's explore these concepts further:

### a) Class Variables

Class variables are defined within the class but outside any methods. They are shared among all instances of the class.

```python
class Circle:
    pi = 3.1416   # Class variable

    def __init__(self, radius):
        self.radius = radius   # Instance variable

    def calculate_area(self):
        return Circle.pi * (self.radius ** 2)

c1 = Circle(5)
c2 = Circle(7)

print(c1.calculate_area())   # Output: 78.54
print(c2.calculate_area())   # Output: 153.9384
```

In this example, the class variable `pi` is shared among all instances of the `Circle` class. Each instance, `c1` and `c2`, has its own `radius` instance variable. The `calculate_area` method uses the class variable `pi` along with the instance variable `radius` to calculate the area of the circle. The outputs demonstrate that the class variable `pi` is accessible and shared by both instances.

### b) Instance Variables (Attributes)

Instance variables are unique to each instance (object) of a class. They are defined within methods, especially the `__init__` method, which is called when creating a new instance.

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width   # Instance variable
        self.height = height   # Instance variable

    def calculate_area(self):
        return self.width * self.height

r1 = Rectangle(5, 7)
r2 = Rectangle(3, 4)

print(r1.calculate_area())   # Output: 35
print(r2.calculate_area())   # Output: 12
```

In this example, the `Rectangle` class has two instance variables: `width` and `height`. Each instance, `r1` and `r2`, has its own values for these instance variables. The `calculate_area` method uses the instance variables to calculate the area of the rectangle. The outputs demonstrate that the instance variables are unique to each instance and hold different values.

### c) Danger of Using Mutable Class Variables

Here's an example that illustrates the potential danger of using a mutable object, such as a list, as a class variable.

```python
class Student:
    courses = []  # Class variable

    def __init__(self, name):
        self.name = name

    def enroll(self, course):
        self.courses.append(course)

student1 = Student("Alice")
student2 = Student("Bob")

student1.enroll("Math")
student2.enroll("Science")

print(student1.name, student1.courses)  # Output: Alice ['Math', 'Science']
print(student2.name, student2.courses)  # Output: Bob ['Math', 'Science']
```

In this example, we have a `Student` class with a class variable `courses`, which is initially an empty list. The `enroll` method is used to add courses to a student's list of courses.

However, since `courses

` is a class variable, it is shared among all instances of the `Student` class. When we create `student1` and `student2` as separate instances and call the `enroll` method on each instance, it appears that we are adding courses individually for each student.

However, because `courses` is a class variable, any modification made to it is reflected across all instances. Thus, when we print the courses for both `student1` and `student2`, we see that both lists contain both "Math" and "Science" courses.

This behavior can be unexpected and can lead to bugs and incorrect data representation. To avoid this, it is recommended to use instance variables for data that should be unique to each instance, rather than relying on mutable class variables.

To resolve the issue in this example, we can use an instance variable instead:

```python
class Student:
    def __init__(self, name):
        self.name = name
        self.courses = []  # Instance variable

    def enroll(self, course):
        self.courses.append(course)

student1 = Student("Alice")
student2 = Student("Bob")

student1.enroll("Math")
student2.enroll("Science")

print(student1.name, student1.courses)  # Output: Alice ['Math']
print(student2.name, student2.courses)  # Output: Bob ['Science']
```

In this updated example, each instance of the `Student` class has its own `courses` list as an instance variable. Now, when we enroll courses for each student, the lists remain separate and contain only the courses specific to each student.

## 3. Immutable vs. Mutable Objects

In Python, objects can be categorized into two types: immutable and mutable. Understanding the differences between these types is essential for writing efficient and error-free code.

### a) Immutable Objects

Immutable objects are those whose values cannot be changed after they are created. When you perform an operation that seems to modify an immutable object, it actually creates a new object with the updated value. Some examples of immutable objects in Python include integers, floats, strings, and tuples.

```python
x = 10
print(id(x))  # Output: 140726284225904

x = x + 5
print(id(x))  # Output: 140726284225840 (new object created)
```

In this example, the value of `x` is initially 10. When we perform `x = x + 5`, Python creates a new object with the value 15. The `id()` function demonstrates that the memory address of `x` changes, indicating the creation of a new object.

### b) Mutable Objects

Mutable objects, on the other hand, are objects whose values can be modified after they are created. This means that the memory location of the object remains the same, but its internal state can be altered. Examples of mutable objects in Python include lists, dictionaries, and sets.

```python
my_list = [1, 2, 3]
print(id(my_list))  # Output: 140726284337744

my_list.append(4)
print(id(my_list))  # Output: 140726284337744 (same object modified)
```

In this example, we have a list `my_list` with the values [1, 2, 3]. When we call the `append()` method and add the value 4 to the list, the object is modified in-place. The `id()` function shows that the memory address of `my_list` remains the same, indicating that the object was modified rather than replaced.

## Conclusion

Understanding variable scope, class scope, and the difference between immutable and mutable objects is crucial for writing effective and reliable Python code. By correctly utilizing variable scope and choosing the appropriate type of objects for your data, you can avoid bugs, improve code readability, and enhance the performance of your programs. Keep practicing these concepts, and you'll become a proficient Python programmer in no time!
