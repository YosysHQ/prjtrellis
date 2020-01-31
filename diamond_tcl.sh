#!/bin/bash

# Script to start a Diamond ispTcl console
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
	diamonddir="${DIAMONDDIR:-/c/lscc/diamond/${diamondver}_x64}"
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
export LM_LICENSE_FILE="${diamonddir}/license/license.dat"

if $WINDOWS; then
    $FOUNDRY/userware/NT/bin/nt64/ispTcl $1
else
    $FOUNDRY/userware/unix/bin/lin64/ispTcl $1
fi
