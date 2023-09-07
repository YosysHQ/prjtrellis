from collections import defaultdict
from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

job = (FuzzConfig(job="START", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl",
                  tiles=["CIB_R1C4:CIB_CFG0"]), "R1C4")

def get_substs(val):
    comment =""
    if val == "0":
        start = ":::STARTCLK=0"
    if val == "1":
        start = ":::STARTCLK=1"
    elif val == "INV":
        start = ":::STARTCLK=#INV"
    else:
        start = "#ON"
    return dict(comment=comment, start=start)


def main():
    pytrellis.load_database("../../../database")
    cfg, rc = job 
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "start.ncl"

    nonrouting.fuzz_enum_setting(cfg, "START.STARTCLK", ["0", "1", "STARTCLK", "INV"],
                                 lambda x: get_substs(val=x), empty_bitfile, False)
    
    cfg.ncl = "start_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["{}_JSTARTCLK_START".format(rc)],
        bidir=True,
        netdir_override=defaultdict(lambda : str("sink"))
    )


if __name__ == "__main__":
    main()
