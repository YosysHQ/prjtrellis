import database
from os import path
import os

def cells_db_path(family, speedgrade):
    tmgroot = path.join(database.get_db_root(), family, "timing")
    if not path.exists(tmgroot):
        os.mkdir(tmgroot)
    sgroot = path.join(tmgroot, "speed_{}".format(speedgrade))
    if not path.exists(sgroot):
        os.mkdir(sgroot)
    return path.join(sgroot, "cells.json")


def interconnect_db_path(family, speedgrade):
    tmgroot = path.join(database.get_db_root(), family, "timing")
    if not path.exists(tmgroot):
        os.mkdir(tmgroot)
    sgroot = path.join(tmgroot, "speed_{}".format(speedgrade))
    if not path.exists(sgroot):
        os.mkdir(sgroot)
    return path.join(sgroot, "interconnect.json")
