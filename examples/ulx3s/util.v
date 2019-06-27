`ifndef _util_v_
`define _util_v_

`define CLOG2(x) \
   x <= 2	 ? 1 : \
   x <= 4	 ? 2 : \
   x <= 8	 ? 3 : \
   x <= 16	 ? 4 : \
   x <= 32	 ? 5 : \
   x <= 64	 ? 6 : \
   x <= 128	 ? 7 : \
   x <= 256	 ? 8 : \
   x <= 512	 ? 9 : \
   x <= 1024	 ? 10 : \
   x <= 2048	 ? 11 : \
   x <= 4096	 ? 12 : \
   x <= 8192	 ? 13 : \
   x <= 16384	 ? 14 : \
   x <= 32768	 ? 15 : \
   x <= 65536	 ? 16 : \
   -1

function [7:0] hexdigit;
	input [3:0] x;
	begin
		hexdigit =
			x == 0 ? "0" :
			x == 1 ? "1" :
			x == 2 ? "2" :
			x == 3 ? "3" :
			x == 4 ? "4" :
			x == 5 ? "5" :
			x == 6 ? "6" :
			x == 7 ? "7" :
			x == 8 ? "8" :
			x == 9 ? "9" :
			x == 10 ? "a" :
			x == 11 ? "b" :
			x == 12 ? "c" :
			x == 13 ? "d" :
			x == 14 ? "e" :
			x == 15 ? "f" :
			"?";
	end
endfunction

module divide_by_n(
	input clk,
	input reset,
	output reg out
);
	parameter N = 2;

	reg [`CLOG2(N)-1:0] counter;

	always @(posedge clk)
	begin
		out <= 0;

		if (reset)
			counter <= 0;
		else
		if (counter == 0)
		begin
			out <= 1;
			counter <= N - 1;
		end else
			counter <= counter - 1;
	end
endmodule

`endif
