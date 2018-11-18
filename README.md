# Project Trellis
 
## For FPGA Toolchain Users

Project Trellis enables a fully open-source flow for ECP5 FPGAs using [Yosys](https://github.com/YosysHQ/yosys)
for Verilog synthesis and [nextpnr](https://github.com/YosysHQ/nextpnr) for place and route.
Project Trellis itself provides the device database and tools for bitstream creation.

### Getting Started

Install the dependencies for Project Trellis:
 - Python 3.5 or later, including development libraries (`python3-dev` on Ubuntu)
 - A modern C++14 compiler (Clang is recommended)
 - CMake 3.5 or later
 - Boost including boost-python
 - Git
 
Clone the Project Trellis repository and download the latest database:

     git clone --recursive https://github.com/SymbiFlow/prjtrellis
     
Install _libtrellis_ and associated tools. You _must_ run `cmake` from the libtrellis directory.
Out-of-tree builds are currently unsupported when coupled with `nextpnr`:

    cd libtrellis
    cmake -DCMAKE_INSTALL_PREFIX=/usr .
    make
    sudo make install

Clone and install **latest git master** versions (Yosys 0.8 is not sufficient for ECP5 development) of [Yosys](https://github.com/YosysHQ/yosys)
 and [nextpnr](https://github.com/YosysHQ/nextpnr) according to their own instructions. Ensure
 to include the ECP5 architecture when building nextpnr; and point it towards your prjtrellis
 folder.

You should now be able to build the [examples](examples).

### Current Status
 
The following features are currently working in the Yosys/nextpnr/Trellis flow.
 - Logic slice functionality, including carries
 - Distributed RAM inside logic slices
 - All internal interconnect
 - Basic IO, including tristate, using `TRELLIS_IO` primitives. Pin location and IO type
 must be specified as attributes on these primitives, separate IO constraint files are not yet implemented.
 - Block RAM, using either inference in Yosys or manual instantiation of the DP16KD primitive
 - Multipliers using manual instantiation of the MULT18X18D primitive. Inference and more advanced DSP features
 are not yet supported.
 - Global networks (automatically promoted and routed in nextpnr)

### Development Boards
Project Trellis supports all ECP5 devices and should work with any development board. The following
boards have been tested and confirmed working:
 - [Lattice ECP5-5G Versa Development Kit](http://www.latticesemi.com/Products/DevelopmentBoardsAndKits/ECP55GVersaDevKit.aspx)
 - [Lattice ECP5 Evaluation Board](http://www.latticesemi.com/ecp5-evaluation)
 - [Radiona ULX3S](https://github.com/emard/ulx3s) (open hardware)
 - [TinyFPGA](https://tinyfpga.com/) Ex (coming soon)

## For Developers

Project Trellis documents the Lattice ECP5 bit-stream format and internal architecture. Current documentation is
located in machine-readable format in [prjtrellis-db](https://github.com/SymbiFlow/prjtrellis-db)
and is also [published online as HTML](https://symbiflow.github.io/prjtrellis-db/).

This repository contains both tools and scripts which allow you to document the
bit-stream format of Lattice ECP5 series FPGAs.

More documentation can be found published on
[prjtrellis ReadTheDocs site](http://prjtrellis.readthedocs.io/en/latest/) -
this includes;
 * [Highlevel Bitstream Architecture](http://prjtrellis.readthedocs.io/en/latest/architecture/overview.html)
 * [Overview of DB Development Process](http://prjrellis.readthedocs.io/en/latest/db_dev_process/overview.html)
 * [libtrellis Documentation](http://prjrellis.readthedocs.io/en/latest/libtrellis/overview.html)

This follows follows the lead of
[Project X-Ray](https://github.com/SymbiFlow/prjxray) - which is documenting
the bitstream format for the Xilinx Series 7 devices.

### Quickstart Guide

Currently Project Trellis is tested on Arch Linux, Ubuntu 17.10 and
Ubuntu 16.04.

Install the dependencies:
 - Lattice Diamond 3.10
 - Python 3.5 or later, including development libraries (`python3-dev` on Ubuntu)
 - A modern C++14 compiler (Clang is recommended)
 - CMake 3.5 or later
 - Boost including boost-python
 
For a generic environment:

    source environment.sh

Optionally, modify `user_environment.sh` and rerun the above command if needed.

Build libtrellis:

    cd libtrellis
    cmake .
    make


(Re-)creating parts of the database, for example LUT interconnect:

    cd fuzzers/001-plc2_routing
    TRELLIS_JOBS=`nproc` python3 fuzzer.py

## Process

The documentation is done through a "black box" process were Diamond is asked to
generate a large number of designs which then used to create bitstreams. The
resulting bit streams are then cross correlated to discover what different bits
do.

This follows the same process as
[Project X-Ray](https://github.com/SymbiFlow/prjxray) -
[more documentation can be found here](https://prjxray.readthedocs.org).

### Parts

#### [Minitests](minitests)

There are also "minitests" which are small tests of features used to build fuzers.

#### [Fuzzers](fuzzers)

Fuzzers are the scripts which generate the large number of bitstream.

They are called "fuzzers" because they follow an approach similar to the
[idea of software testing through fuzzing](https://en.wikipedia.org/wiki/Fuzzing).

#### [Tools](tools)

Miscellaneous tools for exploring the database and experimenting with bitstreams.

#### [Util](util)

Python libraries used for fuzzers and other purposes

#### [libtrellis](libtrellis)

libtrellis is a library for manipulating ECP5 bitstreams, tiles and the Project
Trellis databases. It is written with C++, with Python bindings exposed using
Boost::Python so that fuzzers and utilities can be written in Python.

### Database

Running the all fuzzers in order will produce a database which documents the
bitstream format in the [database](database) directory.


## Credits

Thanks to @tinyfpga for the original inspiration, and @mithro for the name and initial support.

Thanks to @q3k, @emard and @tinyfpga for their donations of ECP5 hardware that have made real-world
testing and demos possible.

## Contributing

There are a couple of guidelines when contributing to Project Trellis which are
listed here.

### Sending

All contributions should be sent as
[GitHub Pull requests](https://help.github.com/articles/creating-a-pull-request-from-a-fork/).

### License

All code in the Project Trellis repository is licensed under the very permissive
[ISC Licence](COPYING). A copy can be found in the [`COPYING`](COPYING) file.

All new contributions must also be released under this license.

### Code of Conduct

By contributing you agree to the [code of conduct](CODE_OF_CONDUCT.md). We
follow the open source best practice of using the [Contributor
Covenant](https://www.contributor-covenant.org/) for our Code of Conduct.
