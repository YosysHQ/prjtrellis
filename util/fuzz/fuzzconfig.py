"""
This module provides a structure to define the fuzz environment
"""
import os
from os import path
from string import Template
import diamond


class FuzzConfig:
    def __init__(self, job, family, device, tiles, ncl):
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

    @property
    def workdir(self):
        return path.join(".", "work", self.job)

    def make_workdir(self):
        """Create the working directory for this job, if it doesn't exist already"""
        os.makedirs(self.workdir, exist_ok=True)

    def setup(self):
        """
        Create a working directory, and run Diamond on a minimal ncl file to create a ncd/prf for Tcl usage
        """
        self.make_workdir()
        self.build_design(self.ncl, {})

    def build_design(self, ncl_template, ncl_substitutions, prefix=""):
        """
        Run Diamond on a given NCL template, applying a map of substitutions, plus some standard substitutions
        if not overriden.

        :param ncl_template: path to template NCL file
        :param ncl_substitutions: dictionary containing template subsitutions to apply to NCL file
        :param prefix: prefix to append to filename, for running concurrent jobs without collisions

        Returns the path to the output bitstream
        """
        subst = dict(ncl_substitutions)
        if "route" not in subst:
            subst["route"] = ""
        nclfile = path.join(self.workdir, prefix + "design.ncl")
        with open(ncl_template, "r") as inf:
            with open(nclfile, "w") as ouf:
                ouf.write(Template(inf.read()).substitute(**subst))
        diamond.run(self.device, nclfile)
        if self.ncd_specimen is None:
            self.ncd_specimen = path.join(self.workdir, prefix + "design.tmp", "par_impl.ncd")
        return path.join(self.workdir, prefix + "design.bit")

    @property
    def ncd_prf(self):
        """
        A (ncd, prf) file tuple for Tcl. build_design must have been run at least once prior to accessing this property
        """
        assert self.ncd_specimen is not None
        prf = self.ncd_specimen.replace("par_impl.ncd", "synth_impl.prf")
        return self.ncd_specimen, prf
