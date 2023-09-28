/*  This file is part of JT7759.
    JT7759 program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT7759 program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT7759.  If not, see <http://www.gnu.org/licenses/>.

    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 5-7-2020 */

module jt7759(
    input                  rst,
    input                  clk,  // Use same clock as sound CPU
    input                  cen,  // 640kHz
    input                  stn,  // STart (active low)
    input                  cs,
    input                  mdn,  // MODE: 1 for stand alone mode, 0 for slave mode
                                 // see chart in page 13 of PDF
    output                 busyn,
    // CPU interface
    input                  wrn,  // for slave mode only, 31.7us after drqn is set
    input         [ 7:0]   din,
    output                 drqn,  // data request. 50-70us delay after mdn goes low
    // ROM interface
    output                 rom_cs,      // equivalent to DRQn in original chip
    output        [16:0]   rom_addr,
    input         [ 7:0]   rom_data,
    input                  rom_ok,
    // Sound output
    output signed [ 8:0]   sound

`ifdef DEBUG
    ,output [3:0] debug_nibble
    ,output       debug_cen_dec
    ,output       debug_dec_rst
`endif
);

wire   [ 5:0] divby;
wire          cen_dec;    // internal clock enable for sound
wire          cen_ctl;    // cen_dec x4

wire          dec_rst;
wire   [ 3:0] encoded;

wire          ctrl_cs, ctrl_ok, ctrl_flush;
wire   [16:0] ctrl_addr;
wire   [ 7:0] ctrl_din;


`ifdef DEBUG
    assign debug_nibble  = encoded;
    assign debug_cen_dec = cen_dec;
    assign debug_dec_rst = dec_rst;
`endif

jt7759_div u_div(
    .clk        ( clk       ),
    .cen        ( cen       ),
    .cen_ctl    ( cen_ctl   ),
    .divby      ( divby     ),
    .cen_dec    ( cen_dec   )
);

jt7759_ctrl u_ctrl(
    .rst        ( rst       ),
    .clk        ( clk       ),
    .cen_ctl    ( cen_ctl   ),
    .cen_dec    ( cen_dec   ),
    .divby      ( divby     ),
    // chip interface
    .stn        ( stn       ),
    .cs         ( cs        ),
    .mdn        ( mdn       ),
    .drqn       ( drqn      ),
    .busyn      ( busyn     ),
    .wrn        ( wrn       ),
    .din        ( din       ),
    // ADPCM engine
    .dec_rst    ( dec_rst   ),
    .dec_din    ( encoded   ),
    // ROM interface
    .rom_cs     ( ctrl_cs   ),
    .rom_addr   ( ctrl_addr ),
    .rom_data   ( ctrl_din  ),
    .rom_ok     ( ctrl_ok   ),
    .flush      ( ctrl_flush)
);

jt7759_data u_data(
    .rst        ( rst       ),
    .clk        ( clk       ),
    .cen_ctl    ( cen_ctl   ),
    .mdn        ( mdn       ),
    // Control interface
    .ctrl_flush ( ctrl_flush),
    .ctrl_cs    ( ctrl_cs   ),
    .ctrl_addr  ( ctrl_addr ),
    .ctrl_din   ( ctrl_din  ),
    .ctrl_ok    ( ctrl_ok   ),
    .ctrl_busyn ( busyn     ),
    // ROM interface
    .rom_cs     ( rom_cs    ),
    .rom_addr   ( rom_addr  ),
    .rom_data   ( rom_data  ),
    .rom_ok     ( rom_ok    ),
    // Passive interface
    .cs         ( cs        ),
    .wrn        ( wrn       ),
    .din        ( din       ),
    .drqn       ( drqn      )
);

jt7759_adpcm u_adpcm(
    .rst        ( dec_rst   ),
    .clk        ( clk       ),
    .cen_dec    ( cen_dec   ),
    .encoded    ( encoded   ),
    .sound      ( sound     )
);


`ifdef SIMULATION
integer fsnd;
initial begin
    fsnd=$fopen("jt7759.raw","wb");
end
wire signed [15:0] snd_log = { sound, 7'b0 };
always @(posedge cen_dec) begin
    $fwrite(fsnd,"%u", {snd_log, snd_log});
end
`endif
endmodule

