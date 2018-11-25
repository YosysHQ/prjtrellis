import re
import tiles

# REGEXs for global/clock signals

# Globals including spine inputs, TAP_DRIVE inputs and TAP_DRIVE outputs
global_spine_tap_re = re.compile(r'R\d+C\d+_[HV]P[TLBR]X(\d){2}00')
# CMUX outputs
global_cmux_out_re = re.compile(r'R\d+C\d+_[UL][LR]PCLK\d+')
# CMUX inputs
global_cmux_in_re = re.compile(r'R\d+C\d+_[HV]PF[NESW](\d){2}00')
# Clock pins
clock_pin_re = re.compile(r'R\d+C\d+_J?PCLK[TBLR]\d+')
# PLL global outputs
pll_out_re = re.compile(r'R\d+C\d+_J?[UL][LR][QC]PLL\dCLKO[PS]\d?')

# CIB clock inputs
cib_clk_re = re.compile(r'R\d+C\d+_J?[ULTB][LR][QCM]PCLKCIB\d+')
# Oscillator output
osc_clk_re = re.compile(r'R\d+C\d+_J?OSC')
# Clock dividers
cdivx_clk_re = re.compile(r'R\d+C\d+_J?[UL]CDIVX\d+')
# SED clock output
sed_clk_re = re.compile(r'R\d+C\d+_J?SEDCLKOUT')

# SERDES reference clocks
pcs_clk_re = re.compile(r'R\d+C\d+_J?PCS[AB][TR]XCLK\d')


# DDRDEL delay signals
ddr_delay_re = re.compile(r'R\d+C\d+_[UL][LR]DDRDEL')

# DCC signals
dcc_clk_re = re.compile(r'R\d+C\d+_J?(CLK[IO]|CE)_[BLTR]?DCC(\d+|[BT][LR])')
# DCC inputs
dcc_clki_re = re.compile(r'R\d+C\d+_[BLTR]?DCC(\d+|[BT][LR])CLKI')
# DCS signals
dcs_sig_re = re.compile(r'R\d+C\d+_J?(CLK\d|SEL\d|DCSOUT|MODESEL)_DCS\d')
# DCS clocks
dcs_clk_re = re.compile(r'R\d+C\d+_DCS\d(CLK\d)?')
# Misc. center clocks
center_clk_re = re.compile(r'R\d+C\d+_J?(LE|RE)CLK\d')

# Shared DQS signals
dqs_ssig_re = re.compile(r'R\d+C\d+_(DQS[RW]\d*|(RD|WR)PNTR\d)$')

# Bank edge clocks
bnk_eclk_re = re.compile('R\d+C\d+_BANK\d+(ECLK\d+)')
# CIB ECLK inputs
cib_eclk_re = re.compile(r'R\d+C\d+_J?[ULTB][LR][QCM]ECLKCIB\d+')



def is_global(wire):
    """Return true if a wire is part of the global clock network"""
    return bool(global_spine_tap_re.match(wire) or
                global_cmux_out_re.match(wire) or
                global_cmux_in_re.match(wire) or
                clock_pin_re.match(wire) or
                pll_out_re.match(wire) or
                cib_clk_re.match(wire) or
                osc_clk_re.match(wire) or
                cdivx_clk_re.match(wire) or
                sed_clk_re.match(wire) or
                ddr_delay_re.match(wire) or
                dcc_clk_re.match(wire) or
                dcc_clki_re.match(wire) or
                dcs_sig_re.match(wire) or
                dcs_clk_re.match(wire) or
                pcs_clk_re.match(wire) or
                center_clk_re.match(wire) or
                cib_eclk_re.match(wire))


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


