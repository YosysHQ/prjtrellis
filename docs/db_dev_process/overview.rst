Database Development Overview
=============================

A targeted approach is used to construct bitstream databases as quickly as possible. The planned flow is for every
routing mux or configuration setting we want to determine, to create post-place-and-route designs for all possibilities
then run them through bitstream generation and compare the outputs.

NCL Files
----------
NCL files are file format used by Lattice (originating from NeoCAD), which are a textual representation of the internal
design database. Although there is little documentation on them, the format is relatively straightforward. There are
tools included with Diamond to convert the design database to and from a NCL file (``ncd2ncl`` and ``ncl2ncd``). These
are wrapped by the script ``diamond.sh`` included in Project Trellis, that allows two possibilities:

 - If given a Verilog file, it will use Diamond for synthesis and PAR, and as well as a bitstream also dump the
   post-place-and-route design as a NCL file. This way you can inspect how the design maps to an NCL file, and the
   routing and configuration inside the tile.
 - If given a NCL file, it will skip synthesis and PAR. It will convert the NCL file to a design database, then
   generate a bitstream from that.

In the planned fuzzing flow, we will first create a Verilog design for what we want to fuzz by hand, and convert it to
an NCL file. Then we will manually create a template NCL file containing only the mux/config to be fuzzed. The Python
fuzzer script will then subsitute this template file for each fuzz possibility.

A template file for LUT initialisation is shown as an example:

.. code-block:: none

    ::FROM-WRITER;
    design top
    {
       device
       {
          architecture sa5p00;
          device LFE5U-25F;
          package CABGA381;
          performance "8";
       }

       comp SLICE_0
          [,,,,A0,B0,D0,C0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,]
       {
          logical
          {
             cellmodel-name SLICE;
             program "MODE:LOGIC "
                     "K0::H0=${lut_func} "
                     "F0:F ";
             primitive K0 i3_4_lut;
          }
          site R2C2A;
       }

    }

The NCL file contains information about the device, components and routing (routing is not included in this example). As
this was from a LUT initialisation fuzzer, ${lut_func} will be replaced by a function corresponding to the LUT init bit
to be fuzzed (NCL files require an expression for LUT initialisation, rather than a series of bits).

