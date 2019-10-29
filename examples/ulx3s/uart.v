`ifndef _uart_v_
`define _uart_v_
 /*
  * This module is designed a 3 Mbaud serial port.
  * This is the highest data rate supported by
  * the popular FT232 USB-to-serial chip.
  *
  * Copyright (C) 2009 Micah Dowty
  *           (C) 2018 Trammell Hudson
  *
  * Permission is hereby granted, free of charge, to any person obtaining a copy
  * of this software and associated documentation files (the "Software"), to deal
  * in the Software without restriction, including without limitation the rights
  * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  * copies of the Software, and to permit persons to whom the Software is
  * furnished to do so, subject to the following conditions:
  *
  * The above copyright notice and this permission notice shall be included in
  * all copies or substantial portions of the Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
  * THE SOFTWARE.
  */


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
   reg [1:0] serial_buf;
   wire serial_sync = serial_buf[1];
   always @(posedge clk)
	serial_buf <= { serial_buf[0], serial };

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
          shiftreg <= { serial_sync, shiftreg[8:1] };

        data_strobe <= stop_bit && !error;

     end
     else begin
        data_strobe <= 0;
     end

endmodule


module uart(
	input clk,
	input reset,
	// physical interface
	input serial_rxd,
	output serial_txd,

	// logical interface
	output [7:0] rxd,
	output rxd_strobe,
	input [7:0] txd,
	input txd_strobe,
	output txd_ready
);
	// todo: rx/tx could share a single clock
	parameter DIVISOR = 40; // must be divisible by 4 for rx clock

	uart_rx #(.DIVISOR(DIVISOR/4)) rx(
		.clk(clk),
		.reset(reset),
		.serial(serial_rxd),
		.data_strobe(rxd_strobe),
		.data(rxd),
	);

	uart_tx #(.DIVISOR(DIVISOR)) tx(
		.clk(clk),
		.reset(reset),
		.serial(serial_txd),
		.data(txd),
		.data_strobe(txd_strobe),
		.ready(txd_ready),
	);
endmodule

`endif
