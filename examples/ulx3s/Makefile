all: blinky.bit hello.bit

hello.json: pll_120.v

IDCODE ?= 0x21111043 # 12f

%.json: %.v
	yosys \
		-p "synth_ecp5 -json $@" \
		-E .$(basename $@).d \
		$<

%.config: %.json
	nextpnr-ecp5 \
		--json $< \
		--textcfg $@ \
		--lpf ulx3s_v20.lpf \
		--25k \
		--package CABGA381

%.bit: %.config
	ecppack --idcode $(IDCODE) $< $@

%.svf: %.config
	ecppack --idcode $(IDCODE) --input $< --svf $@

%.flash: %.bit
	ujprog $<
%.terminal: %.bit
	ujprog -t -b 3000000 $<

pll_%.v:
	ecppll \
		-i 25 \
		-o $(subst pll_,,$(basename $@)) \
		-n $(basename $@) \
		-f $@

clean:
	$(RM) *.config *.bit .*.d *.svf
-include .*.d
