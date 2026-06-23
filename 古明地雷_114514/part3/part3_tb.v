`timescale 1ns/1ps

module part3_tb;
    reg clk;
    reg rst_n;
    reg card_valid;
    reg sensor_A;
    reg sensor_B;
    wire gate_open;
    wire led_green;
    wire led_red;
    wire alarm;

    part3 dut (
        .clk(clk),
        .rst_n(rst_n),
        .card_valid(card_valid),
        .sensor_A(sensor_A),
        .sensor_B(sensor_B),
        .gate_open(gate_open),
        .led_green(led_green),
        .led_red(led_red),
        .alarm(alarm)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("part3.vcd");
        $dumpvars(0, part3_tb);

        clk = 0;
        rst_n = 0;
        card_valid = 0;
        sensor_A = 0;
        sensor_B = 0;

        $display("Part 3 simple simulation start");
        #20;
        rst_n = 1;

        #20;
        sensor_B = 1;
        #10;
        sensor_B = 0;

        #150;
        $display("Part 3 simple simulation finish");
        $finish;
    end
endmodule
