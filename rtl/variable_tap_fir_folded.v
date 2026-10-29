`timescale 1ns / 1ps

module variable_tap_fir_folded #(
    parameter DATA_WIDTH  = 16,
    parameter COEFF_WIDTH = 16
)(
    input  wire                            clk,
    input  wire                            rst_n,
    input  wire [4:0]                      tap_sel,
    input  wire signed [DATA_WIDTH-1:0]    data_in,
    output reg  signed [DATA_WIDTH-1:0]    data_out
);

    localparam MAX_TAPS = 31;
    localparam N5  = 5;
    localparam N15 = 15;
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

    reg signed [COEFF_WIDTH-1:0] cb5  [0:15];      
    reg signed [COEFF_WIDTH-1:0] cb15 [0:15];      
    reg signed [COEFF_WIDTH-1:0] cb31 [0:15];     
    integer init_j;

        initial begin
        for (init_j = 0; init_j < 16; init_j = init_j + 1) begin
            cb5[init_j] = 0; cb15[init_j] = 0; cb31[init_j] = 0;
        end

        // --- PPG 5-Tap ---
        cb5[0] = 982; cb5[1] = 8055; cb5[2] = 15858;

        // --- PPG 15-Tap ---
        cb15[0] = -196; cb15[1] = -193; cb15[2] = 0; cb15[3] = 867;
        cb15[4] = 2625; cb15[5] = 4923; cb15[6] = 6907; cb15[7] = 7694;

        // --- PPG 31-Tap ---
        cb31[0] = 0; cb31[1] = 20; cb31[2] = 24; cb31[3] = -15;
        cb31[4] = -140; cb31[5] = -377; cb31[6] = -697; cb31[7] = -991;
        cb31[8] = -1083; cb31[9] = -791; cb31[10] = 0; cb31[11] = 1263;
        cb31[12] = 2804; cb31[13] = 4300; cb31[14] = 5389; cb31[15] = 5787;
    end
    wire signed [DATA_WIDTH:0] sym_sum [0:MID];
    wire signed [COEFF_WIDTH-1:0] csel [0:MID];
    
    genvar g;
    generate
        for (g = 0; g <= MID; g = g + 1) begin : g_pair
            wire signed [DATA_WIDTH-1:0] p5, p15, p31;
            wire signed [DATA_WIDTH-1:0] partner;
            
            if (g < 2) assign p5 = shift_reg[4-g]; else assign p5 = 0;
            if (g < 7) assign p15 = shift_reg[14-g]; else assign p15 = 0;
            if (g < 15) assign p31 = shift_reg[30-g]; else assign p31 = 0;

            assign partner = (tap_sel <= N5) ? p5 : (tap_sel <= N15) ? p15 : p31;
            assign sym_sum[g] = shift_reg[g] + partner;
            
            assign csel[g] = (tap_sel <= N5)  ? cb5[g] :
                             (tap_sel <= N15) ? cb15[g] : cb31[g];
        end
    endgenerate

    localparam ACC_W = DATA_WIDTH + COEFF_WIDTH + $clog2(MAX_TAPS) + 1;
    localparam FRAC = COEFF_WIDTH - 1; // FIXED: Generic parameter
    reg signed [ACC_W-1:0] accum;
    integer mac_j;
    
    always @(*) begin
        accum = 0;
        for (mac_j = 0; mac_j <= MID; mac_j = mac_j + 1)
            accum = accum + (sym_sum[mac_j] * csel[mac_j]);
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