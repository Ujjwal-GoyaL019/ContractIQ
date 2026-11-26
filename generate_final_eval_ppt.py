import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


def build_final_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # EXECUTIVE DEEP TECH PALETTE (Rich Navy + Vibrant High-Contrast Accents)
    # =========================================================================
    BG_DARK = RGBColor(10, 15, 29)            # #0A0F1D Deep Midnight Navy
    SURFACE = RGBColor(17, 24, 44)            # #11182C Slate Navy Surface
    SURFACE_ALT = RGBColor(22, 32, 58)        # #16203A Table Row Alt
    DIVIDER = RGBColor(36, 49, 82)            # #243152 Crisp Hairline Divider

    TEXT_TITLE = RGBColor(255, 255, 255)      # #FFFFFF Pure White
    TEXT_BODY = RGBColor(226, 232, 240)       # #E2E8F0 Ice Slate
    TEXT_MUTED = RGBColor(148, 163, 184)      # #94A3B8 Cool Muted Slate

    CYAN = RGBColor(0, 229, 255)              # #00E5FF Electric Cyan
    BLUE = RGBColor(59, 130, 246)             # #3B82F6 Royal Blue
    INDIGO = RGBColor(99, 102, 241)           # #6366F1 Vivid Indigo
    PURPLE = RGBColor(168, 85, 247)           # #A855F7 Violet
    EMERALD = RGBColor(16, 185, 129)          # #10B981 Mint Emerald
    AMBER = RGBColor(245, 158, 11)            # #F59E0B Amber Gold
    CORAL = RGBColor(244, 63, 94)             # #F43F5E Coral Red

    TOTAL_SLIDES = 12

    def apply_bg(slide):
        fill = slide.background.fill
        fill.solid()
        fill.fore_color.rgb = BG_DARK

    def add_line(slide, left, top, width, height, color):
        shp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
        shp.fill.solid()
        shp.fill.fore_color.rgb = color
        shp.line.fill.background()
        return shp

    def add_header(slide, slide_num, tag_text, title_text, subtitle_text=None, accent=CYAN):
        # Top short glowing accent bar
        add_line(slide, Inches(0.75), Inches(0.36), Inches(1.8), Inches(0.045), accent)

        # Slide counter top-right
        num_box = slide.shapes.add_textbox(Inches(11.3), Inches(0.35), Inches(1.3), Inches(0.3))
        ntf = num_box.text_frame
        np_ = ntf.paragraphs[0]
        np_.alignment = PP_ALIGN.RIGHT
        np_.text = f"{slide_num:02d} / {TOTAL_SLIDES:02d}"
        np_.font.size = Pt(9.5)
        np_.font.bold = True
        np_.font.color.rgb = TEXT_MUTED

        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.46), Inches(10.5), Inches(0.28))
        ttf = tag_box.text_frame
        ttf.margin_left = ttf.margin_top = ttf.margin_right = ttf.margin_bottom = 0
        tp = ttf.paragraphs[0]
        tp.text = tag_text.upper()
        tp.font.size = Pt(9.5)
        tp.font.bold = True
        tp.font.color.rgb = accent

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.75), Inches(0.72), Inches(11.8), Inches(0.48))
        tf = title_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = TEXT_TITLE

        if subtitle_text:
            ps = tf.add_paragraph()
            ps.text = subtitle_text
            ps.font.size = Pt(11)
            ps.font.color.rgb = TEXT_MUTED
            ps.space_before = Pt(2)

        # Subtle header underline
        add_line(slide, Inches(0.75), Inches(1.44), Inches(11.83), Inches(0.015), DIVIDER)

    def add_footer(slide, text_left="ContractIQ  •  Final Project Evaluation", text_right="U23AI074  |  U23AI079  |  U23AI094  |  U23AI072"):
        add_line(slide, Inches(0.75), Inches(7.05), Inches(11.83), Inches(0.012), DIVIDER)
        lb = slide.shapes.add_textbox(Inches(0.75), Inches(7.10), Inches(6.0), Inches(0.28))
        lp = lb.text_frame.paragraphs[0]
        lp.text = text_left
        lp.font.size = Pt(8.5)
        lp.font.color.rgb = TEXT_MUTED

        rb = slide.shapes.add_textbox(Inches(6.8), Inches(7.10), Inches(5.78), Inches(0.28))
        rp = rb.text_frame.paragraphs[0]
        rp.alignment = PP_ALIGN.RIGHT
        rp.text = text_right
        rp.font.size = Pt(8.5)
        rp.font.color.rgb = TEXT_MUTED

    def style_cell(cell, text, font_size=9.5, bold=False, color=TEXT_BODY, bg_color=None, align=PP_ALIGN.LEFT):
        if bg_color is not None:
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_color
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = Inches(0.08)
        cell.margin_right = Inches(0.08)
        cell.margin_top = Inches(0.04)
        cell.margin_bottom = Inches(0.04)
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = align
        p.text = text
        p.font.size = Pt(font_size)
        p.font.bold = bold
        p.font.color.rgb = color

    # =========================================================================
    # SLIDE 1: TITLE SLIDE (Allowed Extra Slide)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    # Tricolor glowing top ribbon
    add_line(s1, Inches(0.75), Inches(0.65), Inches(3.94), Inches(0.065), CYAN)
    add_line(s1, Inches(4.69), Inches(0.65), Inches(3.94), Inches(0.065), BLUE)
    add_line(s1, Inches(8.63), Inches(0.65), Inches(3.95), Inches(0.065), INDIGO)

    # Tag + Main Title
    tb1 = s1.shapes.add_textbox(Inches(0.75), Inches(0.95), Inches(11.8), Inches(2.2))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p_tag = tf1.paragraphs[0]
    p_tag.text = "FINAL PROJECT PRESENTATION  •  APPLIED AI, RAG & OPERATIONS RESEARCH"
    p_tag.font.size = Pt(11)
    p_tag.font.bold = True
    p_tag.font.color.rgb = INDIGO

    p_main = tf1.add_paragraph()
    p_main.text = "CONTRACTIQ"
    p_main.font.size = Pt(46)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_TITLE
    p_main.space_before = Pt(6)

    p_sub = tf1.add_paragraph()
    p_sub.text = "Zero-Hallucination Contract RAG, Multi-Model Demand Forecasting & MILP Sourcing Advisor"
    p_sub.font.size = Pt(19)
    p_sub.font.bold = True
    p_sub.font.color.rgb = CYAN
    p_sub.space_before = Pt(4)

    add_line(s1, Inches(0.75), Inches(3.25), Inches(11.83), Inches(0.018), DIVIDER)

    # Left Open Editorial Column (Left Cyan Rail)
    add_line(s1, Inches(0.75), Inches(3.6), Inches(0.06), Inches(2.25), CYAN)
    lb1 = s1.shapes.add_textbox(Inches(1.0), Inches(3.55), Inches(6.0), Inches(2.35))
    ltf1 = lb1.text_frame
    ltf1.word_wrap = True

    lp0 = ltf1.paragraphs[0]
    lp0.text = "PROJECT OVERVIEW"
    lp0.font.size = Pt(11)
    lp0.font.bold = True
    lp0.font.color.rgb = CYAN

    intro_pts = [
        ("Unified Intelligence", "Connects multi-page legal vendor PDFs directly with probabilistic demand forecasting and prescriptive split-order optimization."),
        ("Verified Reliability", "3-Stage Zero-Hallucination Guard achieves 0.0% hallucination rate and 100% adversarial trap abstention across 16 audited queries."),
        ("Production Stack", "Next.js 14 • FastAPI • Qdrant HNSW + Okapi BM25 • 7 ML Forecasters • SciPy HiGHS MILP • Docker Compose.")
    ]
    for h, d in intro_pts:
        p = ltf1.add_paragraph()
        p.text = f"▸ {h}: "
        p.font.bold = True
        p.font.size = Pt(10.5)
        p.font.color.rgb = TEXT_TITLE
        p.space_before = Pt(7)
        r = p.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Right Open Editorial Column: Team Roll Numbers ONLY (No work division!)
    add_line(s1, Inches(7.35), Inches(3.6), Inches(0.06), Inches(2.25), BLUE)
    tb_team = s1.shapes.add_textbox(Inches(7.6), Inches(3.55), Inches(4.9), Inches(0.35))
    tp0 = tb_team.text_frame.paragraphs[0]
    tp0.text = "PROJECT TEAM"
    tp0.font.size = Pt(11)
    tp0.font.bold = True
    tp0.font.color.rgb = BLUE

    rolls = ["U23AI074", "U23AI079", "U23AI094", "U23AI072"]
    pill_coords = [
        (Inches(7.6), Inches(4.15)),
        (Inches(10.15), Inches(4.15)),
        (Inches(7.6), Inches(4.95)),
        (Inches(10.15), Inches(4.95)),
    ]
    for i, rnum in enumerate(rolls):
        px, py = pill_coords[i]
        pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, Inches(2.35), Inches(0.58))
        pill.fill.solid()
        pill.fill.fore_color.rgb = SURFACE
        pill.line.color.rgb = INDIGO
        pill.line.width = Pt(1.4)
        pp = pill.text_frame.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = rnum
        pp.font.size = Pt(15)
        pp.font.bold = True
        pp.font.color.rgb = TEXT_TITLE

    # Bottom KPI Highlight Strip (Open minimal bar)
    add_line(s1, Inches(0.75), Inches(6.2), Inches(11.83), Inches(0.015), DIVIDER)
    hero_strip = [
        ("0.0%", "Hallucination Rate", EMERALD),
        ("7 AI Models", "Forecasting Benchmarked", CYAN),
        ("$9,439", "MILP Risk-Cost Savings", AMBER),
        ("39 / 39", "Automated Tests Passed", BLUE),
    ]
    for i, (val, lbl, col) in enumerate(hero_strip):
        hx = Inches(0.75 + i * 3.0)
        hb = s1.shapes.add_textbox(hx, Inches(6.32), Inches(2.85), Inches(0.7))
        htf = hb.text_frame
        hp1 = htf.paragraphs[0]
        hp1.text = val
        hp1.font.size = Pt(18)
        hp1.font.bold = True
        hp1.font.color.rgb = col
        hp2 = htf.add_paragraph()
        hp2.text = lbl
        hp2.font.size = Pt(9.5)
        hp2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT (1 Slide)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)
    add_header(s2, 2, "01 • Problem Statement", "The Disconnected Supply Chain & Legal Compliance Blindspot",
               "Enterprise ERPs manage stock counts in isolation from legal contract obligations and stochastic demand risk", CORAL)

    # Left Editorial Rail
    add_line(s2, Inches(0.75), Inches(1.75), Inches(0.07), Inches(4.2), CORAL)
    lb2 = s2.shapes.add_textbox(Inches(1.0), Inches(1.70), Inches(4.15), Inches(4.3))
    ltf2 = lb2.text_frame
    ltf2.word_wrap = True

    p = ltf2.paragraphs[0]
    p.text = "CORE STATEMENT"
    p.font.size = Pt(11.5)
    p.font.bold = True
    p.font.color.rgb = CORAL

    p2 = ltf2.add_paragraph()
    p2.text = "Modern procurement teams cannot automatically link unstructured supplier PDF contracts with real-time demand volatility and multi-vendor sourcing decisions."
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_TITLE
    p2.space_before = Pt(8)

    p3 = ltf2.add_paragraph()
    p3.text = "As a result, companies either under-order during supply disruptions—triggering cascading factory stockouts and SLA breach penalties—or over-order blindly and trap working capital in excess inventory."
    p3.font.size = Pt(10.5)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(10)

    # Right 3 Open Rows with Circular Badges (No Boxes)
    probs = [
        ("01", CORAL, "Unstructured Multi-Page Contract Traps",
         "Critical obligations—liquidated damages (2.0%/wk), rush surcharges (+20%), superseding Q2 pricing addendums, and Malacca Strait force majeure notices—remain locked in static PDFs invisible to ERP logic."),
        ("02", AMBER, "Naive Forecasting & Single-Source Concentration",
         "Basic moving-average forecasts suffer 44.56% MAPE on volatile B2B demand, while traditional ERPs route 100% of orders to the lowest nominal unit price—ignoring +12.5% surcharges and 35–42 day port delays."),
        ("03", PURPLE, "Unreliable & Hallucinating Generic RAG Tools",
         "Off-the-shelf LLM PDF wrappers miss exact SKU codes (SKU-LENS-4K) or clause IDs (Section 7.2) in pure vector search, and fabricate non-existent penalty percentages when queried about absent contract terms."),
    ]
    y = 1.75
    for num, col, title, desc in probs:
        circ = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.55), Inches(y), Inches(0.52), Inches(0.52))
        circ.fill.solid()
        circ.fill.fore_color.rgb = SURFACE
        circ.line.color.rgb = col
        circ.line.width = Pt(1.6)
        cp = circ.text_frame.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        cp.text = num
        cp.font.size = Pt(12)
        cp.font.bold = True
        cp.font.color.rgb = col

        rb = s2.shapes.add_textbox(Inches(6.25), Inches(y - 0.04), Inches(6.3), Inches(1.2))
        rtf = rb.text_frame
        rtf.word_wrap = True
        rp1 = rtf.paragraphs[0]
        rp1.text = title
        rp1.font.size = Pt(12.5)
        rp1.font.bold = True
        rp1.font.color.rgb = TEXT_TITLE
        rp2 = rtf.add_paragraph()
        rp2.text = desc
        rp2.font.size = Pt(10.2)
        rp2.font.color.rgb = TEXT_MUTED
        rp2.space_before = Pt(3)

        if num != "03":
            add_line(s2, Inches(6.25), Inches(y + 1.25), Inches(6.3), Inches(0.012), DIVIDER)
        y += 1.44

    # Bottom Objective Ribbon
    bar2 = add_line(s2, Inches(0.75), Inches(6.25), Inches(11.83), Inches(0.52), SURFACE)
    bar2.line.color.rgb = CORAL
    bar2.line.width = Pt(1)
    bp2 = bar2.text_frame.paragraphs[0]
    bp2.alignment = PP_ALIGN.CENTER
    bp2.text = "OBJECTIVE: Build a unified, zero-hallucination AI platform fusing Hybrid Legal RAG, Probabilistic Forecasting & MILP Sourcing."
    bp2.font.size = Pt(10.5)
    bp2.font.bold = True
    bp2.font.color.rgb = CORAL

    add_footer(s2)

    # =========================================================================
    # SLIDE 3: MOTIVATION (1 Slide)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)
    add_header(s3, 3, "02 • Motivation", "Why Supply Chain Intelligence Needs Verified, Prescriptive AI",
               "Moving beyond passive dashboards and fragile LLM wrappers to high-trust autonomous decision support", CYAN)

    # Top 3 Hero Metric Callouts (Open Minimalist Typography)
    mot_kpis = [
        ("+12.5% to 20%", "Hidden Contractual Surcharges", "Unexpected energy surcharges & rush turnaround fees erode margins when contracts aren't monitored.", CORAL),
        ("35 – 42 Days", "Maritime Disruption Shocks", "Single-source reliance on congested shipping corridors turns minor spikes into critical factory stockouts.", AMBER),
        ("0.0% Tolerance", "For Legal Hallucinations", "One fabricated penalty rate or invented SLA waiver breaks enterprise trust and causes direct financial liability.", EMERALD),
    ]
    for i, (big, sub, desc, col) in enumerate(mot_kpis):
        mx = Inches(0.75 + i * 4.05)
        mb = s3.shapes.add_textbox(mx, Inches(1.68), Inches(3.75), Inches(1.8))
        mtf = mb.text_frame
        mtf.word_wrap = True
        mp1 = mtf.paragraphs[0]
        mp1.text = big
        mp1.font.size = Pt(28)
        mp1.font.bold = True
        mp1.font.color.rgb = col
        mp2 = mtf.add_paragraph()
        mp2.text = sub
        mp2.font.size = Pt(12)
        mp2.font.bold = True
        mp2.font.color.rgb = TEXT_TITLE
        mp2.space_before = Pt(3)
        mp3 = mtf.add_paragraph()
        mp3.text = desc
        mp3.font.size = Pt(9.8)
        mp3.font.color.rgb = TEXT_MUTED
        mp3.space_before = Pt(4)

    add_line(s3, Inches(0.75), Inches(3.68), Inches(11.83), Inches(0.015), DIVIDER)

    # Bottom 3 Motivation Pillars (Top Colored Accent Bar, Open Columns)
    pillars = [
        ("PILLAR 01  •  CONTRACT-AWARE OPS", CYAN, "Bridge Legal Text & Inventory Math",
         "Extract binding MOQs, surcharges, and penalty rates verbatim from supplier PDFs and feed them directly into lead-time safety stock and capital-at-risk equations."),
        ("PILLAR 02  •  PRESCRIPTIVE DECISIONS", INDIGO, "Optimize, Don't Just Alert",
         "Instead of stopping at red risk badges, apply Mixed-Integer Linear Programming (MILP) to compute the exact optimal split order across competing primary and backup vendors."),
        ("PILLAR 03  •  PRIVACY & EMPIRICAL RIGOR", EMERALD, "Local, Auditable & Deployment-Ready",
         "Execute quantized BGE embeddings locally via ONNX Runtime (zero data leakage), benchmark 7 ML models scientifically, and package everything for one-command Docker deployment."),
    ]
    for i, (tag, col, title, desc) in enumerate(pillars):
        px = Inches(0.75 + i * 4.05)
        add_line(s3, px, Inches(3.95), Inches(3.75), Inches(0.06), col)
        pb = s3.shapes.add_textbox(px, Inches(4.12), Inches(3.75), Inches(2.55))
        ptf = pb.text_frame
        ptf.word_wrap = True
        pp1 = ptf.paragraphs[0]
        pp1.text = tag
        pp1.font.size = Pt(9)
        pp1.font.bold = True
        pp1.font.color.rgb = col
        pp2 = ptf.add_paragraph()
        pp2.text = title
        pp2.font.size = Pt(13)
        pp2.font.bold = True
        pp2.font.color.rgb = TEXT_TITLE
        pp2.space_before = Pt(4)
        pp3 = ptf.add_paragraph()
        pp3.text = desc
        pp3.font.size = Pt(10.2)
        pp3.font.color.rgb = TEXT_BODY
        pp3.space_before = Pt(6)

    add_footer(s3)

    # =========================================================================
    # SLIDE 4: DATASET (1 Slide)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)
    add_header(s4, 4, "03 • Dataset", "Multi-Modal Dataset: Enterprise Contract PDFs, Time-Series & Eval Benchmarks",
               "Combines unstructured multi-page legal PDFs, 400-day B2B sales histories, supplier telemetry, and adversarial test queries", BLUE)

    # Left: Multi-PDF Corpus Table
    lt_lbl = s4.shapes.add_textbox(Inches(0.75), Inches(1.58), Inches(7.3), Inches(0.3))
    lp = lt_lbl.text_frame.paragraphs[0]
    lp.text = "A. UNSTRUCTURED MULTI-PDF LEGAL CORPUS (6 PDFs  •  14 PAGES  •  54 INDEXED CHUNKS)"
    lp.font.size = Pt(10)
    lp.font.bold = True
    lp.font.color.rgb = CYAN

    pdf_rows = [
        ["Document (PDF)", "Type", "Pg", "Key Contractual Clauses & Risk Terms"],
        ["Apex_Master_SLA_2025.pdf", "Contract", "3", "SKU-MCU-32B, MOQ 500, 20% rush fee, 15% force majeure, Sec 7.2 2%/wk"],
        ["Apex_Addendum_2026_Q2.pdf", "Addendum", "2", "Superseding 6% discount >1,500 units, reduced 250-unit pilot MOQ"],
        ["Pacific_Optics_Risk_2026.pdf", "Risk Notice", "2", "SKU-LENS-4K Malacca delay (35–42d), +12.5% surcharge, SLA waiver"],
        ["Nordic_Silicon_FPA_2025.pdf", "Contract", "3", "SKU-BLE-SOC + backup MCU, 14d FOB Oslo, 1.5%/wk penalty, 5% disc."],
        ["Titan_Polymers_Terms_2025.pdf", "Contract", "2", "SKU-ENC-IP67, 10d Chicago domestic, ISO 9001:2015, IP67, overnight"],
        ["EuroOptics_Backup_SLA_2026.pdf", "Compliance", "2", "Backup SKU-LENS-4K (Germany), ISO Class 5, 0.02% defect, $21.40"],
    ]
    tbl_shape = s4.shapes.add_table(len(pdf_rows), 4, Inches(0.75), Inches(1.92), Inches(7.35), Inches(4.75))
    tbl = tbl_shape.table
    tbl.columns[0].width = Inches(2.25)
    tbl.columns[1].width = Inches(0.95)
    tbl.columns[2].width = Inches(0.45)
    tbl.columns[3].width = Inches(3.70)

    for r_idx, row_data in enumerate(pdf_rows):
        is_hdr = (r_idx == 0)
        bg = RGBColor(21, 35, 66) if is_hdr else (SURFACE if r_idx % 2 == 1 else SURFACE_ALT)
        for c_idx, val in enumerate(row_data):
            col = CYAN if is_hdr else (TEXT_TITLE if c_idx == 0 else TEXT_BODY)
            style_cell(tbl.cell(r_idx, c_idx), val, font_size=8.8 if not is_hdr else 9.0,
                       bold=(is_hdr or c_idx == 0), color=col, bg_color=bg,
                       align=PP_ALIGN.CENTER if c_idx == 2 else PP_ALIGN.LEFT)

    # Right Top: Structured Time-Series & ERP Dataset
    add_line(s4, Inches(8.45), Inches(1.62), Inches(0.06), Inches(2.35), INDIGO)
    rt = s4.shapes.add_textbox(Inches(8.68), Inches(1.58), Inches(3.9), Inches(2.45))
    rttf = rt.text_frame
    rttf.word_wrap = True
    rtp0 = rttf.paragraphs[0]
    rtp0.text = "B. STRUCTURED ERP & TIME-SERIES DATA"
    rtp0.font.size = Pt(10)
    rtp0.font.bold = True
    rtp0.font.color.rgb = INDIGO

    ts_pts = [
        ("Sales History", "1,600 daily records (400 days × 4 SKUs) capturing B2B weekday cycles, yearly Fourier seasonality, upward trend, and 8% promo spikes."),
        ("Supplier Catalog", "5 global vendors (Taiwan, Norway, Singapore, US, Germany) with reliability (78–98%), lead times (10–35d), and disruption indices."),
        ("Inventory & POs", "Live on-hand, allocated, incoming pipeline stock, reorder points, and delayed purchase orders."),
    ]
    for h, d in ts_pts:
        p = rttf.add_paragraph()
        p.text = f"• {h}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_TITLE
        p.space_before = Pt(5)
        r = p.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Right Bottom: Evaluation & Adversarial Datasets
    add_line(s4, Inches(8.45), Inches(4.32), Inches(0.06), Inches(2.35), EMERALD)
    rb = s4.shapes.add_textbox(Inches(8.68), Inches(4.28), Inches(3.9), Inches(2.45))
    rbtf = rb.text_frame
    rbtf.word_wrap = True
    rbp0 = rbtf.paragraphs[0]
    rbp0.text = "C. EVALUATION & ADVERSARIAL BENCHMARKS"
    rbp0.font.size = Pt(10)
    rbp0.font.bold = True
    rbp0.font.color.rgb = EMERALD

    ev_pts = [
        ("10 Golden Legal QA Pairs", "Targeted queries testing exact SKUs, clause IDs (Sec 7.2), Q2 addendum discounts, and ISO specs."),
        ("6 Adversarial Hallucination Traps", "Unanswerable prompts (fake SKUs, Quantum Chips, Bitcoin discount, radiation warranty, carbon tax, Apple stock) verifying 100% safe abstention."),
        ("14-Day Holdout Split", "Strict out-of-sample test window across all 4 SKUs for leak-free 7-model forecasting comparison."),
    ]
    for h, d in ev_pts:
        p = rbtf.add_paragraph()
        p.text = f"• {h}: "
        p.font.bold = True
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_TITLE
        p.space_before = Pt(5)
        r = p.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    add_footer(s4)

    # =========================================================================
    # SLIDE 5: APPROACHES (1 of 2) — HYBRID RAG & ZERO-HALLUCINATION SHIELD
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_bg(s5)
    add_header(s5, 5, "04 • Approaches (1/2)", "Hybrid Legal RAG Architecture & 3-Stage Zero-Hallucination Shield",
               "Fusing dense semantics with sparse legal tokenization, RRF cross-reranking, and deterministic claim verification", CYAN)

    # Top Section: 4-Step Hybrid Retrieval Flow Ribbon
    sec_lbl = s5.shapes.add_textbox(Inches(0.75), Inches(1.58), Inches(11.8), Inches(0.28))
    slp = sec_lbl.text_frame.paragraphs[0]
    slp.text = "A. TWO-STAGE HYBRID RETRIEVAL ENGINE (DENSE HNSW + SPARSE OKAPI BM25 + RRF CROSS-RERANKER)"
    slp.font.size = Pt(10)
    slp.font.bold = True
    slp.font.color.rgb = CYAN

    rag_cols = [
        ("01", "PDF Parsing & Chunking", EMERALD,
         "PyMuPDF extracts multi-page text & tables with exact page coordinates. Sentence-aware chunking (600 chars, 100 overlap) preserves full legal clauses."),
        ("02", "Dual Vector + BM25 Index", CYAN,
         "FastEmbed ONNX generates local 384-d BGE embeddings in Qdrant HNSW. Parallel Okapi BM25 (k1=1.5, b=0.75) indexes exact SKUs, %, and section IDs."),
        ("03", "Reciprocal Rank Fusion", BLUE,
         "Merges top-20 Dense & BM25 lists via RRF(d) = Σ w_r / (60 + rank_r(d)) with weights 0.60 Dense + 0.40 BM25—robust to scale differences."),
        ("04", "Entity Cross-Reranker", INDIGO,
         "Re-scores candidates by combining RRF, dense/BM25 norms, bigram proximity, and exact legal entity overlap (SKU codes, ISO specs, % penalties)."),
    ]
    cw = Inches(2.74)
    cgap = Inches(0.29)
    for i, (num, title, col, desc) in enumerate(rag_cols):
        cx = Inches(0.75) + i * (cw + cgap)
        add_line(s5, cx, Inches(1.94), cw, Inches(0.06), col)
        cb = s5.shapes.add_textbox(cx, Inches(2.06), cw, Inches(1.85))
        ctf = cb.text_frame
        ctf.word_wrap = True
        cp1 = ctf.paragraphs[0]
        cp1.text = f"STEP {num}  •  {title}"
        cp1.font.size = Pt(10.5)
        cp1.font.bold = True
        cp1.font.color.rgb = col
        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.size = Pt(9.5)
        cp2.font.color.rgb = TEXT_BODY
        cp2.space_before = Pt(5)

        if i < 3:
            arr = s5.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, cx + cw + Inches(0.06), Inches(2.12), Inches(0.16), Inches(0.18))
            arr.fill.solid()
            arr.fill.fore_color.rgb = INDIGO
            arr.line.fill.background()

    add_line(s5, Inches(0.75), Inches(4.02), Inches(11.83), Inches(0.015), DIVIDER)

    # Bottom Section: 3-Stage Anti-Hallucination Shield (Stacked Accent Ribbons)
    sh_lbl = s5.shapes.add_textbox(Inches(0.75), Inches(4.14), Inches(11.8), Inches(0.28))
    sh_p = sh_lbl.text_frame.paragraphs[0]
    sh_p.text = "B. THREE-STAGE DETERMINISTIC ANTI-HALLUCINATION SHIELD (HALLUCINATIONGUARD)"
    sh_p.font.size = Pt(10)
    sh_p.font.bold = True
    sh_p.font.color.rgb = EMERALD

    stages_guard = [
        ("STAGE 1: PRE-GENERATION ABSTENTION GATE", AMBER,
         "Verifies queried SKUs, vendor names, numeric traps, and retrieval confidence (dense ≥ 0.48 or BM25 ≥ 2.0). Hard-refuses with 'Clause Not Specified' when evidence is absent."),
        ("STAGE 2: ZERO-TEMPERATURE GROUNDED SYNTHESIS", CYAN,
         "Runs Groq Llama 3.3 70B strictly at temperature = 0.0 with mandatory [Doc, Page] citation rules, paired with a verbatim sentence-level Extractive Grounder offline."),
        ("STAGE 3: POST-GENERATION CLAIM & NUMERIC AUDITOR", EMERALD,
         "Extracts every %, $, SKU, lead-time duration, ISO spec, DPPM, and Section ID from generated answers; checks verbatim against source PDFs and auto-replaces any unverified claim."),
    ]
    sy = 4.50
    for st_title, col, st_desc in stages_guard:
        add_line(s5, Inches(0.75), Inches(sy), Inches(0.07), Inches(0.68), col)
        rib = add_line(s5, Inches(0.82), Inches(sy), Inches(11.76), Inches(0.68), SURFACE)
        sb = s5.shapes.add_textbox(Inches(1.0), Inches(sy + 0.04), Inches(11.45), Inches(0.62))
        stf = sb.text_frame
        stf.word_wrap = True
        sp1 = stf.paragraphs[0]
        sp1.text = st_title
        sp1.font.size = Pt(9.8)
        sp1.font.bold = True
        sp1.font.color.rgb = col
        sp2 = stf.add_paragraph()
        sp2.text = st_desc
        sp2.font.size = Pt(9.5)
        sp2.font.color.rgb = TEXT_BODY
        sp2.space_before = Pt(2)
        sy += 0.80

    add_footer(s5)

    # =========================================================================
    # SLIDE 6: APPROACHES (2 of 2) — FORECASTING, RISK MATH & MILP SOLVER
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_bg(s6)
    add_header(s6, 6, "04 • Approaches (2/2)", "Multi-Model Forecasting, Stochastic Risk Math & MILP Sourcing Solver",
               "Combining 7 demand forecasting architectures with Mixed-Integer Linear Programming for prescriptive order allocation", PURPLE)

    # Left Pillar: Forecasting & Stochastic Risk Math
    add_line(s6, Inches(0.75), Inches(1.68), Inches(0.07), Inches(5.12), PURPLE)
    lb6 = s6.shapes.add_textbox(Inches(1.0), Inches(1.64), Inches(5.55), Inches(5.18))
    ltf6 = lb6.text_frame
    ltf6.word_wrap = True

    p = ltf6.paragraphs[0]
    p.text = "A. 7-MODEL PROBABILISTIC DEMAND FORECASTING"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PURPLE

    fc_items = [
        ("Feature Engineering", "7/14/30-day rolling means & std dev, recursive lags, day-of-week & yearly cyclical encodings."),
        ("7 Model Families Tested", "Naive MA-7 Baseline, Ridge L2 Autoregressive, Facebook Prophet (Fourier harmonics), Random Forest (per-tree quantiles), XGBoost, LightGBM Pinball Quantile (P10/P50/P90), and Stacked Meta-Ensemble."),
        ("Uncertainty Calibration", "Upper P90 surge forecasts feed directly into safety buffers instead of risking 50% mean-demand stockouts."),
    ]
    for h, d in fc_items:
        bp = ltf6.add_paragraph()
        bp.text = f"▸ {h}: "
        bp.font.bold = True
        bp.font.size = Pt(9.8)
        bp.font.color.rgb = TEXT_TITLE
        bp.space_before = Pt(5)
        r = bp.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    p_math = ltf6.add_paragraph()
    p_math.text = "B. STOCHASTIC INVENTORY & PENALTY FORMULATIONS"
    p_math.font.size = Pt(11)
    p_math.font.bold = True
    p_math.font.color.rgb = CYAN
    p_math.space_before = Pt(14)

    formulas = [
        ("Effective Stock:", "I_eff = I_on_hand + I_in_transit − Backorders"),
        ("Lead-Time Buffer:", "D_LT = (μ_daily × L) + (Z × σ_daily × √L)"),
        ("Stockout Risk (0–100):", "Risk = clamp( ((D_LT − I_eff) / D_LT) × 100 )"),
        ("Capital at Risk ($):", "Exposure = Contract Penalty Rate × Deficit × Price"),
    ]
    for lbl, eq in formulas:
        fp = ltf6.add_paragraph()
        fp.text = f"• {lbl}  "
        fp.font.bold = True
        fp.font.size = Pt(9.5)
        fp.font.color.rgb = AMBER
        fp.space_before = Pt(5)
        r = fp.add_run()
        r.text = eq
        r.font.bold = True
        r.font.color.rgb = TEXT_TITLE

    # Right Pillar: Prescriptive MILP Optimizer
    add_line(s6, Inches(6.95), Inches(1.68), Inches(0.07), Inches(5.12), EMERALD)
    rb6 = s6.shapes.add_textbox(Inches(7.2), Inches(1.64), Inches(5.38), Inches(5.18))
    rtf6 = rb6.text_frame
    rtf6.word_wrap = True

    rp = rtf6.paragraphs[0]
    rp.text = "C. PRESCRIPTIVE MILP MULTI-SUPPLIER OPTIMIZER"
    rp.font.size = Pt(11)
    rp.font.bold = True
    rp.font.color.rgb = EMERALD

    rp_sub = rtf6.add_paragraph()
    rp_sub.text = "Solved globally via SciPy HiGHS Branch-and-Cut MILP Solver"
    rp_sub.font.size = Pt(10)
    rp_sub.font.bold = True
    rp_sub.font.color.rgb = CYAN
    rp_sub.space_before = Pt(4)

    milp_pts = [
        ("Decision Variables", "Integer order units x_i ∈ Z≥0 and binary supplier activation indicator y_i ∈ {0, 1} for each qualified vendor i."),
        ("Objective Function (Minimize Risk-Adjusted Cost)", "min Σ [ (c_i^eff + λ · r_i^risk · c_i^eff + LeadPenalty_i) · x_i + FixedSetup_i · y_i ]"),
        ("Contractual Landed Cost", "c_i^eff = BaseCost_i × (1 + Surcharge_i%) incorporates active PDF surcharges (e.g., Pacific Optics +12.5%)."),
        ("Demand Satisfaction Constraint", "Σ x_i ≥ Q  (fulfills required replenishment volume with ≤15% MOQ overbuy cap)."),
        ("MOQ & Capacity Coupling", "MOQ_i · y_i ≤ x_i ≤ min(Capacity_i, α · Q) · y_i enforces MOQ floors and single-supplier concentration cap α (e.g., max 70%)."),
        ("Graceful Feasibility Handling", "Automatically relaxes caps/MOQs on small batches with transparent solver audit notes."),
    ]
    for h, d in milp_pts:
        bp = rtf6.add_paragraph()
        bp.text = f"▸ {h}: "
        bp.font.bold = True
        bp.font.size = Pt(9.8)
        bp.font.color.rgb = TEXT_TITLE
        bp.space_before = Pt(6)
        r = bp.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    add_footer(s6)

    # =========================================================================
    # SLIDE 7: COMPLETE PIPELINE OF THE SYSTEM (1 Slide)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_bg(s7)
    add_header(s7, 7, "05 • Complete System Pipeline", "End-to-End Architecture: Multi-PDF & ERP Ingestion to Prescriptive Action",
               "Five integrated pipeline stages running atop a 3-tier Dockerized FastAPI + Next.js 14 production topology", CYAN)

    # 5-Stage Horizontal Pipeline Flow
    pipe_stages = [
        ("01", "INGESTION", EMERALD, [
            "6 Multi-Page PDFs (PyMuPDF)",
            "Sales CSV / SQLite & Postgres",
            "SHA-256 hash & magic-byte validation",
        ]),
        ("02", "REPRESENTATION", CYAN, [
            "600-char overlapping chunks",
            "FastEmbed 384-d ONNX vectors",
            "Okapi BM25 + 7/14/30d lag features",
        ]),
        ("03", "AI INFERENCE", BLUE, [
            "Hybrid Qdrant HNSW + BM25 RRF",
            "Entity Cross-Reranker (<6 ms)",
            "7 ML Forecasters (P10/P50/P90)",
        ]),
        ("04", "GUARD & MILP", PURPLE, [
            "Pre-gen Abstention Gate",
            "Post-gen Numeric Claim Audit",
            "SciPy HiGHS MILP Split Solver",
        ]),
        ("05", "LIVE DELIVERY", AMBER, [
            "Next.js 14 Dashboard (/optimize, /chat)",
            "SSE Token & Grounding Shield",
            "169× LRU Cache & RBAC JWT",
        ]),
    ]
    pw = Inches(2.14)
    pgap = Inches(0.28)
    for i, (num, title, col, pts) in enumerate(pipe_stages):
        px = Inches(0.75) + i * (pw + pgap)

        # Stage header pill
        badge = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, Inches(1.75), pw, Inches(0.55))
        badge.fill.solid()
        badge.fill.fore_color.rgb = SURFACE
        badge.line.color.rgb = col
        badge.line.width = Pt(1.5)
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.alignment = PP_ALIGN.CENTER
        bp.text = f"{num}  •  {title}"
        bp.font.size = Pt(10)
        bp.font.bold = True
        bp.font.color.rgb = col

        # Vertical drop line
        add_line(s7, px + pw / 2 - Inches(0.015), Inches(2.30), Inches(0.03), Inches(0.22), col)

        # Open bullet list under stage
        tb = s7.shapes.add_textbox(px, Inches(2.55), pw, Inches(2.05))
        ttf = tb.text_frame
        ttf.word_wrap = True
        for j, pt_txt in enumerate(pts):
            p = ttf.paragraphs[0] if j == 0 else ttf.add_paragraph()
            p.text = f"▸ {pt_txt}"
            p.font.size = Pt(9.3)
            p.font.color.rgb = TEXT_BODY
            p.space_before = Pt(5 if j > 0 else 0)

        if i < 4:
            arr = s7.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, px + pw + Inches(0.05), Inches(1.93), Inches(0.18), Inches(0.2))
            arr.fill.solid()
            arr.fill.fore_color.rgb = INDIGO
            arr.line.fill.background()

    add_line(s7, Inches(0.75), Inches(4.72), Inches(11.83), Inches(0.015), DIVIDER)

    # Bottom 3-Tier Production Deployment Stack
    lbl7 = s7.shapes.add_textbox(Inches(0.75), Inches(4.84), Inches(11.8), Inches(0.28))
    lp7 = lbl7.text_frame.paragraphs[0]
    lp7.text = "3-TIER CONTAINERIZED DEPLOYMENT TOPOLOGY (DOCKER COMPOSE + HEALTHCHECKS + NON-ROOT SECURITY)"
    lp7.font.size = Pt(9.8)
    lp7.font.bold = True
    lp7.font.color.rgb = CYAN

    tiers7 = [
        ("CLIENT TIER", CYAN, "Next.js 14 Standalone (Port 3000)",
         "3-stage Alpine Docker build • React Server Components • Interactive /optimize MILP & /chat SSE Studio"),
        ("GATEWAY TIER", BLUE, "FastAPI Async API (Port 8000)",
         "Pydantic v2 • JWT RBAC • Sliding-Window Rate Limiter • HTTP Security Headers • GZip • Auto-Seed Entrypoint"),
        ("DATA & AI TIER", INDIGO, "Postgres + Qdrant + Redis + ONNX",
         "Qdrant HNSW persistent storage • BM25 startup hydration • Local FastEmbed ONNX • SciPy HiGHS + LightGBM/XGBoost"),
    ]
    for i, (ttag, col, tname, tdesc) in enumerate(tiers7):
        tx = Inches(0.75 + i * 4.05)
        add_line(s7, tx, Inches(5.22), Inches(0.06), Inches(1.55), col)
        add_line(s7, tx + Inches(0.06), Inches(5.22), Inches(3.69), Inches(1.55), SURFACE)
        tb = s7.shapes.add_textbox(tx + Inches(0.18), Inches(5.28), Inches(3.48), Inches(1.42))
        ttf = tb.text_frame
        ttf.word_wrap = True
        p1 = ttf.paragraphs[0]
        p1.text = ttag
        p1.font.size = Pt(9)
        p1.font.bold = True
        p1.font.color.rgb = col
        p2 = ttf.add_paragraph()
        p2.text = tname
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_TITLE
        p2.space_before = Pt(2)
        p3 = ttf.add_paragraph()
        p3.text = tdesc
        p3.font.size = Pt(9)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(4)

    add_footer(s7)

    # =========================================================================
    # SLIDE 8: EXPERIMENTAL RESULTS (1 of 2) — 7-MODEL FORECASTING & MILP
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_bg(s8)
    add_header(s8, 8, "06 • Experimental Results (1/2)", "7-Model Forecasting Leaderboard & MILP Optimization Gains",
               "Empirical 14-day out-of-sample holdout backtest across 4 SKUs (1,600 rows) & live SciPy HiGHS MILP sourcing proof", EMERALD)

    lbl8a = s8.shapes.add_textbox(Inches(0.75), Inches(1.55), Inches(11.8), Inches(0.28))
    p8a = lbl8a.text_frame.paragraphs[0]
    p8a.text = "A. HEAD-TO-HEAD 7-MODEL AI FORECASTING LEADERBOARD (14-DAY HOLDOUT ACROSS ALL 4 SKUs)"
    p8a.font.size = Pt(10)
    p8a.font.bold = True
    p8a.font.color.rgb = CYAN

    fc_rows = [
        ["Rank", "AI Model Family", "Avg MAPE", "Avg RMSE", "Avg MAE", "Avg WAPE", "P90 Cov.", "Fit Latency"],
        ["#1", "Ridge L2 Autoregressive ML (Best MAPE)", "27.20%", "6.32", "4.26", "27.14%", "91.1%", "676.6 ms"],
        ["#2", "Random Forest (Bagged Tree Quantiles)", "32.73%", "6.43", "4.57", "28.96%", "91.1%", "1,495.5 ms"],
        ["#3", "LightGBM Quantile Pinball GBDT (Best RMSE)", "33.67%", "6.26", "4.63", "29.81%", "91.1%", "1,789.5 ms"],
        ["#4", "XGBoost (Depth-Wise Regularized GBDT)", "33.72%", "6.73", "4.82", "30.79%", "84.0%", "891.7 ms"],
        ["#5", "Stacked Ensemble (LGBM + XGB + Prophet)", "33.81%", "6.35", "4.56", "29.40%", "92.9%", "3,821.0 ms"],
        ["#6", "Facebook Prophet (Bayesian Fourier)", "39.88%", "6.62", "4.93", "32.57%", "92.9%", "1,139.8 ms"],
        ["#7", "Naive 7-Day Moving Average (Baseline)", "44.56%", "7.26", "6.11", "37.28%", "89.3%", "0.7 ms"],
    ]
    t8_shape = s8.shapes.add_table(len(fc_rows), 8, Inches(0.75), Inches(1.86), Inches(11.83), Inches(2.92))
    t8 = t8_shape.table
    col_widths = [0.65, 4.38, 1.15, 1.10, 1.05, 1.15, 1.10, 1.25]
    for ci, w in enumerate(col_widths):
        t8.columns[ci].width = Inches(w)

    for r_idx, row_data in enumerate(fc_rows):
        is_hdr = (r_idx == 0)
        is_best = (r_idx == 1)
        is_base = (r_idx == 7)
        bg = RGBColor(21, 35, 66) if is_hdr else (RGBColor(14, 48, 46) if is_best else (RGBColor(42, 20, 32) if is_base else (SURFACE if r_idx % 2 == 1 else SURFACE_ALT)))
        for c_idx, val in enumerate(row_data):
            col = CYAN if is_hdr else (EMERALD if (is_best and c_idx in (0, 2, 4, 5)) else (CYAN if (r_idx == 3 and c_idx == 3) else (CORAL if is_base and c_idx in (2, 3) else TEXT_TITLE if c_idx <= 1 else TEXT_BODY)))
            style_cell(t8.cell(r_idx, c_idx), val, font_size=9.0 if is_hdr else 8.9,
                       bold=(is_hdr or is_best or c_idx == 0 or (r_idx == 3 and c_idx == 3)),
                       color=col, bg_color=bg,
                       align=PP_ALIGN.LEFT if c_idx == 1 else PP_ALIGN.CENTER)

    # Bottom: MILP Prescriptive Optimization Results Spotlight
    lbl8b = s8.shapes.add_textbox(Inches(0.75), Inches(4.92), Inches(11.8), Inches(0.28))
    p8b = lbl8b.text_frame.paragraphs[0]
    p8b.text = "B. MILP PRESCRIPTIVE OPTIMIZATION PROOF — SKU-LENS-4K (600 UNITS, λ = 1.5, 70% VENDOR CAP)"
    p8b.font.size = Pt(10)
    p8b.font.bold = True
    p8b.font.color.rgb = EMERALD

    # Left comparison text + Right 3 Hero Savings KPIs
    add_line(s8, Inches(0.75), Inches(5.26), Inches(0.07), Inches(1.55), EMERALD)
    add_line(s8, Inches(0.82), Inches(5.26), Inches(6.18), Inches(1.55), SURFACE)
    mb8 = s8.shapes.add_textbox(Inches(1.0), Inches(5.32), Inches(5.9), Inches(1.45))
    mtf8 = mb8.text_frame
    mtf8.word_wrap = True
    mp1 = mtf8.paragraphs[0]
    mp1.text = "Naive Single-Source ERP (Pacific Optics — Malacca Delay + 12.5% Surcharge):"
    mp1.font.size = Pt(9.5)
    mp1.font.bold = True
    mp1.font.color.rgb = CORAL
    mp2 = mtf8.add_paragraph()
    mp2.text = "Risk-Adjusted Cost: $24,854.72  •  Disruption Risk: 65.0/100  •  Lead Time: 35.0d  •  Reliability: 78.0%"
    mp2.font.size = Pt(9.2)
    mp2.font.color.rgb = TEXT_MUTED
    mp2.space_before = Pt(2)

    mp3 = mtf8.add_paragraph()
    mp3.text = "SciPy HiGHS MILP Optimal Split Allocation (Solved in <10 ms):"
    mp3.font.size = Pt(9.5)
    mp3.font.bold = True
    mp3.font.color.rgb = EMERALD
    mp3.space_before = Pt(8)
    mp4 = mtf8.add_paragraph()
    mp4.text = "• 420 units (70%) → EuroOptics GmbH (Germany, $21.40, 18d, risk 10.0)\n• 180 units (30%) → Apex Microelectronics (Taiwan, $22.80, 21d, risk 15.0)"
    mp4.font.size = Pt(9.2)
    mp4.font.color.rgb = TEXT_TITLE
    mp4.space_before = Pt(2)

    milp_kpis = [
        ("$9,438.93", "Risk-Cost Savings", "vs. Naive ERP ($15,416 vs $24,855)", EMERALD),
        ("-82.3%", "Disruption Reduction", "Risk dropped 65.0 → 11.5/100", CYAN),
        ("18.9 Days", "Weighted Lead Time", "Down from 35d • 96.1% Reliability", AMBER),
    ]
    for i, (val, ttl, sub, col) in enumerate(milp_kpis):
        kx = Inches(7.25 + i * 1.82)
        kb = s8.shapes.add_textbox(kx, Inches(5.30), Inches(1.75), Inches(1.5))
        ktf = kb.text_frame
        ktf.word_wrap = True
        kp1 = ktf.paragraphs[0]
        kp1.text = val
        kp1.font.size = Pt(20)
        kp1.font.bold = True
        kp1.font.color.rgb = col
        kp2 = ktf.add_paragraph()
        kp2.text = ttl
        kp2.font.size = Pt(9.5)
        kp2.font.bold = True
        kp2.font.color.rgb = TEXT_TITLE
        kp2.space_before = Pt(2)
        kp3 = ktf.add_paragraph()
        kp3.text = sub
        kp3.font.size = Pt(8.5)
        kp3.font.color.rgb = TEXT_MUTED
        kp3.space_before = Pt(2)

    add_footer(s8)

    # =========================================================================
    # SLIDE 9: EXPERIMENTAL RESULTS (2 of 2) — RAG ABLATION & ZERO-HALLUCINATION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_bg(s9)
    add_header(s9, 9, "06 • Experimental Results (2/2)", "RAG Retrieval Ablation, Zero-Hallucination Audit & System Benchmarks",
               "Quantitative proof of hybrid retrieval precision, 0.0% hallucination rate, and production performance", CYAN)

    # Left Top: RAG Ablation Table
    lbl9a = s9.shapes.add_textbox(Inches(0.75), Inches(1.58), Inches(6.5), Inches(0.28))
    p9a = lbl9a.text_frame.paragraphs[0]
    p9a.text = "A. RAG RETRIEVAL ABLATION (10 LEGAL QUERIES, 6 PDFs, 54 CHUNKS)"
    p9a.font.size = Pt(10)
    p9a.font.bold = True
    p9a.font.color.rgb = CYAN

    rag_rows = [
        ["Retrieval Engine", "Hit@1", "Hit@3", "MRR", "Prec@3", "Latency"],
        ["Dense Only (Qdrant HNSW BGE)", "100%", "100%", "1.000", "0.8667", "179.1 ms"],
        ["Sparse Only (Okapi BM25)", "100%", "100%", "1.000", "0.9333", "0.36 ms"],
        ["Hybrid RRF + Cross-Reranker", "100%", "100%", "1.000", "0.9333", "5.46 ms"],
    ]
    t9_shape = s9.shapes.add_table(4, 6, Inches(0.75), Inches(1.92), Inches(6.55), Inches(2.0))
    t9 = t9_shape.table
    for ci, w in enumerate([2.55, 0.72, 0.72, 0.78, 0.85, 0.93]):
        t9.columns[ci].width = Inches(w)
    for r_idx, row_data in enumerate(rag_rows):
        is_hdr = (r_idx == 0)
        is_hyb = (r_idx == 3)
        bg = RGBColor(21, 35, 66) if is_hdr else (RGBColor(14, 48, 46) if is_hyb else (SURFACE if r_idx % 2 == 1 else SURFACE_ALT))
        for c_idx, val in enumerate(row_data):
            col = CYAN if is_hdr else (EMERALD if is_hyb else (TEXT_TITLE if c_idx == 0 else TEXT_BODY))
            style_cell(t9.cell(r_idx, c_idx), val, font_size=8.8, bold=(is_hdr or is_hyb), color=col, bg_color=bg,
                       align=PP_ALIGN.LEFT if c_idx == 0 else PP_ALIGN.CENTER)

    note9 = s9.shapes.add_textbox(Inches(0.75), Inches(4.02), Inches(6.55), Inches(0.55))
    ntf9 = note9.text_frame
    ntf9.word_wrap = True
    np9 = ntf9.paragraphs[0]
    np9.text = "Key Insight: Hybrid RRF + Cross-Reranker gains +6.7% Precision@3 over Dense-only (0.8667 → 0.9333) while maintaining sub-6ms average retrieval latency."
    np9.font.size = Pt(9.5)
    np9.font.color.rgb = TEXT_MUTED

    # Left Bottom: Engineering & Performance Benchmarks
    lbl9c = s9.shapes.add_textbox(Inches(0.75), Inches(4.78), Inches(6.55), Inches(0.28))
    p9c = lbl9c.text_frame.paragraphs[0]
    p9c.text = "C. PRODUCTION ENGINEERING & TEST BENCHMARKS"
    p9c.font.size = Pt(10)
    p9c.font.bold = True
    p9c.font.color.rgb = BLUE

    eng_kpis = [
        ("39 / 39", "Pytest Suite Passed", "Auth, Forecasting, RAG, MILP & Hallucination", EMERALD),
        ("169×", "LRU Cache Speedup", "380 ms → 2.2 ms on repeat queries", CYAN),
        ("0 Errors", "Next.js Prod Build", "All 11 routes compiled standalone", INDIGO),
    ]
    for i, (val, ttl, sub, col) in enumerate(eng_kpis):
        ex = Inches(0.75 + i * 2.22)
        add_line(s9, ex, Inches(5.14), Inches(2.05), Inches(0.05), col)
        eb = s9.shapes.add_textbox(ex, Inches(5.24), Inches(2.08), Inches(1.5))
        etf = eb.text_frame
        etf.word_wrap = True
        ep1 = etf.paragraphs[0]
        ep1.text = val
        ep1.font.size = Pt(22)
        ep1.font.bold = True
        ep1.font.color.rgb = col
        ep2 = etf.add_paragraph()
        ep2.text = ttl
        ep2.font.size = Pt(10)
        ep2.font.bold = True
        ep2.font.color.rgb = TEXT_TITLE
        ep2.space_before = Pt(2)
        ep3 = etf.add_paragraph()
        ep3.text = sub
        ep3.font.size = Pt(8.8)
        ep3.font.color.rgb = TEXT_MUTED
        ep3.space_before = Pt(2)

    # Right Column: Zero-Hallucination & Adversarial Audit Scorecard
    add_line(s9, Inches(7.65), Inches(1.62), Inches(0.07), Inches(5.18), EMERALD)
    rb9 = s9.shapes.add_textbox(Inches(7.90), Inches(1.58), Inches(4.68), Inches(5.22))
    rtf9 = rb9.text_frame
    rtf9.word_wrap = True

    rp0 = rtf9.paragraphs[0]
    rp0.text = "B. ZERO-HALLUCINATION AUDIT (16 QUERIES)"
    rp0.font.size = Pt(10)
    rp0.font.bold = True
    rp0.font.color.rgb = EMERALD

    audit_stats = [
        ("0.0% Hallucination Rate", "Zero fabricated numbers or unsupported clauses across all 16 audited queries."),
        ("100.0% Answerable Faithfulness (10/10)", "Every SKU, %, dollar amount, and duration verified verbatim against PDFs."),
        ("100.0% Adversarial Trap Abstention (6/6)", "Refused 'Clause Not Specified' on fake SKUs (SKU-FAKE-9999), Quantum Chips, Bitcoin discount, radiation warranty, carbon tax & Apple stock."),
        ("PASS — Synthetic Fabrication Interception", "Injected fake LLM claim ($999.00, 47.5%, 99 days) was 100% caught & blocked."),
    ]
    for h, d in audit_stats:
        p = rtf9.add_paragraph()
        p.text = f"✓ {h}"
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_TITLE
        p.space_before = Pt(11)
        p2 = rtf9.add_paragraph()
        p2.text = d
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(2)

    add_footer(s9)

    # =========================================================================
    # SLIDE 10: CHALLENGES FACED (1 Slide)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_bg(s10)
    add_header(s10, 10, "07 • Challenges Faced", "Real AI & Systems Engineering Challenges Overcome",
               "Concrete technical bottlenecks encountered during development, benchmarking, and hardening—and how we solved them", AMBER)

    challenges = [
        ("01", CORAL, "Eliminating Legal & Numeric Hallucinations in RAG",
         "Challenge: Standard RAG pipelines return top-k chunks even for unanswerable prompts, causing LLMs to invent penalty percentages or confirm fake SKUs.",
         "Resolution: Built a 3-stage HallucinationGuard (SKU/entity/confidence abstention gate + temp=0.0 + regex claim auditor). It even caught a stray '100%' in our own extractive heading during testing!"),
        ("02", CYAN, "Dense Embedding Blindness to Exact SKUs, Clause IDs & Percentages",
         "Challenge: Pure semantic vector search (BGE) struggled to distinguish exact identifiers like 'Section 7.2', 'ADD-APEX-2026-Q2', and '12.5%' across similar contracts.",
         "Resolution: Implemented a legal-aware Okapi BM25 sparse index fused via RRF (k=60) with an entity-boosted Cross-Reranker, lifting Precision@3 from 0.8667 to 0.9333 in 5.46 ms."),
        ("03", PURPLE, "High B2B Demand Volatility & MILP MOQ Infeasibility Edge Cases",
         "Challenge: Promotional surges drove naive baseline MAPE to 44.56%, while strict single-vendor caps (≤70%) + high MOQs caused infeasibility on small batches.",
         "Resolution: Benchmarked 7 forecasting models (cutting MAPE to 27.20% & RMSE to 6.26) and built progressive MILP constraint relaxation with explicit solver audit notes."),
        ("04", AMBER, "Local Qdrant File Locking, Multi-Process Concurrency & Containerization",
         "Challenge: Embedded Qdrant storage threw concurrent access locks across test/script runs, and missing frontend Dockerfiles blocked clean cloud deployment.",
         "Resolution: Added BM25 auto-hydration from Qdrant on startup, isolated hermetic test fixtures (39/39 passing), and authored multi-stage non-root Dockerfiles with service healthchecks."),
    ]
    y = 1.66
    for num, col, title, chal, res in challenges:
        circ = s10.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.75), Inches(y + 0.08), Inches(0.50), Inches(0.50))
        circ.fill.solid()
        circ.fill.fore_color.rgb = SURFACE
        circ.line.color.rgb = col
        circ.line.width = Pt(1.5)
        cp = circ.text_frame.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        cp.text = num
        cp.font.size = Pt(12)
        cp.font.bold = True
        cp.font.color.rgb = col

        tb = s10.shapes.add_textbox(Inches(1.45), Inches(y - 0.02), Inches(11.1), Inches(1.18))
        ttf = tb.text_frame
        ttf.word_wrap = True
        p1 = ttf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(12)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = ttf.add_paragraph()
        p2.text = chal
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(2)

        p3 = ttf.add_paragraph()
        p3.text = res
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = TEXT_BODY
        p3.space_before = Pt(2)

        if num != "04":
            add_line(s10, Inches(1.45), Inches(y + 1.18), Inches(11.1), Inches(0.012), DIVIDER)
        y += 1.32

    add_footer(s10)

    # =========================================================================
    # SLIDE 11: MAJOR LEARNINGS FROM THE PROJECT (1 Slide)
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_bg(s11)
    add_header(s11, 11, "08 • Major Learnings", "Key Scientific & Engineering Insights from Building ContractIQ",
               "Lessons validated through empirical benchmarking, adversarial testing, and full-stack deployment", INDIGO)

    learnings = [
        ("01  •  TRUSTWORTHY RAG", EMERALD, "Prompt Engineering Alone Cannot Guarantee Zero Hallucinations",
         "Telling an LLM 'do not hallucinate' fails on edge cases. Reliable legal AI requires architectural guardrails: Hybrid BM25 + Dense retrieval for exact entity recall, a pre-generation abstention gate for out-of-corpus queries, and deterministic post-generation numeric claim verification."),
        ("02  •  EMPIRICAL MODEL SELECTION", CYAN, "Never Assume Complex Models Always Beat Simpler Regularized Baselines",
         "Running a leak-free 7-model holdout benchmark proved that Ridge L2 over engineered lag/seasonal features achieved the best MAPE (27.20%), while LightGBM Quantile achieved the lowest RMSE (6.26) and calibrated P90 surge coverage (91.1%). Different models optimize different risk metrics."),
        ("03  •  PRESCRIPTIVE OPERATIONS RESEARCH", PURPLE, "Pairing Predictive ML with MILP Turns Alerts into Financial Impact",
         "Forecasting a stockout is only half the solution. Formulating supplier sourcing as a Mixed-Integer Linear Program transforms risk telemetry into concrete split purchase orders—cutting disruption risk by 82.3% and saving $9,439 per replenishment cycle."),
        ("04  •  PRODUCTION AI ENGINEERING", AMBER, "System Reliability, Latency & Security Define Real-World Usability",
         "Moving from a prototype script to deployable software required local ONNX embeddings (data privacy + 5.46 ms hybrid latency), LRU caching (169× speedup), 39 hermetic automated tests, HTTP security headers, and multi-stage standalone Docker packaging."),
    ]

    grid_coords = [
        (Inches(0.75), Inches(1.75)),
        (Inches(6.85), Inches(1.75)),
        (Inches(0.75), Inches(4.40)),
        (Inches(6.85), Inches(4.40)),
    ]
    for i, (tag, col, title, desc) in enumerate(learnings):
        gx, gy = grid_coords[i]
        gw = Inches(5.72)
        add_line(s11, gx, gy, gw, Inches(0.06), col)
        gb = s11.shapes.add_textbox(gx, gy + Inches(0.14), gw, Inches(2.25))
        gtf = gb.text_frame
        gtf.word_wrap = True
        gp1 = gtf.paragraphs[0]
        gp1.text = tag
        gp1.font.size = Pt(9.5)
        gp1.font.bold = True
        gp1.font.color.rgb = col
        gp2 = gtf.add_paragraph()
        gp2.text = title
        gp2.font.size = Pt(13)
        gp2.font.bold = True
        gp2.font.color.rgb = TEXT_TITLE
        gp2.space_before = Pt(4)
        gp3 = gtf.add_paragraph()
        gp3.text = desc
        gp3.font.size = Pt(10.2)
        gp3.font.color.rgb = TEXT_BODY
        gp3.space_before = Pt(6)

    add_footer(s11)

    # =========================================================================
    # SLIDE 12: FINAL SLIDE — GITHUB LINK, HUGGINGFACE REPOS & Q&A
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_bg(s12)

    # Tricolor top ribbon
    add_line(s12, Inches(0.75), Inches(0.55), Inches(3.94), Inches(0.065), CYAN)
    add_line(s12, Inches(4.69), Inches(0.55), Inches(3.94), Inches(0.065), BLUE)
    add_line(s12, Inches(8.63), Inches(0.55), Inches(3.95), Inches(0.065), EMERALD)

    # Header
    h12 = s12.shapes.add_textbox(Inches(0.75), Inches(0.82), Inches(11.8), Inches(1.1))
    htf12 = h12.text_frame
    p = htf12.paragraphs[0]
    p.text = "THANK YOU  •  OPEN SOURCE REPOSITORIES & LIVE DEMO"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = EMERALD
    p2 = htf12.add_paragraph()
    p2.text = "ContractIQ — Codebase, Models & Deployment"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_TITLE
    p2.space_before = Pt(4)

    add_line(s12, Inches(0.75), Inches(2.02), Inches(11.83), Inches(0.015), DIVIDER)

    # Left Column: GitHub & HuggingFace Links
    add_line(s12, Inches(0.75), Inches(2.35), Inches(0.07), Inches(3.55), CYAN)
    lb12 = s12.shapes.add_textbox(Inches(1.0), Inches(2.30), Inches(6.5), Inches(3.65))
    ltf12 = lb12.text_frame
    ltf12.word_wrap = True

    lp1 = ltf12.paragraphs[0]
    lp1.text = "GITHUB REPOSITORY"
    lp1.font.size = Pt(11)
    lp1.font.bold = True
    lp1.font.color.rgb = CYAN

    lp2 = ltf12.add_paragraph()
    lp2.text = "https://github.com/Ujjwal-GoyaL019/ContractIQ"
    lp2.font.size = Pt(12.5)
    lp2.font.bold = True
    lp2.font.color.rgb = TEXT_TITLE
    lp2.space_before = Pt(4)

    lp3 = ltf12.add_paragraph()
    lp3.text = "Includes full FastAPI backend, Next.js 14 frontend, 6 sample contract PDFs, 39 automated tests, MILP solver, and Docker Compose setup."
    lp3.font.size = Pt(9.5)
    lp3.font.color.rgb = TEXT_MUTED
    lp3.space_before = Pt(3)

    lp4 = ltf12.add_paragraph()
    lp4.text = "HUGGINGFACE MODELS USED"
    lp4.font.size = Pt(11)
    lp4.font.bold = True
    lp4.font.color.rgb = AMBER
    lp4.space_before = Pt(16)

    hf_models = [
        ("Dense Embeddings:", "https://huggingface.co/BAAI/bge-small-en-v1.5"),
        ("ONNX Quantized:", "https://huggingface.co/Qdrant/bge-small-en-v1.5-onnx-Q"),
        ("Reasoning LLM:", "https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct"),
    ]
    for lbl, url in hf_models:
        p = ltf12.add_paragraph()
        p.text = f"▸ {lbl}  "
        p.font.bold = True
        p.font.size = Pt(9.8)
        p.font.color.rgb = TEXT_TITLE
        p.space_before = Pt(6)
        r = p.add_run()
        r.text = url
        r.font.bold = False
        r.font.color.rgb = CYAN

    # Right Column: Quick Deployment + Team Roll Numbers
    add_line(s12, Inches(7.85), Inches(2.35), Inches(0.07), Inches(3.55), INDIGO)
    rb12 = s12.shapes.add_textbox(Inches(8.1), Inches(2.30), Inches(4.5), Inches(1.8))
    rtf12 = rb12.text_frame
    rtf12.word_wrap = True

    rp1 = rtf12.paragraphs[0]
    rp1.text = "ONE-COMMAND DEPLOYMENT"
    rp1.font.size = Pt(11)
    rp1.font.bold = True
    rp1.font.color.rgb = INDIGO

    rp2 = rtf12.add_paragraph()
    rp2.text = "docker compose up --build -d"
    rp2.font.size = Pt(13)
    rp2.font.bold = True
    rp2.font.color.rgb = EMERALD
    rp2.space_before = Pt(6)

    rp3 = rtf12.add_paragraph()
    rp3.text = "• Web App: http://localhost:3000\n• Optimizer & Benchmarks: /optimize\n• Swagger API Docs: http://localhost:8000/docs"
    rp3.font.size = Pt(9.8)
    rp3.font.color.rgb = TEXT_BODY
    rp3.space_before = Pt(6)

    # Team Roll Numbers (Clean Badges — No Work Assigned)
    t12_lbl = s12.shapes.add_textbox(Inches(8.1), Inches(4.25), Inches(4.4), Inches(0.32))
    tp12 = t12_lbl.text_frame.paragraphs[0]
    tp12.text = "PROJECT TEAM"
    tp12.font.size = Pt(10.5)
    tp12.font.bold = True
    tp12.font.color.rgb = BLUE

    final_coords = [
        (Inches(8.1), Inches(4.65)),
        (Inches(10.35), Inches(4.65)),
        (Inches(8.1), Inches(5.32)),
        (Inches(10.35), Inches(5.32)),
    ]
    for i, rnum in enumerate(rolls):
        fx, fy = final_coords[i]
        pill = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, fx, fy, Inches(2.08), Inches(0.50))
        pill.fill.solid()
        pill.fill.fore_color.rgb = SURFACE
        pill.line.color.rgb = INDIGO
        pill.line.width = Pt(1.3)
        pp = pill.text_frame.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = rnum
        pp.font.size = Pt(13)
        pp.font.bold = True
        pp.font.color.rgb = TEXT_TITLE

    # Bottom Q&A Callout Banner
    qa_bar = add_line(s12, Inches(0.75), Inches(6.30), Inches(11.83), Inches(0.55), SURFACE)
    qa_bar.line.color.rgb = EMERALD
    qa_bar.line.width = Pt(1.2)
    qap = qa_bar.text_frame.paragraphs[0]
    qap.alignment = PP_ALIGN.CENTER
    qap.text = "QUESTIONS & LIVE DEMONSTRATION  •  CONTRACTIQ (HYBRID RAG + 7-MODEL FORECASTING + MILP OPTIMIZATION)"
    qap.font.size = Pt(10.5)
    qap.font.bold = True
    qap.font.color.rgb = EMERALD

    # Save to all target paths safely
    filename = "ContractIQ_Final_Project_Presentation.pptx"
    targets = [
        r"C:\Users\hp\OneDrive\Desktop",
        r"C:\Users\hp\OneDrive\Desktop\Projects\Rag project",
        r"C:\Users\hp\.gemini\antigravity\brain\40bddb9e-75df-4888-bd68-bb8e478c154c",
    ]
    for d in targets:
        if os.path.exists(d):
            out_path = os.path.join(d, filename)
            try:
                prs.save(out_path)
                print(f"Saved successfully: {out_path}")
            except Exception as e:
                print(f"Warning: Could not save to {out_path}: {e}")


if __name__ == "__main__":
    build_final_presentation()
    print("Final 12-slide presentation built successfully!")
