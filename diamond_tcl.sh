#!/bin/bash

# Script to start a Diamond ispTcl console
WINDOWS= [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]
if $WINDOWS; then
	diamonddir="${DIAMONDDIR:-/c/lscc/diamond/3.10_x64}"
else
	diamonddir="${DIAMONDDIR:-/usr/local/diamond/3.10_x64}"
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
