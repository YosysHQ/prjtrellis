from collections import defaultdict
from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

job = (FuzzConfig(job="TSALL", family="MachXO3", device="LCMXO3LF-1300E", ncl="empty.ncl",
                  tiles=["PT4:CFG0"]), "R1C4")

def get_substs(val):
    comment =""
    if val == "0":
        tsall = ":::TSALL=0"
    if val == "1":
        tsall = ":::TSALL=1"
    elif val == "INV":
        tsall = ":::TSALL=#INV"
    elif val == "NONE":
        tsall = "#ON"
        comment = "//"
    else:
        tsall = "#ON"
    return dict(comment=comment, tsall=tsall)

def main():
    pytrellis.load_database("../../../database")
    cfg, rc = job 
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "tsall.ncl"
    
    nonrouting.fuzz_enum_setting(cfg, "TSALL.MODE", ["TSALL", "NONE"],
                                 lambda x: get_substs(val=x), empty_bitfile, False)

    nonrouting.fuzz_enum_setting(cfg, "TSALL.TSALL", ["0", "1", "TSALL", "INV"],
                                 lambda x: get_substs(val=x), empty_bitfile, False)

    cfg.ncl = "tsall_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["{}_JTSALLI_TSALL".format(rc)],
        bidir=True,
        netdir_override=defaultdict(lambda : str("sink"))
    )


if __name__ == "__main__":
    main()
