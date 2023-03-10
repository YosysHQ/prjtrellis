import re
import tiles

import ecp5
import machxo2


# General inter-tile routing
general_routing_re = re.compile('R\d+C\d+_[VH]\d{2}[NESWTLBR]\d{4}')
# CIB signals
cib_signal_re = re.compile('R\d+C\d+_J?[ABCDFMQ]\d')
# CIB clock/control signals
cib_control_re = re.compile('R\d+C\d+_J?(CLK|LSR|CEN|CE)\d')
# CIB bounce signals
cib_bounce_re = re.compile('R\d+C\d+_[NESW]BOUNCE')


def is_cib(wire):
    """Return true if a wire is considered part of the CIB (rather than
       a special function - EBR, DSP, etc)"""
    return bool(general_routing_re.match(wire) or
                cib_signal_re.match(wire) or
                cib_control_re.match(wire) or
                cib_bounce_re.match(wire))


h_wire_regex = re.compile(r'H(\d{2})([EW])(\d{2})(\d{2})')
v_wire_regex = re.compile(r'V(\d{2})([NS])(\d{2})(\d{2})')


def handle_edge_name(chip_size, tile_pos, wire_pos, netname, row_bias, col_bias):
    """
    At the edges of the device, canonical wire names do not follow normal naming conventions, as they
    would mean the nominal position of the wire would be outside the bounds of the chip. Before we add routing to the
    database, we must however normalise these names to what they would be if not near the edges, otherwise there is a
    risk of database conflicts, having multiple names for the same wire.

    chip_size: chip size as tuple (max_row, max_col)
    tile_pos: tile position as tuple (r, c)
    wire_pos: wire nominal position as tuple (r, c)
    netname: wire name without position prefix
    row_bias: If "1", use Lattice's 1-based row indexing
    col_bias: If "1", use Lattice's 1-based column indexing

    Returns a tuple (netname, wire_pos)
    """
    hm = h_wire_regex.match(netname)
    vm = v_wire_regex.match(netname)
    if hm:
        # MachXO2 doesn't appear to have edge nets for span-1s.
        if hm.group(1) == "01":
            if tile_pos[1] == chip_size[1] - 1:
                # H01xyy00 --> x+1, H01xyy01
                assert hm.group(4) == "00"
                return "H01{}{}01".format(hm.group(2), hm.group(3)), (wire_pos[0], wire_pos[1] + 1)
        elif hm.group(1) == "02":
            if tile_pos[1] == (1 - col_bias):
                # H02E0002 --> x-1, H02E0001
                # H02W0000 --> x-1, H02W00001
                if hm.group(2) == "E" and wire_pos[1] == (1 - col_bias) and hm.group(4) == "02":
                    return "H02E{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] - 1)
                elif hm.group(2) == "W" and wire_pos[1] == (1 - col_bias) and hm.group(4) == "00":
                    return "H02W{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] - 1)
            elif tile_pos[1] == (chip_size[1] - (1 - col_bias)):
                # H02E0000 --> x+1, H02E0001
                # H02W0002 --> x+1, H02W00001
                if hm.group(2) == "E" and wire_pos[1] == (chip_size[1] - (1 - col_bias)) and hm.group(4) == "00":
                    return "H02E{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] + 1)
                elif hm.group(2) == "W" and wire_pos[1] == (chip_size[1] - (1 - col_bias)) and hm.group(4) == "02":
                    return "H02W{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] + 1)
        # Bias only affects columns... span-6s seem to work fine without
        # a correction.
        elif hm.group(1) == "06":
            if tile_pos[1] <= 5:
                # x-2, H06W0302 --> x-3, H06W0303
                # x-2, H06E0004 --> x-3, H06E0003
                # x-1, H06W0301 --> x-3, H06W0303
                # x-1, H06E0305 --> x-3, H06E0303
                if hm.group(2) == "W":
                    return "H06W{}03".format(hm.group(3)), (wire_pos[0], wire_pos[1] - (3 - int(hm.group(4))))
                elif hm.group(2) == "E":
                    return "H06E{}03".format(hm.group(3)), (wire_pos[0], wire_pos[1] - (int(hm.group(4)) - 3))
            if tile_pos[1] >= (chip_size[1] - 5):
                # x+2, H06W0304 --> x+3, H06W0303
                # x+2, H06E0302 --> x+3, H06E0303
                if hm.group(2) == "W":
                    return "H06W{}03".format(hm.group(3)), (wire_pos[0], wire_pos[1] + (int(hm.group(4)) - 3))
                elif hm.group(2) == "E":
                    return "H06E{}03".format(hm.group(3)), (wire_pos[0], wire_pos[1] + (3 - int(hm.group(4))))
        else:
            assert False
    if vm:
        if vm.group(1) == "01":
            if tile_pos[0] == 1:
                # V01N000 --> y-1, V01N0001
                if wire_pos[0] == 1 and vm.group(2) == "N" and vm.group(4) == "00":
                    return "V01{}{}01".format(vm.group(2), vm.group(3)), (wire_pos[0] - 1, wire_pos[1])
                if wire_pos[0] == 1 and vm.group(2) == "S" and vm.group(4) == "01":
                    return "V01{}{}00".format(vm.group(2), vm.group(3)), (wire_pos[0] - 1, wire_pos[1])
        elif vm.group(1) == "02":
            if tile_pos[0] == 1:
                # V02S0002 --> y-1, V02S0001
                # V02N0000 --> y-1, V02N0001
                if vm.group(2) == "S" and wire_pos[0] == 1 and vm.group(4) == "02":
                    return "V02S{}01".format(vm.group(3)), (wire_pos[0] - 1, wire_pos[1])
                elif vm.group(2) == "N" and wire_pos[0] == 1 and vm.group(4) == "00":
                    return "V02N{}01".format(vm.group(3)), (wire_pos[0] - 1, wire_pos[1])
            elif tile_pos[0] == (chip_size[0] - 1):
                # V02S0000 --> y+1, V02S0001
                # V02N0002 --> y+1, V02N00001
                if vm.group(2) == "S" and wire_pos[0] == (chip_size[0] - 1) and vm.group(4) == "00":
                    return "V02S{}01".format(vm.group(3)), (wire_pos[0] + 1, wire_pos[1])
                elif vm.group(2) == "N" and wire_pos[0] == (chip_size[0] - 1) and vm.group(4) == "02":
                    return "V02N{}01".format(vm.group(3)), (wire_pos[0] + 1, wire_pos[1])
        elif vm.group(1) == "06":
            if tile_pos[0] <= 5:
                # y-2, V06N0302 --> y-3, H06W0303
                # y-2, V06S0004 --> y-3, V06S0003
                # y-1, V06N0301 --> y-3, V06N0303
                # y-1, V06S0005 --> y-3, V06S0003
                if vm.group(2) == "N":
                    return "V06N{}03".format(vm.group(3)), (wire_pos[0] - (3 - int(vm.group(4))), wire_pos[1])
                elif vm.group(2) == "S":
                    return "V06S{}03".format(vm.group(3)), (wire_pos[0] - (int(vm.group(4)) - 3), wire_pos[1])
            if tile_pos[0] >= (chip_size[0] - 5):
                # y+2, V06N0304 --> y+3, V06N0303
                # y+2, V06S0302 --> x+3, V06S0303
                if vm.group(2) == "N":
                    return "V06N{}03".format(vm.group(3)), (wire_pos[0] + (int(vm.group(4)) - 3), wire_pos[1])
                elif vm.group(2) == "S":
                    return "V06S{}03".format(vm.group(3)), (wire_pos[0] + (3 - int(vm.group(4))), wire_pos[1])
        else:
            assert False
    return netname, wire_pos


