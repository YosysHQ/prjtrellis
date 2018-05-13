import re

pos_re = re.compile(r'R(\d+)C(\d+)')


def pos_from_name(tile):
    """
    Extract the tile position as a (row, column) tuple from its name
    """
    s = pos_re.search(tile)
    assert s
    return int(s.group(1)), int(s.group(2))