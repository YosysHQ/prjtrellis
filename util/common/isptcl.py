"""
Interface between Python fuzzer scripts and Lattice Diamond ispTcl
"""

from collections import defaultdict

import database
import subprocess
import tempfile
from os import path
import re


# Arc whose direction is ambiguous "---"
class AmbiguousArc:
    # I
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __getitem__(self, idx):
        if idx == 0:
            return self.lhs
        elif idx == 1:
            return self.rhs
        else:
            raise IndexError("AmbiguousArc only connects two nets")

    def __repr__(self):
        return "{} --- {}".format(self.lhs, self.rhs)


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
        "des_read_ncd {}".format(path.abspath(desfiles[0])),
        "des_read_prf {}".format(path.abspath(desfiles[1]))
    ] + commands
    result = run(run_cmds)
    # Remove output of des_read_x
    is_header = True
    output = ""
    for line in result.split('\n'):
        if line.startswith("Reading preference file"):
            is_header = False
        elif not is_header:
            output += line
            output += "\n"
    output = output.replace("ERROR: Placement is not performanced.", "")
    return output


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


def get_arcs_on_wires(desfiles, wires, drivers_only=False, dir_override=dict()):
    """
    Use ispTcl to get a list of arcs sinking or sourcing a list of wires

    desfiles: a tuple (ncdfile, prffile)
    wires: list of canonical names of the wire
    drivers_only: only include arcs driving the wire in the output
    dir_override: Dictionary that specificies whether a net queried by ispTcl
    is a "sink" or "driver" when ispTcl returns "---" (since ISPTcl always puts
    the queried net on the RHS of an an arc). dir_override is only consulted if
    ispTcl returns "---" for the direction of a given net, and will
    additionally override drivers_only=False for any nets specified as
    "driver". Two additional strings are allowed: "ignore" to ignore "---"
    connections to/from the queried net, and "mark" to return the connection as
    an AmbiguousArc for later processing.

    Returns a map between wire name and a list of arc tuples (source, sink)
    """
    arcmap = {}
    wire_idx = 0

    # We can only process a limited number of nodes at a time, due to a memory leak in the Tcl API :facepalm:
    for i in range(0, len(wires), 10):
        subwires = wires[i:i+10]
        command = []
        for wire in subwires:
            command += ["dev_list_arc_by_node_name -to {} -num 100000".format(wire), 'prj_list']
        result = run_ncd_prf(desfiles, command)
        arcs = []
        for line in result.split('\n'):
            sline = line.strip()
            if sline == "":
                pass
            elif sline.startswith("MyIspProject"):
                arcmap[wires[wire_idx]] = list(arcs)
                wire_idx += 1
                arcs = []
            else:
                splitline = re.split('\s+', sline)
                assert len(splitline) >= 3
                if splitline[1].strip() == "-->":
                    arcs.append((splitline[0].strip(), splitline[2].strip()))
                elif splitline[1].strip() == "<--":
                    if not drivers_only:
                        arcs.append((splitline[2].strip(), splitline[0].strip()))
                elif splitline[1].strip() == "---":
                    if isinstance(dir_override, defaultdict):
                        # get() overrides defaultdict behavior, and a user may
                        # have a valid reason to provide a default such as
                        # ignore.
                        override = dir_override[wires[wire_idx]]
                    else:
                        override = dir_override.get(wires[wire_idx], "")
                    if override:
                        if override == "sink":
                            arcs.append((splitline[0].strip(), splitline[2].strip()))
                        elif override == "driver":
                            arcs.append((splitline[2].strip(), splitline[0].strip()))
                        elif override == "mark":
                            arcs.append(AmbiguousArc(splitline[0].strip(), splitline[2].strip()))
                        elif override == "ignore":
                            pass
                        else:
                            assert False, ("invalid override for wire {}".
                                            format(wires[wire_idx]))
                    else:
                        assert False, ("'---' found in ispTcl output, and no netdir_override"
                                       " was given for {wire}. Full line:\n{line}".
                                       format(wire=wires[wire_idx], line=line))
                else:
                    print (splitline)
                    assert False, "invalid output from Tcl command `dev_list_arcs`"
    return arcmap


def main():
    print(run([]))


if __name__ == "__main__":
    main()
