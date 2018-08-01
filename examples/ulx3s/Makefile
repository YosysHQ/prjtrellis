all: blinky.bit

blinky.json: blinky.v
	yosys -p "synth_ecp5 -noccu2 -nomux -nodram -json blinky.json" blinky.v

blinky.bit: blinky.json
	nextpnr-ecp5 --json blinky.json --basecfg ulx3s_empty.config --bit blinky.bit --textcfg blinky_out.config --45k



