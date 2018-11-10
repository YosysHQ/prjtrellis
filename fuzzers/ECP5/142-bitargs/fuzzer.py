from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect
import os

cfg = FuzzConfig(job="BITARGS", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                 tiles=["MIB_R71C4:EFB0_PICB0", "MIB_R71C5:EFB1_PICB1", "MIB_R71C6:EFB2_PICB0",
                        "MIB_R71C7:EFB3_PICB1", "MIB_R71C3:BANKREF8"])


def get_substs(config):
    os.environ["BITARGS"] = " ".join(["-g {}:{}".format(k, v) for k, v in config.items()])
    return {}

def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.DONEPHASE", ["T0", "T1", "T2", "T3"],
                                 lambda x: get_substs(dict(DONEPHASE=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.GOEPHASE", ["T1", "T2", "T3"],
                                 lambda x: get_substs(dict(GOEPHASE=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.GSRPHASE", ["T1", "T2", "T3"],
                                 lambda x: get_substs(dict(GSRPHASE=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.GWEPHASE", ["T1", "T2", "T3"],
                                 lambda x: get_substs(dict(GWEPHASE=x)), empty_bitfile, False)

if __name__ == "__main__":
    main()
