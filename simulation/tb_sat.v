`timescale 1ns / 1ps
module tb_sat();
    reg clk; 
    reg rst_n; 
    reg signed [15:0] data_in;
    wire signed [15:0] data_out;
    reg [15:0] mem [0:1023]; 
    integer i;

    variable_tap_fir_fixed_folded uut (
        .clk(clk), .rst_n(rst_n), .data_in(data_in), .data_out(data_out)
    );

    initial begin clk = 0; forever #5 clk = ~clk; end

    initial begin
        $readmemh("sat_input_vectors.hex", mem);
        rst_n = 0; data_in = 0; #20; rst_n = 1;
        for (i = 0; i < 1000; i = i + 1) begin
            data_in = mem[i]; #10;
        end
        $finish;
    end

    always @(posedge clk) if (rst_n) $display("In: %d | Out: %d", data_in, data_out);
endmodule