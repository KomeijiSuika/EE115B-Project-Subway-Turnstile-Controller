module part4 (
    input clk,
    input rst_n,
    input card_valid,
    input sensor_A,
    input sensor_B,
    output reg gate_open,
    output reg led_green,
    output reg led_red,
    output reg alarm,
    output reg timeout
);
    parameter ALARM_DURATION = 10;
    parameter TIMEOUT_DURATION = 10;

    localparam IDLE       = 3'd0;
    localparam VALID      = 3'd1;
    localparam PASS       = 3'd2;
    localparam CLOSE      = 3'd3;
    localparam ALARM      = 3'd4;
    localparam TIMEOUT    = 3'd5;
    localparam PASS_ALARM = 3'd6;

    reg [2:0] state;
    reg [2:0] next_state;
    reg [31:0] alarm_cnt;
    reg [31:0] timeout_cnt;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
        end else begin
            state <= next_state;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            alarm_cnt <= 32'd0;
        end else if (state != ALARM) begin
            alarm_cnt <= 32'd0;
        end else if (next_state == ALARM) begin
            alarm_cnt <= alarm_cnt + 32'd1;
        end else begin
            alarm_cnt <= 32'd0;
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            timeout_cnt <= 32'd0;
        end else if ((state != VALID) && (state != PASS)) begin
            timeout_cnt <= 32'd0;
        end else if (next_state == state) begin
            timeout_cnt <= timeout_cnt + 32'd1;
        end else begin
            timeout_cnt <= 32'd0;
        end
    end

    always @(*) begin
        case (state)
            IDLE: begin
                if (sensor_B) begin
                    next_state = ALARM;
                end else if (card_valid) begin
                    next_state = VALID;
                end else begin
                    next_state = IDLE;
                end
            end
            VALID: begin
                if (sensor_A) begin
                    next_state = PASS;
                end else if (timeout_cnt == (TIMEOUT_DURATION - 1)) begin
                    next_state = TIMEOUT;
                end else begin
                    next_state = VALID;
                end
            end
            PASS: begin
                if (sensor_B) begin
                    next_state = CLOSE;
                end else if (timeout_cnt == (TIMEOUT_DURATION - 1)) begin
                    next_state = PASS_ALARM;
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
            ALARM: begin
                if (alarm_cnt == (ALARM_DURATION - 1)) begin
                    next_state = IDLE;
                end else begin
                    next_state = ALARM;
                end
            end
            TIMEOUT: begin
                next_state = IDLE;
            end
            PASS_ALARM: begin
                if (sensor_B) begin
                    next_state = CLOSE;
                end else begin
                    next_state = PASS_ALARM;
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
        alarm     = 1'b0;
        timeout   = 1'b0;

        case (state)
            IDLE: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
                alarm     = 1'b0;
                timeout   = 1'b0;
            end
            VALID: begin
                gate_open = 1'b1;
                led_green = 1'b1;
                led_red   = 1'b0;
                alarm     = 1'b0;
                timeout   = 1'b0;
            end
            PASS: begin
                gate_open = 1'b1;
                led_green = 1'b1;
                led_red   = 1'b0;
                alarm     = 1'b0;
                timeout   = 1'b0;
            end
            CLOSE: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
                alarm     = 1'b0;
                timeout   = 1'b0;
            end
            ALARM: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
                alarm     = 1'b1;
                timeout   = 1'b0;
            end
            TIMEOUT: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
                alarm     = 1'b0;
                timeout   = 1'b1;
            end
            PASS_ALARM: begin
                gate_open = 1'b1;
                led_green = 1'b0;
                led_red   = 1'b1;
                alarm     = 1'b1;
                timeout   = 1'b0;
            end
            default: begin
                gate_open = 1'b0;
                led_green = 1'b0;
                led_red   = 1'b1;
                alarm     = 1'b0;
                timeout   = 1'b0;
            end
        endcase
    end

endmodule
