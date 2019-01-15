FILES:= ODDRX1F.v BB.v
TESTBENCHES:= $(patsubst %.v, tests/test_%.v, $(FILES))
VCDS:= $(patsubst %.v, %.vcd, $(FILES))
VFLAGS:=-Dmixed_hdl -Wtimescale

all: $(VCDS)

%.exe: tests/test_%.v %.v lattice/%_l.v gsr_pur_assign.v
	iverilog $(VFLAGS) -o $@ $^ 
%.vcd: %.exe
	vvp $<

