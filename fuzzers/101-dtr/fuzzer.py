from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="DTR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                                          tiles=["CIB_R71C22:DTR"])


def get_substs(mode="DTR"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    return dict(comment=comment)
def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "dtr.ncl"

    nonrouting.fuzz_enum_setting(cfg, "DTR.MODE", ["NONE", "DTR"],
                                 lambda x: get_substs(mode=x), empty_bitfile)
    cfg.ncl = "dtr_routing.ncl"
    interconnect.fuzz_interconnect_with_netnames(
        cfg,
        ["R70C22_JSTARTPULSE_DTR"] + ["R70C22_JDTROUT{}_DTR".format(i) for i in range(8)],
        bidir=True
    )

if __name__ == "__main__":
    main()

