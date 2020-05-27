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

brg_eclk_re = re.compile(r'R\d+C(\d+)_JBRGECLK\d+')


def is_global_brgeclk(wire):
    m = brg_eclk_re.match(wire)
    if not m:
        return False
    if m:
        x = int(m.group(1))
        return x > 5 and x < 67

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
                cib_eclk_re.match(wire) or
                is_global_brgeclk(wire))

def handle_family_net(tile, wire, prefix_pos, tile_pos, netname):
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
    else:
        return None
