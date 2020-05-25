from nets import *

assert ecp5.is_global("R2C7_HPBX0100")
assert ecp5.is_global("R24C12_VPTX0700")
assert ecp5.is_global("R22C40_HPRX0300")
assert ecp5.is_global("R34C67_ULPCLK7")
assert not ecp5.is_global("R22C67_H06E0003")
assert ecp5.is_global("R24C67_VPFS0800")
assert ecp5.is_global("R1C67_JPCLKT01")

assert is_cib("R47C61_Q4")
assert is_cib("R47C58_H06W0003")
assert is_cib("R47C61_CLK0")

assert normalise_name((95, 126), "R48C26", "R48C26_B1", "ECP5") == "B1"
assert normalise_name((95, 126), "R48C26", "R48C26_HPBX0600", "ECP5") == "G_HPBX0600"
assert normalise_name((95, 126), "R48C26", "R48C25_H02E0001", "ECP5") == "W1_H02E0001"
assert normalise_name((95, 126), "R48C1", "R48C1_H02E0002", "ECP5") == "W1_H02E0001"
assert normalise_name((95, 126), "R82C90", "R79C90_V06S0003", "ECP5") == "N3_V06S0003"
assert normalise_name((95, 126), "R5C95", "R3C95_V06S0004", "ECP5") == "N3_V06S0003"
assert normalise_name((95, 126), "R1C95", "R1C95_V06S0006", "ECP5") == "N3_V06S0003"
assert normalise_name((95, 126), "R3C95", "R2C95_V06S0005", "ECP5") == "N3_V06S0003"
assert normalise_name((95, 126), "R82C95", "R85C95_V06N0303", "ECP5") == "S3_V06N0303"
assert normalise_name((95, 126), "R90C95", "R92C95_V06N0304", "ECP5") == "S3_V06N0303"
assert normalise_name((95, 126), "R93C95", "R94C95_V06N0305", "ECP5") == "S3_V06N0303"
