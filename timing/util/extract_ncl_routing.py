"""
Function to get the routed path of a net out of the ncl file
"""

import re


def slice_pin_to_net(site, pin):
    rc = site[:-1]
    slice = site[-1]
    assert slice in "ABCD"
    slicen = "ABCD".index(slice)
    if pin in ("A0", "A1", "B0", "B1", "C0", "C1", "D0", "D1", "DI0", "DI1", "M0", "M1", "F0", "F1", "Q0", "Q1"):
        pin_idx = int(pin[-1])
        pin_name = pin[:-1]
        return "{}_{}{}_SLICE".format(rc, pin_name, 2 * slicen + pin_idx)
    elif pin in ("CLK", "CE", "LSR", "WCK", "WRE"):
        return "{}_{}{}_SLICE".format(rc, pin, slicen)
    elif pin == "FCI":
        if slice == "A":
            return "{}_FCI_SLICE".format(rc)
        else:
            return "{}_FCI{}_SLICE".format(rc, slice)
    elif pin == "FCO":
        if slice == "D":
            return "{}_FCO_SLICE".format(rc)
        else:
            return "{}_FCO{}_SLICE".format(rc, slice)
    elif pin in ("FXA", "FXB") or pin.startswith("WAD") or pin.startswith("WD"):
        return "{}_{}{}_SLICE".format(rc, pin, slice)
    elif pin == "OFX0":
        return "{}_F5{}_SLICE".format(rc, pin, slice)
    elif pin == "OFX1":
        return "{}_FX{}_SLICE".format(rc, pin, slice)
    else:
        assert False, "unhandled pin {} on slice {}".format(pin, slice)

# TODO: Add other bel types?


# Not a full parser, just for standard Diamond NCLs
def parse_ncl(filename):
    signals = {} # name -> (drivers, loads, route)
    bels = {}
    with open(filename, 'r') as f:
        def discard_block():
            while True:
                line = f.readline().strip()
                if "{" in line:
                    discard_block()
                elif "}" in line:
                    return

        def process_comp(name):
            while True:
                line = f.readline().strip()
                if "{" in line:
                    discard_block()
                elif "}" in line:
                    return
                if line.startswith("site"):
                    bels[name] = line.split(' ', 1)[1].replace(";", "").strip()

        def process_signal(name):
            drivers = []
            loads = []
            route = []

            def process_pins():
                is_drv = True
                while True:
                    line = f.readline().strip()
                    if "// loads" in line:
                        is_drv = False
                    elif "// drivers" in line:
                        continue
                    else:
                        m = re.match(r'\("?(?P<bel>[^,"]+)"?,\s*"?(?P<pin>[^,"]+)"?\)', line)
                        assert m
                        pin = (m.group("bel"), m.group("pin"))
                        if is_drv:
                            drivers.append(pin)
                        else:
                            loads.append(pin)
                    if ";" in line:
                        return

            def process_route():
                while True:
                    line = f.readline().strip()
                    m = re.match(r'(?P<a>[A-Za-z0-9_]+)\.(?P<b>[A-Za-z0-9_]+)', line)
                    assert m
                    route.append((m.group("a"), m.group("b")))
                    if ";" in line:
                        return

            while True:
                line = f.readline().strip()
                if "{" in line:
                    discard_block()
                elif "}" in line:
                    signals[name] = (drivers, loads, route)
                    return
                elif "signal-pins" in line:
                    process_pins()
                elif "route" in line:
                    process_route()

        while True:
            line = f.readline()
            if line == "":
                break
            line = line.strip()
            if line.startswith("comp"):
                assert "{" in f.readline().strip()
                process_comp(line.split(' ', 1)[1].strip().replace('"', ''))
            elif line.startswith("signal"):
                assert "{" in f.readline().strip()
                process_signal(line.split(' ', 1)[1].strip().replace('"', ''))
            elif line.startswith("device") or line.startswith("property"):
                assert "{" in f.readline().strip()
                discard_block()
            else:
                continue
    return signals, bels
