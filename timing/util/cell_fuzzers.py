"""
Utilities for fuzzing cell timing
"""
from fuzzconfig import FuzzConfig
import fuzzloops
import cell_timings
import timing_dbs
from os import path


def timing_configs(job, design, density="45", family="ECP5"):
    # speedgrade, fuzzconfig
    if family == "ECP5":
        return [
            ("6", FuzzConfig(job + "_6", "ECP5", "LFE5U-{}F".format(density), [], design, "-s 6")),
            ("7", FuzzConfig(job + "_7", "ECP5", "LFE5U-{}F".format(density), [], design, "-s 7")),
            ("8", FuzzConfig(job + "_8", "ECP5", "LFE5U-{}F".format(density), [], design, "-s 8")),
            ("8_5G", FuzzConfig(job + "_8_5G", "ECP5", "LFE5UM5G-{}F".format(density), [], design, "-s 8"))
        ]
    elif family == "MachXO2":
        return [
            ("1", FuzzConfig(job + "_1", "MachXO2", "LCMXO2-{}ZE".format(density), [], design, "-s 1")),
            ("2", FuzzConfig(job + "_2", "MachXO2", "LCMXO2-{}ZE".format(density), [], design, "-s 2")),
            ("3", FuzzConfig(job + "_3", "MachXO2", "LCMXO2-{}ZE".format(density), [], design, "-s 3")),
            ("4", FuzzConfig(job + "_4", "MachXO2", "LCMXO2-{}HE".format(density), [], design, "-s 4")),
            ("5", FuzzConfig(job + "_5", "MachXO2", "LCMXO2-{}HE".format(density), [], design, "-s 5")),
            ("6", FuzzConfig(job + "_6", "MachXO2", "LCMXO2-{}HE".format(density), [], design, "-s 6")),
        ]
    elif family == "MachXO3":
        return [
            ("5", FuzzConfig(job + "_5", "MachXO3", "LCMXO3LF-{}C".format(density), [], design, "-s 5")),
            ("6", FuzzConfig(job + "_6", "MachXO3", "LCMXO3LF-{}C".format(density), [], design, "-s 6")),
        ]
    elif family == "MachXO3D":
        return [
            ("2", FuzzConfig(job + "_2", "MachXO3D", "LCMXO3D-{}ZC".format(density), [], design, "-s 2")),
            ("3", FuzzConfig(job + "_3", "MachXO3D", "LCMXO3D-{}ZC".format(density), [], design, "-s 3")),
            ("5", FuzzConfig(job + "_5", "MachXO3D", "LCMXO3D-{}HC".format(density), [], design, "-s 5")),
            ("6", FuzzConfig(job + "_6", "MachXO3D", "LCMXO3D-{}HC".format(density), [], design, "-s 6")),
        ]
    assert False


def build_and_add(designs, density="45", family="ECP5", inc_cell=cell_timings.include_cell, rw_cell_func=cell_timings.rewrite_celltype,
                  rw_pin_func=cell_timings.rewrite_pin):
    jobs = []
    sdfs = dict()
    for des in designs:
        jobs += timing_configs(path.basename(des).replace(".v", ""), des, density, family)
    for job in jobs:
        grade, cfg = job
        sdfs[grade] = []

    def per_job(job):
        grade, cfg = job
        cfg.setup(skip_specimen=True)
        bitf = cfg.build_design(cfg.ncl, {}, backanno=True, substitute=False)
        sdf = bitf.replace(".bit", ".sdf")
        sdfs[grade].append(sdf)

    fuzzloops.parallel_foreach(jobs, per_job)
    for grade in sdfs.keys():
        db = timing_dbs.cells_db_path(family, grade)
        for sdf in sdfs[grade]:
            cell_timings.add_sdf_to_database(db, sdf, include_cell_predicate=inc_cell, rewrite_cell_func=rw_cell_func,
                                             rewrite_pin_func=rw_pin_func)
