Asynchronicity
==============

Understanding asynchronicity in Python can be challenging at first, but here's the basics:

Asynchronous programming allows a program to handle many tasks at the same time. In traditional synchronous
programming, tasks are performed one after the other. In asynchronous programming, tasks can be performed out of
order, allowing a program to do more than one thing at a time. In the case of scriptor, this is necessary because
the python-scripts run in pyodide, which runs in a JavaScript-Context, which is asynchronous. If scripts would
run synchronously, the UI wouldn't be able to respond anymore while the script is executing. That means you wouldn't
be able to see messages and the whole Browser would be unresponsive.

async and await in Python
-------------------------

In Python, ``async`` and ``await`` are used to write asynchronous code. They help you manage and control asynchronous
tasks.

async Keyword
~~~~~~~~~~~~~

The ``async`` keyword is used to define an asynchronous function. An asynchronous function is a function that can be
paused and resumed, allowing other code to run in the meantime. Also you can use the ``await``-keyword only in
``async``-functinos and methods.


await Keyword
~~~~~~~~~~~~~

The ``await`` keyword is used to pause the execution of an ``async`` function until an asynchronous task is completed.
When the task is finished, the function resumes execution.
