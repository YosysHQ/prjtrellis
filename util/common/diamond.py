"""
Python wrapper for `diamond.sh`
"""
from os import path
import os
import subprocess
import database


def run(device, source, no_trce=False, mapargs=None, backanno=False):
    """
    Run diamond.sh with a given device name and source Verilog file
    """
    env = os.environ.copy()
    if no_trce:
        env["NO_TRCE"] = "1"
    if backanno:
        env["BACKANNO"] = "1"
    if mapargs is not None:
        env["MAPARGS"] = mapargs
    dsh_path = path.join(database.get_trellis_root(), "diamond.sh")
    return subprocess.run(["bash",dsh_path,device,source], env=env)

