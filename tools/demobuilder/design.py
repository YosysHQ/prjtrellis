import pytrellis
import route
import tiles

# Simple demo design builder
class Design:
    def __init__(self, family):
        self.chip = pytrellis.Chip("LFE5U-45F")
        self.row_bias = self.chip.info.row_bias
        self.col_bias = self.chip.info.col_bias
        self.router = route.Autorouter(self.chip)
        self.config = {_.info.name: pytrellis.TileConfig() for _ in self.chip.get_all_tiles()}
        # TODO: load skeleton config
        self.bels = dict()
        self.bel_to_cell = {}
        self.bels_by_type = {}

        self.auto_netid = 0
        self.auto_cellid = 0

        self.init_bels()

    def get_netid(self, postfix=""):
        self.auto_netid += 1
        return "n{}{}".format(self.auto_netid, postfix)

    def get_cellid(self, postfix=""):
        self.auto_cellid += 1
        return "c{}{}".format(self.auto_cellid, postfix)

    def init_bels(self):
        self.bels_by_type = {"SLICE": []}
        all_tiles = self.chip.get_all_tiles()
        for tile in all_tiles:
            tinf = tile.info
            tname = tinf.name
            chip_size = (self.chip.get_max_row(), self.chip.get_max_col())
            pos = tiles.pos_from_name(tname, chip_size, self.row_bias, self.col_bias)
            if tinf.type == "PLC2":
                for loc in ("A", "B", "C", "D"):
                    bel = "R{}C{}{}".format(pos[0], pos[1], loc)
                    self.bels[bel] = ("SLICE", (tname, loc))
                    self.bels_by_type["SLICE"].append(bel)

    def connect_input(self, wire, net):
        if net is not None:
            self.router.route_net_to_wire(net, wire, self.config)

    def connect_output(self, wire, net):
        if net is not None:
            self.router.bind_net_to_port(net, wire)

    def bel_for_cell(self, cell, type):
        for bel in self.bels_by_type["SLICE"]:
            if bel not in self.bel_to_cell:
                self.bel_to_cell[bel] = cell
                return bel
        assert False, "can't place cell {}, no remaining bels of type {}".format(cell, type)

    def inst_slice(self, name, a0=None, a1=None, b0=None, b1=None, c0=None, c1=None, d0=None, d1=None, m0=None, m1=None,
                   clk=None, ce=None, lsr=None, f0=None, f1=None, q0=None, q1=None, params=dict()):
        print("Instantiating slice {}".format(name))
        bel = self.bel_for_cell(name, "SLICE")
        beltype, belloc = self.bels[bel]
        tile, loc = belloc
        chip_size = (self.chip.get_max_row(), self.chip.get_max_col())
        pos = tiles.pos_from_name(tile, chip_size, self.row_bias, self.col_bias)
        net_prefix = "R{}C{}".format(pos[0], pos[1])
        slice_index = "ABCD".index(loc)
        lc0 = 2 * slice_index
        lc1 = 2 * slice_index + 1

        self.connect_output("{}_F{}".format(net_prefix, lc0), f0)
        self.connect_output("{}_F{}".format(net_prefix, lc1), f1)
        self.connect_output("{}_Q{}".format(net_prefix, lc0), q0)
        self.connect_output("{}_Q{}".format(net_prefix, lc1), q1)

        self.connect_input("{}_A{}".format(net_prefix, lc0), a0)
        self.connect_input("{}_A{}".format(net_prefix, lc1), a1)
        self.connect_input("{}_B{}".format(net_prefix, lc0), b0)
        self.connect_input("{}_B{}".format(net_prefix, lc1), b1)
        self.connect_input("{}_C{}".format(net_prefix, lc0), c0)
        self.connect_input("{}_C{}".format(net_prefix, lc1), c1)
        self.connect_input("{}_D{}".format(net_prefix, lc0), d0)
        self.connect_input("{}_D{}".format(net_prefix, lc1), d1)

        self.connect_input("{}_M{}".format(net_prefix, lc0), m0)
        self.connect_input("{}_M{}".format(net_prefix, lc1), m1)

        self.connect_input("{}_MUXCLK{}".format(net_prefix, slice_index), clk)
        self.connect_input("{}_CE{}".format(net_prefix, slice_index), ce)
        self.connect_input("{}_MUXLSR{}".format(net_prefix, slice_index), lsr)

        for key, value in sorted(params.items()):
            if key.endswith(".INIT"):
                bv = pytrellis.BoolVector()
                for x in value:
                    bv.append(x)
                self.config[tile].add_word("SLICE{}.{}".format(loc, key), bv)
            else:
                self.config[tile].add_enum("SLICE{}.{}".format(loc, key), value)
        print()

    def make_bitstream(self, filename):
        # Open debug file
        debugfile = filename + ".dbg"
        with open(debugfile, 'w') as dbgf:
            for tname, tcfg in sorted(self.config.items()):
                tile = self.chip.tiles[tname]
                tinfo = tile.info
                tdb = pytrellis.get_tile_bitdata(
                    pytrellis.TileLocator(self.chip.info.family, self.chip.info.name, tinfo.type))
                tile.cram.clear()
                tdb.config_to_tile_cram(tcfg, tile.cram)
                textcfg = tcfg.to_string()
                if len(textcfg.strip()) > 0:
                    dbgf.write(".tile {}\n".format(tname))
                    dbgf.write(textcfg)
                    dbgf.write("\n")

        bs = pytrellis.Bitstream.serialise_chip(self.chip)
        bs.write_bit(filename)
