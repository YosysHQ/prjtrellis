PROJ ?= blinky
TRELLIS_ROOT ?= ../..

all: ${PROJ}.bit ${PROJ}-nextpnr.bit ${PROJ}.txt ${PROJ}-nextpnr.txt

# Get proportion of known bits.
stats:
	@python3 -c "import sys; print(\"{:.3f}\".format(int(sys.argv[1]) / int(sys.argv[2])))" \
		`grep -e arc -e word -e enum ${PROJ}.txt | wc -l` \
		`grep -e arc -e word -e enum -e unknown  ${PROJ}.txt | wc -l`

%.txt: %.bit
	ecpunpack --db ${TRELLIS_ROOT}/database --input $< --textcfg $@

# Diamond rules.
%.bit: %.v %.lpf
	DEV_PACKAGE=TQFP100 ${TRELLIS_ROOT}/diamond.sh LCMXO2-1200HC ${PROJ}.v

# FOSS rules.
# yosys
%.json: %.v %.lpf
	@true

# ecppack --db ${TRELLIS_ROOT}/database --input $< $@
%-nextpnr.bit: %-nextpnr.txt
	@true

# nextpnr-generic
${PROJ}-nextpnr.txt: ${PROJ}.json
	@true

clean:
	rm -rf ${PROJ}.tmp ${PROJ}_out.ncl ${PROJ}.bit ${PROJ}.dump ${PROJ}.twr ${PROJ}.txt ${PROJ}.json ${PROJ}-nextpnr.*
