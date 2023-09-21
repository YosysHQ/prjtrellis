/*  This file is part of JT49.

    JT49 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT49 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT49.  If not, see <http://www.gnu.org/licenses/>.

    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 10-Nov-2018

    Based on sqmusic, by the same author

    */

module jt49 ( // note that input ports are not multiplexed
    input            rst_n,
    input            clk,    // signal on positive edge
    input            clk_en /* synthesis direct_enable = 1 */,
    input  [3:0]     addr,
    input            cs_n,
    input            wr_n,  // write
    input  [7:0]     din,
    input            sel, // if sel is low, the clock is divided by 2
    output reg [7:0] dout,
    output reg [9:0] sound,  // combined channel output
    //output reg [7:0] A,      // linearised channel output
    //output reg [7:0] B,
    //output reg [7:0] C,
    output           sample

    //input      [7:0] IOA_in,
    //output     [7:0] IOA_out,
    //output           IOA_oe,

    //input      [7:0] IOB_in,
    //output     [7:0] IOB_out,
    //output           IOB_oe
);

reg [7:0] A;      // linearised channel output
reg [7:0] B;
reg [7:0] C;
parameter [1:0] COMP=2'b00;
parameter       CLKDIV=3;
wire [1:0] comp = COMP;

reg  [7:0] regarray[15:0];
wire [7:0] port_A, port_B;

wire [4:0] envelope;
wire bitA, bitB, bitC;
wire noise;
reg Amix, Bmix, Cmix;

wire cen16, cen256;

//assign IOA_out = regarray[14];
//assign IOB_out = regarray[15];
//assign port_A  = IOA_in;
//assign port_B  = IOB_in;
//assign IOA_oe  = regarray[7][6];
//assign IOB_oe  = regarray[7][7];
assign sample  = cen16;

jt49_cen #(.CLKDIV(CLKDIV)) u_cen(
    .clk    ( clk     ),
    .rst_n  ( rst_n   ),
    .cen    ( clk_en  ),
    .sel    ( sel     ),
    .cen16  ( cen16   ),
    .cen256 ( cen256  )
);

// internal modules operate at clk/16
jt49_div #(12) u_chA(
    .clk        ( clk           ),
    .rst_n      ( rst_n         ),
    .cen        ( cen16         ),
    .period     ( {regarray[1][3:0], regarray[0][7:0] } ),
    .div        ( bitA          )
);

jt49_div #(12) u_chB(
    .clk        ( clk           ),
    .rst_n      ( rst_n         ),
    .cen        ( cen16         ),
    .period     ( {regarray[3][3:0], regarray[2][7:0] } ),
    .div        ( bitB          )
);

jt49_div #(12) u_chC(
    .clk        ( clk           ),
    .rst_n      ( rst_n         ),
    .cen        ( cen16         ),
    .period     ( {regarray[5][3:0], regarray[4][7:0] } ),
    .div        ( bitC          )
);

jt49_noise u_ng(
    .clk    ( clk               ),
    .cen    ( cen16             ),
    .rst_n  ( rst_n             ),
    .period ( regarray[6][4:0]  ),
    .noise  ( noise             )
);

// envelope generator
wire eg_step;
wire [15:0] eg_period   = {regarray[4'hc],regarray[4'hb]};
wire        null_period = eg_period == 16'h0;

jt49_div #(16) u_envdiv(
    .clk    ( clk               ),
    .cen    ( cen256            ),
    .rst_n  ( rst_n             ),
    .period ( eg_period         ),
    .div    ( eg_step           )
);

reg eg_restart;