/*  This file is part of JT7759.
    JT7759 program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public Licen4se as published by
    the Free Software Foundation, either version 3 of the Licen4se, or
    (at your option) any later version.

    JT7759 program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public Licen4se for more details.

    You should have received a copy of the GNU General Public Licen4se
    along with JT7759.  If not, see <http://www.gnu.org/licen4ses/>.

    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 5-7-2020 */

module jt7759_adpcm #(parameter SW=9) (
    input                      rst,
    input                      clk,
    input                      cen_dec,
    input             [   3:0] encoded,
    output reg signed [SW-1:0] sound
);

// The look-up table could have been compressed. One obvious way is to realize that one
// half of it is just the negative version of the other.
// However, because it will be synthesized as a 1 kilo word memory of 9-bit words, i.e. 1BRAM
// this is the best choice.
// This is generated by the file doc/lut.c

reg  signed [8:0] lut[0:255];
reg  signed [3:0] st_lut[0:7];
reg         [3:0] st;
reg         [3:0] st_delta;
reg  signed [5:0] st_next, st_sum;
reg  signed [SW:0] next_snd, lut_step;

function [SW:0] sign_ext;
    input signed [8:0] din;
    sign_ext = { {SW-8{din[8]}}, din };
endfunction

always @(*) begin
    st_delta = st_lut[ encoded[2:0] ];
    st_sum   = {2'b0, st } + {{2{st_delta[3]}}, st_delta };
    if( st_sum[5] )
        st_next = 6'd0;
    else if( st_sum[4] )
        st_next = 6'd15;
    else
        st_next = st_sum;
    lut_step = sign_ext( lut[{st,encoded}] );
    next_snd = { sound[SW-1], sound } + lut_step;
end

always @(posedge clk, posedge rst ) begin
    if( rst ) begin
        sound <= {SW{1'd0}};
        st    <= 4'd0;
    end else if(cen_dec) begin
        if( next_snd[SW]==next_snd[SW-1] )
            sound <= next_snd[SW-1:0];
        else sound <= next_snd[SW] ? {1'b1,{SW-1{1'b0}}} : {1'b0,{SW-1{1'b1}}};
        st    <= st_next[3:0];
    end
end

initial begin
    st_lut[0]=-4'd1; st_lut[1]=-4'd1; st_lut[2]=4'd0; st_lut[3]=4'd0;
    st_lut[4]=4'd1;  st_lut[5]=4'd2;  st_lut[6]=4'd2; st_lut[7]=4'd3;
end


