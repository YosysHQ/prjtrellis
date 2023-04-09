def pll_nets(tile):
    netlist = []
    for n in range(5):
        netlist.append(("R{}C{}_JPLLADDR{}_PLL".format(tile[0], tile[1], n), "sink"))

    for n in range(8):
        netlist.append(("R{}C{}_JPLLDATI{}_PLL".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_JPLLDATO{}_PLL".format(tile[0], tile[1], n), "driver"))
        if n not in (1,2):
            netlist.append(("R{}C{}_JREFCLK{}_PLL".format(tile[0], tile[1], n), "sink"))
        else:
            netlist.append(("R{}C{}_JREFCLK{}_0_PLL".format(tile[0], tile[1], n), "sink"))
            netlist.append(("R{}C{}_JREFCLK{}_1_PLL".format(tile[0], tile[1], n), "sink"))

    for n in range(2):
        netlist.append(("R{}C{}_CLK{}_PLLREFCS".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_REFCLK{}".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_TECLK{}".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_JPHASESEL{}_PLL".format(tile[0], tile[1], n), "sink"))

    for n in (0,1,2,4):
        netlist.append(("R{}C{}_JCLKFB{}".format(tile[0], tile[1], n), "sink"))

    for n in ("P", "S", "S2", "S3"):
        netlist.append(("R{}C{}_JCLKO{}_PLL".format(tile[0], tile[1], n), "driver"))
        netlist.append(("R{}C{}_JENCLKO{}_PLL".format(tile[0], tile[1], n), "sink"))

    for n in ("C", "D", "M"):
        netlist.append(("R{}C{}_JRESET{}_PLL".format(tile[0], tile[1], n), "sink"))

    netlist.append(("R{}C{}_CLKFB".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_CLKFB_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_CLKINTFB".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_CLKINTFB_PLL".format(tile[0], tile[1]), "driver"))
    netlist.append(("R{}C{}_CLKI_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JDPHSRC_PLL".format(tile[0], tile[1]), "driver"))
    netlist.append(("R{}C{}_JINTLOCK_PLL".format(tile[0], tile[1]), "driver"))

    netlist.append(("R{}C{}_JLOADREG_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JLOCK_PLL".format(tile[0], tile[1]), "driver"))
    netlist.append(("R{}C{}_JPHASEDIR_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JPHASESTEP_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JPLLACK_PLL".format(tile[0], tile[1]), "driver"))
    netlist.append(("R{}C{}_JPLLCLK_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JPLLRST_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JPLLSTB_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JPLLWAKESYNC_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JPLLWE_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JREFCLK_PLL".format(tile[0], tile[1]), "driver"))
    netlist.append(("R{}C{}_JRST_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JSEL_PLLREFCS".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JSTDBY_PLL".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_PLLCSOUT_PLLREFCS".format(tile[0], tile[1]), "driver"))
    return netlist

def main():
    for i, n in enumerate(pll_nets((1,2))):
        print(i, n)

if __name__ == "__main__":
    main()
