`timescale 1ns / 1ps

module variable_tap_fir_buildtime #(
    parameter DATA_WIDTH  = 16,
    parameter COEFF_WIDTH = 16,
    parameter MAX_TAPS    = 15
)(
    input  wire                            clk,
    input  wire                            rst_n,
    input  wire signed [DATA_WIDTH-1:0]    data_in,
    output reg  signed [DATA_WIDTH-1:0]    data_out
);

    reg signed [COEFF_WIDTH-1:0] coeff [0:MAX_TAPS-1];

    generate
    if (MAX_TAPS == 5) begin : g_c5
        initial begin
            coeff[0] = 982; coeff[1] = 8055; coeff[2] = 15858;
            coeff[3] = 8055; coeff[4] = 982;
        end
    end
    else if (MAX_TAPS == 15) begin : g_c15
        initial begin
            coeff[ 0] = -196; coeff[ 1] = -193; coeff[ 2] = 0;    coeff[ 3] = 867;
            coeff[ 4] = 2625; coeff[ 5] = 4923; coeff[ 6] = 6907; coeff[ 7] = 7694;
            // Mirror the coefficients for the second half:
            coeff[ 8] = 6907; coeff[ 9] = 4923; coeff[10] = 2625; coeff[11] = 867;
            coeff[12] = 0;    coeff[13] = -193; coeff[14] = -196;
        end
    end
    else if (MAX_TAPS == 31) begin : g_c31
        initial begin
            coeff[ 0] = 0;     coeff[ 1] = 20;    coeff[ 2] = 24;    coeff[ 3] = -15;
            coeff[ 4] = -140;  coeff[ 5] = -377;  coeff[ 6] = -697;  coeff[ 7] = -991;
            coeff[ 8] = -1083; coeff[ 9] = -791;  coeff[10] = 0;     coeff[11] = 1263;
            coeff[12] = 2804;  coeff[13] = 4300;  coeff[14] = 5389;  coeff[15] = 5787;
            // Mirror the coefficients for the second half:
            coeff[16] = 5389;  coeff[17] = 4300;  coeff[18] = 2804;  coeff[19] = 1263;
            coeff[20] = 0;     coeff[21] = -791;  coeff[22] = -1083; coeff[23] = -991;
            coeff[24] = -697;  coeff[25] = -377;  coeff[26] = -140;  coeff[27] = -15;
            coeff[28] = 24;    coeff[29] = 20;    coeff[30] = 0;
        end
    end
    else begin : g_cbad
        initial $error("MAX_TAPS must be 5, 15, or 31");
    end
    endgenerate

    reg signed [DATA_WIDTH-1:0] shift_reg [0:MAX_TAPS-1];
    integer i;

    // Shift register for input samples
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            for (i = 0; i < MAX_TAPS; i = i + 1) shift_reg[i] <= 0;
        end else begin
            shift_reg[0] <= data_in;
            for (i = 1; i < MAX_TAPS; i = i + 1)
                shift_reg[i] <= shift_reg[i-1];
        end
    end

    localparam ACC_W = DATA_WIDTH + COEFF_WIDTH + $clog2(MAX_TAPS) + 1;
    localparam FRAC = COEFF_WIDTH - 1;
    reg signed [ACC_W-1:0] accum;
    integer k; 

    // MAC Accumulation
    always @(*) begin
        accum = 0;
        for (k = 0; k < MAX_TAPS; k = k + 1)
            accum = accum + (shift_reg[k] * coeff[k]);
    end

    // Rounding and Scaling
    wire signed [ACC_W-1:0] scaled = (accum + (1 <<< (FRAC-1))) >>> FRAC;
    
    localparam signed [ACC_W-1:0] MAX_V =  (1 <<< (DATA_WIDTH-1)) - 1;
    localparam signed [ACC_W-1:0] MIN_V = -(1 <<< (DATA_WIDTH-1));

    // Output with Saturation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)              data_out <= 0;
        else if (scaled > MAX_V) data_out <= MAX_V[DATA_WIDTH-1:0]; 
        else if (scaled < MIN_V) data_out <= MIN_V[DATA_WIDTH-1:0];
        else                     data_out <= scaled[DATA_WIDTH-1:0];
    end

endmodule