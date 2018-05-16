"""
General Utilities for Fuzzing
"""

from joblib import Parallel, delayed
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
    Parallel(n_jobs=jobs)(delayed(func)(i) for i in items)
