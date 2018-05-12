"""
Interface between Python fuzzer scripts and Lattice Diamond ispTcl
"""

import database
import subprocess
import tempfile
from os import path
import re

def run(commands):
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

# All these following commands require a tuple (ncdfile, prffile) containing
# a specimen design for the target device

def run_ncd_prf(desfiles, commands):
    """
    Run a list of Tcl commands after loading given .ncd and .prf files

    desfiles: a tuple (ncdfile, prffile)
    commands: list of Tcl commands to run

    Returns the output from IspTcl, excluding header and pleasantry
    """
    run_cmds = [
        "des_read_ncd {}".format(desfiles[0]),
        "des_read_prf {}".format(desfiles[1])
    ] + commands
    return run(run_cmds)


def get_wires_at_position(desfiles, position):
    """
    Use ispTcl to get a list of wires at a given grid position

    desfiles: a tuple (ncdfile, prffile)
    position: a tuple (row, col)

    Returns a list of tuples
    (name, type, typeid)
    """
    command = ["dev_list_node_at_location -row {} -col {}".format(position[0], position[1])]
    result = run_ncd_prf(desfiles, command)
    wires = []
    for line in result.split('\n'):
        sline = line.strip()
        if sline == "":
            continue
        splitline = re.split('\s+', sline)
        assert len(splitline) >= 3
        wires.append((splitline[2].strip(), splitline[0].strip(), int(splitline[1])))
    return wires


def get_arcs_on_wire(desfiles, wire, drivers_only = False):
    """
    Use ispTcl to get a list of arcs sinking or sourcing a given wire

    desfiles: a tuple (ncdfile, prffile)
    wire: canonical name of the wire
    drivers_only: only include arcs driving the wire in the output

    Returns a list of arc tuples
    (source, sink)
    """
    command = ["dev_list_arcs -to {} -num 100000".format(wire)]
    result = run_ncd_prf(desfiles, command)
    arcs = []
    for line in result.split('\n'):
        sline = line.strip()
        if sline == "":
            continue
        splitline = re.split('\s+', sline)
        assert len(splitline) >= 3
        if splitline[1].strip() == "-->":
            arcs.append((splitline[0].strip(), splitline[1].strip()))
        elif splitline[1].strip() == "<--" and not drivers_only:
            arcs.append((splitline[1].strip(), splitline[0].strip()))
        else:
            assert False, "invalid output from Tcl command `dev_list_arcs`"
    return arcs


def main():
    print(run([]))


if __name__ == "__main__":
    main()
