from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="USRMCLK", family="ECP5", device="LFE5U-45F", ncl="empty.ncl",
                 tiles=["MIB_R71C4:EFB0_PICB0", "MIB_R71C5:EFB1_PICB1", "MIB_R71C6:EFB2_PICB0",
                        "MIB_R71C7:EFB3_PICB1", "MIB_R71C3:BANKREF8"])


def get_substs(config):
    return dict(sysconfig=(" ".join(["{}={}".format(k, v) for k, v in config.items()])))


def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.BACKGROUND_RECONFIG", ["OFF", "ON"],
                                 lambda x: get_substs(dict(BACKGROUND_RECONFIG=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.TRANSFR", ["OFF", "ON"],
                                 lambda x: get_substs(dict(TRANSFR=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.DONE_EX", ["OFF", "ON"],
                                 lambda x: get_substs(dict(DONE_EX=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.DONE_OD", ["OFF", "ON"],
                                 lambda x: get_substs(dict(DONE_OD=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.DONE_PULL", ["OFF", "ON"],
                                 lambda x: get_substs(dict(DONE_PULL=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.SLAVE_SPI_PORT", ["DISABLE", "ENABLE"],
                                 lambda x: get_substs(dict(SLAVE_SPI_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.MASTER_SPI_PORT", ["DISABLE", "ENABLE"],
                                 lambda x: get_substs(dict(MASTER_SPI_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.SLAVE_PARALLEL_PORT", ["DISABLE", "ENABLE"],
                                 lambda x: get_substs(dict(SLAVE_PARALLEL_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.CONFIG_IOVOLTAGE", ["1.2", "1.5", "1.8", "2.5", "3.3"],
                                 lambda x: get_substs(dict(CONFIG_IOVOLTAGE=x, SLAVE_SPI_PORT="ENABLE")), empty_bitfile,
                                 False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.WAKE_UP", ["4", "21"],
                                 lambda x: get_substs(dict(WAKE_UP=x)), empty_bitfile, False)


if __name__ == "__main__":
    main()
