from fuzzconfig import FuzzConfig
import pytrellis
import fuzzloops
import interconnect

jobs = [
        (FuzzConfig(job="TCLKDIV0_4300", family="MachXO3D", device="LCMXO3D-4300HC", ncl="routing_4300.ncl",
                    tiles=["PT16:PIC_T_DUMMY_VIQ"]), "T", "R1C16", "4300D_"),
        (FuzzConfig(job="BCLKDIV0_4300", family="MachXO3D", device="LCMXO3D-4300HC", ncl="routing_4300.ncl",
                    tiles=["PB16:PIC_B_DUMMY_VIQ_VREF"]), "B", "R21C16", "4300D_"),

        (FuzzConfig(job="TCLKDIV0_9400", family="MachXO3D", device="LCMXO3D-9400HC", ncl="routing_9400.ncl",
                    tiles=["PT25:PIC_T_DUMMY_VIQ"]), "T", "R1C25", "9400D_"),
        (FuzzConfig(job="BCLKDIV0_9400", family="MachXO3D", device="LCMXO3D-9400HC", ncl="routing_9400.ncl",
                    tiles=["PB25:PIC_B_DUMMY_VIQ_VREF"]), "B", "R30C25", "9400D_"),
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
