import pytrellis
import database
import itertools
import json
import argparse

# This mirrors center_map in libtrellis. Somehow expose center_map.
center_map = {
    # LCMXO2-256
    (7, 9): (3, 4),
    # LCMXO2-640
    (8, 17): (3, 7),
    # LCMXO2-1200, LCMXO3-1300
    (12, 21): (6, 12),
    # LCMXO2-2000, LCMXO3-2100
    (15, 25): (8, 13),
    # LCMXO2-4000, LCMXO3-4300
    (22, 31): (11, 15),
    # LCMXO2-7000, LCMXO3-6900
    (27, 40): (13, 18),
    # LCMXO3-9400
    (31, 48): (15, 24),
}

row_spans = {
    # LCMXO2-256
    (7, 9): (0, 0),
    # LCMXO2-640
    (8, 17): (0, 0),
    # LCMXO2-1200, LCMXO3-1300
    (12, 21): (5, 5),
    # LCMXO2-2000, LCMXO3-2100
    (15, 25): (0, 0),
    # LCMXO2-4000, LCMXO3-4300
    (22, 31): (0, 0),
    # LCMXO2-7000, LCMXO3-6900
    (27, 40): (0, 0),
    # LCMXO3-9400
    (31, 48): (0, 0),
}

start_stride = {
    # LCMXO2-256
    (7, 9): (0, 4),
    # LCMXO2-640
    (8, 17): (1, 5),
    # LCMXO2-1200, LCMXO3-1300
    (12, 21): (0, 4),
    # LCMXO2-2000, LCMXO3-2100
    (15, 25): (3, 7),
    # LCMXO2-4000, LCMXO3-4300
    (22, 31): (1, 5),
    # LCMXO2-7000, LCMXO3-6900
    (27, 40): (2, 6),
    # LCMXO3-9400
    (31, 48): (0, 4),
}

# There are 8 global nets. For a given column, globals are routed in pairs.
# Convert from a pair to an index of global pairs.
global_group = {
    (0, 4): 0,
    (1, 5): 1,
    (2, 6): 2,
    (3, 7): 3
}

inv_global_group = [(0, 4), (1, 5), (2, 6), (3, 7)]

# Generate which columns route which globals.
def column_routing(num_cols, col_1=(0, 4)):
    i = 1
    stride = (0, 4, 1, 5, 2, 6, 3, 7)

    # Find which globals in column 0 will be routed, given which globals
    # are routed in column 1.
    #
    # Column "0" in prjtrellis ("1" in Lattice numbering) always has six of
    # the globals routed. The explanation for the final column applies here,
    # except we are missing the four globals that would span from the right
    # side of the U/D routing connection (and thus approach column 0 from the
    # left).
    col_0 = []

    for g in stride:
        if g not in col_1:
            col_0.append(g)

    yield tuple(col_0)

    # Rotate the stride so the correct pair of globals are at the beginning
    # of the list.
    idx = global_group[col_1]*2
    rotated_stride = stride[idx:] + stride[:idx]

    # Take two at a time: https://docs.python.org/3/library/functions.html#zip
    col_iter = itertools.cycle(zip(*[iter(rotated_stride)]*2))

    for c in col_iter:
        yield c

        i = i + 1
        if i >= num_cols:
            break

    # The final column will have 4 globals routed- the two expected globals
    # for the column as well as the next two globals in the stride. This is
    # because BRANCH wires that connect globals to CIBs span two columns to the
    # right and one column to the left from where they connect to U/D routing.
    # Since we are at the right bound of the chip, the globals we would expect
    # to span from the left side of the U/D routing (and thus approach the
    # final column from the right) don't physically exist! So we take care
    # of them here.
    yield next(col_iter) + next(col_iter)

