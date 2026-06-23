module part1 (
    input clk,
    input rst_n,
    input card_valid,
    input sensor_B,
    output reg gate_open,
    output reg led_green,
    output reg led_red
);

    localparam LOCKED   = 1'b0;
    localparam UNLOCKED = 1'b1;

    reg state;
    reg next_state;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= LOCKED;
        end else begin
            state <= next_state;
        end
    end

    always @(*) begin
        case (state)
            LOCKED: begin
                if (card_valid) begin
                    next_state = UNLOCKED;
                end else begin
                    next_state = LOCKED;
                end
            end
            UNLOCKED: begin
                if (sensor_B) begin
                    next_state = LOCKED;
                end else begin
                    next_state = UNLOCKED;
                end
            end
            default: begin
                next_state = LOCKED;
            end
        endcase
    end

    always @(*) begin
        gate_open = 1'b0;
        led_green = 1'b0;
        led_red   = 1'b1;

        case (state)
            LOCKED: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
            end
            UNLOCKED: begin
                gate_open = 1'b1;
                led_green = 1'b1;
                led_red   = 1'b0;
            end
            default: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
            end
        endcase
    end

endmodule
