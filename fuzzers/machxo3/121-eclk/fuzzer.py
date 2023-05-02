from fuzzconfig import FuzzConfig
import pytrellis
import fuzzloops
import interconnect

jobs = [
        (FuzzConfig(job="TCLKDIV0_1300", family="MachXO3", device="LCMXO3LF-1300E", ncl="routing_1300.ncl",
                    tiles=["PT13:PIC_T_DUMMY_VIQ"]), "T", "R1C13", "1300_"),
        (FuzzConfig(job="BCLKDIV0_1300", family="MachXO3", device="LCMXO3LF-1300E", ncl="routing_1300.ncl",
                    tiles=["PB13:PIC_B_DUMMY_VIQ"]), "B", "R11C13", "1300_"),

        (FuzzConfig(job="TCLKDIV0_2100", family="MachXO3", device="LCMXO3LF-2100C", ncl="routing_2100.ncl",
                    tiles=["PT14:PIC_T_DUMMY_VIQ"]), "T", "R1C14", "2100_"),
        (FuzzConfig(job="BCLKDIV0_2100", family="MachXO3", device="LCMXO3LF-2100C", ncl="routing_2100.ncl",
                    tiles=["PB14:PIC_B_DUMMY_VIQ_VREF"]), "B", "R14C14", "2100_"),

        (FuzzConfig(job="TCLKDIV0_4300", family="MachXO3", device="LCMXO3LF-4300C", ncl="routing_4300.ncl",
                    tiles=["PT16:PIC_T_DUMMY_VIQ"]), "T", "R1C16", "4300_"),
        (FuzzConfig(job="BCLKDIV0_4300", family="MachXO3", device="LCMXO3LF-4300C", ncl="routing_4300.ncl",
                    tiles=["PB16:PIC_B_DUMMY_VIQ_VREF"]), "B", "R21C16", "4300_"),

        (FuzzConfig(job="TCLKDIV0_6900", family="MachXO3", device="LCMXO3LF-6900C", ncl="routing_6900.ncl",
                    tiles=["PT19:PIC_T_DUMMY_VIQ"]), "T", "R1C19", "6900_"),
        (FuzzConfig(job="BCLKDIV0_6900", family="MachXO3", device="LCMXO3LF-6900C", ncl="routing_6900.ncl",
                    tiles=["PB19:PIC_B_DUMMY_VIQ_VREF"]), "B", "R26C19", "6900_"),

        (FuzzConfig(job="TCLKDIV0_9400", family="MachXO3", device="LCMXO3LF-9400C", ncl="routing_9400.ncl",
                    tiles=["PT25:PIC_T_DUMMY_VIQ"]), "T", "R1C25", "9400_"),
        (FuzzConfig(job="BCLKDIV0_9400", family="MachXO3", device="LCMXO3LF-9400C", ncl="routing_9400.ncl",
                    tiles=["PB25:PIC_B_DUMMY_VIQ_VREF"]), "B", "R30C25", "9400_"),
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
