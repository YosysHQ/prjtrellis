"""
General Utilities for Fuzzing
"""

import os


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
    # TODO: actually make this parallel
    for i in items:
        func(i)


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
