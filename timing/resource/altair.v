module top
(
  input  clk,
  input  rx,
  output tx,
  input  rx2,
  output tx2
);

  reg [5:0] reset_cnt = 0;
	wire resetn = &reset_cnt;

	always @(posedge clk) begin
		reset_cnt <= reset_cnt + !resetn;
	end

  altair machine0(.clk(clk),.reset(~resetn),.rx(rx),.tx(tx));
  altair machine1(.clk(clk),.reset(~resetn),.rx(rx2),.tx(tx2));

endmodule

module altair(
	input clk,
	input reset,
	input rx,
	output tx
);
	reg ce = 0;
	reg intr = 0;
	reg [7:0] idata;
	wire [15:0] addr;
	wire rd;
	wire wr_n;
	wire inta_n;
	wire [7:0] odata;
	wire inte_o;
	wire sync;

	// Memory is sync so need one more clock to write/read
	// This slows down CPU
	always @(posedge clk) begin
		ce <= !ce;
	end

	reg[7:0] sysctl;

	wire [7:0] rom_out;
	wire [7:0] ram_out;
	wire [7:0] rammain_out;
	wire [7:0] boot_out;
	wire [7:0] sio_out;


	wire boot;

	reg wr_ram;
	reg wr_rammain;
	reg wr_sio;

	reg rd_boot;
	reg rd_ram;
	reg rd_rammain;
	reg rd_rom;
	reg rd_sio;

	always @(*)
	begin
		rd_boot = 0;
		rd_ram = 0;
		rd_rammain = 0;
		rd_rom = 0;
		rd_sio = 0;
		idata = 8'hff;
		casex ({boot,sysctl[6],addr[15:8]})
			// Turn-key BOOT
			{2'b10,8'bxxxxxxxx}: begin idata = boot_out; rd_boot = rd; end       // any address
			// MEM MAP
			{2'b00,8'b000xxxxx}: begin idata = rammain_out; rd_rammain = rd; end // 0x0000-0x1fff
			{2'b00,8'b11111011}: begin idata = ram_out; rd_ram = rd; end         // 0xfb00-0xfbff
			{2'b00,8'b11111101}: begin idata = rom_out; rd_rom = rd; end         // 0xfd00-0xfdff
			// I/O MAP - addr[15:8] == addr[7:0] for this section
			{2'b01,8'b000x000x}: begin idata = sio_out; rd_sio = rd; end         // 0x00-0x01 0x10-0x11
		endcase
	end

	always @(*)
	begin
		wr_ram = 0;
		wr_sio = 0;
		wr_rammain = 0;

		casex ({sysctl[4],addr[15:8]})
			// MEM MAP
			{1'b0,8'b000xxxxx}: wr_rammain = ~wr_n; // 0x0000-0x1fff
			{1'b0,8'b11111011}: wr_ram     = ~wr_n; // 0xfb00-0xfbff
										  		    // 0xfd00-0xfdff read-only
			// I/O MAP - addr[15:8] == addr[7:0] for this section
			{1'b1,8'b000x000x}: wr_sio     = ~wr_n; // 0x00-0x01 0x10-0x11
		endcase
	end

	always @(posedge clk)
	begin
		if (sync) sysctl <= odata;
	end

	i8080 cpu(.clk(clk),.ce(ce),.reset(reset),.intr(intr),.idata(idata),.addr(addr),.sync(sync),.rd(rd),.wr_n(wr_n),.inta_n(inta_n),.odata(odata),.inte_o(inte_o));

	jmp_boot boot_ff(.clk(clk),.reset(reset),.rd(rd_boot),.data_out(boot_out),.valid(boot));

	rom_memory #(.ADDR_WIDTH(8),.FILENAME("turnmon.bin.mem")) rom(.clk(clk),.addr(addr[7:0]),.rd(rd_rom),.data_out(rom_out));

	ram_memory #(.ADDR_WIDTH(8)) stack(.clk(clk),.addr(addr[7:0]),.data_in(odata),.rd(rd_ram),.we(wr_ram),.data_out(ram_out));

	ram_memory #(.ADDR_WIDTH(13),.FILENAME("basic4k32.bin.mem")) mainmem(.clk(clk),.addr(addr[12:0]),.data_in(odata),.rd(rd_rammain),.we(wr_rammain),.data_out(rammain_out));

	mc6850 sio(.clk(clk),.reset(reset),.addr(addr[0]),.data_in(odata),.rd(rd_sio),.we(wr_sio),.data_out(sio_out),.ce(ce),.rx(rx),.tx(tx));

