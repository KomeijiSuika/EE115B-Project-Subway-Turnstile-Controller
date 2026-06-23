module part2 (
    input clk,
    input rst_n,
    input card_valid,
    input sensor_A,
    input sensor_B,
    output reg gate_open,
    output reg led_green,
    output reg led_red
);

    localparam IDLE  = 2'd0;
    localparam VALID = 2'd1;
    localparam PASS  = 2'd2;
    localparam CLOSE = 2'd3;

    reg [1:0] state;
    reg [1:0] next_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end

    always @(*) begin
        case (state)
            IDLE: begin
                if (card_valid) begin
                    next_state = VALID;
                end else begin
                    next_state = IDLE;
                end
            end
            VALID: begin
                if (sensor_A) begin
                    next_state = PASS;
                end else begin
                    next_state = VALID;
                end
            end
            PASS: begin
                if (sensor_B) begin
                    next_state = CLOSE;
                end else begin
                    next_state = PASS;
                end
            end
            CLOSE: begin
                if (!sensor_B) begin
                    next_state = IDLE;
                end else begin
                    next_state = CLOSE;
                end
            end
            default: begin
                next_state = IDLE;
            end
        endcase
    end

    always @(*) begin
        gate_open = 1'b0;
        led_green = 1'b0;
        led_red   = 1'b1;

        case (state)
            IDLE: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
            end
            VALID: begin
                gate_open = 1'b1;
                led_green = 1'b1;
                led_red   = 1'b0;
            end
            PASS: begin
                gate_open = 1'b1;
                led_green = 1'b1;
                led_red   = 1'b0;
            end
            CLOSE: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
            end
            default: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
            end
        endcase
    end

endmodule
