`timescale 1ns / 1ps

module variable_tap_fir_fixed_folded #(
    parameter DATA_WIDTH  = 16,
    parameter COEFF_WIDTH = 16
)(
    input  wire                            clk,
    input  wire                            rst_n,
    input  wire signed [DATA_WIDTH-1:0]    data_in,
    output reg  signed [DATA_WIDTH-1:0]    data_out
);

    localparam MAX_TAPS = 31;
    localparam MID = (MAX_TAPS-1)/2; // 15

    reg signed [DATA_WIDTH-1:0] shift_reg [0:MAX_TAPS-1];
    integer i;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < MAX_TAPS; i = i + 1) shift_reg[i] <= 0;
        end else begin
            shift_reg[0] <= data_in;
            for (i = 1; i < MAX_TAPS; i = i + 1)
                shift_reg[i] <= shift_reg[i-1];
        end
    end

    // Fixed 31-tap folded coefficients
    reg signed [COEFF_WIDTH-1:0] cb31 [0:15];

        initial begin
        cb31[0] = 0; cb31[1] = 20; cb31[2] = 24; cb31[3] = -15;
        cb31[4] = -140; cb31[5] = -377; cb31[6] = -697; cb31[7] = -991;
        cb31[8] = -1083; cb31[9] = -791; cb31[10] = 0; cb31[11] = 1263;
        cb31[12] = 2804; cb31[13] = 4300; cb31[14] = 5389; cb31[15] = 5787;
        end
    wire signed [DATA_WIDTH:0] sym_sum [0:MID];

    genvar g;
    generate
        for (g = 0; g <= MID; g = g + 1) begin : g_pair
            wire signed [DATA_WIDTH-1:0] partner;
            if (g < 15) assign partner = shift_reg[30-g]; 
            else assign partner = 0;
            assign sym_sum[g] = shift_reg[g] + partner;
        end
    endgenerate

    localparam ACC_W = DATA_WIDTH + COEFF_WIDTH + $clog2(MAX_TAPS) + 1;
    localparam FRAC = COEFF_WIDTH - 1;
    reg signed [ACC_W-1:0] accum;
    integer mac_j;
    
    always @(*) begin
        accum = 0;
        for (mac_j = 0; mac_j <= MID; mac_j = mac_j + 1)
            accum = accum + (sym_sum[mac_j] * cb31[mac_j]);
    end

    wire signed [ACC_W-1:0] scaled = (accum + (1 <<< (FRAC-1))) >>> FRAC;

    localparam signed [ACC_W-1:0] MAX_V =  (1 <<< (DATA_WIDTH-1)) - 1;
    localparam signed [ACC_W-1:0] MIN_V = -(1 <<< (DATA_WIDTH-1));

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)              data_out <= 0;
        else if (scaled > MAX_V) data_out <= MAX_V[DATA_WIDTH-1:0];
        else if (scaled < MIN_V) data_out <= MIN_V[DATA_WIDTH-1:0];
        else                     data_out <= scaled[DATA_WIDTH-1:0];
    end
endmodule