import re
import tiles

# REGEXs for global/clock signals

# Oscillator output
osc_clk_re = re.compile(r'R\d+C\d+_J?OSC')

def is_global(wire):
    """Return true if a wire is part of the global clock network"""
    return bool(osc_clk_re.match(wire))

def handle_family_net(tile, wire, prefix_pos, tile_pos, netname):
    raise NotImplementedError("MachXO2 device family not implemented.")