endmodule

// ====================================================================
//                Bashkiria-2M FPGA REPLICA
//
//            Copyright (C) 2010 Dmitry Tselikov
//
// This core is distributed under modified BSD license.
// For complete licensing information see LICENSE.TXT.
// --------------------------------------------------------------------
//
// An open implementation of Bashkiria-2M home computer
//
// Author: Dmitry Tselikov   http://bashkiria-2m.narod.ru/
//
// Design File: k580wm80a.v
//
// Processor k580wm80a core design file of Bashkiria-2M replica.

module i8080(
	input clk,
	input ce,
	input reset,
	input intr,
	input [7:0] idata,
	output reg [15:0] addr,
	output reg sync,
	output rd,
	output reg wr_n,
	output inta_n,
	output reg [7:0] odata,
	output inte_o);

reg M1,M2,M3,M4,M5,M6,M7,M8,M9,M10,M11,M12,M13,M14,M15,M16,M17,T5;
reg[2:0] state;

wire M1n = M2|M3|M4|M5|M6|M7|M8|M9|M10|M11|M12|M13|M14|M15|M16|M17;

reg[15:0] PC;
reg[15:0] SP;
reg[7:0] B,C,D,E,H,L,A;
reg[7:0] W,Z,IR;
reg[9:0] ALU;
reg FS,FZ,FA,FP,FC,_FA;

reg rd_,intproc;
assign rd = rd_&~intproc;
assign inta_n = ~(rd_&intproc);
assign inte_o = inte[1];

reg[1:0] inte;
reg jmp,call,halt;
reg save_alu,save_a,save_r,save_rp,read_r,read_rp;
reg incdec,xthl,xchg,sphl,daa;
reg ccc;

always @(*) begin
	casex (IR[5:3])
	3'b00x: ALU = {1'b0,A,1'b1}+{1'b0,Z,FC&IR[3]};
	3'b01x: ALU = {1'b0,A,1'b0}-{1'b0,Z,FC&IR[3]};
	3'b100: ALU = {1'b0,A & Z,1'b0};
	3'b101: ALU = {1'b0,A ^ Z,1'b0};
	3'b110: ALU = {1'b0,A | Z,1'b0};
	3'b111: ALU = {1'b0,A,1'b0}-{1'b0,Z,1'b0};
	endcase
end

always @(*) begin
	casex (IR[5:3])
	3'b00x:  _FA = A[4]^Z[4]^ALU[5];
	3'b100:  _FA = A[3]|Z[3];
	3'b101:  _FA = 1'b0;
	3'b110:  _FA = 1'b0;
	default: _FA = ~(A[4]^Z[4]^ALU[5]);
	endcase
end

always @(*) begin
	// SZ.A.P.C
	case(idata[5:3])
	3'h0: ccc = ~FZ;
	3'h1: ccc = FZ;
	3'h2: ccc = ~FC;
	3'h3: ccc = FC;
	3'h4: ccc = ~FP;
	3'h5: ccc = FP;
	3'h6: ccc = ~FS;
	3'h7: ccc = FS;
	endcase
end

