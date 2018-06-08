"""
Utilities for fuzzing non-routing configuration. This is the counterpart to interconnect.py
"""

import threading
import tiles
import pytrellis


def fuzz_word_setting(config, name, length, get_ncl_substs, empty_bitfile=None):
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


def fuzz_enum_setting(config, name, values, get_ncl_substs, empty_bitfile=None, include_zeros=True):
    """
    Fuzz a setting with multiple possible values

    :param config: FuzzConfig instance containing target device and tile of interest
    :param name: name of the setting to store in the database
    :param values: list of values taken by the enum
    :param get_ncl_substs: a callback function, that is first called with an array of bits to create a design with that setting
    :param empty_bitfile: a path to a bit file without the parameter included, optional, which is used to determine the
    default value
    :param include_zeros: if set, bits set to zero are not included in db. Needed for settings such as CEMUX which share
    bits with routing muxes to prevent conflicts.
    """
    prefix = "thread{}_".format(threading.get_ident())
    tile_dbs = {tile: pytrellis.get_tile_bitdata(
        pytrellis.TileLocator(config.family, config.device, tiles.type_from_fullname(tile))) for tile in
        config.tiles}
    if empty_bitfile is not None:
        none_chip = pytrellis.Bitstream.read_bit(empty_bitfile).deserialise_chip()
    else:
        none_chip = None

    changed_bits = set()
    prev_tiles = {}
    tiles_changed = set()
    for val in values:
        print("****** Fuzzing {} = {} ******".format(name, val))
        bit_bitf = config.build_design(config.ncl, get_ncl_substs(val), prefix)
        bit_chip = pytrellis.Bitstream.read_bit(bit_bitf).deserialise_chip()
        for prev in prev_tiles.values():
            for tile in config.tiles:
                diff = bit_chip.tiles[tile].cram - prev[tile]
                if len(diff) > 0:
                    tiles_changed.add(tile)
                    for bit in diff:
                        changed_bits.add((tile, bit.frame, bit.bit))
        prev_tiles[val] = {}
        for tile in config.tiles:
            prev_tiles[val][tile] = bit_chip.tiles[tile].cram

    for tile in tiles_changed:
        esb = pytrellis.EnumSettingBits()
        esb.name = name
        for val in values:
            bg = pytrellis.BitGroup()
            for (btile, bframe, bbit) in changed_bits:
                if btile == tile:
                    state = prev_tiles[val][tile].bit(bframe, bbit)
                    if state == 0 and not include_zeros and (
                            none_chip is not None and not none_chip.tiles[tile].cram.bit(bframe, bbit)):
                        continue
                    cb = pytrellis.ConfigBit()
                    cb.frame = bframe
                    cb.bit = bbit
                    cb.inv = (state == 0)
                    bg.bits.add(cb)
            esb.options[val] = bg
            if none_chip is not None and bg.match(none_chip.tiles[tile].cram):
                esb.defval = val
        tile_dbs[tile].add_setting_enum(esb)
        tile_dbs[tile].save()
