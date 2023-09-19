import cell_fuzzers

def include_cell_XO2(name, type):
    type = type.split('/')[-1].split("_")[0]
    return type.isupper() and "_" not in type


def rewrite_celltype_XO2(name, type):
    return type.split('/')[-1].split("_")[0]

def main():
    cell_fuzzers.build_and_add(["../../../resource/picorv32_large.v", "../../../resource/picorv32_large_blockram.v", "../../../resource/distributed_ram.v"], density="7000", family="MachXO2", inc_cell=include_cell_XO2, rw_cell_func=rewrite_celltype_XO2)


if __name__ == "__main__":
    main()
