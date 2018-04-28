"""
Python wrapper for `diamond.sh`
"""
from os import path
import subprocess
from common import database


def run(device, source):
    """
    Run diamond.sh with a given device name and source Verilog file
    """
    dsh_path = path.join(database.get_trellis_root(), "diamond.sh")
    return subprocess.run(["bash",dsh_path,device,source])

