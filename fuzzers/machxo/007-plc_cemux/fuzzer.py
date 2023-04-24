from fuzzconfig import FuzzConfig
import nonrouting
import fuzzloops
import pytrellis

cfg_plc = FuzzConfig(job="PLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R9C5:PLC"])
cfg_fplc = FuzzConfig(job="FPLC2REG", family="MachXO", device="LCMXO2280C", ncl="empty.ncl", tiles=["R2C2:FPLC"])

def main():
    pytrellis.load_database("../../../database")
    cfg_plc.setup()
    empty_bitfile_plc = cfg_plc.build_design(cfg_plc.ncl, {})
    cfg_plc.ncl = "cemux_plc.ncl"
    cfg_fplc.setup()
    empty_bitfile_fplc = cfg_plc.build_design(cfg_fplc.ncl, {})
    cfg_fplc.ncl = "cemux_fplc.ncl"

    def per_slice(slicen):
        def get_substs_plc(cemux):
            if cemux == "INV":
                cemux = "CE:::CE=#INV"
            if cemux == "0":
                cemux = "1:::1=0"
            return dict(slice=slicen, cemux=cemux)
        def get_substs_fplc(cemux):
            if cemux == "INV":
                cemux = "CE:::CE=#INV"
            if cemux == "0":
                cemux = "1:::1=0"
            return dict(slice=slicen, cemux=cemux)

        nonrouting.fuzz_enum_setting(cfg_plc, "SLICE{}.CEMUX".format(slicen), ["0", "1", "CE", "INV"],
                                     lambda x: get_substs_plc(cemux=x),
                                     empty_bitfile_plc, False)

        nonrouting.fuzz_enum_setting(cfg_fplc, "FSLICE{}.CEMUX".format(slicen), ["0", "1", "CE", "INV"],
                                     lambda x: get_substs_fplc(cemux=x),
                                     empty_bitfile_fplc, False)

    fuzzloops.parallel_foreach(["A", "B", "C", "D"], per_slice)


if __name__ == "__main__":
    main()
