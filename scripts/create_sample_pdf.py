#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生成用于全方位体现 baidu/Unlimited-OCR 三大核心能力的评测样本集：
1. unlimited_ocr_benchmark_3pages.pdf: 3页跨页论文与财报表格 PDF（测 Multi-page One-shot 连跑与 <page> 连续抄写）
2. dense_table_formula_scan.png: 单张高密度财报表格 + 数学公式 + 极小字号脚注扫描图（测 Gundam 640动态高清切片 vs Base 1024）
3. two_column_paper_scan.pdf: 2页双栏学术论文排版 PDF（测复杂双栏阅读顺序 Reading Order 与跨页段落衔接）
"""

from pathlib import Path
import fitz  # PyMuPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TESTSET_DIR = PROJECT_ROOT / "testset"


def create_all_samples():
    TESTSET_DIR.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # 样本 1: 3页跨页论文与评测报告 PDF (unlimited_ocr_benchmark_3pages.pdf)
    # =========================================================================
    out_pdf1 = TESTSET_DIR / "unlimited_ocr_benchmark_3pages.pdf"
    doc = fitz.open()

    # Page 1
    p1 = doc.new_page(width=595, height=842)
    p1.insert_text(
        (50, 62),
        "Unlimited OCR Works: One-shot Long-horizon Parsing",
        fontsize=17,
        fontname="helv",
    )
    p1.insert_text(
        (50, 88),
        "Baidu Vision & Document Intelligence Report (arXiv:2606.23050)",
        fontsize=10.5,
        fontname="helv",
        color=(0.35, 0.38, 0.45),
    )
    p1.draw_line((50, 102), (545, 102), color=(0.8, 0.82, 0.86), width=1)

    p1.insert_text((50, 130), "1. Core Motivation & Human Working Memory", fontsize=13, fontname="helv")
    p1.insert_textbox(
        fitz.Rect(50, 145, 545, 255),
        "End-to-end OCR models using an LLM decoder suffer from linear KV cache growth as output length "
        "increases. When parsing 20 to 40 pages of PDF documents, standard Multi-Head Attention (MHA) "
        "accumulates tens of thousands of text tokens, causing severe GPU memory pressure and latency spikes.\n\n"
        "Unlimited-OCR replaces all decoder attention layers with Reference Sliding Window Attention (R-SWA). "
        "Every generated token attends globally to all visual reference tokens (m = 256 per 1024x1024 page), "
        "while restricting causal text attention to a sliding window of n = 128 tokens.",
        fontsize=10.5,
        fontname="helv",
    )

    p1.insert_text((50, 278), "2. Mathematical Formulation of R-SWA", fontsize=13, fontname="helv")
    p1.draw_rect(fitz.Rect(50, 292, 545, 365), color=(0.75, 0.78, 0.85), fill=(0.96, 0.97, 0.99))
    p1.insert_textbox(
        fitz.Rect(62, 302, 535, 358),
        "KV_Cache(R-SWA) = L_prefix (visual + prompt) + n (sliding window = 128)\n"
        "Cache_Ratio(T)  = (L_m + n) / (L_m + T)  -->  Constant O(1) decode footprint as T >> n",
        fontsize=10,
        fontname="cour",
    )

    p1.insert_text((50, 395), "3. Architecture Specifications (DeepSeek-OCR MoE Baseline)", fontsize=13, fontname="helv")
    spec_rows = [
        ["Module / Component", "Configuration", "Engineering Benefit"],
        ["Vision Tower (DeepEncoder)", "SAM-ViT + CLIP-ViT (16x compression)", "1024x1024 page -> 256 static tokens"],
        ["Language Decoder (MoE)", "3.3B Total / 500M Active per token", "Runs on consumer GPUs & Mac M1 MLX"],
        ["Decoder Attention (R-SWA)", "Global Prefix + 128-token Window", "Flat FlashAttention-3 latency curve"],
        ["Max Context Window", "32,768 tokens (Base & Gundam modes)", "20-40 pages parsed in a single pass"],
    ]
    y_top = 412
    col_widths = [165, 175, 155]
    for r_idx, row in enumerate(spec_rows):
        row_h = 26
        x_cur = 50
        for c_idx, cell in enumerate(row):
            rect = fitz.Rect(x_cur, y_top, x_cur + col_widths[c_idx], y_top + row_h)
            fill = (0.91, 0.93, 0.98) if r_idx == 0 else (1.0, 1.0, 1.0)
            p1.draw_rect(rect, color=(0.75, 0.78, 0.84), fill=fill)
            p1.insert_textbox(rect + (6, 6, -4, -4), cell, fontsize=9.2, fontname="helv")
            x_cur += col_widths[c_idx]
        y_top += row_h

    # Page 2
    p2 = doc.new_page(width=595, height=842)
    p2.insert_text((50, 62), "4. OmniDocBench v1.5 / v1.6 Benchmark Comparison", fontsize=14, fontname="helv")
    p2.insert_textbox(
        fitz.Rect(50, 82, 545, 145),
        "Restricting the text sliding window to 128 tokens does not degrade accuracy. Instead, avoiding long-range "
        "text attention divergence improves table structure recognition (TEDS +5.96%) and reading order accuracy.",
        fontsize=10.5,
        fontname="helv",
    )

    bench_rows = [
        ["Model Name", "Active Params", "OmniDocBench v1.5", "OmniDocBench v1.6", "Throughput (512 conc.)"],
        ["DeepSeek-OCR (Baseline)", "500M (MoE)", "87.00%", "88.45%", "4,951 tokens/s"],
        ["DeepSeek-OCR 2", "500M (MoE)", "90.85%", "91.60%", "5,120 tokens/s"],
        ["baidu/Unlimited-OCR", "500M (MoE)", "93.00% (+6.0%)", "93.92% (SOTA)", "5,580 tokens/s (+12.7%)"],
    ]
    y_top = 160
    col_w2 = [135, 85, 95, 95, 85]
    for r_idx, row in enumerate(bench_rows):
        row_h = 28
        x_cur = 50
        for c_idx, cell in enumerate(row):
            rect = fitz.Rect(x_cur, y_top, x_cur + col_w2[c_idx], y_top + row_h)
            fill = (0.91, 0.93, 0.98) if r_idx == 0 else ((0.94, 0.99, 0.96) if r_idx == 3 else (1, 1, 1))
            p2.draw_rect(rect, color=(0.75, 0.78, 0.84), fill=fill)
            p2.insert_textbox(rect + (5, 6, -4, -4), cell, fontsize=8.8, fontname="helv")
            x_cur += col_w2[c_idx]
        y_top += row_h

    p2.insert_text((50, 305), "5. Long-Horizon Decoding Speed Stability (TPS vs Output Length)", fontsize=13, fontname="helv")
    p2.insert_textbox(
        fitz.Rect(50, 322, 545, 420),
        "At 256 generated tokens, Unlimited-OCR and DeepSeek-OCR run at nearly identical speeds. "
        "However, by 6,000 generated tokens, DeepSeek-OCR suffers a 35% throughput drop due to linear KV cache "
        "accumulation, while Unlimited-OCR maintains a constant generation speed across 20 to 40+ pages.",
        fontsize=10.5,
        fontname="helv",
    )

    # Page 3
    p3 = doc.new_page(width=595, height=842)
    p3.insert_text((50, 62), "6. Resolution Modes & Practical Engineering Caveats", fontsize=14, fontname="helv")
    p3.insert_textbox(
        fitz.Rect(50, 84, 545, 220),
        "1) Single-page Gundam Mode (base_size=1024, image_size=640, crop_mode=True):\n"
        "   Uses dynamic high-resolution cropping for dense single-page tables, formulas, and tiny footnotes.\n\n"
        "2) Multi-page Base Mode (image_size=1024, crop_mode=False):\n"
        "   Used for one-shot PDF parsing. Pages are rendered at 300 DPI via PyMuPDF and concatenated with <page>.\n\n"
        "3) N-gram Anti-Repetition Guard (no_repeat_ngram_size=35):\n"
        "   Must be enabled (window=128 for single page, 1024 for multi-page) to prevent loops on blank borders.",
        fontsize=10.5,
        fontname="helv",
    )

    p3.insert_text((50, 245), "7. Quick Local Deployment Commands", fontsize=13, fontname="helv")
    p3.draw_rect(fitz.Rect(50, 262, 545, 360), color=(0.75, 0.78, 0.85), fill=(0.96, 0.97, 0.99))
    p3.insert_textbox(
        fitz.Rect(62, 272, 535, 350),
        "# Option A: vLLM OpenAI-compatible Server\n"
        "vllm serve \"baidu/Unlimited-OCR\"\n\n"
        "# Option B: Apple Silicon Mac M1 Pro (MLX 4-bit / 8-bit)\n"
        "python -m mlx_vlm generate --model sahilchachra/unlimited-ocr-mxfp4-mlx --image page_0001.png",
        fontsize=9.2,
        fontname="cour",
    )

    doc.save(str(out_pdf1))
    doc.close()

    # =========================================================================
    # 样本 2: 单张高密度报表 + 公式 + 极小字号脚注扫描图 (dense_table_formula_scan.png)
    # 专门用于对比 Gundam (1024+640 切片) 与 Base (1024) 在极小字号脚注上的识别差异
    # =========================================================================
    out_img2 = TESTSET_DIR / "dense_table_formula_scan.png"
    doc2 = fitz.open()
    ps = doc2.new_page(width=640, height=860)
    # 模拟轻微扫描纸张底色
    ps.draw_rect(fitz.Rect(0, 0, 640, 860), color=None, fill=(0.985, 0.982, 0.972))
    ps.insert_text((42, 54), "Q3 Consolidated Financial & Token Efficiency Audit Sheet", fontsize=15.5, fontname="helv")
    ps.insert_text(
        (42, 76),
        "Scanned Archival Document #2026-BAIDU-OCR-09 | High-Density Table & Tiny Footnote Test",
        fontsize=9.5,
        fontname="helv",
        color=(0.4, 0.4, 0.45),
    )
    ps.draw_line((42, 88), (598, 88), color=(0.75, 0.75, 0.78), width=1)

    ps.insert_text((42, 114), "1. Attention Kernel & Memory Scaling Equation", fontsize=12.5, fontname="helv")
    ps.draw_rect(fitz.Rect(42, 126, 598, 198), color=(0.7, 0.74, 0.82), fill=(0.95, 0.96, 0.98))
    ps.insert_textbox(
        fitz.Rect(52, 134, 588, 192),
        "Attn(q_t, K_N(t), V_N(t)) = softmax( q_t * K_N(t)^T / sqrt(d_k) ) * V_N(t)\n"
        "where N(t) = P_prefix (1..L_m) U D_window (t - 128 .. t - 1)",
        fontsize=9.8,
        fontname="cour",
    )

    ps.insert_text((42, 224), "2. Multi-Page Long-Horizon Parsing Breakdown (2 to 40+ Pages)", fontsize=12.5, fontname="helv")
    dense_rows = [
        ["Page Bucket", "Visual Prefix (L_m)", "Decode Window (n)", "Edit Distance (lower better)", "Distinct-35 Score"],
        ["2 Pages PDF", "512 tokens", "128 tokens (Fixed)", "0.041", "99.4%"],
        ["5 Pages PDF", "1,280 tokens", "128 tokens (Fixed)", "0.052", "99.1%"],
        ["10 Pages PDF", "2,560 tokens", "128 tokens (Fixed)", "0.068", "98.7%"],
        ["20 Pages PDF", "5,120 tokens", "128 tokens (Fixed)", "0.084", "98.2%"],
        ["40+ Pages PDF", "10,240+ tokens", "128 tokens (Fixed)", "0.106 (< 0.11 target)", "97.1%"],
    ]
    y_t = 238
    cw = [95, 115, 110, 135, 101]
    for r_i, row in enumerate(dense_rows):
        rh = 26
        xc = 42
        for c_i, cell in enumerate(row):
            r = fitz.Rect(xc, y_t, xc + cw[c_i], y_t + rh)
            fill = (0.89, 0.92, 0.97) if r_i == 0 else (1.0, 1.0, 1.0)
            ps.draw_rect(r, color=(0.72, 0.75, 0.8), fill=fill)
            ps.insert_textbox(r + (5, 5, -3, -3), cell, fontsize=8.5, fontname="helv")
            xc += cw[c_i]
        y_t += rh

    ps.insert_text((42, 425), "3. Micro-Print Archival Footnotes (6pt Font — Needs Gundam 640 Crop Mode)", fontsize=11.5, fontname="helv")
    ps.draw_rect(fitz.Rect(42, 438, 598, 535), color=(0.82, 0.65, 0.35), fill=(0.99, 0.97, 0.92))
    ps.insert_textbox(
        fitz.Rect(50, 446, 590, 528),
        "[Footnote *1]: Under Multi-page Base mode (1024x1024 global downsampling without 640x640 dynamic cropping), "
        "ultra-small 6pt subscript serial numbers such as #SN-884920-B01 and tolerance +/-0.0035mm may blur slightly.\n"
        "[Footnote *2]: Enabling Gundam mode (base_size=1024, image_size=640, crop_mode=True) slices the page into "
        "4 local high-res tiles plus 1 global overview, recovering 100% of micro-print characters.",
        fontsize=8.0,
        fontname="helv",
    )

    pix = ps.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    pix.save(str(out_img2))
    doc2.close()

    # =========================================================================
    # 样本 3: 双栏学术排版 2页 PDF (two_column_paper_scan.pdf)
    # 专门测试双栏阅读顺序 (Reading Order) 与跨页段落连续性
    # =========================================================================
    out_pdf3 = TESTSET_DIR / "two_column_paper_scan.pdf"
    doc3 = fitz.open()
    p_col = doc3.new_page(width=595, height=842)
    p_col.insert_text((50, 58), "Dual-Column Reading Order & Cross-Page Continuity Test", fontsize=15.5, fontname="helv")
    p_col.draw_line((50, 74), (545, 74), color=(0.78, 0.8, 0.85), width=1)

    # 左栏
    p_col.insert_text((50, 100), "1. Left Column: Pipeline Bottlenecks", fontsize=11.5, fontname="helv")
    p_col.insert_textbox(
        fitz.Rect(50, 114, 285, 310),
        "Traditional pipeline OCR tools split layout detection, formula recognition, and table extraction into "
        "separate models. When faced with two-column academic papers, heuristic sorting rules frequently scramble "
        "the reading order by merging lines horizontally across columns.",
        fontsize=9.8,
        fontname="helv",
    )
    # 右栏
    p_col.insert_text((310, 100), "2. Right Column: R-SWA Causal Tracking", fontsize=11.5, fontname="helv")
    p_col.insert_textbox(
        fitz.Rect(310, 114, 545, 310),
        "By feeding the 128-token causal sliding window continuously, Unlimited-OCR tracks its exact reading "
        "position from the bottom of the left column to the top of the right column, achieving a 7/9 win rate "
        "over DeepSeek-OCR 2 on reading order edit distance.",
        fontsize=9.8,
        fontname="helv",
    )

    doc3.save(str(out_pdf3))
    doc3.close()
    print(f"✅ 已生成全部 3 套评测样本至: {TESTSET_DIR}")


if __name__ == "__main__":
    create_all_samples()
