import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_mid_eval_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean Light Theme Palette (Academic & Seminar Projector Friendly)
    BG_COLOR = RGBColor(248, 250, 252)       # Light Slate 50
    CARD_BG = RGBColor(255, 255, 255)        # Pure White Card
    CARD_BORDER = RGBColor(226, 232, 240)    # Slate 200
    TEXT_MAIN = RGBColor(15, 23, 42)         # Deep Slate 900
    TEXT_MUTED = RGBColor(71, 85, 105)       # Slate 600
    TEXT_SUB = RGBColor(100, 116, 139)       # Slate 500
    
    # Accents
    BRAND_BLUE = RGBColor(2, 132, 199)       # Sky / Blue 600
    BRAND_CYAN = RGBColor(8, 145, 178)       # Cyan 600
    BRAND_INDIGO = RGBColor(79, 70, 229)     # Indigo 600
    ACCENT_GREEN = RGBColor(16, 185, 129)    # Emerald 500
    ACCENT_ROSE = RGBColor(225, 29, 72)      # Rose 600
    ACCENT_AMBER = RGBColor(217, 119, 6)     # Amber 600

    def set_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

    def add_header(slide, tag_text, title_text, subtitle_text=None):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = BRAND_BLUE

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.55))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN

        if subtitle_text:
            p_sub = tf_title.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = TEXT_MUTED
            p_sub.space_before = Pt(3)

    def add_card(slide, left, top, width, height, border_color=CARD_BORDER, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: TITLE & TEAM (MID-EVALUATION)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_bg(s1)

    # Top accent band
    band = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.08))
    band.fill.solid()
    band.fill.fore_color.rgb = BRAND_BLUE
    band.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(0.8), Inches(1.1), Inches(11.7), Inches(2.3))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "CONTRACTIQ"
    p.font.size = Pt(38)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous AI Supply Chain & Risk Advisor"
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = BRAND_BLUE
    p2.space_before = Pt(4)

    p3 = tf1.add_paragraph()
    p3.text = "MID-TERM PROJECT EVALUATION  •  SYSTEM PIPELINE & ARCHITECTURE DEFENSE"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = BRAND_INDIGO
    p3.space_before = Pt(8)

    # Left Card: Project Overview & Scope
    add_card(s1, Inches(0.8), Inches(3.7), Inches(5.7), Inches(3.2), border_color=CARD_BORDER)
    lbox = s1.shapes.add_textbox(Inches(1.05), Inches(3.9), Inches(5.2), Inches(2.8))
    ltf = lbox.text_frame
    ltf.word_wrap = True

    lp1 = ltf.paragraphs[0]
    lp1.text = "PROJECT HIGHLIGHTS"
    lp1.font.size = Pt(12)
    lp1.font.bold = True
    lp1.font.color.rgb = BRAND_BLUE

    points_intro = [
        ("Core Focus", "Bridging legal contract intelligence (RAG) with machine-learned demand forecasting."),
        ("Architecture", "Next.js 14 Client • FastAPI REST Gateway • Qdrant Vector DB • Prophet & LightGBM."),
        ("Mid-Term Milestone", "Core pipeline fully functional, verified with 28 automated tests and live UI.")
    ]
    for h, d in points_intro:
        p = ltf.add_paragraph()
        p.text = f"• {h}: "
        p.font.bold = True
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)
        
        # Add description
        run = p.add_run()
        run.text = d
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Card: Project Team Roll Numbers
    add_card(s1, Inches(6.8), Inches(3.7), Inches(5.7), Inches(3.2), border_color=BRAND_BLUE)
    rbox = s1.shapes.add_textbox(Inches(7.05), Inches(3.9), Inches(5.2), Inches(2.8))
    rtf = rbox.text_frame
    rtf.word_wrap = True

    rp1 = rtf.paragraphs[0]
    rp1.text = "PROJECT TEAM (ROLL NUMBERS)"
    rp1.font.size = Pt(12)
    rp1.font.bold = True
    rp1.font.color.rgb = BRAND_BLUE

    team_members = [
        ("U23AI074", "Demand Forecasting & ML Feature Pipeline"),
        ("U23AI079", "RAG Pipeline, Ingestion & Vector Retrieval"),
        ("U23AI094", "Multi-Factor Risk Engine & Capital Formulation"),
        ("U23AI072", "System Architecture, Gateway & Security / RBAC")
    ]
    for roll, role in team_members:
        p = rtf.add_paragraph()
        p.text = f"•  {roll}"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(5)

        run = p.add_run()
        run.text = f"  —  {role}"
        run.font.size = Pt(11)
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_bg(s2)
    add_header(s2, "Problem Context", "Why ContractIQ? The Operational Blindspot", "Bridging the disconnect between legal procurement documents and operational demand")

    cards_prob = [
        ("1. Unstructured Contract Blindspot", 
         "Critical clauses (force majeure, lead-time amendments from 21 to 42 days, 15% freight surcharges, SLA penalties) remain trapped in PDF contracts and emails.",
         "Impact: Procurement only realizes stockouts are looming after factory lines stall.", ACCENT_ROSE),
        ("2. Inaccurate Demand Planning", 
         "Traditional ERPs rely on naive moving averages that miss day-of-week seasonality, promotional spikes, and asymmetric downside risk bounds.",
         "Impact: Either millions locked in excess inventory or sudden stockout emergencies.", ACCENT_AMBER),
        ("3. Isolated Risk Metrics", 
         "Inventory balances, vendor on-time scores, and demand trends are tracked in disjointed spreadsheets with no dollar-denominated exposure ($ at risk).",
         "Impact: Reactive firefighting rather than proactive mitigation during lead-time windows.", BRAND_BLUE)
    ]

    for i, (title, desc, impact, col) in enumerate(cards_prob):
        left = Inches(0.8 + i * 3.95)
        add_card(s2, left, Inches(1.8), Inches(3.8), Inches(4.9), border_color=col)
        
        box = s2.shapes.add_textbox(left + Inches(0.25), Inches(2.0), Inches(3.3), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED
        p2.space_before = Pt(10)

        p3 = tf.add_paragraph()
        p3.text = impact
        p3.font.size = Pt(11)
        p3.font.bold = True
        p3.font.color.rgb = col
        p3.space_before = Pt(12)

    # =========================================================================
    # SLIDE 3: WHOLE STRUCTURE / HIGH-LEVEL SYSTEM ARCHITECTURE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_bg(s3)
    add_header(s3, "System Structure", "Full System Structure & Architectural Layers", "A modular, decoupled architecture engineered for high speed, reliability, and security")

    tiers = [
        ("Client Presentation Layer", "Next.js 14 • React • Tailwind", BRAND_CYAN, [
            "Executive Dashboard: Real-time risk cards & live indicators",
            "Interactive Inventory Ledger: Stock adjustment modal with instant recalibration",
            "Visualizer: Dynamic code-split Recharts for demand & confidence curves",
            "Contract RAG Chat: Live token streaming via Server-Sent Events (SSE)",
            "Authentication: 1-Click Demo Login pills (Admin, Analyst, Viewer)"
        ]),
        ("REST Gateway & Middleware", "FastAPI • Python 3.12", BRAND_BLUE, [
            "RBAC Security: Bcrypt password hashing + signed JWT (HS256)",
            "Sliding Window Rate Limiter: IP-based burst & DoS protection",
            "GZip Middleware: 70-85% payload compression over the wire",
            "Multi-Tier Cache Manager: Nanosecond in-memory LRU with tag invalidation",
            "Upload Guard: 15MB ceiling + binary %PDF- magic-byte validation"
        ]),
        ("Analytical & Vector Engines", "Dual ML & Embedded Search", BRAND_INDIGO, [
            "Prophet Engine: Generalized additive seasonal decomposition",
            "LightGBM Engine: Quantile GBDT (α=0.05, 0.50, 0.95) with 30d lag features",
            "FastEmbed: BGE-small-en-v1.5 384-d semantic embedding",
            "Qdrant Vector DB: HNSW cosine graph search with payload filtering",
            "Composite Risk Engine: Formulates stockout, vendor & financial exposure"
        ])
    ]

    for i, (tier_title, tier_tech, tier_col, items) in enumerate(tiers):
        left = Inches(0.8 + i * 3.95)
        add_card(s3, left, Inches(1.8), Inches(3.8), Inches(4.9), border_color=tier_col)

        box = s3.shapes.add_textbox(left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = tier_title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

        p_sub = tf.add_paragraph()
        p_sub.text = tier_tech
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = tier_col
        p_sub.space_before = Pt(2)

        for it in items:
            p_it = tf.add_paragraph()
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = TEXT_MUTED
            p_it.space_before = Pt(7)

    # =========================================================================
    # SLIDE 4: END-TO-END PIPELINE OVERVIEW
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_bg(s4)
    add_header(s4, "Data & Logic Flow", "End-to-End Pipeline: From Raw Data to Advisory", "How raw sales history and unstructured supplier contracts flow through ContractIQ")

    stages = [
        ("STAGE 1", "Data Ingestion", BRAND_BLUE, 
         "Raw Inputs:\n• Historical sales (daily units, promo flags, prices)\n• Supplier PDF contracts, SLAs, risk notices\n• Active inventory balances & PO delivery schedules"),
        ("STAGE 2", "Processing & Indexing", BRAND_CYAN,
         "Transformations:\n• Lag features (t-1..t-30), rolling stats (7d, 28d)\n• PyMuPDF text extraction + 512-token chunking\n• BGE dense vector embedding (384-d) into Qdrant"),
        ("STAGE 3", "Inference & Modeling", BRAND_INDIGO,
         "Intelligence Layer:\n• Prophet: Trend + weekly/yearly Fourier seasonality\n• LightGBM: 95% Quantile bounds prediction\n• Qdrant HNSW cosine search + Groq Llama 3.3 70B"),
        ("STAGE 4", "Risk Synthesis & Output", ACCENT_GREEN,
         "Advisory Outputs:\n• 0-100 Composite Risk score & Dollar capital exposure\n• Cited RAG answers with exact page numbers\n• Real-time stock calibration & mitigation guidance")
    ]

    for i, (stg_tag, stg_title, stg_col, stg_desc) in enumerate(stages):
        left = Inches(0.8 + i * 2.95)
        add_card(s4, left, Inches(1.8), Inches(2.85), Inches(4.9), border_color=stg_col)

        box = s4.shapes.add_textbox(left + Inches(0.18), Inches(2.0), Inches(2.5), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = stg_tag
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = stg_col

        p2 = tf.add_paragraph()
        p2.text = stg_title
        p2.font.size = Pt(15)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_MAIN
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = stg_desc
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = TEXT_MUTED
        p3.space_before = Pt(12)

    # =========================================================================
    # SLIDE 5: PIPELINE DEEP DIVE - DEMAND FORECASTING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_bg(s5)
    add_header(s5, "Pipeline Component A", "Demand Forecasting: Prophet vs. LightGBM", "Dual-engine approach combining seasonal baseline robustness with non-linear feature boosting")

    # Left Card: Pipeline Steps
    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=BRAND_BLUE)
    fb = s5.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.5))
    ftf = fb.text_frame
    ftf.word_wrap = True

    p = ftf.paragraphs[0]
    p.text = "Forecasting Feature Pipeline"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    f_steps = [
        ("Feature Engineering", "Extracts lag windows (t-1, t-7, t-14, t-30), rolling mean/std (7d, 28d), day-of-week seasonality, and promotional impulse flags."),
        ("Prophet Model", "Generalized Additive Model decomposing trend g(t) + seasonality s(t) + holidays h(t). Highly robust to missing observation periods."),
        ("LightGBM Quantile GBDT", "Pinball loss regression across quantiles (α=0.05, 0.50, 0.95). Generates median demand + empirical 95% confidence intervals."),
        ("Cross-Validation Evaluator", "Rolling-origin expanding window evaluation measuring MAPE, RMSE, MAE, and WAPE to benchmark model accuracy.")
    ]
    for title, desc in f_steps:
        p = ftf.add_paragraph()
        p.text = f"• {title}: "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = BRAND_BLUE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = desc
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Card: Sample Forecast Comparison Table / Benchmark
    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=CARD_BORDER)
    rb = s5.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.2), Inches(4.5))
    rtf = rb.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "Model Evaluation & Metrics"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    p_sub = rtf.add_paragraph()
    p_sub.text = "Empirical performance across seeded SKU catalog:"
    p_sub.font.size = Pt(11)
    p_sub.font.color.rgb = TEXT_SUB
    p_sub.space_before = Pt(2)

    skus = [
        ("SKU-MCU-32B (Cortex-M4 MCU)", "Prophet MAPE: 26.3%  |  LightGBM: 22.1% (Winner)", "High weekly cycle"),
        ("SKU-BLE-SOC (BLE 5.3 Module)", "Prophet MAPE: 48.6%  |  LightGBM: 44.8% (Winner)", "Promotional spikes"),
        ("SKU-LENS-4K (Precision Optics)", "Prophet MAPE: 35.8%  |  LightGBM: 38.3% (Prophet Wins)", "Steady baseline"),
        ("SKU-ENC-IP67 (Enclosure)", "Prophet MAPE: 41.2%  |  LightGBM: 32.9% (Winner)", "Non-linear batches")
    ]
    for s_name, s_metric, s_note in skus:
        p = rtf.add_paragraph()
        p.text = s_name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = BRAND_INDIGO
        p.space_before = Pt(7)

        p2 = rtf.add_paragraph()
        p2.text = f"  {s_metric}  [{s_note}]"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: PIPELINE DEEP DIVE - CONTRACT RAG
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_bg(s6)
    add_header(s6, "Pipeline Component B", "Contract RAG: Document Semantic Intelligence", "Unlocking static PDF agreements with vector embeddings and grounded citations")

    rag_cards = [
        ("1. Extraction & Chunking", BRAND_CYAN,
         ["PyMuPDF extracts raw text and structural metadata.",
          "Recursive token-aware chunker (chunk_size=512, overlap=64) preserves legal paragraph semantics.",
          "Attaches metadata: supplier_id, doc_type (contract/SLA/notice), page_number."]),
        ("2. Dense Embeddings", BRAND_BLUE,
         ["FastEmbed BGE-small-en-v1.5 generates 384-dimensional dense vectors.",
          "Runs via local ONNX runtime for ultra-fast, zero-GPU embedding.",
          "LRU Query Cache (2,048 entries) delivers cached queries in <0.8ms."]),
        ("3. Vector Retrieval & Grounding", BRAND_INDIGO,
         ["Qdrant HNSW graph cosine search retrieves Top-K relevant legal snippets.",
          "Payload filtering guarantees queries only search designated vendor contracts.",
          "Groq Llama 3.3 70B synthesizes grounded answer with verifiable citations ([Doc: SLA, p.2])."])
    ]

    for i, (title, col, bullets) in enumerate(rag_cards):
        left = Inches(0.8 + i * 3.95)
        add_card(s6, left, Inches(1.8), Inches(3.8), Inches(4.9), border_color=col)

        box = s6.shapes.add_textbox(left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

        for b in bullets:
            bp = tf.add_paragraph()
            bp.text = f"• {b}"
            bp.font.size = Pt(10.5)
            bp.font.color.rgb = TEXT_MUTED
            bp.space_before = Pt(8)

    # =========================================================================
    # SLIDE 7: PIPELINE DEEP DIVE - RISK ENGINE & CAPITAL
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_bg(s7)
    add_header(s7, "Pipeline Component C", "Composite Risk & Capital Exposure Formulation", "Translating lead times, stock buffers, and contract disruptions into business numbers")

    # Left: Formulas
    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=ACCENT_ROSE)
    rb = s7.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.5))
    rtf = rb.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "Mathematical Formulations"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    formulas = [
        ("Net Inventory Runway", "Stock_net = On_Hand - Allocated + Incoming_PO"),
        ("Lead-Time Demand", "D_LT = Forecast_daily × Supplier_LeadTime_Days"),
        ("Safety Buffer Ratio", "R_buffer = (Stock_net - D_LT) / SafetyStock_min"),
        ("Stockout Risk Score (0-100)", "If R_buffer < 0: min(100, 60 + |R_buffer| × 40)\nIf 0 ≤ R_buffer < 1: 30 + (1 - R_buffer) × 30\nIf R_buffer ≥ 1: max(0, 30 - (R_buffer - 1) × 15)"),
        ("Financial Exposure", "CapitalAtRisk = max(0, D_LT - Stock_net) × UnitCost")
    ]
    for f_title, f_eqn in formulas:
        p = rtf.add_paragraph()
        p.text = f"• {f_title}:"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = BRAND_BLUE
        p.space_before = Pt(5)

        eq = rtf.add_paragraph()
        eq.text = f"   {f_eqn}"
        eq.font.size = Pt(10)
        eq.font.color.rgb = TEXT_MUTED

    # Right: Severity & Prioritization Matrix
    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=ACCENT_AMBER)
    mb = s7.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.2), Inches(4.5))
    mtf = mb.text_frame
    mtf.word_wrap = True

    p = mtf.paragraphs[0]
    p.text = "Automated Severity & Prioritization"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN

    p_sub = mtf.add_paragraph()
    p_sub.text = "Composite Index = 55% Stockout + 30% Supplier + 15% Financial Weight"
    p_sub.font.size = Pt(10.5)
    p_sub.font.bold = True
    p_sub.font.color.rgb = BRAND_INDIGO
    p_sub.space_before = Pt(2)

    sevs = [
        ("CRITICAL (Score ≥ 70)", "Stockout imminent within lead time. Triggers emergency order reorder alerts.", ACCENT_ROSE),
        ("HIGH (50 ≤ Score < 70)", "Safety buffer actively eroding. Approaching replenishment trigger.", ACCENT_AMBER),
        ("MEDIUM (25 ≤ Score < 50)", "Normal lead-time cycle with minor vendor variability.", BRAND_BLUE),
        ("HEALTHY (Score < 25)", "Buffer runway exceeds lead time demand with reliable vendor.", ACCENT_GREEN)
    ]
    for s_label, s_desc, s_color in sevs:
        p = mtf.add_paragraph()
        p.text = s_label
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = s_color
        p.space_before = Pt(6)

        p_d = mtf.add_paragraph()
        p_d.text = f"  {s_desc}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: MID-TERM IMPLEMENTATION STATUS & PROGRESS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_bg(s8)
    add_header(s8, "Current Status", "Mid-Term Implementation Status & Benchmarks", "What has been engineered, integrated, and verified to date")

    # Left Card: Completed Modules
    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=ACCENT_GREEN)
    cb = s8.shapes.add_textbox(Inches(1.05), Inches(2.0), Inches(5.2), Inches(4.5))
    ctf = cb.text_frame
    ctf.word_wrap = True

    p = ctf.paragraphs[0]
    p.text = "100% Completed & Verified Modules"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    items_done = [
        ("FastAPI Backend Core", "All REST endpoints live: /inventory, /forecast, /risk, /chat, /auth, /documents."),
        ("Next.js 14 Frontend", "10 responsive routes compiled with zero build errors and dynamic Recharts visualizer."),
        ("Security & RBAC", "Bcrypt hashing, JWT (HS256) auth, 3 role tiers (Admin, Analyst, Viewer) + 1-Click demo pills."),
        ("Unit & Integration Tests", "28 / 28 automated tests passing in Pytest across ML, RAG, and security suites."),
        ("Database & Vector Seeding", "Initialized with 4 suppliers, 4 SKUs, 1,600 sales records, and indexed contracts.")
    ]
    for head, body in items_done:
        p = ctf.add_paragraph()
        p.text = f"✔ {head}: "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # Right Card: Performance Metrics
    add_card(s8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=BRAND_BLUE)
    pb = s8.shapes.add_textbox(Inches(7.05), Inches(2.0), Inches(5.2), Inches(4.5))
    ptf = pb.text_frame
    ptf.word_wrap = True

    p = ptf.paragraphs[0]
    p.text = "Benchmark & Performance Results"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = BRAND_BLUE

    b_items = [
        ("169x API Latency Speedup", "GET /api/v1/risk dropped from 583ms down to 3.44ms on cache hits."),
        ("Zero N+1 Query Overhead", "Reduced database queries from 3N+1 down to 2 via SQLAlchemy joinedload."),
        ("75-85% Bandwidth Reduction", "GZip response compression middleware deployed on all JSON payloads."),
        ("46% Frontend Bundle Drop", "Dynamic code-splitting reduced initial page JS from 225 kB down to 121 kB."),
        ("Sub-Second Vector Search", "Qdrant HNSW cosine retrieval returns Top-5 clauses in <12ms.")
    ]
    for head, body in b_items:
        p = ptf.add_paragraph()
        p.text = f"⚡ {head}: "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = BRAND_BLUE
        p.space_before = Pt(6)

        run = p.add_run()
        run.text = body
        run.font.bold = False
        run.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 9: REMAINING WORK & ROADMAP TO FINAL EVALUATION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_bg(s9)
    add_header(s9, "Final Phase Roadmap", "Planned Work for Final Evaluation", "Strategic enhancements to expand enterprise readiness between mid and final defense")

    roadmap_steps = [
        ("Phase 1: Direct ERP Connectors", BRAND_BLUE, 
         ["Build bi-directional webhooks for SAP S/4HANA & Oracle NetSuite.",
          "Live synchronization of purchase order receipts and warehouse stock adjustments.",
          "Automated ledger reconciliation with ERP tables."]),
        ("Phase 2: Autonomous Negotiation Agent", BRAND_INDIGO,
         ["Deploy LangGraph / AutoGen multi-agent framework.",
          "Automatically draft supplier contract amendments upon SLA breaches.",
          "Simulate price discount negotiations based on delivery delinquency."]),
        ("Phase 3: Live Macro & Logistics Telemetry", BRAND_CYAN,
         ["Integrate marine AIS satellite shipping data and port congestion APIs.",
          "Dynamically scale supplier lead-time parameters based on Malacca Strait & Suez backlogs.",
          "Automate weather and route disruption factor weighting."]),
        ("Phase 4: Multi-Modal Document RAG", ACCENT_GREEN,
         ["Expand vector pipeline to parse engineering CAD drawings and circuit schematics.",
          "Vision-Language Model (VLM) extraction of ISO compliance and QA inspection stamps.",
          "Automated quality score calculation from factory inspection certificates."])
    ]

    for i, (title, col, bullets) in enumerate(roadmap_steps):
        left = Inches(0.8 + i * 2.95)
        add_card(s9, left, Inches(1.8), Inches(2.85), Inches(4.9), border_color=col)

        box = s9.shapes.add_textbox(left + Inches(0.18), Inches(2.0), Inches(2.5), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN

        for b in bullets:
            bp = tf.add_paragraph()
            bp.text = f"• {b}"
            bp.font.size = Pt(10)
            bp.font.color.rgb = TEXT_MUTED
            bp.space_before = Pt(8)

    # Save to all 3 paths
    paths = [
        os.path.join(r"C:\Users\hp\OneDrive\Desktop\Projects\Rag project", "ContractIQ_Mid_Evaluation_Pipeline.pptx"),
        os.path.join(r"C:\Users\hp\OneDrive\Desktop\Rag project", "ContractIQ_Mid_Evaluation_Pipeline.pptx"),
        os.path.join(r"C:\Users\hp\OneDrive\Desktop", "ContractIQ_Mid_Evaluation_Pipeline.pptx"),
        os.path.join(r"C:\Users\hp\.gemini\antigravity\brain\40bddb9e-75df-4888-bd68-bb8e478c154c", "ContractIQ_Mid_Evaluation_Pipeline.pptx")
    ]
    for p in paths:
        try:
            prs.save(p)
            print(f"Saved: {p}")
        except Exception as e:
            print(f"Error saving {p}: {e}")

if __name__ == "__main__":
    build_mid_eval_presentation()
