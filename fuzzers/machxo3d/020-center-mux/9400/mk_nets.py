from nets import net_product

hfsn_cib = []
hfsn_cib.extend(net_product(["R15C25_JSNETCIBL{0}",
    "R15C25_JSNETCIBR{0}",
    "R15C25_JSNETCIBT{0}",
    "R15C25_JSNETCIBB{0}"],
    range(2)))
hfsn_cib.extend(net_product(["R15C25_JSNETCIBMID{0}"], range(8)))

hfsn_out = []
hfsn_out.extend(net_product(["R15C25_VSRX0{0}00"], range(8)))

global_cib = []
global_cib.extend(net_product(["R15C25_JPCLKCIBLLQ{0}",
    "R15C25_JPCLKCIBLRQ{0}",
    "R15C25_JPCLKCIBVIQB{0}",
    "R15C25_JPCLKCIBVIQT{0}"],
    range(2)))
global_cib.extend(net_product(["R15C25_JPCLKCIBMID{0}"], range(2, 4)))
global_cib.extend(net_product(["R15C25_PCLKCIBLLQ{0}",
    "R15C25_PCLKCIBLRQ{0}",
    "R15C25_PCLKCIBVIQB{0}",
    "R15C25_PCLKCIBVIQT{0}"],
    range(2)))
global_cib.extend(net_product(["R15C25_PCLKCIBMID{0}"], range(2, 4)))

global_out = []
global_out.extend(net_product(["R15C25_VPRXCLKI{0}"], range(6)))
global_out.extend(net_product(["R15C25_VPRXCLKI6{0}",
    "R15C25_VPRXCLKI7{0}"],
    range(2)))

eclk_cib = []
eclk_cib.extend(net_product(["R15C25_JECLKCIBB{0}",
    "R15C25_JECLKCIBT{0}"],
    range(2)))
eclk_cib.extend(net_product(["R15C25_ECLKCIBB{0}",
    "R15C25_ECLKCIBT{0}"],
    range(2)))

eclk_div = []
eclk_div.extend(net_product(["R15C25_JBCDIVX{0}",
    "R15C25_JBCDIV1{0}",
    "R15C25_JTCDIVX{0}",
    "R15C25_JTCDIV1{0}"],
    range(2)))

eclk_out = []
eclk_out.extend(net_product(["R15C25_EBRG0CLK{0}",
    "R15C25_EBRG1CLK{0}"],
    range(2)))

pll = []
pll.extend(net_product(["R15C25_JLPLLCLK{0}"], range(4)))

clock_pin = []
clock_pin.extend(net_product(["R15C25_JPCLKT2{0}",
    "R15C25_JPCLKT0{0}"],
    range(2)))
clock_pin.extend(net_product(["R15C25_JPCLKT3{0}"], range(3)))
clock_pin.extend(net_product(["R15C25_JPCLKT1{0}"], range(1)))

dcc = []
dcc.extend(net_product(["R15C25_CLKI{0}_DCC",
    "R15C25_CLKO{0}_DCC",
    "R15C25_JCE{0}_DCC"],
    range(8)))

# Unfortunately, same deal w/ concatenated nets also applies to the
# output.
# "second" is kinda a misnomer here- clock nets go through tristates,
# although TCL claims a fixed connection. There are multiple layers of
# fixed connections where the net names change on the outputs, so we
# just take care of all suspected fixed connections in one fell swoop.
#
# All the initial output connections are attached to muxes controlled
# by config bits, and thus are _not_ fixed.
dcm = []
# Global nets 6 and 7 are "MUX"ed twice- once to choose between two
# connections, another for clock enable (CEN). First net.
dcm.extend(net_product(["R15C25_CLK{0}_6_DCM",
    "R15C25_CLK{0}_7_DCM"],
    range(2)))
dcm.extend(net_product(["R15C25_JSEL{0}_DCM",
    "R15C25_DCMOUT{0}_DCM"],
    range(6, 8)))

# TODO: CLK{0,1}_{0,1}_ECLKBRIDGECS do not in fact drive
# R15C25_JSEL{0}_ECLKBRIDGECS. R6C13_JSEL{0}_ECLKBRIDGECS is driven from
# elsewhere.
eclkbridge = []
eclkbridge.extend(net_product(["R15C25_CLK{0}_0_ECLKBRIDGECS",
    "R15C25_CLK{0}_1_ECLKBRIDGECS",
    "R15C25_JECSOUT{0}_ECLKBRIDGECS",
    "R15C25_JSEL{0}_ECLKBRIDGECS"],
    range(2)))

all = [hfsn_cib, hfsn_out, global_cib, global_out, eclk_cib, eclk_div,
    eclk_out, pll, clock_pin, dcc, dcm, eclkbridge]

all_flat = []

def main():
    import json

    for l in all:
        all_flat.extend(l)

    print(json.dumps(all_flat))


if __name__ == "__main__":
    main()
