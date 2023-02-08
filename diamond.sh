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
#  - LCMXO2-1200HC

# Currently this script supports Linux and Windows using a MINGW64 bash shell.

# You need to set the DIAMONDDIR environment variable to the path where you have
# installed Lattice Diamond, unless it matches this default.

if [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
	WINDOWS=true
else
	WINDOWS=false
fi

if [ -z "$DIAMONDVER" ]; then
	diamondver="3.10"
else
	diamondver="$DIAMONDVER"
fi

if $WINDOWS; then
	case $diamondver in
		"3.12")
			diamonddir="${DIAMONDDIR:-/c/lscc/diamond/${diamondver}}"
			;;
		*)
			diamonddir="${DIAMONDDIR:-/c/lscc/diamond/${diamondver}_x64}"
			;;
	esac
else
	diamonddir="${DIAMONDDIR:-/usr/local/diamond/${diamondver}_x64}"
fi
export FOUNDRY="${diamonddir}/ispfpga"

if $WINDOWS; then
	bindir="${diamonddir}/bin/nt64"
else
	bindir="${diamonddir}/bin/lin64"
fi
LSC_DIAMOND=true
export LSC_DIAMOND
export NEOCAD_MAXLINEWIDTH=32767
export TCL_LIBRARY="${diamonddir}/tcltk/lib/tcl8.5"

if $WINDOWS; then
	export fpgabindir=${FOUNDRY}/bin/nt64
else
	export fpgabindir=${FOUNDRY}/bin/lin64
fi

if $WINDOWS; then
	export PATH="${bindir}:${fpgabindir}:$PATH"
else
	export LD_LIBRARY_PATH="${bindir}:${fpgabindir}"
fi
export LM_LICENSE_FILE="${LM_LICENSE_FILE:=${diamonddir}/license/license.dat}"

set -ex
if [[ $2 == *.ncl ]]
then
USE_NCL=1
else
USE_NCL=
fi

V_SUB=${2%.v}
NCL_SUB=${V_SUB%.ncl}

set -- "$1" $NCL_SUB

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
	LFE5U-12F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5U-12F"
		LSE_ARCH="ECP5U"
		;;

	LFE5UM-85F)
		PACKAGE="${DEV_PACKAGE:-CABGA756}"
		DEVICE="LFE5UM-85F"
		LSE_ARCH="ECP5UM"
		;;
	LFE5UM-45F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5UM-45F"
		LSE_ARCH="ECP5UM"
		;;
	LFE5UM-25F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5UM-25F"
		LSE_ARCH="ECP5UM"
		;;

	LFE5UM5G-85F)
		PACKAGE="${DEV_PACKAGE:-CABGA756}"
		DEVICE="LFE5UM5G-85F"
		LSE_ARCH="ECP5UM5G"
		;;
	LFE5UM5G-45F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5UM5G-45F"
		LSE_ARCH="ECP5UM5G"
		;;
	LFE5UM5G-25F)
		PACKAGE="${DEV_PACKAGE:-CABGA381}"
		DEVICE="LFE5UM5G-25F"
		LSE_ARCH="ECP5UM5G"
		;;

	LCMXO2-256HC)
		PACKAGE="${DEV_PACKAGE:-QFN32}"
		DEVICE="LCMXO2-256HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-640HC)
		PACKAGE="${DEV_PACKAGE:-QFN48}"
		DEVICE="LCMXO2-640HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-1200HC)
		PACKAGE="${DEV_PACKAGE:-QFN32}"
		DEVICE="LCMXO2-1200HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-2000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO2-2000HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-4000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LCMXO2-4000HC"
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
if [ -n "$USE_NCL" ]; then
cp "$2.ncl" "$2.tmp/input.ncl"
if test -f "$2.prf"; then cp "$2.prf" "$2.tmp/input.prf"; fi
else
cp "$2.v" "$2.tmp/input.v"
fi

if test -f "$2.sdc"; then cp "$2.sdc" "$2.tmp/input.sdc"; fi
if test -f "$2.lpf"; then cp "$2.lpf" "$2.tmp/input.lpf"; fi
if test -f "$2.prf"; then cp "$2.prf" "$2.tmp/input.prf"; fi
if test -f "$2.dat"; then cp "$2.dat" "$2.tmp/$2.dat"; fi
cd "$2.tmp"

touch input.sdc
touch input.lpf

if [ -n "$USE_NCL" ]; then

if $WINDOWS; then
	"$FOUNDRY"/userware/NT/bin/nt64/ncl2ncd input.ncl -drc -o par_impl.ncd
else
	"$FOUNDRY"/userware/unix/bin/lin64/ncl2ncd input.ncl -drc -o par_impl.ncd
fi

if test -f "input.prf"; then
cp "input.prf" "synth_impl.prf"
else
touch synth_impl.prf
fi


else
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
"$fpgabindir"/map -a $LSE_ARCH -p $DEVICE -t $PACKAGE synth_impl.ngd -o map_impl.ncd  -lpf synth_impl.lpf -lpf input.lpf $MAPARGS

# place and route design
"$fpgabindir"/par map_impl.ncd par_impl.ncd synth_impl.prf

fi

# Forcefully disable compression
echo "SYSCONFIG COMPRESS_CONFIG=OFF ;" >> synth_impl.prf

# make bitmap
"$fpgabindir"/bitgen -d par_impl.ncd $BITARGS output.bit synth_impl.prf

if [ -n "$JEDEC_BITSTREAM" ]; then
"$fpgabindir"/bitgen -d par_impl.ncd -jedec output.jed synth_impl.prf
fi

if [ -n "$COMPRESSED_BITSTREAM" ]; then
	sed 's/COMPRESS_CONFIG=OFF/COMPRESS_CONFIG=ON/' synth_impl.prf > synth_impl_comp.prf
	"$fpgabindir"/bitgen -d par_impl.ncd $BITARGS output-comp.bit synth_impl_comp.prf
fi

# dump bitmap
"$fpgabindir"/bstool -d output.bit > output.dump

if [ -z "$USE_NCL" ]; then
# run test on bitmap (for tilemap)
"$fpgabindir"/bstool -t output.bit > output.test

# convert ngd to ncl
if $WINDOWS; then
	"$FOUNDRY"/userware/NT/bin/nt64/ncd2ncl par_impl.ncd output.ncl
else
	"$FOUNDRY"/userware/unix/bin/lin64/ncd2ncl par_impl.ncd output.ncl
fi

fi

if [ -z "$NO_TRCE" ]; then
# run trce
"$fpgabindir"/trce -v -u -c  par_impl.ncd
fi

if [ -n "$BACKANNO" ]; then
# run trce
"$fpgabindir"/ldbanno -n Verilog par_impl.ncd synth_impl.prf
fi

export LD_LIBRARY_PATH=""
)

cp "$2.tmp"/output.bit "$2.bit"
cp "$2.tmp"/output.dump "$2.dump"
if [ -z "$NO_TRCE" ]; then
cp "$2.tmp"/par_impl.twr "$2.twr"
fi
if [ -z "$USE_NCL" ]; then
cp "$2.tmp"/output.ncl "$2_out.ncl"
fi
if [ -n "$JEDEC_BITSTREAM" ]; then
cp "$2.tmp"/output.jed "$2.jed"
fi
if [ -n "$COMPRESSED_BITSTREAM" ]; then
cp "$2.tmp"/output-comp.bit "$2-comp.bit"
fi
if [ -n "$BACKANNO" ]; then
cp "$2.tmp"/par_impl.sdf "$2.sdf"
fi