def normalise_name(chip_size, tile, wire, family):
    """
    Wire name normalisation for tile wires and fuzzing
    All net names that we have access too are canonical, global names
    These are thus no good for building up a database that is the same for all tiles
    of a given type, as the names will be different in each location.

    Lattice names are of the form R{r}C{c}_{NETNAME}

    Hence, we normalise names in the following way:
     - Global wires have the prefix "G_" added
     - Wires where (r, c) correspond to the current tile have their prefix removed
     - Wires to the left (in TAP_DRIVEs) are given the prefix L, and wires to the right
       are given the prefix R
     - Wires within a DQS group are given the prefix DQSG_
     - Wires within a bank are given the prefix BNK_
     - Other wires are given a relative position prefix using the syntax
       ([NS]\d+)?([EW]\d+)?_
       so a wire whose nominal location is 6 tiles up would be given a prefix N6_
       a wire whose nominal location is 2 tiles down and 1 tile right would be given a prefix
       S2E1_

    TODO: this is more complicated at the edges of the device, where irregular names are used to keep the row and column
    of the nominal position in bounds. Extra logic will be needed to catch and regularise these cases.

    chip_size: chip size as tuple (max_row, max_col)
    tile: name of the relevant tile
    wire: full Lattice name of the wire
    family: Device family to normalise. Affects column indexing (e.g. MachXO2 uses 1-based
          column indexing) and naming of global wires, TAP_DRIVEs, DQS, bank wires,
          etc..

    Returns the normalised netname
    """

    if family == "ECP5":
        def handle_family_net(tile, wire, prefix_pos, tile_pos, netname):
            return ecp5.handle_family_net(tile, wire, prefix_pos, tile_pos, netname)
        row_bias = 0
        col_bias = 0
    elif family.startswith("MachXO"):
        def handle_family_net(tile, wire, prefix_pos, tile_pos, netname):
            return machxo2.handle_family_net(tile, wire, prefix_pos, tile_pos, netname)
        row_bias = 1 if family == "MachXO" else 0
        col_bias = 1
    else:
        raise ValueError("Unknown device family.")

    upos = wire.index("_")
    prefix = wire[:upos]
    prefix_pos = tiles.pos_from_name(prefix, chip_size, row_bias, col_bias)
    tile_pos = tiles.pos_from_name(tile, chip_size, row_bias, col_bias)
    netname = wire[upos+1:]

    family_net = handle_family_net(tile, wire, prefix_pos, tile_pos, netname)
    if family_net:
        return family_net

    netname, prefix_pos = handle_edge_name(chip_size, tile_pos, prefix_pos, netname, row_bias, col_bias)
    if tile_pos == prefix_pos:
        return netname
    else:
        prefix = ""
        if prefix_pos[0] < tile_pos[0]:
            prefix += "N{}".format(tile_pos[0] - prefix_pos[0])
        elif prefix_pos[0] > tile_pos[0]:
            prefix += "S{}".format(prefix_pos[0] - tile_pos[0])
        if prefix_pos[1] > tile_pos[1]:
            prefix += "E{}".format(prefix_pos[1] - tile_pos[1])
        elif prefix_pos[1] < tile_pos[1]:
            prefix += "W{}".format(tile_pos[1] - prefix_pos[1])
        return prefix + "_" + netname


