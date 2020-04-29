from fuzzconfig import FuzzConfig
import nonrouting
import pytrellis
import fuzzloops

dsp_tiles = [
    "MIB_R13C4:MIB_DSP0", "MIB_R13C4:MIB2_DSP0",
    "MIB_R13C5:MIB_DSP1", "MIB_R13C5:MIB2_DSP1",
    "MIB_R13C6:MIB_DSP2", "MIB_R13C6:MIB2_DSP2",
    "MIB_R13C7:MIB_DSP3", "MIB_R13C7:MIB2_DSP3",
    "MIB_R13C8:MIB_DSP4", "MIB_R13C8:MIB2_DSP4",
    "MIB_R13C9:MIB_DSP5", "MIB_R13C9:MIB2_DSP5",
    "MIB_R13C10:MIB_DSP6", "MIB_R13C10:MIB2_DSP6",
    "MIB_R13C11:MIB_DSP7", "MIB_R13C11:MIB2_DSP7",
    "MIB_R13C12:MIB_DSP8", "MIB_R13C12:MIB2_DSP8",
]

jobs = [
    ("MULT18_R13C4", "MULT18_0", FuzzConfig(job="MULT18_0", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C5", "MULT18_1", FuzzConfig(job="MULT18_1", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C8", "MULT18_4", FuzzConfig(job="MULT18_4", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("MULT18_R13C9", "MULT18_5", FuzzConfig(job="MULT18_5", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("ALU54_R13C7", "ALU54_3", FuzzConfig(job="ALU54_3", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
    ("ALU54_R13C11", "ALU54_7", FuzzConfig(job="ALU54_7", family="ECP5", device="LFE5U-25F", ncl="empty.ncl",
                                            tiles=dsp_tiles)),
]


def main():
    pytrellis.load_database("../../../database")

    def per_job(job):
        def get_substs(net, value):
            if net == value:
                settings = "{}=#SIG".format(net, net)
            else:
                settings = "{}=#INV".format(net)
            return dict(loc=loc, mode=mode, settings=settings,
                        cmodel=cellmodel)

        loc, mult, cfg = job
        cellmodel = loc.split("_")[0]
        mode = "MULT18X18D" if cellmodel == "MULT18" else "ALU54B"
        cfg.setup()
        empty_bitfile = cfg.build_design(cfg.ncl, {})
        cfg.ncl = "dspconfig.ncl"
        for port in ["CLK", "CE", "RST"]:
            for i in range(4):
                sig = port + str(i)
                nonrouting.fuzz_enum_setting(cfg, "{}.{}MUX".format(mult, sig), [sig, "INV"],
                                             lambda x: get_substs(sig, x), empty_bitfile,
                                             False)
        extra_ports = []
        if cellmodel == "ALU54":
            extra_ports = ["OP{}".format(i) for i in range(11)]
        if cellmodel == "MULT18":
            extra_ports = ["SIGNEDA", "SIGNEDB", "SOURCEA", "SOURCEB"]
        for port in extra_ports:
            nonrouting.fuzz_enum_setting(cfg, "{}.{}MUX".format(mult, port), [port, "INV"],
                                         lambda x: get_substs(port, x), empty_bitfile,
                                         False)
    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
