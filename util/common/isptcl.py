"""
Interface between Python fuzzer scripts and Lattice Diamond ispTcl
"""

import database
import subprocess
import tempfile
from os import path


def tcl_run(commands):
    """Run a list of Tcl commands, returning the output as a string"""
    dtcl_path = path.join(database.get_trellis_root(), "diamond_tcl.sh")
    workdir = tempfile.mkdtemp()
    scriptfile = path.join(workdir, "script.tcl")
    with open(scriptfile, 'w') as f:
        f.write('source $::env(FOUNDRY)/data/tcltool/IspTclDev.tcl\n')
        f.write('source $::env(FOUNDRY)/data/tcltool/IspTclCmd.tcl\n')
        for c in commands:
            f.write(c + '\n')
    result = subprocess.run(["bash", dtcl_path, scriptfile], cwd=workdir).returncode
    assert result == 0, "ispTcl returned non-zero status code {}".format(result)
    outfile = path.join(workdir, 'ispTcl.log')
    with open(outfile, 'r') as f:
        output = f.read()
    # Strip Lattice header
    delimiter = "-" * 80
    output = output[output.rindex(delimiter)+81:].strip()
    # Strip Lattice pleasantry
    pleasantry = "Thank you for using ispTcl."
    output = output.replace(pleasantry, "").strip()
    return output


def tcl_run_ncd_prf(ncdfile, prffile, commands):
    """
    Run a list of Tcl commands after loading given .ncd and .prf files
    """
    run_cmds = [
        "des_read_ncd {}".format(ncdfile),
        "des_read_prf {}".format(prffile)
    ] + commands
    return tcl_run(run_cmds)


def main():
    print(tcl_run([]))


if __name__ == "__main__":
    main()