rel_netname_re = re.compile(r'^([NS]\d+)?([EW]\d+)?_.*')

def canonicalise_name(chip_size, tile, wire, row_bias, col_bias):
    """
    Convert a normalised name in a given tile back to a canonical global name
    :param chip_size: chip size as tuple (max_row, max_col)
    :param tile: tilename
    :param wire: normalised netname
    :return: global canonical netname
    """
    if wire.startswith("G_"):
        return wire
    m = rel_netname_re.match(wire)
    tile_pos = tiles.pos_from_name(tile, chip_size, row_bias, col_bias)
    wire_pos = tile_pos
    if m:
        assert len(m.groups()) >= 1
        for g in m.groups():
            if g is not None:
                delta = int(g[1:])
                if g[0] == "N":
                    wire_pos = (wire_pos[0] - delta, wire_pos[1])
                elif g[0] == "S":
                    wire_pos = (wire_pos[0] + delta, wire_pos[1])
                elif g[0] == "W":
                    wire_pos = (wire_pos[0], wire_pos[1] - delta)
                elif g[0] == "E":
                    wire_pos = (wire_pos[0], wire_pos[1] + delta)
        wire = wire.split("_", 1)[1]
    if wire_pos[0] < 0 or wire_pos[0] > chip_size[0] or wire_pos[1] < 0 or wire_pos[1] > chip_size[1]:
        return None #TODO: edge normalisation
    return "R{}C{}_{}".format(wire_pos[0], wire_pos[1], wire)
