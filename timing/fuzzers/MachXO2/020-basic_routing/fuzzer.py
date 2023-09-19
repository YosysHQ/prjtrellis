import timing_solver
import timing_dbs
import cell_fuzzers
import json
import fuzzloops


def main():
    jobs = []
    jobs += cell_fuzzers.timing_configs("picorv32", "../../../resource/picorv32_large.v", density="7000", family="MachXO2")

    def per_job(job):
        grade, cfg = job
        cfg.setup(skip_specimen=True)
        bitf = cfg.build_design(cfg.ncl, {}, backanno=True, substitute=False)
        ncl = bitf.replace(".bit", "_out.ncl")
        sdf = bitf.replace(".bit", ".sdf")
        data = timing_solver.solve_pip_delays(ncl, sdf)
        db = timing_dbs.interconnect_db_path("MachXO2", grade)
        with open(db, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)

    fuzzloops.parallel_foreach(jobs, per_job)


if __name__ == "__main__":
    main()
