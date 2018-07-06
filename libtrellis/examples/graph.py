#!/usr/bin/env python3
"""
Testing the routing graph generator
"""
import pytrellis
import sys

pytrellis.load_database("../../database")
chip = pytrellis.Chip("LFE5U-25F")
rg = chip.get_routing_graph()
