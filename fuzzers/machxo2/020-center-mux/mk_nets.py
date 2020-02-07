# This script is used to autogenerate a list of suspected fixed-connection nets
# within the center MUX that controls global nets.
def mk_numbered_nets(net_list, range_iter):
    return [n.format(i) for i in range_iter for n in net_list]

# Some inputs to the center MUX are two nets concatenated together; the "first"
# net is a sink from locations throughout the FPGA, the "second" is the actual
# input to the center MUX. They should all become fixed connections, but
# fuzz _just_ in case.
inputs_2a = mk_numbered_nets(["R6C13_JPCLKCIBLLQ{0}",
                             "R6C13_JPCLKCIBLRQ{0}",
                             "R6C13_JPCLKCIBVIQB{0}",
                             "R6C13_JECLKCIBB{0}",
                             "R6C13_JECLKCIBT{0}",
                             "R6C13_JPCLKCIBVIQT{0}"], range(2)) + \
           mk_numbered_nets(["R6C13_JPCLKCIBMID{0}"], range(2,4))

# The "second" net of the concatenated inputs.
inputs_2b = mk_numbered_nets(["R6C13_PCLKCIBLLQ{0}",
                           "R6C13_PCLKCIBLRQ{0}",
                           "R6C13_PCLKCIBVIQB{0}",
                           "R6C13_ECLKCIBB{0}",
                           "R6C13_ECLKCIBT{0}",
                           "R6C13_PCLKCIBVIQT{0}"], range(2)) + \
         mk_numbered_nets(["R6C13_PCLKCIBMID{0}"], range(2,4))

# All other inputs which are _not_ concatenations of two nets.
inputs_1 = mk_numbered_nets(["R6C13_JSNETCIBMID{0}"], range(8)) + \
           mk_numbered_nets(["R6C13_JPCLKT2{0}",
                             "R6C13_JBCDIVX{0}",
                             "R6C13_JBCDIV1{0}",
                             "R6C13_JTCDIVX{0}",
                             "R6C13_JTCDIV1{0}",
                             "R6C13_JPCLKT0{0}",
                             "R6C13_JSNETCIBL{0}",
                             "R6C13_JSNETCIBT{0}",
                             "R6C13_JSNETCIBR{0}",
                             "R6C13_JSNETCIBB{0}"], range(2)) + \
           mk_numbered_nets(["R6C13_JLPLLCLK{0}"], range(4)) + \
           mk_numbered_nets(["R6C13_JPCLKT3{0}"], range(3)) + \
           ["R6C13_JPCLKT10"]

# Mux selects on the outputs.
sels = mk_numbered_nets(["R6C13_JCE{0}_DCC"], range(8)) + \
       mk_numbered_nets(["R6C13_JSEL{0}_DCM"], range(6,8))

# Unfortunately, same deal w/ concatenated nets also applies to the output.
# "second" is kinda a misnomer here- clock nets go through tristates, although
# TCL claims a fixed connection. There are multiple layers of fixed connections
# where the net names change on the outputs, so we just take care of all
# suspected fixed connections in one fell swoop.

# Global nets 6 and 7 are "MUX"ed twice- once to choose between two
# connections, another for clock enable (CEN).
# All the initial output connections are attached to Muxes
# outputs_3a = []

outputs_3b = mk_numbered_nets(["R6C13_CLK{0}_6_DCM",
                               "R6C13_CLK{0}_7_DCM"], range(2)) + \
             mk_numbered_nets(["R6C13_CLK{0}_0_ECLKBRIDGECS",
                               "R6C13_CLK{0}_1_ECLKBRIDGECS"], range(2))

outputs_3c = mk_numbered_nets(["R6C13_DCMOUT{0}_DCM"], range(6,8)) + \
             mk_numbered_nets(["R6C13_JECSOUT{0}_ECLKBRIDGECS"], range(2))

# CLKO connections gated by a MUX connected to fabric; defaults to pass-through
# in configuration.
outputs_2a =  mk_numbered_nets(["R6C13_CLKI{0}_DCC"], range(8))

outputs_2b =  mk_numbered_nets(["R6C13_CLKO{0}_DCC"], range(8))

# And also include muxed connections.
muxed =  mk_numbered_nets(["R6C13_VSRX0{0}00"], range(8)) + \
         mk_numbered_nets(["R6C13_VPRXCLKI{0}"], range(6)) + \
         mk_numbered_nets(["R6C13_VPRXCLKI6{0}",
                           "R6C13_VPRXCLKI7{0}"], range(2)) + \
         mk_numbered_nets(["R6C13_EBRG0CLK{0}",
                           "R6C13_EBRG1CLK{0}"], range(2))

# CLK{0,1}_{0,1}_ECLKBRIDGECS do not in fact drive R6C13_JSEL{0}_ECLKBRIDGECS.
# R6C13_JSEL{0}_ECLKBRIDGECS is driven from elsewhere. Ignore for now.
muxed2 = mk_numbered_nets(["R6C13_JSEL{0}_ECLKBRIDGECS"], range(2))

def main():
    print("inputs_2a:", len(inputs_2a))
    print("inputs_2b:", len(inputs_2b))
    print("inputs_1:", len(inputs_1))
    print("sels:", len(sels))
    print("outputs_3b:", len(outputs_3b))
    print("outputs_3c:", len(outputs_3c))
    print("outputs_2a:", len(outputs_2a))
    print("outputs_2b:", len(outputs_2b))
    print("muxed:", len(muxed))
    print("alternate muxed:", len(muxed2))

    all_fixed = inputs_2a + inputs_2b + inputs_1 + sels + \
                outputs_3b + outputs_3c + outputs_2a + outputs_2b

    print("total fixed:", len(all_fixed))
    print("grand total:", len(all_fixed) + len(muxed) + len(muxed2))

    with open("global_fixed.txt", "w") as fp:
        fp.write("\n".join(all_fixed))

    with open("global_mux.txt", "w") as fp:
        fp.write("\n".join(muxed))

    with open("global_mux2.txt", "w") as fp:
        fp.write("\n".join(muxed2))

if __name__ == "__main__":
    main()
