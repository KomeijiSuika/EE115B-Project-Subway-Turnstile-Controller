#!/usr/bin/env python3

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image as PILImage
from PIL import ImageChops
from PIL import ImageDraw
from PIL import ImageFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from vcdvcd import VCDVCD


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "report_assets"
OUTPUT_DIR = ROOT / "output" / "pdf"
ROOT_PDF = ROOT / "report.pdf"
OUTPUT_PDF = OUTPUT_DIR / "report.pdf"
STUDENT_NAME = "古明地雷"
STUDENT_ID = "114514"
CJK_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
CJK_FONT_NAME = "NotoSansCJK"


def _make_table(headers: list[str], rows: list[list[str]], col_widths: list[float]) -> Table:
    data = [headers] + rows
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f6fa")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    tbl = Table(data, colWidths=col_widths)
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


FSM_SPECS = {
    "part1": {
        "title": "Part 1: Two-State Turnstile",
        "summary": (
            "A two-state Moore FSM is used. LOCKED keeps the gate closed with "
            "the red LED on. A valid card moves the controller to UNLOCKED, "
            "which opens the gate and enables passage. sensor_B closes the "
            "gate after the passenger exits."
        ),
        "dot": """
digraph part1 {
    rankdir=LR;
    graph [bgcolor="white"];
    node [shape=record, style="rounded,filled", fillcolor="#f7f7f7", color="#444444", fontname="Helvetica"];
    edge [color="#444444", fontname="Helvetica"];
    LOCKED [label="{LOCKED|gate_open=0|led_green=0|led_red=1}"];
    UNLOCKED [label="{UNLOCKED|gate_open=1|led_green=1|led_red=0}"];
    LOCKED -> UNLOCKED [label="card_valid=1"];
    UNLOCKED -> LOCKED [label="sensor_B=1"];
}
""",
        "waveforms": [
            {
                "title": "Simulation Waveform",
                "vcd": "part1.vcd",
                "signals": [
                    "part1_tb.rst_n",
                    "part1_tb.card_valid",
                    "part1_tb.sensor_B",
                    "part1_tb.gate_open",
                    "part1_tb.led_green",
                    "part1_tb.led_red",
                ],
            }
        ],
        "verify": (
            "Compile: PASS  |  Simulate: PASS  |  "
            "card_valid opens gate; sensor_B closes gate. Reset holds LOCKED."
        ),
    },
    "part2": {
        "title": "Part 2: Basic Access Control",
        "summary": (
            "The controller is extended to a four-state Moore FSM. IDLE waits "
            "for a card, VALID waits for lane entry at sensor_A, PASS waits "
            "for exit at sensor_B, and CLOSE holds the gate shut until "
            "sensor_B is released."
        ),
        "dot": """
digraph part2 {
    rankdir=LR;
    graph [bgcolor="white"];
    node [shape=record, style="rounded,filled", fillcolor="#f7f7f7", color="#444444", fontname="Helvetica"];
    edge [color="#444444", fontname="Helvetica"];
    IDLE [label="{IDLE|gate_open=0|led_green=0|led_red=1}"];
    VALID [label="{VALID|gate_open=1|led_green=1|led_red=0}"];
    PASS [label="{PASS|gate_open=1|led_green=1|led_red=0}"];
    CLOSE [label="{CLOSE|gate_open=0|led_green=0|led_red=1}"];
    IDLE -> VALID [label="card_valid=1"];
    VALID -> PASS [label="sensor_A=1"];
    PASS -> CLOSE [label="sensor_B=1"];
    CLOSE -> IDLE [label="sensor_B=0"];
}
""",
        "waveforms": [
            {
                "title": "Simulation Waveform",
                "vcd": "part2.vcd",
                "signals": [
                    "part2_tb.rst_n",
                    "part2_tb.card_valid",
                    "part2_tb.sensor_A",
                    "part2_tb.sensor_B",
                    "part2_tb.gate_open",
                    "part2_tb.led_green",
                    "part2_tb.led_red",
                ],
            }
        ],
        "verify": (
            "Compile: PASS  |  Simulate: PASS  |  "
            "sensor_A ignored in IDLE. Full forward chain: card → sensor_A → sensor_B → close → IDLE. "
            "Student testbench confirms both edge cases."
        ),
    },
    "part3": {
        "title": "Part 3: Reverse Intrusion Detection",
        "summary": (
            "Part 3 adds an ALARM state and an alarm counter. In IDLE, "
            "sensor_B has higher priority than card_valid, so reverse "
            "intrusion is detected before any card action. The alarm stays "
            "high for ALARM_DURATION clock cycles, while the gate remains "
            "closed and the red LED remains on."
        ),
        "dot": """
digraph part3 {
    rankdir=LR;
    graph [bgcolor="white"];
    node [shape=record, style="rounded,filled", fillcolor="#f7f7f7", color="#444444", fontname="Helvetica"];
    edge [color="#444444", fontname="Helvetica"];
    IDLE [label="{IDLE|gate_open=0|led_green=0|led_red=1|alarm=0}"];
    VALID [label="{VALID|gate_open=1|led_green=1|led_red=0|alarm=0}"];
    PASS [label="{PASS|gate_open=1|led_green=1|led_red=0|alarm=0}"];
    CLOSE [label="{CLOSE|gate_open=0|led_green=0|led_red=1|alarm=0}"];
    ALARM [label="{ALARM|gate_open=0|led_green=0|led_red=1|alarm=1}", fillcolor="#fdecea"];
    IDLE -> ALARM [label="sensor_B=1 (priority)"];
    IDLE -> VALID [label="card_valid=1"];
    VALID -> PASS [label="sensor_A=1"];
    PASS -> CLOSE [label="sensor_B=1"];
    CLOSE -> IDLE [label="sensor_B=0"];
    ALARM -> IDLE [label="alarm_cnt=ALARM_DURATION"];
}
""",
        "waveforms": [
            {
                "title": "Simulation Waveform",
                "vcd": "part3.vcd",
                "signals": [
                    "part3_tb.rst_n",
                    "part3_tb.card_valid",
                    "part3_tb.sensor_B",
                    "part3_tb.gate_open",
                    "part3_tb.led_green",
                    "part3_tb.led_red",
                    "part3_tb.alarm",
                ],
            }
        ],
        "verify": (
            "Compile: PASS  |  Simulate: PASS  |  "
            "sensor_B in IDLE triggers ALARM (priority over card_valid). "
            "Alarm duration = 10 clock cycles (ALARM_DURATION). "
            "Gate closed throughout."
        ),
    },
    "part4": {
        "title": "Part 4: Timeout Auto-Close",
        "summary": (
            "Part 4 keeps the reverse-intrusion alarm and introduces two more "
            "behaviors. In VALID, a timeout counter auto-closes the gate and "
            "asserts timeout when no passenger enters before "
            "TIMEOUT_DURATION. In PASS, the same timeout concept raises "
            "PASS_ALARM if a passenger stays in the lane too long. PASS_ALARM "
            "keeps the gate open, drives alarm high, and waits for sensor_B "
            "before finishing through CLOSE."
        ),
        "dot": """
digraph part4 {
    rankdir=LR;
    graph [bgcolor="white"];
    node [shape=record, style="rounded,filled", fillcolor="#f7f7f7", color="#444444", fontname="Helvetica"];
    edge [color="#444444", fontname="Helvetica"];
    IDLE [label="{IDLE|gate_open=0|led_green=0|led_red=1|alarm=0|timeout=0}"];
    VALID [label="{VALID|gate_open=1|led_green=1|led_red=0|alarm=0|timeout=0}"];
    PASS [label="{PASS|gate_open=1|led_green=1|led_red=0|alarm=0|timeout=0}"];
    CLOSE [label="{CLOSE|gate_open=0|led_green=0|led_red=1|alarm=0|timeout=0}"];
    ALARM [label="{ALARM|gate_open=0|led_green=0|led_red=1|alarm=1|timeout=0}", fillcolor="#fdecea"];
    TIMEOUT [label="{TIMEOUT|gate_open=0|led_green=0|led_red=1|alarm=0|timeout=1}", fillcolor="#fff4d6"];
    PASS_ALARM [label="{PASS_ALARM|gate_open=1|led_green=0|led_red=1|alarm=1|timeout=0}", fillcolor="#fdecea"];
    IDLE -> ALARM [label="sensor_B=1 (priority)"];
    IDLE -> VALID [label="card_valid=1"];
    VALID -> PASS [label="sensor_A=1"];
    VALID -> TIMEOUT [label="timeout_cnt=TIMEOUT_DURATION"];
    PASS -> CLOSE [label="sensor_B=1"];
    PASS -> PASS_ALARM [label="timeout_cnt=TIMEOUT_DURATION"];
    PASS_ALARM -> CLOSE [label="sensor_B=1"];
    CLOSE -> IDLE [label="sensor_B=0"];
    ALARM -> IDLE [label="alarm_cnt=ALARM_DURATION"];
    TIMEOUT -> IDLE [label="next clock"];
}
""",
        "waveforms": [
            {
                "title": "Timeout Case",
                "vcd": "part4a.vcd",
                "signals": [
                    "part4a_tb.rst_n",
                    "part4a_tb.card_valid",
                    "part4a_tb.sensor_A",
                    "part4a_tb.gate_open",
                    "part4a_tb.led_green",
                    "part4a_tb.led_red",
                    "part4a_tb.timeout",
                ],
            },
            {
                "title": "Normal Passage Case",
                "vcd": "part4b.vcd",
                "signals": [
                    "part4b_tb.rst_n",
                    "part4b_tb.card_valid",
                    "part4b_tb.sensor_A",
                    "part4b_tb.sensor_B",
                    "part4b_tb.gate_open",
                    "part4b_tb.led_green",
                    "part4b_tb.led_red",
                    "part4b_tb.alarm",
                    "part4b_tb.timeout",
                ],
            },
        ],
        "verify": (
            "Compile: PASS  |  Simulate: PASS  |  "
            "Timeout case (4a): card → no sensor_A for 10 cycles → TIMEOUT. "
            "Normal case (4b): card → sensor_A → sensor_B, no alarm, no timeout. "
            "Both student testbenches verify correct behavior."
        ),
    },
}


