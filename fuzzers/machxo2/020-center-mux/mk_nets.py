from nets import net_product

templates = {
    "fixed": [
        # Some inputs to the center MUX are two nets concatenated together; the
        # "first" net is a sink from locations throughout the FPGA, the
        # "second" is the actual input to the center MUX. They should all
        # become fixed connections, but fuzz _just_ in case.
        (["R6C13_JPCLKCIBLLQ{0}",
          "R6C13_JPCLKCIBLRQ{0}",
          "R6C13_JPCLKCIBVIQB{0}",
          "R6C13_JECLKCIBB{0}",
          "R6C13_JECLKCIBT{0}",
          "R6C13_JPCLKCIBVIQT{0}"], range(2)),
        (["R6C13_JPCLKCIBMID{0}"], range(2, 4)),

        # The "second" net of the concatenated inputs.
        (["R6C13_PCLKCIBLLQ{0}",
          "R6C13_PCLKCIBLRQ{0}",
          "R6C13_PCLKCIBVIQB{0}",
          "R6C13_ECLKCIBB{0}",
          "R6C13_ECLKCIBT{0}",
          "R6C13_PCLKCIBVIQT{0}"], range(2)),
        (["R6C13_PCLKCIBMID{0}"], range(2, 4)),

        # All other inputs which are _not_ concatenations of two nets.
        (["R6C13_JSNETCIBMID{0}"], range(8)),
        (["R6C13_JPCLKT2{0}",
          "R6C13_JBCDIVX{0}",
          "R6C13_JBCDIV1{0}",
          "R6C13_JTCDIVX{0}",
          "R6C13_JTCDIV1{0}",
          "R6C13_JPCLKT0{0}",
          "R6C13_JSNETCIBL{0}",
          "R6C13_JSNETCIBT{0}",
          "R6C13_JSNETCIBR{0}",
          "R6C13_JSNETCIBB{0}"], range(2)),
        (["R6C13_JLPLLCLK{0}"], range(4)),
        (["R6C13_JPCLKT3{0}"], range(3)),
        (["R6C13_JPCLKT10"], range(1)),

        # Mux selects on the outputs.
        (["R6C13_JCE{0}_DCC"], range(8)),
        (["R6C13_JSEL{0}_DCM"], range(6, 8)),

        # Unfortunately, same deal w/ concatenated nets also applies to the
        # output.
        # "second" is kinda a misnomer here- clock nets go through tristates,
        # although TCL claims a fixed connection. There are multiple layers of
        # fixed connections where the net names change on the outputs, so we
        # just take care of all suspected fixed connections in one fell swoop.
        #
        # All the initial output connections are attached to muxes controlled
        # by config bits, and thus are _not_ fixed.

        # Global nets 6 and 7 are "MUX"ed twice- once to choose between two
        # connections, another for clock enable (CEN). First net.
        (["R6C13_CLK{0}_6_DCM",
          "R6C13_CLK{0}_7_DCM"], range(2)),
        (["R6C13_CLK{0}_0_ECLKBRIDGECS",
          "R6C13_CLK{0}_1_ECLKBRIDGECS"], range(2)),

        # Second net. Connects to R6C13_CLKI{6,7}_DCC.
        (["R6C13_DCMOUT{0}_DCM"], range(6, 8)),
        (["R6C13_JECSOUT{0}_ECLKBRIDGECS"], range(2)),

        # All CLKO connections are gated by a MUX connected to fabric; defaults
        # to pass-through in configuration bits.
        (["R6C13_CLKI{0}_DCC"], range(8)),
        (["R6C13_CLKO{0}_DCC"], range(8)),
    ],

    "muxed": [
        # And also include muxed connections.
        (["R6C13_VSRX0{0}00"], range(8)),
        (["R6C13_VPRXCLKI{0}"], range(6)),
        (["R6C13_VPRXCLKI6{0}",
          "R6C13_VPRXCLKI7{0}"], range(2)),
        (["R6C13_EBRG0CLK{0}",
          "R6C13_EBRG1CLK{0}"], range(2))
    ],

    "ignore": [
        # CLK{0,1}_{0,1}_ECLKBRIDGECS do not in fact drive
        # R6C13_JSEL{0}_ECLKBRIDGECS. R6C13_JSEL{0}_ECLKBRIDGECS is driven from
        # elsewhere. Ignore for now.
        (["R6C13_JSEL{0}_ECLKBRIDGECS"], range(2))
    ],
}

nets = {k: [] for k in templates.keys()}

for (var, temp) in templates.items():
    for (n, r) in temp:
        for p in net_product(n, r):
            nets[var].append(p)


def main():
    for k, v in nets.items():
        print("{}: {}".format(k, v))
        print("")

    sum = 0
    for k in nets.keys():
        s = len(nets[k])
        print("total {}: {}".format(k, s))
        sum = sum + s

    print("grand total: {}".format(sum))


if __name__ == "__main__":
    main()
