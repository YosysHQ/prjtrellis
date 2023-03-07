import re
import pytrellis


def pos_from_name(tile, chip_size, row_bias, col_bias):
    """
    Extract the tile position as a (row, column) tuple from its name
    """
    size = pytrellis.make_IntPair(chip_size[0],chip_size[1])
    pos = pytrellis.get_row_col_pair_from_chipsize(tile, size, row_bias, col_bias)
    return int(pos.first), int(pos.second)


def type_from_fullname(tile):
    """
    Extract the type from a full tile name (in name:type) format
    """
    return tile.split(":")[1]
