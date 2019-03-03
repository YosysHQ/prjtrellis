"""
This helps fix missing tile positions in the MachXO2 family
"""

import re, sys
import database

rc_regex = re.compile(r"[A-Za-z0-9_]*R(\d+)C(\d+)")
# MachXO2-specific
center_regex = re.compile(r"CENTER(\d+)")
centerb_regex = re.compile(r"CENTER_B")
centert_regex = re.compile(r"CENTER_T")
centerebr_regex = re.compile(r"CENTER_EBR(\d+)")
t_regex = re.compile(r"[A-Za-z0-9_]*T(\d+)")
b_regex = re.compile(r"[A-Za-z0-9_]*B(\d+)")
l_regex = re.compile(r"[A-Za-z0-9_]*L(\d+)")
r_regex = re.compile(r"[A-Za-z0-9_]*R(\d+)")

def append_position(left_side, row, col):
    return left_side + "_R" + str(row) + "C" + str(col)

def update_name(name, center_col, ebr_row, right, bottom):
    # Match in order of most-specific to least-specific
    # (E.g. CENTER matches "R" regex too)
    left = 1
    top = 0

    row = top
    col = left

    rc = rc_regex.match(name)
    if rc:
        # no need to rename
        return name

    centert = centert_regex.match(name)
    if centert:
        row = top
        col = center_col
        return append_position(name, row, col)

    centerb = centerb_regex.match(name)
    if centerb:
        row = bottom
        col = center_col
        return append_position(name, row, col)

    centerebr = centerebr_regex.match(name)
    if centerebr:
        row = ebr_row
        col = center_col+1
        return append_position(name, row, col)

    center = center_regex.match(name)
    if center:
        row = int(center.group(1))
        col = center_col
        return append_position(name, row, col)

    t = t_regex.match(name)
    if t:
        row = top
        col = int(t.group(1))
        return append_position(name, row, col)

    b = b_regex.match(name)
    if b:
        row = bottom
        col = int(b.group(1))
        return append_position(name, row, col)

    l = l_regex.match(name)
    if l:
        row = int(l.group(1))
        col = left
        return append_position(name, row, col)

    r = r_regex.match(name)
    if r:
        row = int(r.group(1))
        col = right
        return append_position(name, row, col)

def fix_name(name, device):

    device_info = database.get_devices()["families"]["MachXO2"]["devices"][device]
    max_row = device_info["max_row"]
    max_col = device_info["max_col"]

    if (device == 'LCMXO2-256HC'):
        center_col = 5
        ebr_row = 0 # don't care
    elif (device == 'LCMXO2-1200HC'):
        center_col = 13
        ebr_row = 6
    elif (device == 'LCMXO2-4000HC'):
        center_col = 16
        ebr_row = 11
    else:
        print("unknown device: " + device)
        sys.exit(1)

    return update_name(name, center_col, ebr_row, max_col, max_row)
