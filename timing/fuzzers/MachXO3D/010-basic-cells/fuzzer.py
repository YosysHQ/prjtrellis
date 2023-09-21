import cell_fuzzers

def include_cell_XO3D(name, type):
    type = type.split('/')[-1].split("_")[0]
    return type.isupper() and "_" not in type


def rewrite_celltype_XO3D(name, type):
    return type.split('/')[-1].split("_")[0]

def main():
    cell_fuzzers.build_and_add(["../../../resource/picorv32_large.v", "../../../resource/picorv32_large_blockram.v", "../../../resource/distributed_ram.v", "../../../resource/altair.v", "../../../resource/jt49.v", "../../../resource/jt5205.v", "../../../resource/jt7759.v"], density="9400", family="MachXO3D", inc_cell=include_cell_XO3D, rw_cell_func=rewrite_celltype_XO3D)


if __name__ == "__main__":
    main()
