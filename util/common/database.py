"""
Database and Database Path Management
"""
import os
from os import path
import json
import subprocess


def get_trellis_root():
    """Return the absolute path to the Project Trellis repo root"""
    return path.abspath(path.join(__file__, "../../../"))


def get_db_root():
    """
    Return the path containing the Project Trellis database
    This is database/ in the repo, unless the `PRJTRELLIS_DB` environment
    variable is set to another value.
    """
    if "PRJTRELLIS_DB" in os.environ and os.environ["PRJTRELLIS_DB"] != "":
        return os.environ["PRJTRELLIS_DB"]
    else:
        return path.join(get_trellis_root(), "database")


def get_db_subdir(family = None, device = None, package = None):
    """
    Return the DB subdirectory corresponding to a family, device and
    package (all if applicable), creating it if it doesn't already
    exist.
    """
    subdir = get_db_root()
    dparts = [family, device, package]
    for dpart in dparts:
        if dpart is None:
            break
        subdir = path.join(subdir, dpart)
        if not path.exists(subdir):
            os.mkdir(subdir)
    return subdir


def get_tilegrid(family, device):
    """
    Return the deserialised tilegrid for a family, device
    """
    tgjson = path.join(get_db_subdir(family, device), "tilegrid.json")
    with open(tgjson, "r") as f:
        return json.load(f)


def get_devices():
    """
    Return the deserialised content of devices.json
    """
    djson = path.join(get_db_root(), "devices.json")
    with open(djson, "r") as f:
        return json.load(f)


def get_db_commit():
    return subprocess.getoutput('git -C "{}" rev-parse HEAD'.format(get_db_root()))
