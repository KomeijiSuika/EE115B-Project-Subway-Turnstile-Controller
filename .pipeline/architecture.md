# Architecture Baseline — Subway Turnstile Controller

## Project Overview

数字电路课程设计项目：基于 Moore 型有限状态机（FSM）的地铁闸机控制器。使用 Verilog HDL 实现，由 Icarus Verilog 仿真验证，Graphviz 绘制 FSM 状态图，Python (ReportLab) 自动生成实验报告。

- **作者**: 古明地雷 (114514)
- **语言**: Verilog (HDL)
- **课程**: 数字电路 (EE115B), 上海科技大学
- **状态**: 全部 4 个部分已完成

## Tech Stack

| 类别 | 工具 | 版本 | 用途 |
|---|---|---|---|
| HDL | Verilog (Icarus Verilog) | 11.0 | 硬件描述与仿真编译 |
| 仿真运行时 | vvp | 11.0 | 执行编译后的仿真 |
| 波形查看 | GTKWave | — | 可视化 VCD 波形 |
| FSM 图 | Graphviz (dot) | 12.2.1 | 状态转移图渲染 |
| 报告生成 | Python 3 + ReportLab | 3.13.9 | 自动生成 PDF 报告 |
| VCD 解析 | vcdvcd | — | Python VCD 解析库 |
| 图像处理 | Pillow (PIL) | — | 波形 PNG 渲染 |

## Directory Structure

```
project/
├── problem.pdf                    # 项目需求说明书（9 页）
├── report.pdf                     # 自动生成的完整报告
├── scripts/
│   └── generate_report.py         # Python 报告生成脚本（444 行）
├── report_assets/                 # FSM DOT 文件 + 波形/状态图 PNG
├── output/pdf/                    # 报告输出副本
├── tmp/                           # 临时渲染图片
├── part{1,2,3,4,4a,4b}.vcd       # 仿真波形 dump 文件
└── 古明地雷_114514/             # 提交目录
    ├── report.pdf
    ├── part1/
    │   ├── part1.v                # 2 状态 FSM（LOCKED/UNLOCKED）
    │   └── part1_tb.v             # 测试台
    ├── part2/
    │   ├── part2.v                # 4 状态 FSM（IDLE/VALID/PASS/CLOSE）
    │   └── part2_tb.v             # 学生编写的测试台
    ├── part3/
    │   ├── part3.v                # 5 状态 FSM（+ALARM，逆向入侵检测）
    │   └── part3_tb.v             # 测试台
    └── part4/
        ├── part4.v                # 7 状态 FSM（+TIMEOUT+PASS_ALARM）
        ├── part4a_tb.v            # 超时自动关闭测试
        └── part4b_tb.v            # 正常通行测试
```

## Module Summary

### part1.v — Two-State Turnstile (71 lines)
- **接口**: clk, rst_n, card_valid, sensor_B → gate_open, led_green, led_red
- **FSM**: LOCKED ⇄ UNLOCKED
- **行为**: 刷卡 → 开闸；sensor_B 触发 → 关闸

### part2.v — Basic Access Control (98 lines)
- **接口**: 新增 sensor_A
- **FSM**: IDLE → VALID → PASS → CLOSE → IDLE
- **行为**: 刷卡 → 进入 VALID(开闸)；sensor_A → PASS(通过中)；sensor_B → CLOSE(关门)；sensor_B 释放 → IDLE

### part3.v — Reverse Intrusion Detection (135 lines)
- **接口**: 新增 alarm 输出
- **参数**: ALARM_DURATION = 10
- **FSM**: 新增 ALARM 状态（sensor_B 在 IDLE 中优先级高于 card_valid）
- **行为**: IDLE 中 sensor_B=1 → ALARM（保持 ALARM_DURATION 个周期）

### part4.v — Timeout Auto-Close (187 lines)
- **接口**: 新增 timeout 输出
- **参数**: ALARM_DURATION = 10, TIMEOUT_DURATION = 10
- **FSM**: 新增 TIMEOUT、PASS_ALARM 状态（7 状态 FSM）
- **行为**:
  - VALID 中超时 → TIMEOUT（gate 关闭，timeout=1）→ 下一周期回 IDLE
  - PASS 中超时 → PASS_ALARM（gate 保持打开，alarm=1）→ 等待 sensor_B → CLOSE

## Signal Interface (最终)

| 信号 | 方向 | 位宽 | 描述 |
|---|---|---|---|
| clk | Input | 1 | 系统时钟 (100 MHz) |
| rst_n | Input | 1 | 异步复位，低有效 |
| card_valid | Input | 1 | 有效刷卡脉冲 (1 周期) |
| sensor_A | Input | 1 | 前端红外传感器 |
| sensor_B | Input | 1 | 后端红外传感器 |
| gate_open | Output | 1 | 闸机控制 (1=开) |
| led_green | Output | 1 | 绿色通行指示灯 |
| led_red | Output | 1 | 红色禁行指示灯 |
| alarm | Output | 1 | 逆向入侵报警 (Part 3+, Part 4 PASS_ALARM) |
| timeout | Output | 1 | 超时指示 (Part 4+) |

## Build & Test

无传统构建系统。通过 Icarus Verilog 直接编译和仿真：

```bash
# 编译
iverilog -o part1_tb.vvp part1_tb.v part1.v

# 运行仿真 → 生成 .vcd 波形文件
vvp part1_tb.vvp

# 查看波形
gtkwave part1.vcd
```

## Data Flow

```
Verilog 源码 (.v)
  │
  ├── iverilog 编译 → .vvp (仿真可执行)
  │     │
  │     └── vvp 仿真 → .vcd (波形 dump)
  │           │
  │           ├── GTKWave → 交互式波形查看
  │           │
  │           └── Python (vcdvcd) → 波形 PNG
  │                 │
  │                 └── Python (ReportLab) → report.pdf
  │
  └── Graphviz (dot) → FSM 状态图 PNG
        │
        └── Python (ReportLab) → report.pdf
```

## Grading Score

| 部分 | 内容 | 分值 |
|---|---|---|
| Part 1 | part1.v | 20 |
| Part 2 | part2.v + part2_tb.v | 20 |
| Part 3 | part3.v | 20 |
| Part 4 | part4.v + part4a_tb.v + part4b_tb.v | 20 |
| 报告 | report.pdf | 20 |
| **总计** | | **100** |
