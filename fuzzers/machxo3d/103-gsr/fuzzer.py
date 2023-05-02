from collections import defaultdict
from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

job = (FuzzConfig(job="GSR", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty.ncl",
                  tiles=["PT4:CFG0"]), "R1C4")

def get_substs(gsrmode="ACTIVE_LOW", syncmode="NONE"):
    if gsrmode == "NONE":
        comment = "//"
    else:
        comment = ""
    if syncmode == "NONE":
        syncmode = "#OFF"
    return dict(comment=comment, gsrmode=gsrmode, syncmode=syncmode)


def main():
    pytrellis.load_database("../../../database")
    cfg, rc = job 
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "gsr.ncl"

    nonrouting.fuzz_enum_setting(cfg, "GSR.GSRMODE", ["NONE", "ACTIVE_LOW", "ACTIVE_HIGH"],
                                 lambda x: get_substs(gsrmode=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "GSR.SYNCMODE", ["NONE", "ASYNC", "SYNC"],
                                 lambda x: get_substs(syncmode=x), empty_bitfile, False)
    
    cfg.ncl = "gsr_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["{}_JGSR_GSR".format(rc), "{}_JCLK_GSR".format(rc)],
        bidir=True,
        netdir_override=defaultdict(lambda : str("sink"))
    )


if __name__ == "__main__":
    main()