def handle_edge_name(chip_size, tile_pos, wire_pos, netname):
    """
    At the edges of the device, canonical wire names do not follow normal naming conventions, as they
    would mean the nominal position of the wire would be outside the bounds of the chip. Before we add routing to the
    database, we must however normalise these names to what they would be if not near the edges, otherwise there is a
    risk of database conflicts, having multiple names for the same wire.

    chip_size: chip size as tuple (max_row, max_col)
    tile_pos: tile position as tuple (r, c)
    wire_pos: wire nominal position as tuple (r, c)
    netname: wire name without position prefix

    Returns a tuple (netname, wire_pos)
    """
    hm = h_wire_regex.match(netname)
    vm = v_wire_regex.match(netname)
    if hm:
        if hm.group(1) == "01":
            if tile_pos[1] == chip_size[1] - 1:
                # H01xyy00 --> x+1, H01xyy01
                assert hm.group(4) == "00"
                return "H01{}{}01".format(hm.group(2), hm.group(3)), (wire_pos[0], wire_pos[1] + 1)
        elif hm.group(1) == "02":
            if tile_pos[1] == 1:
                # H02E0002 --> x-1, H02E0001
                # H02W0000 --> x-1, H02W00001
                if hm.group(2) == "E" and wire_pos[1] == 1 and hm.group(4) == "02":
                    return "H02E{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] - 1)
                elif hm.group(2) == "W" and wire_pos[1] == 1 and hm.group(4) == "00":
                    return "H02W{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] - 1)
            elif tile_pos[1] == (chip_size[1] - 1):
                # H02E0000 --> x+1, H02E0001
                # H02W0002 --> x+1, H02W00001
                if hm.group(2) == "E" and wire_pos[1] == (chip_size[1] - 1) and hm.group(4) == "00":
                    return "H02E{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] + 1)
                elif hm.group(2) == "W" and wire_pos[1] == (chip_size[1] - 1) and hm.group(4) == "02":
                    return "H02W{}01".format(hm.group(3)), (wire_pos[0], wire_pos[1] + 1)
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


def normalise_name(chip_size, tile, wire, bias):
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
    bias: Use 1-based column indexing

    Returns the normalised netname
    """
    upos = wire.index("_")
    prefix = wire[:upos]
    prefix_pos = tiles.pos_from_name(prefix, chip_size, bias)
    tile_pos = tiles.pos_from_name(tile, chip_size, bias)
    netname = wire[upos+1:]
    if tile.startswith("TAP") and netname.startswith("H"):
        if prefix_pos[1] < tile_pos[1]:
            return "L_" + netname
        elif prefix_pos[1] > tile_pos[1]:
            return "R_" + netname
        else:
            assert False, "bad TAP_DRIVE netname"
    elif is_global(wire):
        return "G_" + netname
    elif dqs_ssig_re.match(wire):
        return "DQSG_" + netname
    elif bnk_eclk_re.match(wire):
        if "ECLK" in tile:
            return "G_" + netname
        else:
            return "BNK_" + bnk_eclk_re.match(wire).group(1)
    elif netname in ("INRD", "LVDS"):
        return "BNK_" + netname
    netname, prefix_pos = handle_edge_name(chip_size, tile_pos, prefix_pos, netname)
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


def canonicalise_name(chip_size, tile, wire, bias):
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
    tile_pos = tiles.pos_from_name(tile, chip_size, bias)
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


# Useful functions for constructing nets.
def char_range(c1, c2):
    """Generates the characters from `c1` to `c2`, exclusive."""
    for c in range(ord(c1), ord(c2)):
        yield chr(c)

def net_product(net_list, range_iter):
    return [n.format(*i) for i in range_iter for n in net_list]


def main():
    assert is_global("R2C7_HPBX0100")
    assert is_global("R24C12_VPTX0700")
    assert is_global("R22C40_HPRX0300")
    assert is_global("R34C67_ULPCLK7")
    assert not is_global("R22C67_H06E0003")
    assert is_global("R24C67_VPFS0800")
    assert is_global("R1C67_JPCLKT01")

    assert is_cib("R47C61_Q4")
    assert is_cib("R47C58_H06W0003")
    assert is_cib("R47C61_CLK0")

    assert normalise_name((95, 126), "R48C26", "R48C26_B1", 0) == "B1"
    assert normalise_name((95, 126), "R48C26", "R48C26_HPBX0600", 0) == "G_HPBX0600"
    assert normalise_name((95, 126), "R48C26", "R48C25_H02E0001", 0) == "W1_H02E0001"
    assert normalise_name((95, 126), "R48C1", "R48C1_H02E0002", 0) == "W1_H02E0001"
    assert normalise_name((95, 126), "R82C90", "R79C90_V06S0003", 0) == "N3_V06S0003"
    assert normalise_name((95, 126), "R5C95", "R3C95_V06S0004", 0) == "N3_V06S0003"
    assert normalise_name((95, 126), "R1C95", "R1C95_V06S0006", 0) == "N3_V06S0003"
    assert normalise_name((95, 126), "R3C95", "R2C95_V06S0005", 0) == "N3_V06S0003"
    assert normalise_name((95, 126), "R82C95", "R85C95_V06N0303", 0) == "S3_V06N0303"
    assert normalise_name((95, 126), "R90C95", "R92C95_V06N0304", 0) == "S3_V06N0303"
    assert normalise_name((95, 126), "R93C95", "R94C95_V06N0305", 0) == "S3_V06N0303"


if __name__ == "__main__":
    main()