# Generate how far branches span (exclusive span, in tiles) from u/d column
# routing.
def branch_spans(num_cols, col_1=(0, 4)):
    i = 1
    col_0 = [None, (0, 0), (0, 1), (0, 2)]
    default = {
        (0, 4): [(1, 2), None, None, None],
        (1, 5): [None, (1, 2), None, None],
        (2, 6): [None, None, (1, 2), None],
        (3, 7): [None, None, None, (1, 2)]
    }

    idx = global_group[col_1]
    # This works, somehow...
    rotated_col0 = col_0[-idx:] + col_0[:-idx]

    yield rotated_col0

    col_iter = itertools.islice(column_routing(num_cols, col_1), 1, None)
    for c in col_iter:
        yield default[c]

        i = i + 1
        if i > (num_cols - 2):
            break

    # At the second-to-last row of the chip, the branch, which spans two
    # columns to the right, will be truncated by the chip's edge.
    second_last = [None, None, None, None]
    curr_idx = global_group[next(col_iter)]
    second_last[curr_idx] = (1, 1)
    yield second_last

    # At the last row of the chip, BRANCHES connecting to U/D routing (which
    # which normally span two column to the right) will be truncated by the
    # chip's edge.
    last = [None, None, None, None]
    curr_idx = (curr_idx + 1) % 4
    last[curr_idx] = (1, 0)

    # The remaining two globals should come from BRANCHES from the right.
    # But since we run into the chip's edge, we route them to the current
    # column (and only the current column!) here.
    curr_idx = (curr_idx + 1) % 4
    last[curr_idx] = (0, 0)
    yield last

# 256: 9, (0, 4): L: 3, 7 has DCCs R: 0, 4 has DCCs
# 640: 17, (1, 5): L: 0, 4 has DCCs R: 1, 5 has DCCs
# 1200: 21, (0, 4): L: 3, 7 has DCCs R: 0, 4 has DCCs
# 2000: 25, (3, 7), L: 2, 6 has DCCs R: 3, 7 has DCCs
# 4000: 31, (1, 5), L: 0, 4 has DCCs R: 3, 7 has DCCs
# 7000: 40, (2, 6), L: 1, 5 has DCCs R: 1, 5 has DCCs (both top and bottom)
# use fuzzer 024-glb-branch on column 2 (CIB_RxC2:CIB_EBR1)
def main(args):
    pytrellis.load_database(database.get_db_root())
    ci = pytrellis.get_chip_info(pytrellis.find_device_by_name(args.device))
    chip_size = (ci.max_row, ci.max_col)

    globals_json = dict()
    globals_json["lr-conns"] = {
        "lr1" : {
            "row" : center_map[chip_size][0],
            "row-span" : row_spans[chip_size]
        }
    }

    globals_json["ud-conns"] = {}

    for n, c in enumerate(column_routing(chip_size[1], start_stride[chip_size])):
        globals_json["ud-conns"][str(n)] = c
        if n == chip_size[1] - 1:
            last_stride = c

    globals_json["branch-spans"] = {}

    for col, grps in enumerate(branch_spans(chip_size[1], start_stride[chip_size])):
        span_dict = {}
        for gn, span in enumerate(grps):
            if span:
                for glb_no in inv_global_group[gn]:
                    span_dict[str(glb_no)] = span

        globals_json["branch-spans"][str(col)] = span_dict


    # For the first and last columns, globals at the stride's current
    # position have DCCs when viewed in EPIC. These DCCs don't appear to
    # physically exist on-chip. See minitests/machxo2/dcc/dcc2.v. However,
    # in the bitstream (for the first and last columns) global conns going
    # into "DCCs" have different bits controlling them as opposed to globals
    # without DCC connections.
    zero_col_dccs = set(inv_global_group[(global_group[start_stride[chip_size]] - 1) % 4])
    zero_col_conns = set(globals_json["ud-conns"]["0"])
    missing_dccs_l = tuple(zero_col_conns.difference(zero_col_dccs))

    last_col_dccs = set(inv_global_group[(global_group[last_stride] + 1) % 4])
    last_col_conns = set(globals_json["ud-conns"][str(chip_size[1])])
    missing_dccs_r = tuple(last_col_conns.difference(last_col_dccs))

    globals_json["missing-dccs"] = {
        "0" : missing_dccs_l,
        str(chip_size[1]) : missing_dccs_r
    }

    with args.outfile as jsonf:
        jsonf.write(json.dumps(globals_json, indent=4, separators=(',', ': ')))


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Store MachXO2 global information into globals.json.")
    parser.add_argument('device', type=str,
                        help="Device for which to generate globals.json.")
    parser.add_argument('outfile', type=argparse.FileType('w'),
                        help="Output json file (globals.json in the database).")
    args = parser.parse_args()

    main(args)
