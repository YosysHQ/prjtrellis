import cell_fuzzers


def include_cell(name, type):
    return type.startswith("ebr_")


def rewrite_cell_regmode(name, type):
    if type.startswith("ebr_"):
        return "DP16KD:REGMODE_A={},REGMODE_B={}".format(type.split("_", 2)[1], type.split("_", 2)[2])
    else:
        return type

def rewrite_cell_wrmode(name, type):
    if type.startswith("ebr_"):
        return "DP16KD:WRITEMODE_A={},WRITEMODE_B={}".format(type.split("_", 2)[1], type.split("_", 2)[2])
    else:
        return type


def main():
    cell_fuzzers.build_and_add(["ebr_regmode.v"], inc_cell=include_cell, rw_cell_func=rewrite_cell_regmode)
    cell_fuzzers.build_and_add(["ebr_writemode.v"], inc_cell=include_cell, rw_cell_func=rewrite_cell_wrmode)


if __name__ == "__main__":
    main()
