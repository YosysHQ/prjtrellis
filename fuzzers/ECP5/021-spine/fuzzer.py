from fuzzconfig import FuzzConfig
import interconnect
import pytrellis

jobs = [
    {
        "cfg": FuzzConfig(job="EBR_SPINE_UL1", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R10C12:EBR_SPINE_UL1"]),
        "sink_net": "R18C12_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_UL0", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R10C30:EBR_SPINE_UL0"]),
        "sink_net": "R18C30_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_UR0", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R10C50:EBR_SPINE_UR0"]),
        "sink_net": "R18C50_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_UR1", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R10C77:EBR_SPINE_UR1"]),
        "sink_net": "R18C77_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LL1", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R58C12:EBR_SPINE_LL1"]),
        "sink_net": "R53C12_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LL0", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R58C30:EBR_SPINE_LL0"]),
        "sink_net": "R53C30_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LR0", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R58C50:EBR_SPINE_LR0"]),
        "sink_net": "R53C50_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LR1", family="ECP5", device="LFE5U-45F", ncl="spine_45k.ncl",
                          tiles=["MIB_R58C77:EBR_SPINE_LR1"]),
        "sink_net": "R53C77_VPTX{:02d}00"
    },

    {
        "cfg": FuzzConfig(job="DSP_SPINE_UL1", family="ECP5", device="LFE5U-25F", ncl="spine_25k.ncl",
                          tiles=["MIB_R13C3:DSP_SPINE_UL1"]),
        "sink_net": "R13C3_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="DSP_SPINE_UL0", family="ECP5", device="LFE5U-25F", ncl="spine_25k.ncl",
                          tiles=["MIB_R13C21:DSP_SPINE_UL0"]),
        "sink_net": "R13C21_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="DSP_SPINE_UR0", family="ECP5", device="LFE5U-25F", ncl="spine_25k.ncl",
                          tiles=["MIB_R13C41:DSP_SPINE_UR0"]),
        "sink_net": "R13C41_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="DSP_SPINE_UR1", family="ECP5", device="LFE5U-25F", ncl="spine_25k.ncl",
                          tiles=["MIB_R13C59:DSP_SPINE_UR1"]),
        "sink_net": "R13C59_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LL3", family="ECP5", device="LFE5U-25F", ncl="spine_25k.ncl",
                          tiles=["MIB_R37C3:EBR_SPINE_LL3"]),
        "sink_net": "R38C3_VPTX{:02d}00"
    },

    {
        "cfg": FuzzConfig(job="EBR_SPINE_UL2", family="ECP5", device="LFE5U-85F", ncl="spine_85k.ncl",
                          tiles=["MIB_R22C12:EBR_SPINE_UL2"]),
        "sink_net": "R24C12_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_UR2", family="ECP5", device="LFE5U-85F", ncl="spine_85k.ncl",
                          tiles=["MIB_R22C113:EBR_SPINE_UR2"]),
        "sink_net": "R24C113_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LL2", family="ECP5", device="LFE5U-85F", ncl="spine_85k.ncl",
                          tiles=["MIB_R70C12:EBR_SPINE_LL2"]),
        "sink_net": "R71C12_VPTX{:02d}00"
    },
    {
        "cfg": FuzzConfig(job="EBR_SPINE_LR2", family="ECP5", device="LFE5U-85F", ncl="spine_85k.ncl",
                          tiles=["MIB_R70C113:EBR_SPINE_LR2"]),
        "sink_net": "R71C113_VPTX{:02d}00"
    },
]


def main():
    pytrellis.load_database("../../../database")
    for job in jobs:
        cfg = job["cfg"]
        cfg.setup()
        netnames = [job["sink_net"].format(x) for x in range(16)]

        interconnect.fuzz_interconnect_with_netnames(config=cfg, netnames=netnames,
                                                     netname_filter_union=False)


if __name__ == "__main__":
    main()
