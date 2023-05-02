from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops
import interconnect

cfg = FuzzConfig(job="SYSCONFIG", family="MachXO3D", device="LCMXO3D-9400HC", ncl="empty.ncl",
                 tiles=["PT4:CFG0", "PT5:CFG1", "PT6:CFG2", "PT7:CFG3"])


def get_substs(config):
    return dict(sysconfig=("SYSCONFIG " + " ".join(["{}={}".format(k, v) for k, v in config.items()]) + " ;\n"))


# Need to comment line adding COMPRESS_CONFIG=OFF in diamond.sh for this one to work
def main():
    pytrellis.load_database("../../../database")
    cfg.setup()
    empty_bitfile = cfg.build_design(cfg.ncl, {})
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.SDM_PORT", ["PROGRAMN", "PROGRAMN_DONE", "PROGRAMN_DONE_INITN", "DONE", "INITN", "DISABLE"],
                                 lambda x: get_substs(dict(SDM_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.SLAVE_SPI_PORT", ["DISABLE", "ENABLE"],
                                 lambda x: get_substs(dict(SLAVE_SPI_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.MASTER_SPI_PORT", ["DISABLE", "ENABLE", "EFB_USER"],
                                 lambda x: get_substs(dict(MASTER_SPI_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.I2C_PORT", ["DISABLE", "ENABLE"],
                                 lambda x: get_substs(dict(I2C_PORT=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.ENABLE_TRANSFR", ["DISABLE", "ENABLE"],
                                 lambda x: get_substs(dict(ENABLE_TRANSFR=x)), empty_bitfile, False)
    nonrouting.fuzz_enum_setting(cfg, "SYSCONFIG.BACKGROUND_RECONFIG", ["OFF", "ON"],
                                 lambda x: get_substs(dict(BACKGROUND_RECONFIG=x)), empty_bitfile, False)

if __name__ == "__main__":
    main()
