"""
General Utilities for Fuzzing
"""

import os
from threading import Thread, RLock

def parallel_foreach(items, func):
    """
    Run a function over a list of values, running a number of jobs
    in parallel. TRELLIS_JOBS should be set to the number of jobs to run,
    defaulting to 4.
    """
    if "TRELLIS_JOBS" in os.environ:
        jobs = int(os.environ["TRELLIS_JOBS"])
    else:
        jobs = 4
    items_queue = list(items)
    items_lock = RLock()

    def runner():
        while True:
            with items_lock:
                if len(items_queue) == 0:
                    return
                item = items_queue[0]
                items_queue.pop(0)
            func(item)

    threads = [Thread(target=runner) for i in range(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def journal_foreach(items, func):
    """
    Run a function over a list of items, keeping a journal of which items have been visited. If the script is
    interrupted, it will return where it stopped if the list of items have not changed.

    If an exception occurs during an item, that exception will be logged in the journal also.

    Items must have an unambiguous string conversion, and should normally be string keys, that can be saved in the
    journal.

    The journal is called "fuzz.journal" in the current working directory. At present, this implementation is not thread
    safe.
    """
    # TODO
    pass
