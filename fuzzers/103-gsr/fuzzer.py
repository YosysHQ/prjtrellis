from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="GSR", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                 tiles=["MIB_R71C4:EFB0_PICB0", "MIB_R34C41:VIQ_BUF"])


def get_substs(gsrmode="ACTIVE_LOW", syncmode="NONE"):
    if gsrmode == "NONE":
        comment = "//"
    else:
        comment = ""
    if syncmode == "NONE":
        syncmode = "#OFF"
    return dict(comment=comment, gsrmode=gsrmode, syncmode=syncmode)


def main():
    pytrellis.load_database("../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    cfg.ncl = "gsr.ncl"

    nonrouting.fuzz_enum_setting(cfg, "GSR.GSRMODE", ["NONE", "ACTIVE_LOW", "ACTIVE_HIGH"],
                                 lambda x: get_substs(gsrmode=x), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "GSR.SYNCMODE", ["NONE", "ASYNC", "SYNC"],
                                 lambda x: get_substs(syncmode=x), empty_bitfile, False)
    for rcfg, rc, prefix in [
        (FuzzConfig(job="GSR", family="ECP5", device="LFE5U-25F", ncl="gsr_routing_25k.ncl",
                   tiles=["MIB_R50C4:EFB0_PICB0"]), "R49C4", "25K_"),
        (FuzzConfig(job="GSR", family="ECP5", device="LFE5U-45F", ncl="gsr_routing.ncl",
                    tiles=["MIB_R71C4:EFB0_PICB0"]), "R70C4", "45K_"),
        (FuzzConfig(job="GSR", family="ECP5", device="LFE5U-85F", ncl="gsr_routing_85k.ncl",
                    tiles=["MIB_R95C4:EFB0_PICB0"]), "R94C4", "85K_"),
    ]:
        rcfg.setup()
        interconnect.fuzz_interconnect_with_netnames(
            rcfg,
            ["{}_JGSR_GSR".format(rc), "{}_JCLK_GSR".format(rc)],
            bidir=True,
            nonlocal_prefix=prefix
        )


if __name__ == "__main__":
    main()
