"""
Utilities for fuzzing non-routing configuration. This is the counterpart to interconnect.py
"""

import threading
import tiles
import pytrellis


def fuzz_word_setting(config, name, length, get_ncl_substs, empty_bitfile = None):
    """
    Fuzz a multi-bit setting, such as LUT initialisation

    :param config: FuzzConfig instance containing target device and tile of interest
    :param name: name of the setting to store in the database
    :param length: number of bits in the setting
    :param get_ncl_substs: a callback function, that is first called with an array of bits to create a design with that setting
    :param empty_bitfile: a path to a bit file without the parameter included, optional, which is used to determine the
    default value
    """
    prefix = "thread{}_".format(threading.get_ident())
    tile_dbs = {tile: pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(config.family, config.device, tiles.type_from_fullname(tile))) for tile in
        config.tiles}
    if empty_bitfile is not None:
        none_chip = pytrellis.Bitstream.read_bit(empty_bitfile).deserialise_chip()
    else:
        none_chip = None
    baseline_bitf = config.build_design(config.ncl, get_ncl_substs([False for _ in range(length)]), prefix)
    baseline_chip = pytrellis.Bitstream.read_bit(baseline_bitf).deserialise_chip()

    wsb = {tile: pytrellis.WordSettingBits() for tile in
        config.tiles}
    is_empty = {tile: True for tile in config.tiles}
    for t in config.tiles:
        wsb[t].name = name
    for i in range(length):
        bit_bitf = config.build_design(config.ncl, get_ncl_substs([(_ == i) for _ in range(length)]), prefix)
        bit_chip = pytrellis.Bitstream.read_bit(bit_bitf).deserialise_chip()
        diff = bit_chip - baseline_chip
        for tile in config.tiles:
            if tile in diff:
                wsb[tile].bits.append(pytrellis.BitGroup(diff[tile]))
                is_empty[tile] = False
            else:
                wsb[tile].bits.append(pytrellis.BitGroup())
            if none_chip is not None:
                if wsb[tile].bits[i].match(none_chip.tiles[tile].cram):
                    wsb[tile].defval.append(True)
                else:
                    wsb[tile].defval.append(False)
    for t in config.tiles:
        if not is_empty[t]:
            tile_dbs[t].add_setting_word(wsb[t])
            tile_dbs[t].save()