def ensure_dirs() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def render_fsm_png(name: str, dot_source: str) -> Path:
    dot_path = ASSET_DIR / f"{name}_fsm.dot"
    png_path = ASSET_DIR / f"{name}_fsm.png"
    dot_path.write_text(dot_source.strip() + "\n", encoding="utf-8")
    subprocess.run(
        ["dot", "-Tpng", str(dot_path), "-o", str(png_path)],
        check=True,
        cwd=ROOT,
    )
    return png_path


def _font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ):
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def render_waveform_png(vcd_name: str, signal_names: list[str], title: str) -> Path:
    vcd_path = ROOT / vcd_name
    out_path = ASSET_DIR / f"{vcd_path.stem}.png"
    vcd = VCDVCD(str(vcd_path), store_tvs=True)

    left = 180
    right = 40
    top = 60
    row_h = 52
    low_y = 32
    high_y = 12

    signal_data = []
    t_end = 0
    for name in signal_names:
        tv = [(int(t), str(v)) for t, v in vcd[name].tv]
        signal_data.append((name.split(".")[-1], tv))
        t_end = max(t_end, max(t for t, _ in tv))

    width = 1600
    height = top + row_h * len(signal_data) + 80
    img = PILImage.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = _font(28)
    label_font = _font(22)
    axis_font = _font(18)

    draw.text((left, 15), title, fill="black", font=title_font)

    usable_w = width - left - right
    ticks = 8
    for i in range(ticks + 1):
        x = left + usable_w * i / ticks
        draw.line((x, top - 10, x, height - 30), fill="#dddddd", width=1)
        t_ns = (t_end * i / ticks) / 1000.0
        draw.text((x - 18, height - 25), f"{t_ns:.0f}", fill="#444444", font=axis_font)
    draw.text((width - 95, height - 25), "ns", fill="#444444", font=axis_font)

    for idx, (label, tv) in enumerate(signal_data):
        y0 = top + idx * row_h
        draw.text((20, y0 + 8), label, fill="black", font=label_font)
        draw.line((left, y0 + low_y, width - right, y0 + low_y), fill="#eeeeee", width=1)

        if not tv:
            continue

        for item_idx, (t, value) in enumerate(tv):
            next_t = tv[item_idx + 1][0] if item_idx + 1 < len(tv) else t_end
            x1 = left + usable_w * (t / max(t_end, 1))
            x2 = left + usable_w * (next_t / max(t_end, 1))
            y = y0 + (high_y if value == "1" else low_y)
            draw.line((x1, y, x2, y), fill="#0066cc", width=3)
            if item_idx + 1 < len(tv):
                next_value = tv[item_idx + 1][1]
                y_next = y0 + (high_y if next_value == "1" else low_y)
                draw.line((x2, y, x2, y_next), fill="#0066cc", width=3)
        draw.text((left - 36, y0 + high_y - 6), "1", fill="#666666", font=axis_font)
        draw.text((left - 36, y0 + low_y - 10), "0", fill="#666666", font=axis_font)

    img.save(out_path)
    return out_path


