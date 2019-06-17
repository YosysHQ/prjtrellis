`ifndef _uart_v_
`define _uart_v_

`include "util.v"

module uart_tx(
	input clk,
	input reset,
	output serial,
	output reg ready,
	input [7:0] data,
	input data_strobe
);
   parameter DIVISOR = 100;
   wire baud_x1;
   divide_by_n #(.N(DIVISOR)) baud_x1_div(clk, reset, baud_x1);

   reg [7+1+1:0]   shiftreg;
   reg         serial_r;
   assign      serial = !serial_r;

   always @(posedge clk)
     if (reset) begin
        shiftreg <= 0;
        serial_r <= 0;
     end
     else if (data_strobe) begin
        shiftreg <= {
		1'b1, // stop bit
		data,
		1'b0  // start bit (inverted)
	};
	ready <= 0;
     end
     else if (baud_x1) begin
        if (shiftreg == 0)
	begin
          /* Idle state is idle high, serial_r is inverted */
          serial_r <= 0;
	  ready <= 1;
	end else
          serial_r <= !shiftreg[0];
  	// shift the output register down
        shiftreg <= {1'b0, shiftreg[7+1+1:1]};
    end else
    	ready <= (shiftreg == 0);

endmodule


module uart_rx(
	input clk,
	input reset,
	input serial,
	output [7:0] data,
	output data_strobe
);
   parameter DIVISOR = 25; // should the 1/4 the uart_tx divisor
   wire baud_x4;
   divide_by_n #(.N(DIVISOR)) baud_x4_div(clk, reset, baud_x4);

   // Clock crossing into clk domain
   reg [2:0] serial_sync;
   always @(posedge clk)
	serial_sync <= { serial_sync[1:0], serial };

   /*
    * State machine: Four clocks per bit, 10 total bits.
    */
   reg [8:0]    shiftreg;
   reg [5:0]    state;
   reg          data_strobe;
   wire [3:0]   bit_count = state[5:2];
   wire [1:0]   bit_phase = state[1:0];

   wire         sampling_phase = (bit_phase == 1);
   wire         start_bit = (bit_count == 0 && sampling_phase);
   wire         stop_bit = (bit_count == 9 && sampling_phase);

   wire         waiting_for_start = (state == 0 && serial_sync == 1);

   wire         error = ( (start_bit && serial_sync == 1) ||
                          (stop_bit && serial_sync == 0) );

   assign       data = shiftreg[7:0];

   always @(posedge clk or posedge reset)
     if (reset) begin
        state <= 0;
        data_strobe <= 0;
     end
     else if (baud_x4) begin

        if (waiting_for_start || error || stop_bit)
          state <= 0;
        else
          state <= state + 1;

        if (bit_phase == 1)
          shiftreg <= { serial_sync[2], shiftreg[8:1] };

        data_strobe <= stop_bit && !error;

     end
     else begin
        data_strobe <= 0;
     end

endmodule

`endif
