"""
Function to get the routed path of a net out of the ncl file
"""

import re
import sys


def slice_pin_to_net(site, pin):
    if is_slice(site):
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
    elif is_ebr(site):
        rc = site.split("_")[1]
        return "{}_J{}_EBR".format(rc, pin)
# TODO: Add other bel types?


def is_slice(site):
    return re.match(r'R\d+C\d+[ABCD]', site)

def is_ebr(site):
    return re.match(r'EBR_R\d+C\d+', site)


# Convert a parsed net to dict form (sink -> source)
def net_to_dict(signal, bels):
    drivers, loads, route = signal
    has_slice_driver = False
    has_slice_load = False
    route_map = {}
    for driver in drivers:
        if is_slice(bels[driver[0]]) or is_ebr(bels[driver[0]]):
            has_slice_driver = True
            route_map[slice_pin_to_net(bels[driver[0]], driver[1])] = driver
    if not has_slice_driver:
        return None
    for load in loads:
        if is_slice(bels[load[0]]) or is_ebr(bels[load[0]]):
            has_slice_load = True
            route_map[load] = slice_pin_to_net(bels[load[0]], load[1])
    if not has_slice_load:
        return None
    for arc in route:
        route_map[arc[1]] = arc[0]
    return route_map


# Print the route for a given net for a given source/sink pair
def print_route(net_dict, driver, load):
    route = []
    cursor = load
    route.append(cursor)
    while cursor in net_dict:
        cursor = net_dict[cursor]
        route.append(cursor)
    if cursor != driver:
        return
    route[0] = ".".join(route[0])
    route[-1] = ".".join(route[-1])
    print("\t" + " -> ".join(reversed(route)))


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
                    if line.endswith("\","):
                        line += f.readline().strip()
                    if "// loads" in line:
                        is_drv = False
                    elif "// drivers" in line:
                        continue
                    else:
                        m = re.match(r'\("?(?P<bel>[^,"]+)"?,\s*"?(?P<pin>[^,"]+)"?\)', line)
                        assert m, line
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
                while "{" not in f.readline().strip():
                    continue
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


def main():
    signals, bels = parse_ncl(sys.argv[1])
    for name, sig in sorted(signals.items()):
        nd = net_to_dict(sig, bels)
        drivers, loads, route = sig
        if nd is not None:
            print("Signal {}:".format(name))
            for load in loads:
                print_route(nd, drivers[0], load)
            print()


if __name__ == "__main__":
    main()