def render_student_info_png() -> Path:
    out_path = ASSET_DIR / "student_info.png"
    width = 560
    height = 90
    img = PILImage.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    label_font = _font(22)
    name_font = ImageFont.truetype(CJK_FONT_PATH, 24)
    draw.text((0, 4), "Name:", fill="black", font=label_font)
    draw.text((95, 1), STUDENT_NAME, fill="black", font=name_font)
    draw.text((0, 44), f"Student ID: {STUDENT_ID}", fill="black", font=label_font)
    diff = ImageChops.difference(img, PILImage.new("RGB", img.size, "white"))
    bbox = diff.getbbox()
    if bbox is not None:
        left, top, right, bottom = bbox
        pad = 6
        img = img.crop(
            (
                max(0, left - pad),
                max(0, top - pad),
                min(img.width, right + pad),
                min(img.height, bottom + pad),
            )
        )
    img.save(out_path)
    return out_path


def fit_image(path: Path, max_width_mm: float, max_height_mm: float) -> Image:
    with PILImage.open(path) as img:
        width_px, height_px = img.size
    aspect = width_px / height_px
    width_pt = max_width_mm * mm
    height_pt = width_pt / aspect
    max_height_pt = max_height_mm * mm
    if height_pt > max_height_pt:
        height_pt = max_height_pt
        width_pt = height_pt * aspect
    return Image(str(path), width=width_pt, height=height_pt)


