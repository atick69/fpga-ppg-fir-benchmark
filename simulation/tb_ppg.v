`timescale 1ns / 1ps

module tb_ppg();

    reg clk;
    reg rst_n;
    reg signed [15:0] data_in;
    wire signed [15:0] data_out;

    // Memory array to hold the 550 PPG samples
    reg [15:0] ppg_memory [0:1023]; 
    integer i;

    // Instantiate your 31-tap Folded Module
    variable_tap_fir_fixed_folded uut (
        .clk(clk),
        .rst_n(rst_n),
        .data_in(data_in),
        .data_out(data_out)
    );

    // Clock generation (100 MHz -> 10ns period)
    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    // Test sequence
    initial begin
        // Load the Python-generated PPG data
        $readmemh("ppg_input_vectors.hex", ppg_memory);
        
        rst_n = 0; 
        data_in = 0;
        #20; 
        rst_n = 1;
        
        $display("Starting PPG Simulation...");
        
        // Feed the 550 PPG samples one by one
        for (i = 0; i < 550; i = i + 1) begin
            data_in = ppg_memory[i];
            #10; // Wait for one clock cycle
        end
        
        $display("Finished feeding PPG data!");
        $finish;
    end
    
    // Print output to console to compare with Python later
    always @(posedge clk) begin
        if (rst_n && data_in !== 16'hxxxx) begin
            $display("Sample %0d | In: %0d | Out: %0d", i, data_in, data_out);
        end
    end
endmodule