jt49_eg u_env(
    .clk        ( clk               ),
    .cen        ( cen256            ),
    .step       ( eg_step           ),
    .rst_n      ( rst_n             ),
    .restart    ( eg_restart        ),
    .null_period( null_period       ),
    .ctrl       ( regarray[4'hD][3:0] ),
    .env        ( envelope          )
);

reg  [4:0] logA, logB, logC, log;
wire [7:0] lin;

jt49_exp u_exp(
    .clk    ( clk  ),
    .comp   ( comp ),
    .din    ( log  ),
    .dout   ( lin  )
);

wire [4:0] volA = { regarray[ 8][3:0], regarray[ 8][3] };
wire [4:0] volB = { regarray[ 9][3:0], regarray[ 9][3] };
wire [4:0] volC = { regarray[10][3:0], regarray[10][3] };
wire use_envA = regarray[ 8][4];
wire use_envB = regarray[ 9][4];
wire use_envC = regarray[10][4];
wire use_noA  = regarray[ 7][3];
wire use_noB  = regarray[ 7][4];
wire use_noC  = regarray[ 7][5];

reg [3:0] acc_st;

always @(posedge clk) if( clk_en ) begin
    Amix <= (noise|use_noA) & (bitA|regarray[7][0]);
    Bmix <= (noise|use_noB) & (bitB|regarray[7][1]);
    Cmix <= (noise|use_noC) & (bitC|regarray[7][2]);

    logA <= !Amix ? 5'd0 : (use_envA ? envelope : volA );
    logB <= !Bmix ? 5'd0 : (use_envB ? envelope : volB );
    logC <= !Cmix ? 5'd0 : (use_envC ? envelope : volC );
end

reg [9:0] acc;

always @(posedge clk, negedge rst_n) begin
    if( !rst_n ) begin
        acc_st <= 4'b1;
        acc    <= 10'd0;
        A      <= 8'd0;
        B      <= 8'd0;
        C      <= 8'd0;
        sound  <= 10'd0;
    end else if(clk_en) begin
        acc_st <= { acc_st[2:0], acc_st[3] };
        acc <= acc + {2'b0,lin};
        case( acc_st )
            4'b0001: begin
                log   <= logA;
                acc   <= 10'd0;
                sound <= acc;
            end
            4'b0010: begin
                A   <= lin;
                log <= logB;
            end
            4'b0100: begin
                B   <= lin;
                log <= logC;
            end
            4'b1000: begin // last sum
                C   <= lin;
            end
            default:;
        endcase
    end
end

reg  [7:0] read_mask;

always @(*)
    case(addr)
        4'h0,4'h2,4'h4,4'h7,4'hb,4'hc,4'he,4'hf:
            read_mask = 8'hff;
        4'h1,4'h3,4'h5,4'hd:
            read_mask = 8'h0f;
        4'h6,4'h8,4'h9,4'ha:
            read_mask = 8'h1f;
    endcase // addr

// register array
wire write;
reg  last_write;
wire wr_edge = write & ~last_write;

assign write = !wr_n && !cs_n;

always @(posedge clk, negedge rst_n) begin
    if( !rst_n ) begin
        dout       <= 8'd0;
        last_write <= 0;
        eg_restart <= 0;
        regarray[0]<=8'd0; regarray[4]<=8'd0; regarray[ 8]<=8'd0; regarray[12]<=8'd0;
        regarray[1]<=8'd0; regarray[5]<=8'd0; regarray[ 9]<=8'd0; regarray[13]<=8'd0;
        regarray[2]<=8'd0; regarray[6]<=8'd0; regarray[10]<=8'd0; regarray[14]<=8'd0;
        regarray[3]<=8'd0; regarray[7]<=8'd0; regarray[11]<=8'd0; regarray[15]<=8'd0;
    end else begin
        last_write  <= write;
        // Data read
        case( addr )
            4'he: dout <= port_A;
            4'hf: dout <= port_B;
            default: dout <= regarray[ addr ] & read_mask;
        endcase
        // Data write
        if( write ) begin
            regarray[addr] <= din;
            if ( addr == 4'hD && wr_edge ) eg_restart <= 1;
        end else begin
            eg_restart <= 0;
        end
    end
end

endmodule


/*  This file is part of JT49.

    JT49 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT49 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT49.  If not, see <http://www.gnu.org/licenses/>.
    
    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 10-Nov-2018
    
    Based on sqmusic, by the same author
    
    */

module jt49_cen(
    input       clk,
    input       rst_n,
    input       cen,    // base clock enable signal
    input       sel,    // when low, divide by 2 once more
    output  reg cen16,
    output  reg cen256
);

reg [9:0] cencnt;
parameter CLKDIV = 3; // use 3 for standalone JT49 or 2
localparam eg = CLKDIV; //8;

wire toggle16 = sel ? ~|cencnt[CLKDIV-1:0] : ~|cencnt[CLKDIV:0];
wire toggle256= sel ? ~|cencnt[eg-2:0]     : ~|cencnt[eg-1:0];


always @(posedge clk, negedge rst_n) begin
    if(!rst_n)
        cencnt <= 10'd0;
    else begin 
        if(cen) cencnt <= cencnt+10'd1;
    end
end

always @(posedge clk) begin
    cen16  <= cen & toggle16;
    cen256 <= cen & toggle256;
end


endmodule // jt49_cen

/*  This file is part of JT49.

    JT49 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT49 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT49.  If not, see <http://www.gnu.org/licenses/>.
    
    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 10-Nov-2018
    
    Based on sqmusic, by the same author
    
    */


module jt49_div #(parameter W=12 )(   
    (* direct_enable *) input cen,
    input           clk, // this is the divided down clock from the core
    input           rst_n,
    input [W-1:0]  period,
    output reg      div
);

reg [W-1:0]count;

wire [W-1:0] one = { {W-1{1'b0}}, 1'b1};

always @(posedge clk, negedge rst_n ) begin
  if( !rst_n) begin
    count <= one;
    div   <= 1'b0;
  end
  else if(cen) begin
    if( count>=period ) begin
        count <= one;
        div   <= ~div;
    end
    else
        /*if( period!={W{1'b0}} )*/ count <=  count + one ;
  end
end

endmodule


/*  This file is part of JT49.

    JT49 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT49 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT49.  If not, see <http://www.gnu.org/licenses/>.
    
    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 10-Nov-2018
    
    Based on sqmusic, by the same author
    
    */

module jt49_eg(
  (* direct_enable *) input cen,
  input           clk, // this is the divided down clock from the core
  input           step,
  input           null_period,
  input           rst_n,
  input           restart,
  input [3:0]     ctrl,
  output reg [4:0]env
);

reg inv, stop;
reg [4:0] gain;

wire CONT = ctrl[3];
wire ATT  = ctrl[2];
wire ALT  = ctrl[1];
wire HOLD = ctrl[0];

wire will_hold = !CONT || HOLD;

always @(posedge clk)
    if( cen ) env <= inv ? ~gain : gain;

reg  last_step;
wire step_edge = (step && !last_step) || null_period;
wire will_invert = (!CONT&&ATT) || (CONT&&ALT);
reg  rst_latch, rst_clr;

always @(posedge clk) begin
    if( restart ) rst_latch <= 1;
    else if(rst_clr ) rst_latch <= 0;
end

always @( posedge clk, negedge rst_n )
    if( !rst_n) begin
        gain    <= 5'h1F;
        inv     <= 0;
        stop    <= 0;
        rst_clr <= 0;
    end
    else if( cen ) begin
        last_step <= step;
        if( rst_latch ) begin
            gain    <= 5'h1F;
            inv     <= ATT;
            stop    <= 1'b0;
            rst_clr <= 1;
        end
        else begin
            rst_clr <= 0;
            if (step_edge && !stop) begin
                if( gain==5'h00 ) begin
                    if( will_hold )
                        stop <= 1'b1;
                    else
                        gain <= gain-5'b1;
                    if( will_invert ) inv<=~inv;
                end
                else gain <= gain-5'b1;
            end
        end
    end

endmodule


/*  This file is part of JT49.

    JT49 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT49 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT49.  If not, see <http://www.gnu.org/licenses/>.
    
    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 10-Nov-2018
    
    Based on sqmusic, by the same author
    
    */


// Compression vs dynamic range
// 0 -> 43.6dB
// 1 -> 29.1
// 2 -> 21.8
// 3 -> 13.4

module jt49_exp(
    input            clk,
    input      [1:0] comp,  // compression
    input      [4:0] din,
    output reg [7:0] dout 
);

reg [7:0] lut[0:127];

always @(posedge clk)
    dout <= lut[ {comp,din} ];

initial begin
    lut[0] = 8'd0;
    lut[1] = 8'd1;
    lut[2] = 8'd1;
    lut[3] = 8'd1;
    lut[4] = 8'd2;
    lut[5] = 8'd2;
    lut[6] = 8'd3;
    lut[7] = 8'd3;
    lut[8] = 8'd4;
    lut[9] = 8'd5;
    lut[10] = 8'd6;
    lut[11] = 8'd7;
    lut[12] = 8'd9;
    lut[13] = 8'd11;
    lut[14] = 8'd13;
    lut[15] = 8'd15;
    lut[16] = 8'd18;
    lut[17] = 8'd22;
    lut[18] = 8'd26;
    lut[19] = 8'd31;
    lut[20] = 8'd37;
    lut[21] = 8'd45;
    lut[22] = 8'd53;
    lut[23] = 8'd63;
    lut[24] = 8'd75;
    lut[25] = 8'd90;
    lut[26] = 8'd107;
    lut[27] = 8'd127;
    lut[28] = 8'd151;
    lut[29] = 8'd180;
    lut[30] = 8'd214;
    lut[31] = 8'd255;
    lut[32] = 8'd0;
    lut[33] = 8'd7;
    lut[34] = 8'd8;
    lut[35] = 8'd10;
    lut[36] = 8'd11;
    lut[37] = 8'd12;
    lut[38] = 8'd14;
    lut[39] = 8'd15;
    lut[40] = 8'd17;
    lut[41] = 8'd20;
    lut[42] = 8'd22;
    lut[43] = 8'd25;
    lut[44] = 8'd28;
    lut[45] = 8'd31;
    lut[46] = 8'd35;
    lut[47] = 8'd40;
    lut[48] = 8'd45;
    lut[49] = 8'd50;
    lut[50] = 8'd56;
    lut[51] = 8'd63;
    lut[52] = 8'd71;
    lut[53] = 8'd80;
    lut[54] = 8'd90;
    lut[55] = 8'd101;
    lut[56] = 8'd113;
    lut[57] = 8'd127;
    lut[58] = 8'd143;
    lut[59] = 8'd160;
    lut[60] = 8'd180;
    lut[61] = 8'd202;
    lut[62] = 8'd227;
    lut[63] = 8'd255;
    lut[64] = 8'd0;
    lut[65] = 8'd18;
    lut[66] = 8'd20;
    lut[67] = 8'd22;
    lut[68] = 8'd24;
    lut[69] = 8'd26;
    lut[70] = 8'd29;
    lut[71] = 8'd31;
    lut[72] = 8'd34;
    lut[73] = 8'd37;
    lut[74] = 8'd41;
    lut[75] = 8'd45;
    lut[76] = 8'd49;
    lut[77] = 8'd53;
    lut[78] = 8'd58;
    lut[79] = 8'd63;
    lut[80] = 8'd69;
    lut[81] = 8'd75;
    lut[82] = 8'd82;
    lut[83] = 8'd90;
    lut[84] = 8'd98;
    lut[85] = 8'd107;
    lut[86] = 8'd116;
    lut[87] = 8'd127;
    lut[88] = 8'd139;
    lut[89] = 8'd151;
    lut[90] = 8'd165;
    lut[91] = 8'd180;
    lut[92] = 8'd196;
    lut[93] = 8'd214;
    lut[94] = 8'd233;
    lut[95] = 8'd255;
    lut[96] = 8'd0;
    lut[97] = 8'd51;
    lut[98] = 8'd54;
    lut[99] = 8'd57;
    lut[100] = 8'd60;
    lut[101] = 8'd63;
    lut[102] = 8'd67;
    lut[103] = 8'd70;
    lut[104] = 8'd74;
    lut[105] = 8'd78;
    lut[106] = 8'd83;
    lut[107] = 8'd87;
    lut[108] = 8'd92;
    lut[109] = 8'd97;
    lut[110] = 8'd103;
    lut[111] = 8'd108;
    lut[112] = 8'd114;
    lut[113] = 8'd120;
    lut[114] = 8'd127;
    lut[115] = 8'd134;
    lut[116] = 8'd141;
    lut[117] = 8'd149;
    lut[118] = 8'd157;
    lut[119] = 8'd166;
    lut[120] = 8'd175;
    lut[121] = 8'd185;
    lut[122] = 8'd195;
    lut[123] = 8'd206;
    lut[124] = 8'd217;
    lut[125] = 8'd229;
    lut[126] = 8'd241;
    lut[127] = 8'd255;

end
endmodule


/*  This file is part of JT49.

    JT49 is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    JT49 is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with JT49.  If not, see <http://www.gnu.org/licenses/>.
    
    Author: Jose Tejada Gomez. Twitter: @topapate
    Version: 1.0
    Date: 10-Nov-2018
    
    Based on sqmusic, by the same author
    
    */


module jt49_noise(
  (* direct_enable *) input cen,
    input       clk,
    input       rst_n,
    input [4:0] period,
    output reg  noise
);

reg [5:0]count;
reg [16:0]poly17;
wire poly17_zero = poly17==17'b0;
wire noise_en;
reg last_en;

wire noise_up = noise_en && !last_en;

always @(posedge clk ) if(cen) begin
    noise <= ~poly17[0];
end

always @( posedge clk, negedge rst_n )
  if( !rst_n ) 
    poly17 <= 17'd0;
  else if( cen ) begin
    last_en <= noise_en;
    if( noise_up )
        poly17 <= { poly17[0] ^ poly17[3] ^ poly17_zero, poly17[16:1] };
  end

jt49_div #(5) u_div( 
  .clk    ( clk       ), 
  .cen    ( cen       ),
  .rst_n  ( rst_n     ), 
  .period ( period    ), 
  .div    ( noise_en  ) 
);

endmodule
