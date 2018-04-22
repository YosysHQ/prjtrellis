# Project Trellis

Documenting the Lattice ECP5 bit-stream format.

This repository contains both tools and scripts which allow you to document the
bit-stream format of Lattice ECP5 series FPGAs.

More documentation can be found published on
[prjtrellis ReadTheDocs site](http://prjtrellis.readthedocs.io/en/latest/) -
this includes;
 * FIXME(@tinyfpga): Make these documents.
 * [Highlevel Bitstream Architecture](http://prjtrellis.readthedocs.io/en/latest/architecture/overview.html)
 * [Overview of DB Development Process](http://prjrellis.readthedocs.io/en/latest/db_dev_process/overview.html)

This follows follows the lead of
[Project X-Ray](https://github.com/SymbiFlow/prjxray) - which is documenting
the bitstream format for the Xilinx Series 7 devices.

# Quickstart Guide

Install XXXXX
    FIXME(@tinyfpga): Put instructions here.

Pull submodules:

    git submodule update --init --recursive

Get a head start by downloading current database:

    # Give the argument;
    # - https if you to use the https protocol (default)
    # - git+ssh if you want to use git+ssh protocol
    # - git if you want to use the git protocol
    ./download-latest-db.sh

Always make sure to set the environment for the device you are working on before
running any other commands:

    source database/XXXXXX/settings.sh

Creating HTML documentation:

    cd htmlgen
    python3 htmlgen.py

(Re-)creating the database:

    cd fuzzers
    make -j$(nproc)

(Re-)creating parts of the database, for example LUT init bits:

    cd fuzzers/010-lutinit
    make -j$(nproc) run

# Process

The documentation is done through a "black box" process were XXXXX is asked to
generate a large number of designs which then used to create bitstreams. The
resulting bit streams are then cross correlated to discover what different bits
do.

This follows the same process as
[Project X-Ray](https://github.com/SymbiFlow/prjxray) -
[more documentation can be found here](https://prjxray.readthedocs.org).

## Parts

### [Minitests](minitests)

There are also "minitests" which are designs which can be viewed by a human in
Vivado to better understand how to generate more useful designs.

### [Experiments](experiments)

Experiments are like "minitests" except are only useful for a short period of
time. Files are committed here to allow people to see how we are trying to
understand the bitstream.

When an experiment is finished with, it will be moved from this directory into
the latest "prjxray-experiments-archive-XXXX" repository.

### [Fuzzers](fuzzers)

Fuzzers are the scripts which generate the large number of bitstream.

They are called "fuzzers" because they follow an approach similar to the
[idea of software testing through fuzzing](https://en.wikipedia.org/wiki/Fuzzing).

### [Tools](tools) & [Libs](libs)

Tools & libs are useful tools (and libraries) for converting the resulting
bitstreams into various formats.

Binaries in the tools directory are considered more mature and stable then
those in the [utils](utils) directory and could be actively used in other
projects.

### [Utils](utils)

Utils are various tools which are still highly experimental. These tools should
only be used inside this repository.

### [Third Party](third_party)

Third party contains code not developed as part of Project X-Ray.


# Database

Running the all fuzzers in order will produce a database which documents the
bitstream format in the [database](database) directory.

# Current Focus

The current focus is understanding the ECP5 programmable logic cells (PLC) and connectivity between the cells.

The aim is to eventually document all parts in the Lattice ECP5 series FPGAs
but we can not do this alone, **we need your help**!


## TODO List

 - [ ] Write a TODO list


# Contributing

There are a couple of guidelines when contributing to Project Trellis which are
listed here.

### Sending

All contributions should be sent as
[GitHub Pull requests](https://help.github.com/articles/creating-a-pull-request-from-a-fork/).

### License

All code in the Project X-Ray repository is licensed under the very permissive
[ISC Licence](COPYING). A copy can be found in the [`COPYING`](COPYING) file.

All new contributions must also be released under this license.

### Code of Conduct

By contributing you agree to the [code of conduct](CODE_OF_CONDUCT.md). We
follow the open source best practice of using the [Contributor
Covenant](https://www.contributor-covenant.org/) for our Code of Conduct.

### Sign your work

To improve tracking of who did what, we follow the Linux Kernel's
["sign your work" system](https://github.com/wking/signed-off-by).
This is also called a
["DCO" or "Developer's Certificate of Origin"](https://developercertificate.org/).

**All** commits are required to include this sign off and we use the
[Probot DCO App](https://github.com/probot/dco) to check pull requests for
this.

The sign-off is a simple line at the end of the explanation for the
patch, which certifies that you wrote it or otherwise have the right to
pass it on as a open-source patch.  The rules are pretty simple: if you
can certify the below:

        Developer's Certificate of Origin 1.1

        By making a contribution to this project, I certify that:

        (a) The contribution was created in whole or in part by me and I
            have the right to submit it under the open source license
            indicated in the file; or

        (b) The contribution is based upon previous work that, to the best
            of my knowledge, is covered under an appropriate open source
            license and I have the right under that license to submit that
            work with modifications, whether created in whole or in part
            by me, under the same open source license (unless I am
            permitted to submit under a different license), as indicated
            in the file; or

        (c) The contribution was provided directly to me by some other
            person who certified (a), (b) or (c) and I have not modified
            it.

	(d) I understand and agree that this project and the contribution
	    are public and that a record of the contribution (including all
	    personal information I submit with it, including my sign-off) is
	    maintained indefinitely and may be redistributed consistent with
	    this project or the open source license(s) involved.

then you just add a line saying

	Signed-off-by: Random J Developer <random@developer.example.org>

using your real name (sorry, no pseudonyms or anonymous contributions.)
