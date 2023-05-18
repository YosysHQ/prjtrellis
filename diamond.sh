#!/usr/bin/env bash

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
	case $diamondver in
		"3.12")
			diamonddir="${DIAMONDDIR:-/usr/local/diamond/${diamondver}}"
			;;
		*)
			diamonddir="${DIAMONDDIR:-/usr/local/diamond/${diamondver}_x64}"
			;;
	esac
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
	# ECP5U
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

	# ECP5UM
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

	# ECP5UM5G
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

	# MachXO2
	LCMXO2-256|LCMXO2-256HC)
		PACKAGE="${DEV_PACKAGE:-QFN32}"
		DEVICE="LCMXO2-256HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-640|LCMXO2-640HC)
		PACKAGE="${DEV_PACKAGE:-QFN48}"
		DEVICE="LCMXO2-640HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-1200|LCMXO2-1200HC)
		PACKAGE="${DEV_PACKAGE:-QFN32}"
		DEVICE="LCMXO2-1200HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-2000|LCMXO2-2000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO2-2000HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-4000|LCMXO2-4000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LCMXO2-4000HC"
		LSE_ARCH="MachXO2"
		;;
	LCMXO2-7000|LCMXO2-7000HC)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LCMXO2-7000HC"
		LSE_ARCH="MachXO2"
		;;

	# MachXO
	LCMXO256|LCMXO256C)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO256C"
		LSE_ARCH="MachXO"
		;;
	LCMXO640|LCMXO640C)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO640C"
		LSE_ARCH="MachXO"
		;;
	LCMXO1200|LCMXO1200C)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO1200C"
		LSE_ARCH="MachXO"
		;;
	LCMXO2280|LCMXO2280C)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LCMXO2280C"
		LSE_ARCH="MachXO"
		;;

	# MachXO3
	LCMXO3-1300|LCMXO3LF-640E|LCMXO3LF-1300E)
		PACKAGE="${DEV_PACKAGE:-CSFBGA121}"
		DEVICE="LCMXO3LF-1300E"
		LSE_ARCH="MachXO3LF"
		;;
	LCMXO3-2100|LCMXO3LF-2100C)
		PACKAGE="${DEV_PACKAGE:-CABGA256}"
		DEVICE="LCMXO3LF-2100C"
		LSE_ARCH="MachXO3LF"
		;;
	LCMXO3-4300|LCMXO3LF-4300C)
		PACKAGE="${DEV_PACKAGE:-CABGA256}"
		DEVICE="LCMXO3LF-4300C"
		LSE_ARCH="MachXO3LF"
		;;
	LCMXO3-6900|LCMXO3LF-6900C)
		PACKAGE="${DEV_PACKAGE:-CABGA400}"
		DEVICE="LCMXO3LF-6900C"
		LSE_ARCH="MachXO3LF"
		;;
	LCMXO3-9400|LCMXO3LF-9400C)
		PACKAGE="${DEV_PACKAGE:-CABGA484}"
		DEVICE="LCMXO3LF-9400C"
		LSE_ARCH="MachXO3LF"
		;;

	# MachXO3D
	LCMXO3D-4300|LCMXO3D-4300HC)
		PACKAGE="${DEV_PACKAGE:-CABGA256}"
		DEVICE="LCMXO3D-4300HC"
		LSE_ARCH="MachXO3D"
		;;
	LCMXO3D-9400|LCMXO3D-9400HC)
		PACKAGE="${DEV_PACKAGE:-CABGA256}"
		DEVICE="LCMXO3D-9400HC"
		LSE_ARCH="MachXO3D"
		;;

	# LatticeXP2
	LFXP2-5|LFXP2-5E)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LFXP2-5E"
		LSE_ARCH="LatticeXP2"
		;;
	LFXP2-8|LFXP2-8E)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LFXP2-8E"
		LSE_ARCH="LatticeXP2"
		;;
	LFXP2-17|LFXP2-17E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFXP2-17E"
		LSE_ARCH="LatticeXP2"
		;;
	LFXP2-30|LFXP2-30E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFXP2-30E"
		LSE_ARCH="LatticeXP2"
		;;
	LFXP2-40|LFXP2-40E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFXP2-40E"
		LSE_ARCH="LatticeXP2"
		;;
	
	# LatticeECP2
	LFE2-6|LFE2-6E)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LFE2-6E"
		LSE_ARCH="LatticeECP2"
		;;
	LFE2-12|LFE2-12E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFE2-12E"
		LSE_ARCH="LatticeECP2"
		;;
	LFE2-20|LFE2-20E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFE2-20E"
		LSE_ARCH="LatticeECP2"
		;;
	LFE2-35|LFE2-35E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFE2-35E"
		LSE_ARCH="LatticeECP2"
		;;
	LFE2-50|LFE2-50E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFE2-50E"
		LSE_ARCH="LatticeECP2"
		;;
	LFE2-70|LFE2-70E)
		PACKAGE="${DEV_PACKAGE:-FPBGA672}"
		DEVICE="LFE2-70E"
		LSE_ARCH="LatticeECP2"
		;;
	
	# LatticeECP2M
	LFE2M20|LFE2M20E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFE2M20E"
		LSE_ARCH="LatticeECP2M"
		;;
	LFE2M35|LFE2M35E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFE2M35E"
		LSE_ARCH="LatticeECP2M"
		;;
	LFE2M50|LFE2M50E)
		PACKAGE="${DEV_PACKAGE:-FPBGA900}"
		DEVICE="LFE2M50E"
		LSE_ARCH="LatticeECP2M"
		;;
	LFE2M70|LFE2M70E)
		PACKAGE="${DEV_PACKAGE:-FPBGA900}"
		DEVICE="LFE2M70E"
		LSE_ARCH="LatticeECP2M"
		;;
	LFE2M100|LFE2M100E)
		PACKAGE="${DEV_PACKAGE:-FPBGA900}"
		DEVICE="LFE2M100E"
		LSE_ARCH="LatticeECP2M"
		;;
	
	# LatticeECP3
	LFE3-17|LFE3-17EA)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFE3-17EA"
		LSE_ARCH="LatticeECP3"
		;;
	LFE3-35|LFE3-35EA)
		PACKAGE="${DEV_PACKAGE:-FPBGA672}"
		DEVICE="LFE3-35EA"
		LSE_ARCH="LatticeECP3"
		;;
	LFE3-70|LFE3-70EA)
		PACKAGE="${DEV_PACKAGE:-FPBGA672}"
		DEVICE="LFE3-70EA"
		LSE_ARCH="LatticeECP3"
		;;
	LFE3-95|LFE3-95EA)
		PACKAGE="${DEV_PACKAGE:-FPBGA672}"
		DEVICE="LFE3-95EA"
		LSE_ARCH="LatticeECP3"
		;;
	LFE3-150|LFE3-150EA)
		PACKAGE="${DEV_PACKAGE:-FPBGA672}"
		DEVICE="LFE3-150EA"
		LSE_ARCH="LatticeECP3"
		;;

	# LatticeXP
	LFXP3|LFXP3E)
		PACKAGE="${DEV_PACKAGE:-TQFP144}"
		DEVICE="LFXP3E"
		LSE_ARCH="LatticeXP"
		SYNP_TECHNOLOGY="LATTICE-XP"
		SYNP_PART="LFXP3E"
		SYNP_PACKAGE="T144C"
		SYNP_SPEED_GRADE="5"
		;;
	LFXP6|LFXP6E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFXP6E"
		LSE_ARCH="LatticeXP"
		SYNP_TECHNOLOGY="LATTICE-XP"
		SYNP_PART="LFXP6E"
		SYNP_PACKAGE="F256C"
		SYNP_SPEED_GRADE="5"
		;;
	LFXP10|LFXP10E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFXP10E"
		LSE_ARCH="LatticeXP"
		SYNP_TECHNOLOGY="LATTICE-XP"
		SYNP_PART="LFXP10E"
		SYNP_PACKAGE="F256C"
		SYNP_SPEED_GRADE="5"
		;;
	LFXP15|LFXP15E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFXP15E"
		LSE_ARCH="LatticeXP"
		SYNP_TECHNOLOGY="LATTICE-XP"
		SYNP_PART="LFXP15E"
		SYNP_PACKAGE="F256C"
		SYNP_SPEED_GRADE="5"
		;;
	LFXP20|LFXP20E)
		PACKAGE="${DEV_PACKAGE:-FPBGA256}"
		DEVICE="LFXP20E"
		LSE_ARCH="LatticeXP"
		SYNP_TECHNOLOGY="LATTICE-XP"
		SYNP_PART="LFXP20E"
		SYNP_PACKAGE="F256C"
		SYNP_SPEED_GRADE="5"
		;;

	# LIFMD
	LIF-MD6000)
		PACKAGE="${DEV_PACKAGE:-csFBGA81}"
		DEVICE="LIF-MD6000"
		LSE_ARCH="LIFMD"
		SYNP_TECHNOLOGY="LIFMD"
		SYNP_PART="LIF_MD6000"
		SYNP_PACKAGE="MG81I"
		SYNP_SPEED_GRADE="6"
		;;

	# LIFMDF
	LIF-MDF6000)
		PACKAGE="${DEV_PACKAGE:-UCFBGA64}"
		DEVICE="LIF-MDF6000"
		LSE_ARCH="LIFMDF"
		SYNP_TECHNOLOGY="LIFMDF"
		SYNP_PART="LIF_MDF6000"
		SYNP_PACKAGE="UMG64I"
		SYNP_SPEED_GRADE="6"
		;;

	# LatticeEC
	LFEC1E)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LFEC1E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC1E"
		SYNP_PACKAGE="T100I"
		SYNP_SPEED_GRADE="3"
		;;

	LFEC3E)
		PACKAGE="${DEV_PACKAGE:-TQFP100}"
		DEVICE="LFEC3E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC3E"
		SYNP_PACKAGE="T100I"
		SYNP_SPEED_GRADE="3"
		;;

	LFEC6E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFEC6E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC6E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;

	LFEC10E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFEC10E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC10E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;

	LFEC15E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFEC15E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC15E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;

	LFEC20E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFEC20E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC20E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;

	LFEC33E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFEC33E"
		LSE_ARCH="LatticeEC"
		SYNP_TECHNOLOGY="LATTICE-EC"
		SYNP_PART="LFEC33E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;

	# LatticeECP
	LFECP6E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFECP6E"
		LSE_ARCH="LatticeECP"
		SYNP_TECHNOLOGY="LATTICE-ECP"
		SYNP_PART="LFECP6E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;
	LFECP10E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFECP10E"
		LSE_ARCH="LatticeECP"
		SYNP_TECHNOLOGY="LATTICE-ECP"
		SYNP_PART="LFECP10E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;
	LFECP15E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFECP15E"
		LSE_ARCH="LatticeECP"
		SYNP_TECHNOLOGY="LATTICE-ECP"
		SYNP_PART="LFECP15E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;
	LFECP20E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFECP20E"
		LSE_ARCH="LatticeECP"
		SYNP_TECHNOLOGY="LATTICE-ECP"
		SYNP_PART="LFECP20E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;
	LFECP33E)
		PACKAGE="${DEV_PACKAGE:-FPBGA484}"
		DEVICE="LFECP33E"
		LSE_ARCH="LatticeECP"
		SYNP_TECHNOLOGY="LATTICE-ECP"
		SYNP_PART="LFECP33E"
		SYNP_PACKAGE="F484C"
		SYNP_SPEED_GRADE="3"
		;;

	# Platform Manager
	LPTM10|LPTM10-1247)
		PACKAGE="${DEV_PACKAGE:-TQFP128}"
		DEVICE="LPTM10-1247"
		LSE_ARCH="Platform Manager"
		SYNP_TECHNOLOGY="Platform_Manager"
		SYNP_PART="LPTM10_1247"
		SYNP_PACKAGE="TG128CES"
		SYNP_SPEED_GRADE="3"
		;;

	LPTM10-12107)
		PACKAGE="${DEV_PACKAGE:-FTBGA208}"
		DEVICE="LPTM10-12107"
		LSE_ARCH="Platform Manager"
		SYNP_TECHNOLOGY="Platform_Manager"
		SYNP_PART="LPTM10_12107"
		SYNP_PACKAGE="FTG208CES"
		SYNP_SPEED_GRADE="3"
		;;

	# Platform Manager 2
	LPTM21)
		PACKAGE="${DEV_PACKAGE:-FTBGA237}"
		DEVICE="LPTM21"
		LSE_ARCH="Platform Manager 2"
		SYNP_TECHNOLOGY="Platform_Manager_2"
		SYNP_PART="LPTM21"
		SYNP_PACKAGE="FTG237I"
		SYNP_SPEED_GRADE="1A"
		;;

	LPTM21L)
		PACKAGE="${DEV_PACKAGE:-CABGA100}"
		DEVICE="LPTM21L"
		LSE_ARCH="Platform Manager 2"
		SYNP_TECHNOLOGY="Platform_Manager_2"
		SYNP_PART="LPTM21L"
		SYNP_PACKAGE="BG100I"
		SYNP_SPEED_GRADE="1A"
		;;

	# LatticeSC
	LFSC3GA15E)
		PACKAGE="${DEV_PACKAGE:-FPBGA900}"
		DEVICE="LFSC3GA15E"
		LSE_ARCH="LatticeSC"
		SYNP_TECHNOLOGY="LATTICE-SC"
		SYNP_PART="LFSC3GA15E"
		SYNP_PACKAGE="F900C"
		SYNP_SPEED_GRADE="6"
		;;
	LFSC3GA25E)
		PACKAGE="${DEV_PACKAGE:-FPBGA900}"
		DEVICE="LFSC3GA25E"
		LSE_ARCH="LatticeSC"
		SYNP_TECHNOLOGY="LATTICE-SC"
		SYNP_PART="LFSC3GA25E"
		SYNP_PACKAGE="F900C"
		SYNP_SPEED_GRADE="6"
		;;
	LFSC3GA40E)
		PACKAGE="${DEV_PACKAGE:-FCBGA1152}"
		DEVICE="LFSC3GA40E"
		LSE_ARCH="LatticeSC"
		SYNP_TECHNOLOGY="LATTICE-SC"
		SYNP_PART="LFSC3GA40E"
		SYNP_PACKAGE="FF1152C"
		SYNP_SPEED_GRADE="6"
		;;
	LFSC3GA80E)
		PACKAGE="${DEV_PACKAGE:-FCBGA1152}"
		DEVICE="LFSC3GA80E"
		LSE_ARCH="LatticeSC"
		SYNP_TECHNOLOGY="LATTICE-SC"
		SYNP_PART="LFSC3GA80E"
		SYNP_PACKAGE="FF1152C"
		SYNP_SPEED_GRADE="6"
		;;
	LFSC3GA115E)
		PACKAGE="${DEV_PACKAGE:-FCBGA1152}"
		DEVICE="LFSC3GA115E"
		LSE_ARCH="LatticeSC"
		SYNP_TECHNOLOGY="LATTICE-SC"
		SYNP_PART="LFSC3GA115E"
		SYNP_PACKAGE="FC1152C"
		SYNP_SPEED_GRADE="6"
		;;

	# LFMNX
	LFMNX-50)
		PACKAGE="${DEV_PACKAGE:-FBG484}"
		DEVICE="LFMNX-50"
		LSE_ARCH="LFMNX"
		SYNP_TECHNOLOGY="LFMNX"
		SYNP_PART="LFMNX_50"
		SYNP_PACKAGE="FBG484C"
		SYNP_SPEED_GRADE="5"
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

