def ebr_conns(tile):
    netlist = []
    for n in range(13):
        netlist.append(("R{}C{}_JADA{}_EBR".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_JADB{}_EBR".format(tile[0], tile[1], n), "sink"))

    for n in range(9):
        netlist.append(("R{}C{}_JDIA{}_EBR".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_JDIB{}_EBR".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_JDOA{}_EBR".format(tile[0], tile[1], n), "driver"))
        netlist.append(("R{}C{}_JDOB{}_EBR".format(tile[0], tile[1], n), "driver"))

    for n in range(3):
        netlist.append(("R{}C{}_JCSA{}_EBR".format(tile[0], tile[1], n), "sink"))
        netlist.append(("R{}C{}_JCSB{}_EBR".format(tile[0], tile[1], n), "sink"))

    for x in ("A", "B"):
        netlist.append(("R{}C{}_JCE{}_EBR".format(tile[0], tile[1], x), "sink"))
        netlist.append(("R{}C{}_JCLK{}_EBR".format(tile[0], tile[1], x), "sink"))
        netlist.append(("R{}C{}_JRST{}_EBR".format(tile[0], tile[1], x), "sink"))
        netlist.append(("R{}C{}_JWE{}_EBR".format(tile[0], tile[1], x), "sink"))
        netlist.append(("R{}C{}_JOCE{}_EBR".format(tile[0], tile[1], x), "sink"))

    netlist.append(("R{}C{}_JAE_EBR".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JAF_EBR".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JEF_EBR".format(tile[0], tile[1]), "sink"))
    netlist.append(("R{}C{}_JFF_EBR".format(tile[0], tile[1]), "sink"))
    return netlist

def main():
    for i, n in enumerate(ebr_conns((6,17))):
        print(i, n)

if __name__ == "__main__":
    main()
