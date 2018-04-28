#!/bin/bash

# Script to run Lattice Diamond on a Verilog source file and LPF constraints file, then run some extra commands
# to create debug/dump output for the design

# Based on Clifford Wolf's icecube.sh from Project Icestorm

# Usage:
# ./diamond.sh part design.v
# Currently supported parts:
#  - lfe5u-85
#  - lfe5u-45
#  - lfe5u-25

# Currently this script supports Linux only.

# You need to set the DIAMONDDIR environment variable to the path where you have
# installed Lattice Diamond, unless it matches this default.

diamonddir="${DIAMONDDIR:-/usr/local/diamond/3.10_x64}"
export FOUNDRY="${diamonddir}/ispfpga"
bindir="${diamonddir}/bin/lin64"
LSC_DIAMOND=true
export LSC_DIAMOND
export NEOCAD_MAXLINEWIDTH=32767
export TCL_LIBRARY="${diamonddir}/tcltk/lib/tcl8.5"
export fpgabindir=${FOUNDRY}/bin/lin64
export LD_LIBRARY_PATH="${bindir}:${fpgabindir}"
export LM_LICENSE_FILE="${diamonddir}/license/license.dat"

set -ex
set -- "$1" ${2%.v}

PART=$1

case "${PART}" in
	LFE5U-85F)
		PACKAGE="${DEV_PACKAGE:-CABGA756}"
		DEVICE="LFE5U-85F"
		LSE_ARCH="ECP5U"
		;;
	LFE5U-45F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5U-45F"
		LSE_ARCH="ECP5U"
		;;
	LFE5U-25F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5U-25F"
		LSE_ARCH="ECP5U"
		;;
	LFE5UM-85F)
		PACKAGE="${DEV_PACKAGE:-CABGA756}"
		DEVICE="LFE5UM-85F"
		LSE_ARCH="ECP5UM"
		;;
	LCMXO2-2000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO2-2000HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-7000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LCMXO2-7000HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO3LF-9400C)
		PACKAGE="${DEV_PACKAGE:-CABGA256}"
		DEVICE="LCMXO3LF-9400C"
		LSE_ARCH="MachXO3LF"
		;;
	LIF-MD6000)
		PACKAGE="${DEV_PACKAGE:-csFBGA81}"
		DEVICE="LIF-MD6000"
		LSE_ARCH="LIFMD"
		;;
esac

(
rm -rf "$2.tmp"
mkdir -p "$2.tmp"
cp "$2.v" "$2.tmp/input.v"
if test -f "$2.sdc"; then cp "$2.sdc" "$2.tmp/input.sdc"; fi
if test -f "$2.lpf"; then cp "$2.lpf" "$2.tmp/input.lpf"; fi
cd "$2.tmp"

touch input.sdc
touch input.lpf

cat > impl_lse.prj << EOT
#device
-a "$LSE_ARCH"
-d $DEVICE
-t $PACKAGE
-frequency 200
-optimization_goal Timing
-bram_utilization 100
-ramstyle Auto
-romstyle auto
-dsp_utilization 100
-use_dsp 1
-use_carry_chain 1
-carry_chain_length 0
-force_gsr Auto
-resource_sharing 1
-propagate_constants 1
-remove_duplicate_regs 1
-mux_style Auto
-max_fanout 1000
-fsm_encoding_style Auto
-twr_paths 3
-fix_gated_clocks 1
-loop_limit 1950



-use_io_insertion 1
-resolve_mixed_drivers 0
-use_io_reg auto
-ver "input.v"

-p "$PWD"
-ngd "synth_impl.ngd"
-lpf 1
EOT

# run LSE synthesis
"$fpgabindir"/synthesis -f "impl_lse.prj"

# map design
"$fpgabindir"/map -a $LSE_ARCH -p $DEVICE -t $PACKAGE synth_impl.ngd -o map_impl.ncd  -lpf synth_impl.lpf -lpf input.lpf

# place and route design
"$fpgabindir"/par map_impl.ncd par_impl.ncd synth_impl.prf

# make bitmap
"$fpgabindir"/bitgen par_impl.ncd output.bit

# dump bitmap
"$fpgabindir"/bstool -d output.bit > output.dump

# run test on bitmap (for tilemap)
"$fpgabindir"/bstool -t output.bit > output.test

# convert ngd to ncl
"$FOUNDRY"/userware/unix/bin/lin64/ncd2ncl par_impl.ncd output.ncl

# run incdelay
"$fpgabindir"/incdelay -d par_impl.ncd > output.incd


export LD_LIBRARY_PATH=""
)

cp "$2.tmp"/output.bit "$2.bit"
cp "$2.tmp"/output.dump "$2.dump"
cp "$2.tmp"/output.ncl "$2.ncl"
cp "$2.tmp"/output.incd "$2.incd"
