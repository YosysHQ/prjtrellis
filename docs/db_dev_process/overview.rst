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

Fuzzers
--------

There are three types of fuzzer in use in Project Trellis. They are routing fuzzers, non-routing fuzzers and
meta-fuzzers.

Routing fuzzers use the helper functions in ``util/fuzz/nonrouting.py``. These will generally follow the following
algorithm:

 - Use the Tcl API to discover all of the netnames at the target location

 - Use the Tcl API to discover the arcs associated with those netnames

 - Apply filters to remove netnames and/or arcs not applicable to the current fuzzer

    - For example, when fuzzing a CIB_EBR you would ensure to include CIB signals but exclude EBR signals
    - When fuzzing a EBR you would conversely filter out the CIB signals and include EBR signals.

 - Create a reference "empty" bitstream

 - For every arc discovered above:

    - Create a bitstream containing the arc using a NCL file
    - Compare the bitstream against the empty bitstream:

       - If there was a change outside the tile(s) of interest, the arc is ignored
       - If there was a change to any of the tile(s) of interest, add a configurable mux arc to the database of the
         relevant tile
       - If there was no change at all, add the arc as a fixed connection to the database of the first specified tile

Note that routing fuzzers for special function tiles (such as PIO, EBR, etc) are primarily intended to find fixed
connections to CIBs and within special functions rather than significant amounts of configurable routing, but the above
algorithm is still used for consistency (and because it is not possible to know a priori whether an arc is configurable
or fixed).

Non-routing fuzzers are intended to fuzz configuration such as LUT initialisation, flip-flop settings or IO type. It is
possible to fuzz either words or enums. Words are for settings that naturally comprise of one or more bits, such as
LUT initialisation. Enums are for settings with multiple textual values.

The algorithm for word settings is to create one bitstream for each word bit with that bit set, and compare to an all-zero
bitstream to determine the change for that bit. These are also optionally compared against an empty bitstream with
the setting/feature entirely missing to determine a default value, which is not always all-zeros.

The algorithm for enum settings is to create bitstreams with all possible enum values, in each case storing the CRAM of
all tiles of interest. These are then compared to determine the set of bits affected by the enum, and in each case
the bit values for each possible enum value.

Creating non-routing requires more work than routing fuzzers. The settings of interest, possible values, and how to
create them in the Ncl or Verilog input must all be included in the fuzzer script.

Finally meta-fuzzers do not do any fuzzing but perform other necessary manipulations on the database during the fuzzing
flow. For example, these may copy config bits from one tile to other tile types which have identical configuration in
order to reduce the time needed for fuzzing.