wire[7:0] F = {FS,FZ,1'b0,FA,1'b0,FP,1'b1,FC};
wire[7:0] Z1 = incdec ? Z+{{7{IR[0]}},1'b1} : Z;
wire[15:0] WZ1 = incdec ? {W,Z}+{{15{IR[3]}},1'b1} : {W,Z};
wire[3:0] daaZL = FA!=0 || A[3:0] > 4'h9 ? 4'h6 : 4'h0;
wire[3:0] daaZH = FC!=0 || A[7:4] > {3'b100, A[3:0]>4'h9 ? 1'b0 : 1'b1} ? 4'h6 : 4'h0;

always @(posedge clk or posedge reset)
begin
	if (reset) begin
		{M1,M2,M3,M4,M5,M6,M7,M8,M9,M10,M11,M12,M13,M14,M15,M16,M17} <= 0;
		state <= 0; PC <= 0; {FS,FZ,FA,FP,FC} <= 0; {addr,odata} <= 0;
		{sync,rd_,jmp,halt,inte,save_alu,save_a,save_r,save_rp,incdec,intproc} <= 0;
		wr_n <= 1'b1;
	end else if (ce) begin
		sync <= 0; rd_ <= 0; wr_n <= 1'b1;
		if (halt&~(M1|(intr&inte[1]))) begin
			sync <= 1'b1; // state: rd in m1 out hlt stk ~wr int
			odata <= 8'b10001010; // rd? hlt ~wr
		end else
		if (M1|~M1n) begin
			case (state)
			3'b000: begin
				halt <= 0; intproc <= intr&inte[1]; inte[1] <= inte[0];
				M1 <= 1'b1;
				sync <= 1'b1;
				odata <= {7'b1010001,intr&inte[1]}; // rd m1 ~wr
				addr <= jmp ? {W,Z} : PC;
				state <= 3'b001;
				if (intr&inte[1]) inte <= 2'b0;
				if (save_alu) begin
					FS <= ALU[8];
					FZ <= ~|ALU[8:1];
					FA <= _FA;
					FP <= ~^ALU[8:1];
					FC <= ALU[9]|(FC&daa);
					if (IR[5:3]!=3'b111) A <= ALU[8:1];
				end else
				if (save_a) begin
					A <= Z1;
				end else
				if (save_r) begin
					case (IR[5:3])
					3'b000: B <= Z1;
					3'b001: C <= Z1;
					3'b010: D <= Z1;
					3'b011: E <= Z1;
					3'b100: H <= Z1;
					3'b101: L <= Z1;
					3'b111: A <= Z1;
					endcase
					if (incdec) begin
						FS <= Z1[7];
						FZ <= ~|Z1;
						FA <= IR[0] ? Z1[3:0]!=4'b1111 : Z1[3:0]==0;
						FP <= ~^Z1;
					end
				end else
				if (save_rp) begin
					case (IR[5:4])
					2'b00: {B,C} <= WZ1;
					2'b01: {D,E} <= WZ1;
					2'b10: {H,L} <= WZ1;
					2'b11:
						if (sphl || !IR[7]) begin
							SP <= WZ1;
						end else begin
							{A,FS,FZ,FA,FP,FC} <= {WZ1[15:8],WZ1[7],WZ1[6],WZ1[4],WZ1[2],WZ1[0]};
						end
					endcase
				end
			end
			3'b001: begin
				rd_ <= 1'b1;
				PC <= addr+{15'b0,~intproc};
				state <= 3'b010;
			end
			3'b010: begin
				IR <= idata;
				{jmp,call,save_alu,save_a,save_r,save_rp,read_r,read_rp,incdec,xthl,xchg,sphl,T5,daa} <= 0;
				casex (idata)
				8'b00xx0001: {save_rp,M2,M3} <= 3'b111;
				8'b00xx1001: {read_rp,M16,M17} <= 3'b111;
				8'b000x0010: {read_rp,M14} <= 2'b11;
				8'b00100010: {M2,M3,M14,M15} <= 4'b1111;
				8'b00110010: {M2,M3,M14} <= 3'b111;
				8'b000x1010: {read_rp,save_a,M12} <= 3'b111;
				8'b00101010: {save_rp,M2,M3,M12,M13} <= 5'b11111;
				8'b00111010: {save_a,M2,M3,M12} <= 4'b1111;
				8'b00xxx011: {read_rp,save_rp,incdec,T5} <= 4'b1111;
				8'b00xxx10x: {read_r,save_r,incdec,T5} <= {3'b111,idata[5:3]!=3'b110};
				8'b00xxx110: {save_r,M2} <= 2'b11;
				8'b00000111: {FC,A} <= {A,A[7]};
				8'b00001111: {A,FC} <= {A[0],A};
				8'b00010111: {FC,A} <= {A,FC};
				8'b00011111: {A,FC} <= {FC,A};
				8'b00100111: {daa,save_alu,IR[5:3],Z} <= {5'b11000,daaZH,daaZL};
				8'b00101111: A <= ~A;
				8'b00110111: FC <= 1'b1;
				8'b00111111: FC <= ~FC;
				8'b01xxxxxx: if (idata[5:0]==6'b110110) halt <= 1'b1; else {read_r,save_r,T5} <= {2'b11,~(idata[5:3]==3'b110||idata[2:0]==3'b110)};
				8'b10xxxxxx: {read_r,save_alu} <= 2'b11;
				8'b11xxx000: {jmp,M8,M9} <= {3{ccc}};
				8'b11xx0001: {save_rp,M8,M9} <= 3'b111;
				8'b110x1001: {jmp,M8,M9} <= 3'b111;
				8'b11101001: {read_rp,jmp,T5} <= 3'b111;
				8'b11111001: {read_rp,save_rp,T5,sphl} <= 4'b1111;
				8'b11xxx010: {jmp,M2,M3} <= {ccc,2'b11};
				8'b1100x011: {jmp,M2,M3} <= 3'b111;
				8'b11010011: {M2,M7} <= 2'b11;
				8'b11011011: {M2,M6} <= 2'b11;
				8'b11100011: {save_rp,M8,M9,M10,M11,xthl} <= 6'b111111;
				8'b11101011: {read_rp,save_rp,xchg} <= 3'b111;
				8'b1111x011: inte <= idata[3] ? 2'b1 : 2'b0;
				8'b11xxx100: {jmp,M2,M3,T5,M10,M11,call} <= {ccc,3'b111,{3{ccc}}};
				8'b11xx0101: {read_rp,T5,M10,M11} <= 4'b1111;
				8'b11xx1101: {jmp,M2,M3,T5,M10,M11,call} <= 7'b1111111;
				8'b11xxx110: {save_alu,M2} <= 2'b11;
				8'b11xxx111: {jmp,T5,M10,M11,call,W,Z} <= {5'b11111,10'b0,idata[5:3],3'b0};
				endcase
				state <= 3'b011;
			end
			3'b011: begin
				if (read_rp) begin
					case (IR[5:4])
					2'b00: {W,Z} <= {B,C};
					2'b01: {W,Z} <= {D,E};
					2'b10: {W,Z} <= xchg ? {D,E} : {H,L};
					2'b11: {W,Z} <= sphl ? {H,L} : IR[7] ? {A,F} : SP;
					endcase
					if (xchg) {D,E} <= {H,L};
				end else
				if (~(jmp|daa)) begin
					case (incdec?IR[5:3]:IR[2:0])
					3'b000: Z <= B;
					3'b001: Z <= C;
					3'b010: Z <= D;
					3'b011: Z <= E;
					3'b100: Z <= H;
					3'b101: Z <= L;
					3'b110: M4 <= read_r;
					3'b111: Z <= A;
					endcase
					M5 <= save_r && IR[5:3]==3'b110;
				end
				state <= T5 ? 3'b100 : 0;
				M1 <= T5;
			end
			3'b100: begin
				if (M10) SP <= SP-16'b1;
				state <= 0;
				M1 <= 0;
			end
			endcase
		end else
		if (M2 || M3) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b1000001,intproc}; // rd ~wr
				addr <= PC;
				state <= 3'b001;
			end
			3'b001: begin
				rd_ <= 1'b1;
				PC <= addr+{15'b0,~intproc};
				state <= 3'b010;
			end
			3'b010: begin
				if (M2) begin
					Z <= idata;
					M2 <= 0;
				end else begin
					W <= idata;
					M3 <= 0;
				end
				state <= 3'b000;
			end
			endcase
		end else
		if (M4) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b1000001,intproc}; // rd ~wr
				addr <= {H,L};
				state <= 3'b001;
			end
			3'b001: begin
				rd_ <= 1'b1;
				state <= 3'b010;
			end
			3'b010: begin
				Z <= idata;
				M4 <= 0;
				state <= 3'b000;
			end
			endcase
		end else
		if (M5) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b0000000,intproc}; // ~wr=0
				addr <= {H,L};
				state <= 3'b001;
			end
			3'b001: begin
				odata <= Z1;
				wr_n <= 1'b0;
				state <= 3'b010;
			end
			3'b010: begin
				M5 <= 0;
				state <= 3'b000;
			end
			endcase
		end else
		if (M6) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b0100001,intproc}; // in ~wr
				addr <= {Z,Z};
				state <= 3'b001;
			end
			3'b001: begin
				rd_ <= 1'b1;
				state <= 3'b010;
			end
			3'b010: begin
				A <= idata;
				M6 <= 0;
				state <= 3'b000;
			end
			endcase
		end else
		if (M7) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b0001000,intproc}; // out
				addr <= {Z,Z};
				state <= 3'b001;
			end
			3'b001: begin
				odata <= A;
				wr_n <= 1'b0;
				state <= 3'b010;
			end
			3'b010: begin
				M7 <= 0;
				state <= 3'b000;
			end
			endcase
		end else
		if (M8 || M9) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b1000011,intproc}; // rd stk ~wr
				addr <= SP;
				state <= 3'b001;
			end
			3'b001: begin
				rd_ <= 1'b1;
				if (M8 || !xthl) SP <= SP+16'b1;
				state <= 3'b010;
			end
			3'b010: begin
				if (M8) begin
					Z <= idata;
					M8 <= 0;
				end else begin
					W <= idata;
					M9 <= 0;
				end
				state <= 3'b000;
			end
			endcase
		end else
		if (M10 || M11) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b0000010,intproc}; // stk
				addr <= SP;
				state <= 3'b001;
			end
			3'b001: begin
				if (M10) begin
					SP <= SP-16'b1;
					odata <= xthl ? H : call ? PC[15:8] : W;
				end else begin
					odata <= xthl ? L : call ? PC[7:0] : Z;
				end
				wr_n <= 1'b0;
				state <= 3'b010;
			end
			3'b010: begin
				if (M10) begin
					M10 <= 0;
				end else begin
					M11 <= 0;
				end
				state <= 3'b000;
			end
			endcase
		end else
		if (M12 || M13) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b1000001,intproc}; // rd ~wr
				addr <= M12 ? {W,Z} : addr+16'b1;
				state <= 3'b001;
			end
			3'b001: begin
				rd_ <= 1'b1;
				state <= 3'b010;
			end
			3'b010: begin
				if (M12) begin
					Z <= idata;
					M12 <= 0;
				end else begin
					W <= idata;
					M13 <= 0;
				end
				state <= 3'b000;
			end
			endcase
		end else
		if (M14 || M15) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b0000000,intproc}; // ~wr=0
				addr <= M14 ? {W,Z} : addr+16'b1;
				state <= 3'b001;
			end
			3'b001: begin
				if (M14) begin
					odata <= M15 ? L : A;
				end else begin
					odata <= H;
				end
				wr_n <= 1'b0;
				state <= 3'b010;
			end
			3'b010: begin
				if (M14) begin
					M14 <= 0;
				end else begin
					M15 <= 0;
				end
				state <= 3'b000;
			end
			endcase
		end else
		if (M16 || M17) begin
			case (state)
			3'b000: begin
				sync <= 1'b1;
				odata <= {7'b0000001,intproc}; // ~wr
				state <= 3'b001;
			end
			3'b001: begin
				state <= 3'b010;
			end
			3'b010: begin
				if (M16) begin
					M16 <= 0;
				end else begin
					{FC,H,L} <= {1'b0,H,L}+{1'b0,W,Z};
					M17 <= 0;
				end
				state <= 3'b000;
			end
			endcase
		end
	end
end

endmodule

module jmp_boot(
  input clk,
  input reset,
  input rd,
  output reg [7:0] data_out,
  output reg valid
);
  reg [1:0] state = 0;
  reg prev_rd = 0;
  always @(posedge clk)
  begin
	if (reset)
	begin
		state <= 0;
		valid <= 1;
	end
	else
	begin
		if (rd && prev_rd==0)
		begin
			case (state)
				2'b00 : begin
						data_out <= 8'b11000011; // JMP 0xfd00
						state <= 2'b01;
						end
				2'b01 : begin
						data_out <= 8'h00;
						state <= 2'b10;
						end
				2'b10 : begin
						data_out <= 8'hFD;
						state <= 2'b11;
						end
				2'b11 : begin
						state <= 2'b11;
						valid <= 0;
						end
			endcase
		end
		prev_rd = rd;
	end
  end
endmodule

module mc6850(
  input clk,
  input reset,
  input addr,
  input [7:0] data_in,
  input rd,
  input we,
  output reg [7:0] data_out,
  input ce,
  input rx,
  output tx
);
  wire valid;
  wire tdre;
  wire [7:0] uart_out;
  wire dat_wait;

  simpleuart uart(
	.clk(clk),
	.resetn(~reset),

	.ser_tx(tx),
	.ser_rx(rx),

	.cfg_divider(12000000/9600),

	.reg_dat_we(we && (addr==1'b1)),
	.reg_dat_re(rd && (addr==1'b1)),
	.reg_dat_di(data_in & 8'h7f),
	.reg_dat_do(uart_out),
	.reg_dat_wait(dat_wait),
	.recv_buf_valid(valid),
	.tdre(tdre)
);

  always @(posedge clk)
  begin
		if (rd)
		begin
			if (addr==1'b0)
				data_out <= { 2'b00,valid, 1'b0,   2'b00, tdre, valid };
			else
				data_out <= uart_out;
		end
  end
endmodule

module ram_memory(
  input clk,
  input [7:0] addr,
  input [7:0] data_in,
  input rd,
  input we,
  output reg [7:0] data_out
);
  parameter integer ADDR_WIDTH = 8;

  reg [7:0] ram[0:(2 ** ADDR_WIDTH)-1] /* verilator public_flat */;

  parameter FILENAME = "";

  always @(posedge clk)
  begin
    if (we)
      ram[addr] <= data_in;
    if (rd)
      data_out <= ram[addr];
  end
endmodule

module rom_memory(
  input clk,
  input [7:0] addr,
  input rd,
  output reg [7:0] data_out
);
	parameter FILENAME = "";

  parameter integer ADDR_WIDTH = 8;

  reg [7:0] rom[0:(2 ** ADDR_WIDTH)-1] /* verilator public_flat */;

  always @(posedge clk)
  begin
	if (rd)
		data_out <= rom[addr];
  end
endmodule

 /*
 *  PicoSoC - A simple example SoC using PicoRV32
 *
 *  Copyright (C) 2017  Clifford Wolf <clifford@clifford.at>
 *
 *  Permission to use, copy, modify, and/or distribute this software for any
 *  purpose with or without fee is hereby granted, provided that the above
 *  copyright notice and this permission notice appear in all copies.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
 *  WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
 *  MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
 *  ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
 *  WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
 *  ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
 *  OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 */

module simpleuart (
	input clk,
	input resetn,

	output ser_tx,
	input  ser_rx,

	input  [31:0] cfg_divider,

	input         reg_dat_we,
	input         reg_dat_re,
	input  [7:0]  reg_dat_di,
	output [7:0]  reg_dat_do,
	output        reg_dat_wait,
	output 	reg   recv_buf_valid,
	output  reg   tdre
);

	reg [3:0] recv_state;
	reg [31:0] recv_divcnt;
	reg [7:0] recv_pattern;
	reg [7:0] recv_buf_data;

	reg [9:0] send_pattern;
	reg [3:0] send_bitcnt;
	reg [31:0] send_divcnt;
	reg send_dummy;

	assign reg_dat_wait = reg_dat_we && (send_bitcnt || send_dummy);
	assign reg_dat_do = recv_buf_valid ? recv_buf_data : ~0;

	always @(posedge clk) begin
		if (!resetn) begin
			recv_state <= 0;
			recv_divcnt <= 0;
			recv_pattern <= 0;
			recv_buf_data <= 0;
			recv_buf_valid <= 0;
		end else begin
			recv_divcnt <= recv_divcnt + 1;
			if (reg_dat_re)
				recv_buf_valid <= 0;
			case (recv_state)
				0: begin
					if (!ser_rx)
						recv_state <= 1;
					recv_divcnt <= 0;
				end
				1: begin
					if (2*recv_divcnt > cfg_divider) begin
						recv_state <= 2;
						recv_divcnt <= 0;
					end
				end
				10: begin
					if (recv_divcnt > cfg_divider) begin
						recv_buf_data <= recv_pattern;
						recv_buf_valid <= 1;
						recv_state <= 0;
					end
				end
				default: begin
					if (recv_divcnt > cfg_divider) begin
						recv_pattern <= {ser_rx, recv_pattern[7:1]};
						recv_state <= recv_state + 1;
						recv_divcnt <= 0;
					end
				end
			endcase
		end
	end

	assign ser_tx = send_pattern[0];

	always @(posedge clk) begin
		send_divcnt <= send_divcnt + 1;
		if (!resetn) begin
			send_pattern <= ~0;
			send_bitcnt <= 0;
			send_divcnt <= 0;
			send_dummy <= 1;
			tdre <=0;
		end else begin
			if (send_dummy && !send_bitcnt) begin
				send_pattern <= ~0;
				send_bitcnt <= 15;
				send_divcnt <= 0;
				send_dummy <= 0;
			end else
			if (reg_dat_we && !send_bitcnt) begin
				send_pattern <= {1'b1, reg_dat_di, 1'b0};
				send_bitcnt <= 10;
				send_divcnt <= 0;
				tdre <=0;
			end else
			if (send_divcnt > cfg_divider && send_bitcnt) begin
				send_pattern <= {1'b1, send_pattern[9:1]};
				send_bitcnt <= send_bitcnt - 1;
				send_divcnt <= 0;
			end else if (send_bitcnt==0)
			begin
				tdre <=1;
			end
		end
	end
endmodule

