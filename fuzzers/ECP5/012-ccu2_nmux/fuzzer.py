from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

cfg = FuzzConfig(job="PLC2NMUX", family="ECP5", device="LFE5U-25F", ncl="empty.ncl", tiles=["R19C33:PLC2"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "ccu2.ncl"

    def per_slice(slicen):
        def get_substs(sig="A0", conn="A0"):
            subs = {"slice": slicen}
            if conn == "1":
                subs["muxcfg"] = "::{}=1".format(sig)
            else:
                subs["muxcfg"] = ""
            return subs
        for sig in ["A0", "A1", "B0", "B1", "C0", "C1", "D0", "D1"]:
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.{}MUX".format(slicen, sig), [sig, "1"],
                                         lambda x: get_substs(sig=sig, conn=x),
                                         empty_bitfile, False)
    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
