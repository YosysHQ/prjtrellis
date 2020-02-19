from nets import net_product, char_range
from itertools import product, starmap
from collections import defaultdict

# A, B, C, D, F, M, Q- 0-7
# CE, CLK, LSR- 0-3
# Useful helpers to flatten nested iterators.
def char_product(chars, ids):
    return starmap(lambda l, n: "".join([l, n]), product(chars, ids))

# Hint: F/Q are sinks for "driver"s, A-D are sources for "sinks".
templates_override = {
    "b": [
        (["R12C11_JRXDA{}_BIOLOGIC"], range(0,8), "driver"),
        (["R12C11_JDI{}",
          "R12C11_JIN{}_IOLOGIC"], char_range("A","E"), "driver"),
        (["R12C11_JPADDO{}",
          "R12C11_JPADDT{}"], char_range("A","E"), "driver"),
        (["R12C11_JRXD{}A_BIOLOGIC",
          "R12C11_JRXD{}C_BSIOLOGIC"], range(0,4), "driver"),
        (["R12C11_JDEL{}A_BIOLOGIC",
          "R12C11_JDEL{}C_BSIOLOGIC"], range(0,5), "sink"),
        (["R12C11_JI{}A_BIOLOGIC",
          "R12C11_JI{}B_IOLOGIC",
          "R12C11_JI{}C_BSIOLOGIC",
          "R12C11_JI{}D_IOLOGIC"], ["N", "P"], "sink"),
        (["R12C11_JOPOS{}",
          "R12C11_JONEG{}",
          "R12C11_JTS{}",
          "R12C11_JCLK{}",
          "R12C11_JLSR{}",
          "R12C11_JCE{}"], ["A_BIOLOGIC", "B_IOLOGIC", "C_BSIOLOGIC",
                            "D_IOLOGIC"], "sink"),
          (["R12C11_JSLIP{}"], ["A_BIOLOGIC",
                               "C_BSIOLOGIC"], "sink")
    ],

    # Manually verified to be safe to ignore. They are either I/O connections
    # we fuzz in "b" (BIOLOGIC, etc), CIBTEST, or extraneous connections
    # that would imply bidirectional nets.
    # (R11C11_V02N0001 --- R11C11_V02S0000, etc). TODO: Look into bidir nets?
    "b_cib": [
        # (["R11C11_J{}_CIBTEST"], char_product(["A", "B", "C", "D", "F", "M",
        #                                        "Q", "OFX"],
        #                                       char_range("0", "8")), "ignore"),
        # (["R11C11_J{}_CIBTEST"], char_product(["CE", "CLK", "LSR"],
        #                                       char_range("0", "4")), "ignore"),
        # (["R11C11_J{}"], char_product(["A", "B", "C", "D", "M"],
        #                               char_range("0", "8")), "sink"),
        # (["R11C11_J{}"], char_product(["CE", "CLK", "LSR"],
        #                               char_range("0", "4")), "sink"),
        # (["R11C11_J{}"], char_product(["F", "Q", "OFX"], char_range("0", "8")),
        #                               "source"),
    ],

    # Left and Right are done from CIB's POV because
    # there are no tiles dedicated strictly to I/O connections.
    # Ignore loopback/CIBTEST nets for now.
    # A, B, C, D, CLK, CE, F, LSR, M, OFX, Q
    "l": [
        (["R10C1_JA{}",
          "R10C1_JB{}",
          "R10C1_JC{}",
          "R10C1_JCLK{}",
          "R10C1_LSR{}",
          "R10C1_JCE{}"], range(0,4), "driver"),
        (["R10C1_JQ{}"], range(0,4), "sink"),
        (["R10C1_JF{}"], range(0,8), "sink")
    ],

    "r": [
        (["R10C22_JA{}",
          "R10C22_JB{}",
          "R10C22_JC{}",
          "R10C22_JCLK{}",
          "R10C22_LSR{}",
          "R10C22_JCE{}"], range(0,4), "driver"),
        (["R10C22_JQ{}"], range(0,4), "sink"),
        (["R10C22_JF{}"], range(0,8), "sink")
    ]
}

overrides = {k: defaultdict(lambda : str("ignore")) for k in templates_override.keys()}
# overrides = {k: {} for k in templates_override.keys()}

for (var, temp) in templates_override.items():
    for (n, r, d) in temp:
        for p in net_product(n, r):
            overrides[var][p] = d


def main():
    for k, v in overrides.items():
        print("{}: {}".format(k, v))
        print("")

    sum = 0
    for k in overrides.keys():
        s = len(overrides[k])
        print("total {}: {}".format(k, s))
        sum = sum + s

    print("grand total: {}".format(sum))


if __name__ == "__main__":
    main()
