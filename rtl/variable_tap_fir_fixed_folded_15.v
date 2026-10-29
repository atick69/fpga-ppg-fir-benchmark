`timescale 1ns / 1ps

module variable_tap_fir_fixed_folded_15 #(
    parameter DATA_WIDTH  = 16,
    parameter COEFF_WIDTH = 16
)(
    input  wire                            clk,
    input  wire                            rst_n,
    input  wire signed [DATA_WIDTH-1:0]    data_in,
    output reg  signed [DATA_WIDTH-1:0]    data_out
);

    localparam MAX_TAPS = 15;
    localparam MID = (MAX_TAPS-1)/2; // 7

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

    reg signed [COEFF_WIDTH-1:0] cb15 [0:7];

        initial begin
        cb15[0] = -196; cb15[1] = -193; cb15[2] = 0; cb15[3] = 867;
        cb15[4] = 2625; cb15[5] = 4923; cb15[6] = 6907; cb15[7] = 7694;
        end

    wire signed [DATA_WIDTH:0] sym_sum [0:MID];

    genvar g;
    generate
        for (g = 0; g <= MID; g = g + 1) begin : g_pair
            wire signed [DATA_WIDTH-1:0] partner;
            if (g < 7) assign partner = shift_reg[14-g]; 
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
            accum = accum + (sym_sum[mac_j] * cb15[mac_j]);
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