initial begin
    lut[8'h00]= 9'd0;  lut[8'h01]= 9'd0;   lut[8'h02]= 9'd1;   lut[8'h03]= 9'd2;
    lut[8'h04]= 9'd3;  lut[8'h05]= 9'd5;   lut[8'h06]= 9'd7;   lut[8'h07]= 9'd10;
    lut[8'h08]= 9'd0;  lut[8'h09]= 9'd0;   lut[8'h0A]=-9'd1;   lut[8'h0B]=-9'd2;
    lut[8'h0C]=-9'd3;  lut[8'h0D]=-9'd5;   lut[8'h0E]=-9'd7;   lut[8'h0F]=-9'd10;
    lut[8'h10]= 9'd0;  lut[8'h11]= 9'd1;   lut[8'h12]= 9'd2;   lut[8'h13]= 9'd3;
    lut[8'h14]= 9'd4;  lut[8'h15]= 9'd6;   lut[8'h16]= 9'd8;   lut[8'h17]= 9'd13;
    lut[8'h18]= 9'd0;  lut[8'h19]=-9'd1;   lut[8'h1A]=-9'd2;   lut[8'h1B]=-9'd3;
    lut[8'h1C]=-9'd4;  lut[8'h1D]=-9'd6;   lut[8'h1E]=-9'd8;   lut[8'h1F]=-9'd13;
    lut[8'h20]= 9'd0;  lut[8'h21]= 9'd1;   lut[8'h22]= 9'd2;   lut[8'h23]= 9'd4;
    lut[8'h24]= 9'd5;  lut[8'h25]= 9'd7;   lut[8'h26]= 9'd10;  lut[8'h27]= 9'd15;
    lut[8'h28]= 9'd0;  lut[8'h29]=-9'd1;   lut[8'h2A]=-9'd2;   lut[8'h2B]=-9'd4;
    lut[8'h2C]=-9'd5;  lut[8'h2D]=-9'd7;   lut[8'h2E]=-9'd10;  lut[8'h2F]=-9'd15;
    lut[8'h30]= 9'd0;  lut[8'h31]= 9'd1;   lut[8'h32]= 9'd3;   lut[8'h33]= 9'd4;
    lut[8'h34]= 9'd6;  lut[8'h35]= 9'd9;   lut[8'h36]= 9'd13;  lut[8'h37]= 9'd19;
    lut[8'h38]= 9'd0;  lut[8'h39]=-9'd1;   lut[8'h3A]=-9'd3;   lut[8'h3B]=-9'd4;
    lut[8'h3C]=-9'd6;  lut[8'h3D]=-9'd9;   lut[8'h3E]=-9'd13;  lut[8'h3F]=-9'd19;
    lut[8'h40]= 9'd0;  lut[8'h41]= 9'd2;   lut[8'h42]= 9'd3;   lut[8'h43]= 9'd5;
    lut[8'h44]= 9'd8;  lut[8'h45]= 9'd11;  lut[8'h46]= 9'd15;  lut[8'h47]= 9'd23;
    lut[8'h48]= 9'd0;  lut[8'h49]=-9'd2;   lut[8'h4A]=-9'd3;   lut[8'h4B]=-9'd5;
    lut[8'h4C]=-9'd8;  lut[8'h4D]=-9'd11;  lut[8'h4E]=-9'd15;  lut[8'h4F]=-9'd23;
    lut[8'h50]= 9'd0;  lut[8'h51]= 9'd2;   lut[8'h52]= 9'd4;   lut[8'h53]= 9'd7;
    lut[8'h54]= 9'd10; lut[8'h55]= 9'd14;  lut[8'h56]= 9'd19;  lut[8'h57]= 9'd29;
    lut[8'h58]= 9'd0;  lut[8'h59]=-9'd2;   lut[8'h5A]=-9'd4;   lut[8'h5B]=-9'd7;
    lut[8'h5C]=-9'd10; lut[8'h5D]=-9'd14;  lut[8'h5E]=-9'd19;  lut[8'h5F]=-9'd29;
    lut[8'h60]= 9'd0;  lut[8'h61]= 9'd3;   lut[8'h62]= 9'd5;   lut[8'h63]= 9'd8;
    lut[8'h64]= 9'd12; lut[8'h65]= 9'd16;  lut[8'h66]= 9'd22;  lut[8'h67]= 9'd33;
    lut[8'h68]= 9'd0;  lut[8'h69]=-9'd3;   lut[8'h6A]=-9'd5;   lut[8'h6B]=-9'd8;
    lut[8'h6C]=-9'd12; lut[8'h6D]=-9'd16;  lut[8'h6E]=-9'd22;  lut[8'h6F]=-9'd33;
    lut[8'h70]= 9'd1;  lut[8'h71]= 9'd4;   lut[8'h72]= 9'd7;   lut[8'h73]= 9'd10;
    lut[8'h74]= 9'd15; lut[8'h75]= 9'd20;  lut[8'h76]= 9'd29;  lut[8'h77]= 9'd43;
    lut[8'h78]=-9'd1;  lut[8'h79]=-9'd4;   lut[8'h7A]=-9'd7;   lut[8'h7B]=-9'd10;
    lut[8'h7C]=-9'd15; lut[8'h7D]=-9'd20;  lut[8'h7E]=-9'd29;  lut[8'h7F]=-9'd43;
    lut[8'h80]= 9'd1;  lut[8'h81]= 9'd4;   lut[8'h82]= 9'd8;   lut[8'h83]= 9'd13;
    lut[8'h84]= 9'd18; lut[8'h85]= 9'd25;  lut[8'h86]= 9'd35;  lut[8'h87]= 9'd53;
    lut[8'h88]=-9'd1;  lut[8'h89]=-9'd4;   lut[8'h8A]=-9'd8;   lut[8'h8B]=-9'd13;
    lut[8'h8C]=-9'd18; lut[8'h8D]=-9'd25;  lut[8'h8E]=-9'd35;  lut[8'h8F]=-9'd53;
    lut[8'h90]= 9'd1;  lut[8'h91]= 9'd6;   lut[8'h92]= 9'd10;  lut[8'h93]= 9'd16;
    lut[8'h94]= 9'd22; lut[8'h95]= 9'd31;  lut[8'h96]= 9'd43;  lut[8'h97]= 9'd64;
    lut[8'h98]=-9'd1;  lut[8'h99]=-9'd6;   lut[8'h9A]=-9'd10;  lut[8'h9B]=-9'd16;
    lut[8'h9C]=-9'd22; lut[8'h9D]=-9'd31;  lut[8'h9E]=-9'd43;  lut[8'h9F]=-9'd64;
    lut[8'hA0]= 9'd2;  lut[8'hA1]= 9'd7;   lut[8'hA2]= 9'd12;  lut[8'hA3]= 9'd19;
    lut[8'hA4]= 9'd27; lut[8'hA5]= 9'd37;  lut[8'hA6]= 9'd51;  lut[8'hA7]= 9'd76;
    lut[8'hA8]=-9'd2;  lut[8'hA9]=-9'd7;   lut[8'hAA]=-9'd12;  lut[8'hAB]=-9'd19;
    lut[8'hAC]=-9'd27; lut[8'hAD]=-9'd37;  lut[8'hAE]=-9'd51;  lut[8'hAF]=-9'd76;
    lut[8'hB0]= 9'd2;  lut[8'hB1]= 9'd9;   lut[8'hB2]= 9'd16;  lut[8'hB3]= 9'd24;
    lut[8'hB4]= 9'd34; lut[8'hB5]= 9'd46;  lut[8'hB6]= 9'd64;  lut[8'hB7]= 9'd96;
    lut[8'hB8]=-9'd2;  lut[8'hB9]=-9'd9;   lut[8'hBA]=-9'd16;  lut[8'hBB]=-9'd24;
    lut[8'hBC]=-9'd34; lut[8'hBD]=-9'd46;  lut[8'hBE]=-9'd64;  lut[8'hBF]=-9'd96;
    lut[8'hC0]= 9'd3;  lut[8'hC1]= 9'd11;  lut[8'hC2]= 9'd19;  lut[8'hC3]= 9'd29;
    lut[8'hC4]= 9'd41; lut[8'hC5]= 9'd57;  lut[8'hC6]= 9'd79;  lut[8'hC7]= 9'd117;
    lut[8'hC8]=-9'd3;  lut[8'hC9]=-9'd11;  lut[8'hCA]=-9'd19;  lut[8'hCB]=-9'd29;
    lut[8'hCC]=-9'd41; lut[8'hCD]=-9'd57;  lut[8'hCE]=-9'd79;  lut[8'hCF]=-9'd117;
    lut[8'hD0]= 9'd4;  lut[8'hD1]= 9'd13;  lut[8'hD2]= 9'd24;  lut[8'hD3]= 9'd36;
    lut[8'hD4]= 9'd50; lut[8'hD5]= 9'd69;  lut[8'hD6]= 9'd96;  lut[8'hD7]= 9'd143;
    lut[8'hD8]=-9'd4;  lut[8'hD9]=-9'd13;  lut[8'hDA]=-9'd24;  lut[8'hDB]=-9'd36;
    lut[8'hDC]=-9'd50; lut[8'hDD]=-9'd69;  lut[8'hDE]=-9'd96;  lut[8'hDF]=-9'd143;
    lut[8'hE0]= 9'd4;  lut[8'hE1]= 9'd16;  lut[8'hE2]= 9'd29;  lut[8'hE3]= 9'd44;
    lut[8'hE4]= 9'd62; lut[8'hE5]= 9'd85;  lut[8'hE6]= 9'd118; lut[8'hE7]= 9'd175;
    lut[8'hE8]=-9'd4;  lut[8'hE9]=-9'd16;  lut[8'hEA]=-9'd29;  lut[8'hEB]=-9'd44;
    lut[8'hEC]=-9'd62; lut[8'hED]=-9'd85;  lut[8'hEE]=-9'd118; lut[8'hEF]=-9'd175;
    lut[8'hF0]= 9'd6;  lut[8'hF1]= 9'd20;  lut[8'hF2]= 9'd36;  lut[8'hF3]= 9'd54;
    lut[8'hF4]= 9'd76; lut[8'hF5]= 9'd104; lut[8'hF6]= 9'd144; lut[8'hF7]= 9'd214;
    lut[8'hF8]=-9'd6;  lut[8'hF9]=-9'd20;  lut[8'hFA]=-9'd36;  lut[8'hFB]=-9'd54;
    lut[8'hFC]=-9'd76; lut[8'hFD]=-9'd104; lut[8'hFE]=-9'd144; lut[8'hFF]=-9'd214;
end

endmodule

/*  This file is part of JT7759.
    JT7759 program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public Licen_ctlse as published by
    the Free Software Foundation, either version 3 of the Licen_ctlse, or
    (at your option) any later version.

    JT7759 program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public Licen_ctlse for more details.

    You should have received a copy of the GNU General Public Licen_ctlse
    along with JT7759.  If not, see <http://www.gnu.org/licen_ctlses/>.

    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 5-7-2020 */

module jt7759_ctrl(
    input             rst,
    input             clk,
    input             cen_ctl,
    input             cen_dec,
    output reg [ 5:0] divby,
    input             stn,  // STart (active low)
    input             cs,
    input             mdn,  // MODE: 1 for stand alone mode, 0 for slave mode
    input             drqn,
    output            busyn,
    // CPU interface
    input             wrn,  // for slave mode only
    input      [ 7:0] din,
    // ADPCM engine
    output reg        dec_rst,
    output reg [ 3:0] dec_din,
    // ROM interface
    output            rom_cs,      // equivalent to DRQn in original chip
    output reg [16:0] rom_addr,
    input      [ 7:0] rom_data,
    input             rom_ok,
    output reg        flush
);

localparam STW = 12;
localparam [STW-1:0] RST    = 12'd1<<0;  // 1
localparam [STW-1:0] IDLE   = 12'd1<<1;  // 2
localparam [STW-1:0] SND_CNT= 12'd1<<2;  // 4
localparam [STW-1:0] PLAY   = 12'd1<<3;  // 8
localparam [STW-1:0] WAIT   = 12'd1<<4;  // 10
localparam [STW-1:0] GETN   = 12'd1<<5;  // 20
localparam [STW-1:0] MUTED  = 12'd1<<6;  // 40
localparam [STW-1:0] LOAD   = 12'd1<<7;  // 80
localparam [STW-1:0] READCMD= 12'd1<<8;  // 100
localparam [STW-1:0] READADR= 12'd1<<9;  // 200
localparam [STW-1:0] SIGN   = 12'd1<<10; // 400
localparam [STW-1:0] DONE   = 12'd1<<11; // 800

localparam MTB = 10,    // base count at cen_ctl (1.56us) 1.5625us*512=0.8ms
           MTW = 6+MTB; // Mute counter

// reg  [    7:0] max_snd; // sound count: total number of sound samples
reg  [STW-1:0] st;
reg  [    3:0] next;
reg  [MTW-1:0] mute_cnt;
reg  [    8:0] data_cnt;
reg  [    3:0] rep_cnt;
reg  [   15:0] addr_latch;
// reg  [   16:0] rep_latch;
reg  [    7:0] sign[0:3];
reg            last_wr, getdiv, headerok;
// reg            signok; // ROM signature ok
wire           write, wr_posedge;
wire [   16:0] next_rom;
wire [    1:0] sign_addr = rom_addr[1:0]-2'd1;
reg            pre_cs, pulse_cs;

assign      write      = cs && ( (!mdn && !wrn) || !stn );
assign      wr_posedge = !last_wr && write;
assign      busyn      = st == IDLE || st == RST || st == DONE;
assign      next_rom   = rom_addr+1'b1;
assign      rom_cs     = pre_cs & ~pulse_cs;

initial begin
    sign[0] = 8'h5a;
    sign[1] = 8'ha5;
    sign[2] = 8'h69;
    sign[3] = 8'h55;
end

// Simulation log
`ifdef SIMULATION
`define JT7759_SILENCE   $display("\tjt7759: silence");
`define JT7759_PLAY      $display("\tjt7759: play");
`define JT7759_PLAY_LONG $display("\tjt7759: play n");
`define JT7759_REPEAT    $display("\tjt7759: repeat");
`define JT7759_DONE      $display("\tjt7759: sample done");
`else
`define JT7759_SILENCE
`define JT7759_PLAY
`define JT7759_PLAY_LONG
`define JT7759_REPEAT
`define JT7759_DONE
`endif


always @(posedge clk, posedge rst) begin
    if( rst ) begin
        // max_snd   <= 8'd0;
        st        <= RST;
        pre_cs    <= 0;
        rom_addr  <= 17'd0;
        divby     <= 6'h10; // ~8kHz
        last_wr   <= 0;
        dec_rst   <= 1;
        dec_din   <= 4'd0;
        mute_cnt  <= 0;
        data_cnt  <= 9'd0;
        // signok    <= 0;
        rep_cnt   <= ~4'd0;
        // rep_latch <= 17'd0;
        headerok  <= 0;
        addr_latch<= 0;
        pulse_cs  <= 0;
        flush     <= 0;
    end else begin
        last_wr <= write;
        flush   <= 0;
        if( pulse_cs ) begin
            /*if(cen_ctl)*/ pulse_cs <= 0;
        end else begin
            case( st )
                default: if(cen_ctl) begin // start up process
                    if( mdn ) begin
                        rom_addr <= 17'd0;
                        pre_cs   <= 0;
                        dec_rst  <= 1;
                        //pre_cs   <= 1;
                        //st       <= SND_CNT; // Reads the ROM header
                        st       <= IDLE;
                    end
                    else st <= IDLE;
                end
                DONE: begin
                    st <= DONE; // stay here forever
                    flush <= 1;
                end
                // Check the chip signature
                SIGN: if (cen_ctl) begin
                    if( rom_ok ) begin
                        if( !mdn ) begin
                            pulse_cs <= 1;
                            st <= READADR;
                            rom_addr[0] <= 1;
                        end else begin
                            if( rom_data != sign[sign_addr] ) begin
                                // signok <= 0;
                                st <= IDLE;
                                `ifdef SIMULATION
                                $display("Wrong ROM assigned to jt7759");
                                $finish;
                                `endif
                            end
                            else begin
                                if( &sign_addr ) begin
                                    // signok <= 1;
                                    st<=IDLE;
                                end
                                rom_addr<= next_rom;
                            end
                        end
                    end
                end
                IDLE: begin
                    flush <= 1;
                    if( wr_posedge && drqn ) begin
                        //if( din <= max_snd || !mdn ) begin
                            pre_cs   <= 1;
                            pulse_cs <= 1;
                            rom_addr <= { 7'd0, {1'd0, din} + 9'd2, 1'b1 };
                            if( !mdn ) begin
                                st <= SIGN;
                            end else
                                st <= READADR;
                        //end
                    end else begin
                        if( rom_ok ) pre_cs  <= 0;
                        dec_rst <= 1;
                    end
                end
                SND_CNT: begin
                    if( rom_ok ) begin
                        // max_snd <= rom_data;
                        rom_addr<= next_rom;
                        st      <= SIGN;
                    end
                end
                READADR: if(cen_ctl) begin
                    if( rom_ok ) begin
                        if( rom_addr[0] ) begin
                            rom_addr <= next_rom;
                            pulse_cs <= 1;
                            addr_latch[ 7:0] <= rom_data;
                        end else begin
                            addr_latch[15:8] <= addr_latch[7:0];
                            addr_latch[ 7:0] <= rom_data;
                            st               <= LOAD;
                            if( mdn ) begin
                                pre_cs <= 0;
                            end else begin
                                pre_cs <= 1;
                                pulse_cs <= 1;
                            end
                        end
                    end
                end
                LOAD: if(cen_ctl) begin
                    if( mdn || rom_ok ) begin
                        rom_addr <= { addr_latch, 1'b1 };
                        headerok <= 0;
                        st       <= READCMD;
                        pre_cs   <= 1;
                        pulse_cs <= 1;
                        rep_cnt  <= ~4'd0;
                        if ( mdn ) flush <= 1;
                    end
                end
                READCMD: if(cen_ctl) begin
                    if( rom_ok ) begin
                        rom_addr <= next_rom;
                        pre_cs   <= 1;
                        pulse_cs <= 1;
                        if( ~&rep_cnt ) begin
                            rep_cnt  <= rep_cnt-1'd1;
                        end

                        if(rom_data!=0)
                            headerok <= 1;
                        case( rom_data[7:6] )
                            2'd0: begin // Silence
                                `JT7759_SILENCE
                                mute_cnt <= {rom_data[5:0],{MTB{1'b0}}};
                                if( rom_data==0 && headerok) begin
                                    st <= DONE;
                                    dec_rst <= 1;
                                    `JT7759_DONE
                                end else begin
                                    st <= MUTED;
                                end
                                pre_cs  <= 0;
                            end
                            2'd1: begin // 256 nibbles
                                data_cnt  <= 9'hff;
                                divby     <= rom_data[5:0];
                                st        <= PLAY;
                                `JT7759_PLAY
                            end
                            2'd2: begin // n nibbles
                                data_cnt[8] <= 0;
                                divby       <= rom_data[5:0];
                                st          <= GETN;
                                `JT7759_PLAY_LONG
                            end
                            2'd3: begin // repeat loop
                                rep_cnt   <= {1'b0, rom_data[2:0]};
                                // rep_latch <= next_rom;
                                `JT7759_REPEAT
                            end
                        endcase
                    end
                end
                GETN: begin
                    if( rom_ok ) begin
                        rom_addr <= next_rom;
                        pre_cs   <= 1;
                        pulse_cs <= 1;
                        data_cnt <= {1'b0, rom_data};
                        st       <= PLAY;
                    end
                end
                MUTED: if( cen_ctl ) begin
                    if(cen_dec) dec_rst<= 1;
                    if( mute_cnt != 0 ) begin
                        mute_cnt <= mute_cnt-1'd1;
                    end else begin
                        st     <= READCMD;
                        pre_cs <= 1;
                        pulse_cs <= 1;
                    end
                end
                PLAY: begin
                    if(cen_dec) begin
                        if( pre_cs ) begin
                            if( rom_ok ) begin
                                { dec_din, next } <= rom_data;
                                dec_rst           <= 0;
                                pre_cs            <= 0;
                                data_cnt          <= data_cnt-1'd1;
                                if( data_cnt==0 ) begin
                                    pre_cs   <= 1;
                                    pulse_cs <= 1;
                                    st       <= READCMD;
                                end
                            end
                        end else begin
                            dec_din  <= next;
                            rom_addr <= next_rom;
                            pre_cs   <= 1;
                            pulse_cs <= 1;
                            data_cnt <= data_cnt-1'd1;
                            if( data_cnt==0 ) begin
                                st <= READCMD;
                            end
                        end
                    end
                end
            endcase
        end // pulse_cen
    end
end


endmodule


/*  This file is part of JT7759.
    JT7759 program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public Licen_ctlse as published by
    the Free Software Foundation, either version 3 of the Licen_ctlse, or
    (at your option) any later version.

    JT7759 program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public Licen_ctlse for more details.

    You should have received a copy of the GNU General Public Licen_ctlse
    along with JT7759.  If not, see <http://www.gnu.org/licen_ctlses/>.

    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 21-7-2021 */

module jt7759_data(
    input             rst,
    input             clk,
    input             cen_ctl,
    input             mdn,
    // Control interface
    input             ctrl_flush,
    input             ctrl_cs,
    input             ctrl_busyn,
    input      [16:0] ctrl_addr,
    output reg [ 7:0] ctrl_din,
    output reg        ctrl_ok,
    // ROM interface
    output            rom_cs,
    output reg [16:0] rom_addr,
    input      [ 7:0] rom_data,
    input             rom_ok,
    // Passive interface
    input             cs,
    input             wrn,  // for slave mode only
    input      [ 7:0] din,
    output reg        drqn
);

reg  [7:0] fifo[0:3];
reg  [3:0] fifo_ok;
reg        drqn_l, ctrl_cs_l;
reg  [1:0] rd_addr, wr_addr;
reg        readin, readout, readin_l;
reg  [4:0] drqn_cnt;

wire       good    = mdn ? rom_ok & ~drqn_l & ~drqn : (cs&~wrn);
wire [7:0] din_mux = mdn ? rom_data : din;

assign rom_cs  = mdn && !drqn;

always @(posedge clk, posedge rst) begin
    if( rst ) begin
        drqn_cnt <= 0;
    end else begin
        // Minimum time between DRQn pulses
        if( readin || good )
            drqn_cnt <= ~'d0;
        else if( drqn_cnt!=0 && cen_ctl) drqn_cnt <= drqn_cnt-1'd1;
    end
end

always @(posedge clk, posedge rst) begin
    if( rst ) begin
        rom_addr <= 0;
        drqn     <= 1;
        readin_l <= 0;
    end else begin
        readin_l <= readin;

        if( !ctrl_busyn ) begin
            if(!readin && readin_l)
                rom_addr <= rom_addr + 1'd1;
            if(fifo_ok==4'hf || (!readin && readin_l) ) begin
                drqn <= 1;
            end else if(fifo_ok!=4'hf && !readin && drqn_cnt==0 ) begin
                drqn <= 0;
            end
        end else begin
            drqn <= 1;
        end

        if( ctrl_flush )
            rom_addr <= ctrl_addr;
    end
end

always @(posedge clk, posedge rst) begin
    if( rst ) begin
        rd_addr   <= 0;
        ctrl_cs_l <= 0;
        readin    <= 0;
        readout   <= 0;
        ctrl_ok   <= 0;
        fifo_ok   <= 0;
        wr_addr   <= 0;
        drqn_l    <= 1;
    end else begin
        ctrl_cs_l <= ctrl_cs;
        drqn_l <= drqn;

        // read out
        if( ctrl_cs && !ctrl_cs_l ) begin
            readout <= 1;
            ctrl_ok <= 0;
        end
        if( readout && fifo_ok[rd_addr] ) begin
            ctrl_din <= fifo[ rd_addr ];
            ctrl_ok  <= 1;
            rd_addr  <= rd_addr + 1'd1;
            fifo_ok[ rd_addr ] <= 0;
            readout  <= 0;
        end
        if( !ctrl_cs ) begin
            readout <= 0;
            ctrl_ok <= 0;
        end

        // read in
        if( !drqn && drqn_l ) begin
            readin <= 1;
        end
        if( good && readin ) begin
            fifo[ wr_addr ] <= din_mux;
            fifo_ok[ wr_addr ] <= 1;
            wr_addr <= wr_addr + 1'd1;
            readin  <= 0;
            `ifdef JT7759_FIFO_DUMP
            $display("\tjt7759: read %X",din_mux);
            `endif
        end

        if( ctrl_busyn || ctrl_flush ) begin
            fifo_ok <= 0;
            rd_addr <= 0;
            wr_addr <= 0;
        end
    end
end

endmodule


/*  This file is part of JT7759.
    JT7759 program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT7759 program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT7759.  If not, see <http://www.gnu.org/licenses/>.

    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 5-7-2020 */

module jt7759_div(
    input            clk,
    input            cen,  // 640kHz
    input      [5:0] divby,
    output reg       cen_ctl,   // control = 8x faster than decoder
    output reg       cen_dec
);

reg [1:0] cnt4;
reg [5:0] decdiv, /*ctldiv,*/ divby_l;
wire      /*eoc_ctl,*/ eoc_dec, eoc_cnt; //  end of count

// assign eoc_ctl = ctldiv == { 1'b0, divby_l[5:1] };
assign eoc_dec = decdiv == divby_l;
assign eoc_cnt = &cnt4;

`ifdef SIMULATION
initial begin
    cnt4   = 2'd0;
    divby_l= 0;
    decdiv = 6'd3; // bad start numbers to show the auto allignment feature
    //ctldiv = 6'd7;
end
`endif

always @(posedge clk) if(cen) begin
    cnt4   <= cnt4+2'd1;
    if( eoc_cnt ) begin
        decdiv <= eoc_dec ? 6'd0 : (decdiv+1'd1);
        if( eoc_dec ) divby_l <= divby < 6'd9 ? 6'd9 : divby; // The divider is updated only at EOC
    end
    // ctldiv <= eoc_ctl || (eoc_dec && eoc_cnt) ? 6'd0 : (ctldiv+1'd1);
end

always @(posedge clk) begin
    cen_ctl <= cen; // && eoc_ctl;
    cen_dec <= cen && eoc_dec && eoc_cnt;
end

endmodule

