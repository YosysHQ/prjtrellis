from fuzzconfig import FuzzConfig
import interconnect
import nets
import pytrellis
import re

jobs = [
    {
        "pos": [(47, 0), (48, 0), (49, 0)],
        "cfg": FuzzConfig(job="PIOROUTEL", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
                          tiles=["MIB_R47C0:PICL0", "MIB_R48C0:PICL1", "MIB_R49C0:PICL2"])
    },
    {
        "pos": [(47, 90), (48, 90), (49, 90)],
        "cfg": FuzzConfig(job="PIOROUTER", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
                          tiles=["MIB_R47C90:PICR0", "MIB_R48C90:PICR1", "MIB_R49C90:PICR2"])
    },
    {
        "pos": [(0, 22), (1, 23), (0, 22), (1, 23)],
        "cfg": FuzzConfig(job="PIOROUTET", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
                          tiles=["MIB_R0C22:PIOT0", "MIB_R0C23:PIOT1", "MIB_R1C22:PICT0", "MIB_R1C23:PICT1"])
    },
    {
        "pos": [(71, 11), (71, 12), (70, 11), (70, 12)],
        "cfg": FuzzConfig(job="PIOROUTET", family="ECP5", device="LFE5U-45F", ncl="pioroute.ncl",
                          tiles=["MIB_R71C11:PICB0", "MIB_R71C12:PICB1"])
    }
]


def main():
    pytrellis.load_database("../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()

        def nn_filter(net, netnames):
            return not nets.is_cib(net)
        orig_tiles = cfg.tiles
        for pos in job["pos"]:
            # Put fixed connections in the most appropriate tile
            target_tile = None
            for tile in orig_tiles:
                if "R{}C{}".format(pos[0], pos[1]) in tile:
                    target_tile = tile
                    break
            if target_tile is not None:
                cfg.tiles = [target_tile] + [_ for _ in orig_tiles if _ != orig_tiles]
            else:
                cfg.tiles = orig_tiles
            interconnect.fuzz_interconnect(config=cfg, location=pos,
                                           netname_predicate=nn_filter,
                                           netname_filter_union=False,
                                           func_cib=True)


if __name__ == "__main__":
    main()
