from fuzzconfig import FuzzConfig
import pytrellis
import interconnect

jobs = [
        (FuzzConfig(job="EFB_4300", family="MachXO3D", device="LCMXO3D-4300HC", ncl="routing_4300.ncl",
                    tiles=["CIB_R1C4:CIB_CFG0"]), "4300D_"),
        (FuzzConfig(job="EFB_9400", family="MachXO3D", device="LCMXO3D-9400HC", ncl="routing_9400.ncl",
                    tiles=["CIB_R1C4:CIB_CFG0"]), "9400D_"),
]

def main():
    pytrellis.load_database("../../../database")

    for job in jobs:
        cfg, prefix = job
        cfg.setup()

        netlist = []

        # Wishbone
        netlist.append(("R1C4_JWBCUFMIRQ_EFB", "driver"))
        netlist.append(("R1C4_JWBACKO_EFB", "driver"))
        for n in range(8):
            netlist.append(("R1C4_JWBDATO{}_EFB".format(n), "driver"))
            netlist.append(("R1C4_JWBDATI{}_EFB".format(n), "sink"))
            netlist.append(("R1C4_JWBADRI{}_EFB".format(n), "sink"))
            
        netlist.append(("R1C4_JWBWEI_EFB", "sink"))
        netlist.append(("R1C4_JWBSTBI_EFB", "sink"))
        netlist.append(("R1C4_JWBCYCI_EFB", "sink"))
        netlist.append(("R1C4_JWBRSTI_EFB", "sink"))
        netlist.append(("R1C4_JWBCLKI_EFB", "sink"))

        # PCNTR
        netlist.append(("R1C4_CFGWAKE_EFB", "driver"))
        netlist.append(("R1C4_CFGSTDBY_EFB", "driver"))

        # UFM
        netlist.append(("R1C4_JUFMSN_EFB", "sink"))

        # PLL
        for n in range(8):
            netlist.append(("R1C4_JPLLDATO{}_EFB".format(n), "driver"))
        for i in range(2):
            netlist.append(("R1C4_JPLL{}ACKI_EFB".format(i), "sink"))
            netlist.append(("R1C4_JPLL{}STBO_EFB".format(i), "driver"))
            for n in range(8):
                netlist.append(("R1C4_JPLL{}DATI{}_EFB".format(i,n), "sink"))
        for n in range(5):
            netlist.append(("R1C4_JPLLADRO{}_EFB".format(n), "driver"))
        netlist.append(("R1C4_JPLLWEO_EFB", "driver"))
        netlist.append(("R1C4_JPLLRSTO_EFB", "driver"))
        netlist.append(("R1C4_JPLLCLKO_EFB", "driver"))
        
        # Timer/Counter
        netlist.append(("R1C4_JTCOC_EFB", "driver"))
        netlist.append(("R1C4_JTCINT_EFB", "driver"))
        netlist.append(("R1C4_JTCIC_EFB", "sink"))
        netlist.append(("R1C4_JTCRSTN_EFB", "sink"))
        netlist.append(("R1C4_JTCCLKI_EFB", "sink"))

        # SPI
        netlist.append(("R1C4_JSPIIRQO_EFB", "driver"))
        netlist.append(("R1C4_JSPISCSN_EFB", "sink"))
        netlist.append(("R1C4_JSPICSNEN_EFB", "driver"))
        netlist.append(("R1C4_JSPIMOSIEN_EFB", "driver"))
        netlist.append(("R1C4_JSPIMOSIO_EFB", "driver"))
        netlist.append(("R1C4_JSPIMOSII_EFB", "sink"))
        netlist.append(("R1C4_JSPIMISOEN_EFB", "driver"))
        netlist.append(("R1C4_JSPIMISOO_EFB", "driver"))
        netlist.append(("R1C4_JSPIMISOI_EFB", "sink"))
        netlist.append(("R1C4_JSPISCKEN_EFB", "driver"))
        netlist.append(("R1C4_JSPISCKO_EFB", "driver"))
        netlist.append(("R1C4_JSPISCKI_EFB", "sink"))
        for n in range(8):
            netlist.append(("R1C4_JSPIMCSN{}_EFB".format(n), "driver"))

        # I2C primary
        netlist.append(("R1C4_JI2C1IRQO_EFB", "driver"))
        netlist.append(("R1C4_JI2C1SDAOEN_EFB", "driver"))
        netlist.append(("R1C4_JI2C1SDAO_EFB", "driver"))
        netlist.append(("R1C4_JI2C1SDAI_EFB", "sink"))
        netlist.append(("R1C4_JI2C1SCLOEN_EFB", "driver"))
        netlist.append(("R1C4_JI2C1SCLO_EFB", "driver"))
        netlist.append(("R1C4_JI2C1SCLI_EFB", "sink"))
        # I2C secondary
        netlist.append(("R1C4_JI2C2IRQO_EFB", "driver"))
        netlist.append(("R1C4_JI2C2SDAOEN_EFB", "driver"))
        netlist.append(("R1C4_JI2C2SDAO_EFB", "driver"))
        netlist.append(("R1C4_JI2C2SDAI_EFB", "sink"))
        netlist.append(("R1C4_JI2C2SCLOEN_EFB", "driver"))
        netlist.append(("R1C4_JI2C2SCLO_EFB", "driver"))
        netlist.append(("R1C4_JI2C2SCLI_EFB", "sink"))

        # Tamper
        netlist.append(("R1C4_JTAMPERDET_EFB", "driver"))
        netlist.append(("R1C4_JTAMPERTYPE0_EFB", "driver"))
        netlist.append(("R1C4_JTAMPERTYPE1_EFB", "driver"))
        netlist.append(("R1C4_JTAMPERSRC0_EFB", "driver"))
        netlist.append(("R1C4_JTAMPERSRC1_EFB", "driver"))
        netlist.append(("R1C4_JTAMPERDETEN_EFB", "sink"))
        netlist.append(("R1C4_JTAMPERLOCKSRC_EFB", "sink"))
        netlist.append(("R1C4_JTAMPERDETCLK_EFB", "sink"))

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
