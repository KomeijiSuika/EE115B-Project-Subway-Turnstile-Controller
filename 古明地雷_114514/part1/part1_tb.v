`timescale 1ns/1ps

module part1_tb;
    reg clk;
    reg rst_n;
    reg card_valid;
    reg sensor_B;
    wire gate_open;
    wire led_green;
    wire led_red;

    part1 dut (
        .clk(clk),
        .rst_n(rst_n),
        .card_valid(card_valid),
        .sensor_B(sensor_B),
        .gate_open(gate_open),
        .led_green(led_green),
        .led_red(led_red)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("part1.vcd");
        $dumpvars(0, part1_tb);

        clk = 0;
        rst_n = 0;
        card_valid = 0;
        sensor_B = 0;

        $display("Part 1 simple simulation start");
        #20;
        rst_n = 1;

        #10;
        card_valid = 1;
        #10;
        card_valid = 0;

        #50;
        sensor_B = 1;
        #20;
        sensor_B = 0;

        #30;
        $display("Part 1 simple simulation finish");
        $finish;
    end
endmodule
