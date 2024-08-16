ProgressBar
===========
The ``ProgressBar`` is used to visualize progress, i.e. for tasks that take a long time. It has a ``set``- and an
``unset``-method.
With the ``set``-method, you can signal the progress of your task to scriptor. With the ``unset``-method you hide the
progressbar when you're done.

Here's an example. We also import ``time`` to make the script wait (``sleep``) in every step, to simulate work.
Otherwise the progressbar would fill so fast and then be hidden, that you wouldn't be able to see it.

.. code-block:: python

    #### scriptor ####
    from viur.scriptor import *
    import time

    async def main():
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        counter = 0
        for letter in letters:
            counter += 1
            ProgressBar.set(
                counter/len(letters)*100,
                counter,
                len(letters),
                f"Currently working on {letter}"
            )
            time.sleep(0.2)
        ProgressBar.unset()