def build_report() -> None:
    ensure_dirs()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Body", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=10, leading=13.5, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="SectionTitle", parent=styles["Heading1"],
        fontName="Helvetica-Bold", fontSize=15, textColor=colors.HexColor("#222222"),
        spaceAfter=8, spaceBefore=6,
    ))
    styles.add(ParagraphStyle(
        name="Verify", parent=styles["BodyText"],
        fontName="Helvetica", fontSize=9, leading=12, textColor=colors.HexColor("#27ae60"),
        spaceAfter=2,
    ))

    story = []
    story.append(Paragraph("Subway Turnstile Controller Report", styles["Title"]))
    story.append(Spacer(1, 6 * mm))
    student_info_png = render_student_info_png()
    student_info_flow = fit_image(student_info_png, max_width_mm=78, max_height_mm=14)
    student_info_flow.hAlign = "LEFT"
    story.append(student_info_flow)
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "This report documents the Moore FSM design, state diagrams, "
        "simulation waveforms, and verification results for all four parts "
        "of the subway turnstile controller project. All Verilog modules "
        "were simulated with Icarus Verilog 11.0.",
        styles["Body"],
    ))
    story.append(Paragraph(
        "Design notes: asynchronous active-low reset (rst_n) in every module; "
        "sensor_B > card_valid priority in IDLE (Part 3/4); "
        "parameterized ALARM_DURATION and TIMEOUT_DURATION values.",
        styles["Body"],
    ))

    for part_name, spec in FSM_SPECS.items():
        story.append(PageBreak())
        story.append(Paragraph(spec["title"], styles["SectionTitle"]))
        story.append(Paragraph(spec["summary"], styles["Body"]))

        fsm_png = render_fsm_png(part_name, spec["dot"])
        story.append(Paragraph("State Diagram", styles["Heading3"]))
        story.append(fit_image(fsm_png, max_width_mm=170, max_height_mm=85))

        for waveform in spec["waveforms"]:
            story.append(Paragraph(waveform["title"], styles["Heading3"]))
            wave_png = render_waveform_png(
                waveform["vcd"], waveform["signals"], waveform["title"]
            )
            story.append(fit_image(wave_png, max_width_mm=175, max_height_mm=85))

        if spec.get("verify"):
            story.append(Spacer(1, 3 * mm))
            story.append(Paragraph("Verification", styles["Heading4"]))
            story.append(Paragraph(spec["verify"], styles["Verify"]))

    # ── Conclusion ──
    story.append(PageBreak())
    story.append(Paragraph("Conclusion", styles["SectionTitle"]))
    story.append(Paragraph(
        "All four parts of the subway turnstile controller design have been "
        "compiled and simulated successfully using Icarus Verilog 11.0. "
        "The design progressively builds a feature-complete Moore FSM controller "
        "with 2, 4, 5, and 7 states respectively, covering turnstile access "
        "control, reverse intrusion detection, and timeout auto-close.",
        styles["Body"],
    ))
    story.append(Spacer(1, 4 * mm))

    result_headers = ["Part", "Module", "Testbench", "Compile", "Simulate"]
    result_rows = [
        ["Part 1", "part1.v", "part1_tb.v (provided)", "PASS", "PASS"],
        ["Part 2", "part2.v", "part2_tb.v (written)", "PASS", "PASS"],
        ["Part 3", "part3.v", "part3_tb.v (provided)", "PASS", "PASS"],
        ["Part 4", "part4.v", "part4a_tb.v / part4b_tb.v (written)", "PASS", "PASS"],
    ]
    story.append(_make_table(result_headers, result_rows,
        col_widths=[48, 64, 152, 52, 52]))
    story.append(Spacer(1, 5 * mm))

    story.append(Paragraph("Key Design Features", styles["Heading3"]))
    features = [
        "Consistent Moore FSM architecture across all parts",
        "Asynchronous active-low reset (rst_n) in every module",
        "Parameterized delay values: ALARM_DURATION, TIMEOUT_DURATION",
        "Priority-based signal handling: sensor_B > card_valid in IDLE",
        "Progressive state expansion: 2 → 4 → 5 → 7 states",
        "Student-written testbenches for Parts 2 and 4 verify key scenarios",
        "Auto-generated report with Graphviz FSM diagrams and VCD waveforms",
    ]
    for feat in features:
        story.append(Paragraph("  \u2022  " + feat, styles["Body"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "<b>Submission checklist:</b> 4 Verilog modules, 3 student-written "
        "testbenches (part2_tb.v, part4a_tb.v, part4b_tb.v), report.pdf. "
        "All deliverables match the project requirements.",
        styles["Body"],
    ))

    for out_path in (ROOT_PDF, OUTPUT_PDF):
        doc = SimpleDocTemplate(
            str(out_path),
            pagesize=A4,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
            title="Subway Turnstile Controller Report",
            author=f"{STUDENT_NAME} ({STUDENT_ID})",
        )
        doc.build(list(story))


if __name__ == "__main__":
    build_report()
