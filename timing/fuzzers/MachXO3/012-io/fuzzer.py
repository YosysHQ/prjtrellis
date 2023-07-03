import cell_fuzzers


def include_cell(name, type):
    return type.startswith("io_")


def rewrite_cell(name, type, family):
    if type.startswith("io_"):
        return "PIO:IOTYPE={}".format(type.split("_", 1)[1])
    else:
        return type


def rewrite_pin(name, celltype, pin):
    if type(pin) is list:
        return list(rewrite_pin(name, celltype, x) for x in pin)
    if pin.startswith("io_"):
        return "PAD"
    else:
        return pin


def main():
    cell_fuzzers.build_and_add(["pio.v"], inc_cell=include_cell, rw_cell_func=rewrite_cell, rw_pin_func=rewrite_pin, density="6900", family="MachXO3")


if __name__ == "__main__":
    main()
