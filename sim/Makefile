FILES:= ODDRX1F.v BB.v IDDRX1F.v ODDRX2F.v
TESTBENCHES:= $(patsubst %.v, tests/test_%.v, $(FILES))
VCDS:= $(patsubst %.v, %.vcd, $(FILES))
VFLAGS:=-Dmixed_hdl -Wtimescale -Wall 

all: $(VCDS)

%.exe: tests/test_%.v %.v lattice/%_l.v gsr_pur_assign.v
	iverilog $(VFLAGS) -o $@ $^ 
%.vcd: %.exe
	vvp $<

