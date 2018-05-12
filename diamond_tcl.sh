#!/bin/bash

# Script to start a Diamond ispTcl consoke
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
$FOUNDRY/userware/unix/bin/lin64/ispTcl $1
