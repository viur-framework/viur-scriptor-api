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






..
    ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT ALT
    ===============================================================

    Async and await
    ===============
    The Scriptor utilizes the built-in functionality of asynchronous (async) functions in Python. Async functions in Python are similar to conventional functions, with the difference that they return a coroutine or, in technical terms, a Promise instead of a value.

    Understanding Asynchrony
    ------------------------

    To understand the concept of asynchrony, let's consider three individuals: Tom, Pascal, and Felix. Tom wants to order a drink for each of his friends. In a synchronous workflow, Tom would run to Pascal and ask him what he would like, then place the order for him. Only after Pascal receives his drink would Tom move on to Felix, take his order, and give him his drink. The process of getting a drink follows the sequence of approaching each person, going to the bartender, placing an order, and then receiving the drink. This is a synchronous workflow because Tom can only hold one drink at a time, as he also needs to hold his own drink.

    Now, let's consider an asynchronous workflow: Tom still wants to order drinks for Pascal and Felix. Instead of running to each friend in sequence, Tom goes directly to the bartender and places orders for all the drinks at once. While the bartender prepares the drinks, Tom can continue with his own activities instead of waiting for each individual drink to be ready. Once the drinks are prepared, Pascal and Felix can pick up their respective drinks. In this case, Tom can place the orders and then proceed with other tasks while the drinks are being prepared in the background. This asynchronous workflow allows Tom to proceed with other tasks concurrently, without being blocked, while the drinks are being prepared.

    This example highlights the difference between synchronous and asynchronous workflows and demonstrates how asynchrony enables parallel execution of tasks, thereby enhancing efficiency.

    Coding sample
    ~~~~~~~~~~~~~
    .. code-block:: python

        import asyncio, time

        async def main():
            async def say_hello(x):
                await asyncio.sleep(x)
                #print("Hallo Welt!", x)

            # sequenziell (nacheinander)
            start = time.time()
            for i in (1, 2, 3):
                await say_hello(i)

            print("SEQUENZ ENDE", time.time() - start)

            # parallel
            start = time.time()
            list = (asyncio.create_task(say_hello(i)) for i in (1, 2, 3))
            await asyncio.gather(*list)
            print("PARALLEL ENDE", time.time() - start)

    Use of Asynchronous Functions in the Scriptor
    ---------------------------------------------
    The Scriptor makes use of asynchronous (async) functions in various cases to enable networking and handle requests, including 'fetch' operations, by leveraging Pyodide and the JavaScript 'fetch' function. Additionally, it employs the 'Google Chrome' Filesystem API, which is built on asynchronous functions. However, please note that not all modules of the Scriptor can be used in every browser. For example, the FilePicker API of the Scriptor cannot be utilized in Firefox as there is no interface available to directly interact with the operating system's file system through the browser.

