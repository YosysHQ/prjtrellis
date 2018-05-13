import re
import tiles

# REGEXs for global/clock signals

# Globals including spine inputs, TAP_DRIVE inputs and TAP_DRIVE outputs
global_spine_tap_re = re.compile(r'R\d+C\d+_[HV]P[TLBR]X(\d){2}00')
# CMUX outputs
global_cmux_out_re = re.compile(r'R\d+C\d+_[UL][LR]PCLK\d+')
# CMUX inputs
global_cmux_in_re = re.compile(r'R\d+C\d+_[HV]PF[NESW](\d){2}00')
# PLL outputs
pll_out_re = re.compile(r'R\d+C\d+_J?[UL][LR][QC]PLL\dCLKO[PS]\d?')
# CIB clock inputs
cib_clk_re = re.compile(r'R\d+C\d+_J?[ULTB][LR][QCM]PCLKCIB\d+')
# Oscillator output
osc_clk_re = re.compile(r'R\d+C\d+_J?OSC')
# Clock dividers
cdivx_clk_re = re.compile(r'R\d+C\d+_J?[UL]CDIVX\d+')
# SED clock output
sed_clk_re = re.compile(r'R\d+C\d+_J?SEDCLKOUT')


def is_global(wire):
    """Return true if a wire is part of the global clock network"""
    return bool(global_spine_tap_re.match(wire) or
                global_cmux_out_re.match(wire) or
                global_cmux_in_re.match(wire) or
                pll_out_re.match(wire) or
                cib_clk_re.match(wire) or
                osc_clk_re.match(wire) or
                cdivx_clk_re.match(wire) or
                sed_clk_re.match(wire))


# General inter-tile routing
general_routing_re = re.compile('R\d+C\d+_[VH]\d{2}[NESWTLBR]\d{4}')
# CIB signals
cib_signal_re = re.compile('R\d+C\d+_J?[ABCDFMQ]\d')
# CIB clock/control signals
cib_control_re = re.compile('R\d+C\d+_J?(CLK|LSR)\d')


def is_cib(wire):
    """Return true if a wire is considered part of the CIB (rather than
       a special function - EBR, DSP, etc)"""
    return bool(general_routing_re.match(wire) or
                cib_signal_re.match(wire) or
                cib_control_re.match(wire))


def normalise_name(tile, wire):
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
     - Other wires are given a relative position prefix using the syntax
       ([NS]\d+)?([EW]\d+)?_
       so a wire whose nominal location is 6 tiles up would be given a prefix N6_
       a wire whose nominal location is 2 tiles down and 1 tile right would be given a prefix
       S2E1_

    TODO: this is more complicated at the edges of the device, where irregular names are used to keep the row and column
    of the nominal position in bounds. Extra logic will be needed to catch and regularise these cases.
    """
    upos = wire.index("_")
    prefix = wire[:upos]
    prefix_pos = tiles.pos_from_name(prefix)
    tile_pos = tiles.pos_from_name(tile)
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
    elif tile_pos == prefix_pos:
        return netname
    else:
        prefix = ""
        if prefix_pos[0] > tile_pos[0]:
            prefix += "N{}".format(prefix_pos[0] - tile_pos[0])
        elif prefix_pos[0] < tile_pos[0]:
            prefix += "S{}".format(tile_pos[0] - prefix_pos[0])
        if prefix_pos[1] > tile_pos[1]:
            prefix += "E{}".format(prefix_pos[1] - tile_pos[1])
        elif prefix_pos[1] < tile_pos[1]:
            prefix += "W{}".format(tile_pos[1] - prefix_pos[1])
        return prefix + "_" + netname
