"""
This module provides a structure to define the fuzz environment
"""
import os
from os import path
from string import Template
import diamond


class FuzzConfig:
    def __init__(self, job, family, device, tiles, ncl, mapargs=None):
        """
        :param job: user-friendly job name, used for folder naming etc
        :param family: Target family name
        :param device: Target device name
        :param tiles: List of tiles to consider during fuzzing
        :param ncl: Minimal NCL file to use as a base for interconnect fuzzing
        """
        self.job = job
        self.family = family
        self.device = device
        self.tiles = tiles
        self.ncl = ncl
        self.ncd_specimen = None
        self.mapargs = mapargs

    @property
    def workdir(self):
        return path.join(".", "work", self.job)

    def make_workdir(self):
        """Create the working directory for this job, if it doesn't exist already"""
        os.makedirs(self.workdir, exist_ok=True)

    def setup(self, skip_specimen=False):
        """
        Create a working directory, and run Diamond on a minimal ncl file to create a ncd/prf for Tcl usage
        """
        self.make_workdir()
        if not skip_specimen:
            self.build_design(self.ncl, {})

    def build_design(self, des_template, substitutions, prefix="", no_trce=True, backanno=False):
        """
        Run Diamond on a given design template, applying a map of substitutions, plus some standard substitutions
        if not overriden.

        :param des_template: path to template NCL/Verilog file
        :param substitutions: dictionary containing template subsitutions to apply to NCL/Verilog file
        :param prefix: prefix to append to filename, for running concurrent jobs without collisions

        Returns the path to the output bitstream
        """
        subst = dict(substitutions)
        if "route" not in subst:
            subst["route"] = ""
        if "sysconfig" not in subst:
            subst["sysconfig"] = ""
        ext = des_template.split(".")[-1]
        lpf_template = des_template.replace("." + ext, ".lpf")
        prf_template = des_template.replace("." + ext, ".prf")

        desfile = path.join(self.workdir, prefix + "design." + ext)
        bitfile = path.join(self.workdir, prefix + "design.bit")
        lpffile = path.join(self.workdir, prefix + "design.lpf")
        prffile = path.join(self.workdir, prefix + "design.prf")

        if path.exists(bitfile):
            os.remove(bitfile)
        with open(des_template, "r") as inf:
            with open(desfile, "w") as ouf:
                ouf.write(Template(inf.read()).substitute(**subst))
        if path.exists(lpf_template):
            with open(lpf_template, "r") as inf:
                with open(lpffile, "w") as ouf:
                    ouf.write(Template(inf.read()).substitute(**subst))
        if path.exists(prf_template):
            with open(prf_template, "r") as inf:
                with open(prffile, "w") as ouf:
                    ouf.write(Template(inf.read()).substitute(**subst))
        diamond.run(self.device, desfile, no_trce=no_trce, backanno=backanno, mapargs=self.mapargs)
        if ext == "ncl" and self.ncd_specimen is None:
            self.ncd_specimen = path.join(self.workdir, prefix + "design.tmp", "par_impl.ncd")
        return bitfile


    @property
    def ncd_prf(self):
        """
        A (ncd, prf) file tuple for Tcl. build_design must have been run at least once prior to accessing this property
        """
        assert self.ncd_specimen is not None
        prf = self.ncd_specimen.replace("par_impl.ncd", "synth_impl.prf")
        return self.ncd_specimen, prf
