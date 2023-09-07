from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import interconnect

cfg = FuzzConfig(job="JTAGF", family="MachXO2", device="LCMXO2-2000HC", ncl="empty.ncl", tiles=["PT4:CFG0"])

jobs = [
        (FuzzConfig(job="JTAGF", family="MachXO2", device="LCMXO2-1200HC", ncl="routing_1200.ncl",
                    tiles=["PT4:CFG0"]), "1200_"),
        (FuzzConfig(job="JTAGF", family="MachXO2", device="LCMXO2-2000HC", ncl="routing_2000.ncl",
                    tiles=["PT4:CFG0"]), "2000_"),
        (FuzzConfig(job="JTAGF", family="MachXO2", device="LCMXO2-4000HC", ncl="routing_4000.ncl",
                    tiles=["PT4:CFG0"]), "4000_"),
        (FuzzConfig(job="JTAGF", family="MachXO2", device="LCMXO2-7000HC", ncl="routing_7000.ncl",
                    tiles=["PT4:CFG0"]), "7000_"),
]
def get_substs(mode="JTAGF", er1="DISABLED", er2="DISABLED"):
    if mode == "NONE":
        comment = "//"
    else:
        comment = ""
    return dict(comment=comment, er1=er1, er2=er2)

def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "jtag.ncl"

    nonrouting.fuzz_enum_setting(cfg, "JTAG.MODE", ["NONE", "JTAGF"],
                                 lambda x: get_substs(mode=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "JTAG.ER1", ["DISABLED", "ENABLED"],
                                 lambda x: get_substs(er1=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "JTAG.ER2", ["DISABLED", "ENABLED"],
                                 lambda x: get_substs(er2=x), empty_bitfile, False)
    for job in jobs:
        rcfg, prefix = job
        rcfg.setup()
        override_dict = { "R1C4_JJTDO1_JTAG" : "sink",
                    "R1C4_JJTDO2_JTAG" : "sink",
                    "R1C4_JTCK_JTAG" : "sink",
                    "R1C4_JTMS_JTAG" : "sink",
                    "R1C4_JTDI_JTAG" : "sink",
                    "R1C4_JJTDI_JTAG" : "driver",
                    "R1C4_JJTCK_JTAG" : "driver",
                    "R1C4_JJRTI1_JTAG" : "driver",
                    "R1C4_JJRTI2_JTAG" : "driver",
                    "R1C4_JJSHIFT_JTAG" : "driver",
                    "R1C4_JJUPDATE_JTAG" : "driver",
                    "R1C4_JJRSTN_JTAG" : "driver",
                    "R1C4_JJCE1_JTAG" : "driver",
                    "R1C4_JJCE2_JTAG" : "driver",
                    "R1C4_JTDO_JTAG" : "driver" }

        nets = [net for net in override_dict]

        interconnect.fuzz_interconnect_with_netnames(
            rcfg,
            nets,
            bidir=True,
            nonlocal_prefix = prefix,
            netdir_override=override_dict
        )

if __name__ == "__main__":
    main()

