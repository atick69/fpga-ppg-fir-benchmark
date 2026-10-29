`timescale 1ns / 1ps

module variable_tap_fir_fixed_folded_5 #(
    parameter DATA_WIDTH  = 16,
    parameter COEFF_WIDTH = 16
)(
    input  wire                            clk,
    input  wire                            rst_n,
    input  wire signed [DATA_WIDTH-1:0]    data_in,
    output reg  signed [DATA_WIDTH-1:0]    data_out
);

    localparam MAX_TAPS = 5;
    localparam MID = (MAX_TAPS-1)/2; // 2

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

    reg signed [COEFF_WIDTH-1:0] cb5 [0:2];

        initial begin
        cb5[0] = 982; cb5[1] = 8055; cb5[2] = 15858;
        end

    wire signed [DATA_WIDTH:0] sym_sum [0:MID];

    genvar g;
    generate
        for (g = 0; g <= MID; g = g + 1) begin : g_pair
            wire signed [DATA_WIDTH-1:0] partner;
            if (g < 2) assign partner = shift_reg[4-g]; 
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
            accum = accum + (sym_sum[mac_j] * cb5[mac_j]);
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