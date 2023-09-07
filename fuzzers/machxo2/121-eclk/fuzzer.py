from fuzzconfig import FuzzConfig
import pytrellis
import fuzzloops
import interconnect

jobs = [
        (FuzzConfig(job="TCLKDIV0_1200", family="MachXO2", device="LCMXO2-1200HC", ncl="routing_1200.ncl",
                    tiles=["PT13:PIC_T_DUMMY_VIQ"]), "T", "R1C13", "1200_"),
        (FuzzConfig(job="BCLKDIV0_1200", family="MachXO2", device="LCMXO2-1200HC", ncl="routing_1200.ncl",
                    tiles=["PB13:PIC_B_DUMMY_VIQ"]), "B", "R11C13", "1200_"),

        (FuzzConfig(job="TCLKDIV0_2000", family="MachXO2", device="LCMXO2-2000HC", ncl="routing_2000.ncl",
                    tiles=["PT14:PIC_T_DUMMY_VIQ"]), "T", "R1C14", "2000_"),
        (FuzzConfig(job="BCLKDIV0_2000", family="MachXO2", device="LCMXO2-2000HC", ncl="routing_2000.ncl",
                    tiles=["PB14:PIC_B_DUMMY_VIQ_VREF"]), "B", "R14C14", "2000_"),

        (FuzzConfig(job="TCLKDIV0_4000", family="MachXO2", device="LCMXO2-4000HC", ncl="routing_4000.ncl",
                    tiles=["PT16:PIC_T_DUMMY_VIQ"]), "T", "R1C16", "4000_"),
        (FuzzConfig(job="BCLKDIV0_4000", family="MachXO2", device="LCMXO2-4000HC", ncl="routing_4000.ncl",
                    tiles=["PB16:PIC_B_DUMMY_VIQ_VREF"]), "B", "R21C16", "4000_"),

        (FuzzConfig(job="TCLKDIV0_7000", family="MachXO2", device="LCMXO2-7000HC", ncl="routing_7000.ncl",
                    tiles=["PT19:PIC_T_DUMMY_VIQ"]), "T", "R1C19", "7000_"),
        (FuzzConfig(job="BCLKDIV0_7000", family="MachXO2", device="LCMXO2-7000HC", ncl="routing_7000.ncl",
                    tiles=["PB19:PIC_B_DUMMY_VIQ_VREF"]), "B", "R26C19", "7000_"),
]

def main():
    pytrellis.load_database("../../../database")

    for job in jobs:
        cfg, side, rc, prefix = job
        cfg.setup()

        for idx in range(2):
            netlist = []
            netlist.append(("{}_JCDIVX{}_CLKDIV".format(rc, idx), "driver"))
            netlist.append(("{}_JCDIV1{}_CLKDIV".format(rc, idx), "driver"))
            netlist.append(("{}_CLKI{}_CLKDIV".format(rc, idx), "sink"))
            netlist.append(("{}_JRST{}_CLKDIV".format(rc, idx), "sink"))
            netlist.append(("{}_JALIGNWD{}_CLKDIV".format(rc, idx), "sink"))
            netlist.append(("{}_ECLKI{}".format(rc, idx), "sink"))
            netlist.append(("{}_ECLKI{}_ECLKSYNC".format(rc, idx), "sink"))
            netlist.append(("{}_{}ECLK{}".format(rc, side, idx), "sink"))
            netlist.append(("{}_JINECK{}".format(rc, idx), "sink"))        
            netlist.append(("{}_JECLKO{}_ECLKSYNC".format(rc, idx), "driver"))
            netlist.append(("{}_JSTOP{}_ECLKSYNC".format(rc, idx), "sink"))
            netlist.append(("{}_JECLKBRG{}".format(rc, idx), "sink"))
            netlist.append(("{}_JECLKCIB{}".format(rc, idx), "sink"))
            netlist.append(("{}_JPLLCLKOP{}".format(rc, idx), "sink"))
            netlist.append(("{}_JPLLCLKOS{}".format(rc, idx), "sink"))
            if (side == "B"):
                netlist.append(("{}_ECLK{}".format(rc, idx), "sink"))
                netlist.append(("{}_CLKFBBUF{}".format(rc, idx), "sink"))
                netlist.append(("{}_Z{}_CLKFBBUF".format(rc, idx), "driver"))
                netlist.append(("{}_JA{}_CLKFBBUF".format(rc, idx), "sink"))
                netlist.append(("{}_JPLLCLKFB{}".format(rc, idx), "sink"))

            nets = [net[0] for net in netlist]
            override_dict = {net[0]: net[1] for net in netlist}

            interconnect.fuzz_interconnect_with_netnames(config=cfg,      
                                                        netnames=nets,
                                                        netname_filter_union=False,
                                                        bidir=True,
                                                        nonlocal_prefix=prefix,
                                                        netdir_override=override_dict)


if __name__ == "__main__":
    main()
