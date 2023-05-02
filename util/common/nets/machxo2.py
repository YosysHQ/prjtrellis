import re
import tiles

# REGEXs for global/clock signals

# Globals
global_entry_re = re.compile(r'R\d+C\d+_VPRX(\d){2}00')
global_left_right_re = re.compile(r'R\d+C\d+_HPSX(\d){2}00')
global_up_down_re = re.compile(r'R\d+C\d+_VPTX(\d){2}00')
global_branch_re = re.compile(r'R\d+C\d+_HPBX(\d){2}00')

# High Fanout Secondary Nets
hfsn_entry_re = re.compile(r'R\d+C\d+_VSRX(\d){2}00')
hfsn_left_right_re = re.compile(r'R\d+C\d+_HSSX(\d){2}00')
# L2Rs control bidirectional portion of HFSNs!!
hfsn_l2r_re = re.compile(r'R\d+C\d+_HSSX(\d){2}00_[RL]2[LR]')
hfsn_up_down_re = re.compile(r'R\d+C\d+_VSTX(\d){2}00')
# HSBX(\d){2}00 are fixed connections to HSBX(\d){2}01s.
hfsn_branch_re = re.compile(r'R\d+C\d+_HSBX(\d){2}0[01]')

# Center Mux
# Outputs- entry to DCCs connected to globals (VPRXI -> DCC -> VPRX) *
center_mux_glb_out_re = re.compile(r'R\d+C\d+_VPRXCLKI\d+')
# Outputs- connected to ECLKBRIDGEs *
center_mux_ebrg_out_re = re.compile(r'R\d+C\d+_EBRG(\d){1}CLK(\d){1}')

# Inputs- CIB routing to HFSNs
cib_out_to_hfsn_re = re.compile(r'R\d+C\d+_JSNETCIB([TBRL]|MID)(\d){1}')
# Inputs- CIB routing to globals
cib_out_to_glb_re = re.compile(r'R\d+C\d+_J?PCLKCIB(L[TBRL]Q|MID|VIQ[TBRL])(\d){1}')
# Inputs- CIB routing to ECLKBRIDGEs
cib_out_to_eclk_re = re.compile(r'R\d+C\d+_J?ECLKCIB[TBRL](\d){1}')

# Inputs- Edge clocks dividers
eclk_out_re = re.compile(r'R\d+C\d+_J?[TBRL]CDIV(X(\d){1}|(\d){2})')
# Inputs- PLL
pll_out_re = re.compile(r'R\d+C\d+_J?[LR]PLLCLK\d+')
# Inputs- Clock pads
clock_pin_re = re.compile(r'R\d+C\d+_J?PCLK[TBLR]\d+')

# Part of center-mux but can also be found elsewhere
# DCCs connected to globals *
dcc_sig_re = re.compile(r'R\d+C\d+_J?(CLK[IO]|CE)(\d){1}[TB]?_DCC')

# DCMs- connected to DCCs on globals 6 and 7 *
dcm_sig_re = re.compile(r'R\d+C\d+_J?(CLK(\d){1}_|SEL|DCMOUT)(\d){1}_DCM')

# ECLKBRIDGEs- TODO
eclkbridge_sig_re = re.compile(r'R\d+C\d+_J?(CLK(\d){1}_|SEL|ECSOUT)(\d){1}_ECLKBRIDGECS')

# Oscillator output
osc_clk_re = re.compile(r'R\d+C\d+_J?OSC')

# Soft Error Detection Clock *
sed_clk_re = re.compile(r'R\d+C\d+_J?SEDCLKOUT')

# PLL/DLL Clocks
pll_clk_re = re.compile(r'R\d+C\d+_[TB]ECLK\d')

# PG/INRD/LVDS
pg_re = re.compile(r'R\d+C\d+_PG')
inrd_re = re.compile(r'R\d+C\d+_INRD')
lvds_re = re.compile(r'R\d+C\d+_LVDS')

# DDR
ddrclkpol_re = re.compile(r'R\d+C\d+_DDRCLKPOL')
dqsr90_re = re.compile(r'R\d+C\d+_DQSR90')
dqsw90_re = re.compile(r'R\d+C\d+_DQSW90')

def is_global(wire):
    """Return true if a wire is part of the global clock network"""
    return bool(global_entry_re.match(wire) or
        global_left_right_re.match(wire) or
        global_up_down_re.match(wire) or
        global_branch_re.match(wire) or
        hfsn_entry_re.match(wire) or
        hfsn_left_right_re.match(wire) or
        hfsn_l2r_re.match(wire) or
        hfsn_up_down_re.match(wire) or
        hfsn_branch_re.match(wire) or
        center_mux_glb_out_re.match(wire) or
        center_mux_ebrg_out_re.match(wire) or
        cib_out_to_hfsn_re.match(wire) or
        cib_out_to_glb_re.match(wire) or
        cib_out_to_eclk_re.match(wire) or
        eclk_out_re.match(wire) or
        pll_out_re.match(wire) or
        clock_pin_re.match(wire) or
        dcc_sig_re.match(wire) or
        dcm_sig_re.match(wire) or
        eclkbridge_sig_re.match(wire) or
        osc_clk_re.match(wire) or
        sed_clk_re.match(wire) or
        pll_clk_re.match(wire) or
        pg_re.match(wire) or
        inrd_re.match(wire) or
        lvds_re.match(wire) or
        ddrclkpol_re.match(wire) or
        dqsr90_re.match(wire) or
        dqsw90_re.match(wire))

def handle_family_net(tile, wire, prefix_pos, tile_pos, netname):
    if tile.startswith("CENTER") and global_left_right_re.match(wire):
        if prefix_pos[1] < tile_pos[1]:
            return "L_" + netname
        elif prefix_pos[1] > tile_pos[1]:
            return "R_" + netname
        else:
            assert False, "bad CENTER netname"
    elif "CIB_EBR" in tile and "10K" not in tile and global_up_down_re.match(wire) :
        if prefix_pos[0] < tile_pos[0]:
            return "U_" + netname
        elif prefix_pos[0] > tile_pos[0]:
            return "D_" + netname
        else:
            assert False, "bad CIB_EBR netname"
    elif global_branch_re.match(wire):
        return "BRANCH_" + netname
    elif is_global(wire):
        return "G_" + netname
    else:
        return None
