from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import nets
import pytrellis
import re

# At present, I don't believe this affects any bits. Keeping this around
# just in case I figure out I'm wrong...

cfg = FuzzConfig(job="PLC2NMUX", family="MachXO2", device="LCMXO2-1200HC", ncl="empty.ncl", tiles=["R10C11:PLC"])


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "ccu2.ncl"

    def per_slice(slicen):
        def get_substs(sig="A0", conn="A0"):
            subs = {"slice": slicen}
            if conn == "0":
                # subs["muxcfg"] = "::{}=0".format(sig)
                subs["muxcfg"] = "::A0=0,A1=0,B0=0,B1=0,C0=0,C1=0,D0=0,D1=0"
            else:
                subs["muxcfg"] = ""
            return subs
        # for sig in ["A0", "A1", "B0", "B1", "C0", "C1", "D0", "D1"]:
        for sig in ["A0"]:
            nonrouting.fuzz_enum_setting(cfg, "SLICE{}.{}MUX".format(slicen, sig), [sig, "0"],
                                         lambda x: get_substs(sig=sig, conn=x),
                                         empty_bitfile, False)
    # fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)
    fuzzloops.parallel_foreach(["A"], per_slice)


if __name__ == "__main__":
    main()