cat > impl_synplify.tcl << EOT

set_option -technology $SYNP_TECHNOLOGY
set_option -part $SYNP_PART
set_option -package $SYNP_PACKAGE
set_option -speed_grade -$SYNP_SPEED_GRADE

set_option -symbolic_fsm_compiler true
set_option -resource_sharing true

set_option -vlog_std v2001

#-- add_file options
set_option -include_path {$PWD}
add_file -verilog -vlog_std v2001 {input.v}

#-- top module name
set_option -top_module top

#-- set result format/file last
project -result_file {$PWD/synth_impl.edi}

#-- error message log file
project -log_file {x03lf_impl1.srf}

#-- set any command lines input by customer


#-- run Synplify with 'arrange HDL file'
project -run

EOT

if [ -z "$SYNP_TECHNOLOGY" ]; then
	# run LSE synthesis
	"$fpgabindir"/synthesis -f "impl_lse.prj"
else
	# run Synplify synthesis
	"$bindir"/synpwrap -msg -prj "impl_synplify.tcl" 
	"$fpgabindir"/edif2ngd  -l "$LSE_ARCH" -d $DEVICE -path "$PWD" "synth_impl.edi" "synth_impl.ngo"   
	"$fpgabindir"/ngdbuild  -a "$LSE_ARCH" -d $DEVICE  -p "$PWD"  "synth_impl.ngo" "synth_impl.ngd"
fi
# map design
"$fpgabindir"/map -a "$LSE_ARCH" -p $DEVICE -t $PACKAGE synth_impl.ngd -o map_impl.ncd  -lpf synth_impl.lpf -lpf input.lpf $MAPARGS

# place and route design
"$fpgabindir"/par map_impl.ncd par_impl.ncd synth_impl.prf

fi

# Forcefully disable compression
if [ "$LSE_ARCH" != "MachXO" ]; then
	echo "SYSCONFIG COMPRESS_CONFIG=OFF ;" >> synth_impl.prf
fi

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
