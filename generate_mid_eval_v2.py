import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_v2_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # PREMIUM DEEP TECH PALETTE (Executive Navy & Radiant Accents - No Plain White)
    # =========================================================================
    BG_DARK = RGBColor(10, 15, 29)            # Deep Midnight Navy #0A0F1D
    PANEL_DARK = RGBColor(17, 24, 44)         # Slate Navy Panel #11182C
    PANEL_BORDER = RGBColor(30, 41, 69)       # Subtle Border #1E2945
    
    TEXT_TITLE = RGBColor(255, 255, 255)      # Pure Crisp White #FFFFFF
    TEXT_BODY = RGBColor(226, 232, 240)       # Ice Blue / Slate 200 #E2E8F0
    TEXT_MUTED = RGBColor(148, 163, 184)      # Cool Slate 400 #94A3B8
    TEXT_DARK = RGBColor(15, 23, 42)          # For light pill contrast
    
    # Vibrant Accent Colors
    ACCENT_CYAN = RGBColor(0, 229, 255)       # Electric Cyan #00E5FF
    ACCENT_BLUE = RGBColor(59, 130, 246)      # Royal Blue #3B82F6
    ACCENT_INDIGO = RGBColor(99, 102, 241)    # Vivid Indigo #6366F1
    ACCENT_PURPLE = RGBColor(168, 85, 247)    # Neon Purple #A855F7
    ACCENT_EMERALD = RGBColor(16, 185, 129)   # Mint Emerald #10B981
    ACCENT_AMBER = RGBColor(245, 158, 11)     # Amber Gold #F59E0B
    ACCENT_CORAL = RGBColor(244, 63, 94)      # Coral Red #F43F5E

    def apply_bg(slide):
        bg = slide.background
        fill = bg.fill
        fill.solid()
        fill.fore_color.rgb = BG_DARK

    def add_slide_header(slide, tag_text, title_text, subtitle_text=None, tag_color=ACCENT_CYAN):
        # Decorative top glowing strip
        strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.5), Inches(0.04))
        strip.fill.solid()
        strip.fill.fore_color.rgb = tag_color
        strip.line.fill.background()

        # Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.48), Inches(11.7), Inches(0.32))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = tag_color

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.7), Inches(0.55))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_TITLE

        if subtitle_text:
            p_sub = tf_title.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(11.5)
            p_sub.font.color.rgb = TEXT_MUTED
            p_sub.space_before = Pt(3)

    # =========================================================================
    # SLIDE 1: TITLE & TEAM (MID-EVALUATION) — NO BOXES, NO ROLES/WORK
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_bg(s1)

    # Tricolor top ambient bar (Cyan -> Blue -> Indigo)
    b1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.8), Inches(3.9), Inches(0.06))
    b1.fill.solid()
    b1.fill.fore_color.rgb = ACCENT_CYAN
    b1.line.fill.background()

    b2 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.7), Inches(0.8), Inches(3.9), Inches(0.06))
    b2.fill.solid()
    b2.fill.fore_color.rgb = ACCENT_BLUE
    b2.line.fill.background()

    b3 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.6), Inches(0.8), Inches(3.9), Inches(0.06))
    b3.fill.solid()
    b3.fill.fore_color.rgb = ACCENT_INDIGO
    b3.line.fill.background()

    # Title text frame
    tbox = s1.shapes.add_textbox(Inches(0.8), Inches(1.15), Inches(11.7), Inches(2.4))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "CONTRACTIQ"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = TEXT_TITLE

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous Supply Chain Intelligence & Contract Compliance Engine"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_CYAN
    p2.space_before = Pt(4)

    p3 = tf1.add_paragraph()
    p3.text = "PROJECT MID-TERM EVALUATION  •  SYSTEM PIPELINE & ARCHITECTURE DEFENSE"
    p3.font.size = Pt(12)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_INDIGO
    p3.space_before = Pt(8)

    # Subtle horizontal divider line
    div1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.3), Inches(11.7), Inches(0.02))
    div1.fill.solid()
    div1.fill.fore_color.rgb = PANEL_BORDER
    div1.line.fill.background()

    # Left Section: Project Summary (Open Layout with Left Accent Line)
    accent_bar1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.7), Inches(0.06), Inches(2.6))
    accent_bar1.fill.solid()
    accent_bar1.fill.fore_color.rgb = ACCENT_CYAN
    accent_bar1.line.fill.background()

    sum_box = s1.shapes.add_textbox(Inches(1.05), Inches(3.65), Inches(5.6), Inches(2.7))
    stf = sum_box.text_frame
    stf.word_wrap = True

    sp1 = stf.paragraphs[0]
    sp1.text = "EXECUTIVE SCOPE & MID-TERM OBJECTIVE"
    sp1.font.size = Pt(12)
    sp1.font.bold = True
    sp1.font.color.rgb = ACCENT_CYAN

    bullets = [
        ("Core Innovation", "Synchronizing unstructured vendor legal PDF terms with machine-learned demand forecasting."),
        ("Architecture", "Next.js 14 Web Client, FastAPI Async Gateway, Qdrant Vector DB, Prophet & LightGBM."),
        ("Mid-Term Focus", "Pipeline demonstration, data transformations, vector embeddings, and verified risk formulations.")
    ]
    for h, d in bullets:
        bp = stf.add_paragraph()
        bp.text = f"• {h}: "
        bp.font.bold = True
        bp.font.size = Pt(11)
        bp.font.color.rgb = TEXT_TITLE
        bp.space_before = Pt(7)
        r = bp.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Right Section: Project Team Roll Numbers (Clean horizontal badge pills, NO work assigned)
    accent_bar2 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.1), Inches(3.7), Inches(0.06), Inches(2.6))
    accent_bar2.fill.solid()
    accent_bar2.fill.fore_color.rgb = ACCENT_BLUE
    accent_bar2.line.fill.background()

    team_box = s1.shapes.add_textbox(Inches(7.35), Inches(3.65), Inches(5.2), Inches(0.4))
    ttf = team_box.text_frame
    tp = ttf.paragraphs[0]
    tp.text = "PROJECT TEAM MEMBERS"
    tp.font.size = Pt(12)
    tp.font.bold = True
    tp.font.color.rgb = ACCENT_BLUE

    roll_numbers = ["U23AI074", "U23AI079", "U23AI094", "U23AI072"]
    
    # 2x2 Clean Pill Grid for Roll Numbers (No Work Attached)
    pill_w = Inches(2.4)
    pill_h = Inches(0.65)
    coords = [
        (Inches(7.35), Inches(4.3)),
        (Inches(10.05), Inches(4.3)),
        (Inches(7.35), Inches(5.2)),
        (Inches(10.05), Inches(5.2))
    ]
    for i, roll in enumerate(roll_numbers):
        px, py = coords[i]
        pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pill_w, pill_h)
        pill.fill.solid()
        pill.fill.fore_color.rgb = PANEL_DARK
        pill.line.color.rgb = ACCENT_INDIGO
        pill.line.width = Pt(1.5)

        ptf = pill.text_frame
        ptf.word_wrap = False
        pp = ptf.paragraphs[0]
        pp.alignment = PP_ALIGN.CENTER
        pp.text = roll
        pp.font.size = Pt(15)
        pp.font.bold = True
        pp.font.color.rgb = TEXT_TITLE

    # Bottom Technology Banner
    bot_div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.02))
    bot_div.fill.solid()
    bot_div.fill.fore_color.rgb = PANEL_BORDER
    bot_div.line.fill.background()

    tech_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.75), Inches(11.7), Inches(0.35))
    tech_tf = tech_box.text_frame
    tech_p = tech_tf.paragraphs[0]
    tech_p.text = "TECH STACK:  FastAPI Gateway  •  Qdrant Vector DB  •  FastEmbed (BGE 384-d)  •  Prophet & LightGBM  •  Groq Llama 3.3  •  Next.js 14"
    tech_p.font.size = Pt(9.5)
    tech_p.font.bold = True
    tech_p.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT (NO BOXES: SPLIT CONTRAST WITH CIRCULAR BADGES)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_bg(s2)
    add_slide_header(s2, "Problem Context", "The Systemic Operational Blindspot in Modern Supply Chains", 
                     "Critical vendor obligations stay trapped in legal PDFs while inventory planning runs on isolated formulas", ACCENT_CORAL)

    # Left Side: The Core Dilemma (Open Column with Coral Indicator Strip)
    c_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.06), Inches(4.5))
    c_bar.fill.solid()
    c_bar.fill.fore_color.rgb = ACCENT_CORAL
    c_bar.line.fill.background()

    l_box = s2.shapes.add_textbox(Inches(1.05), Inches(1.75), Inches(4.5), Inches(4.6))
    ltf = l_box.text_frame
    ltf.word_wrap = True

    p = ltf.paragraphs[0]
    p.text = "THE CORE FRICTION"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CORAL

    p_body = ltf.add_paragraph()
    p_body.text = "Enterprise ERPs record what is in stock today, but have zero visibility into what supplier contracts legally require."
    p_body.font.size = Pt(11.5)
    p_body.font.color.rgb = TEXT_BODY
    p_body.space_before = Pt(8)

    p_body2 = ltf.add_paragraph()
    p_body2.text = "When sudden demand spikes or shipment disruptions occur, purchasing managers make decisions blind to contractual penalty formulas, lead-time guarantees, or tiered pricing thresholds."
    p_body2.font.size = Pt(11.5)
    p_body2.font.color.rgb = TEXT_MUTED
    p_body2.space_before = Pt(8)

    # Right Side: 3 Operational Gaps (Circular Badges with Open Text Rows)
    gaps = [
        ("01", ACCENT_CORAL, "Unstructured Legal PDF Traps", 
         "SLAs, liquidated damages, delivery grace periods, and minimum order commitments stay buried in dozens of 50-page legal PDFs without automated system linkage."),
        ("02", ACCENT_AMBER, "Naive Moving-Average Forecasting", 
         "Traditional ERPs rely on basic historical averages, failing to capture complex Fourier seasonality, non-linear promotional spikes, or supplier lead-time variance."),
        ("03", ACCENT_CYAN, "Disconnected Financial Risk", 
         "Stockout risks and penalty liabilities are calculated in silos. Procurement teams unknowingly pay massive late-delivery fees or hoard costly excess buffer stock.")
    ]

    y_pos = 1.75
    for num, color, title, desc in gaps:
        # Circular step badge
        circle = s2.shapes.add_shape(MSO_SHAPE.OVAL, Inches(6.0), Inches(y_pos), Inches(0.55), Inches(0.55))
        circle.fill.solid()
        circle.fill.fore_color.rgb = PANEL_DARK
        circle.line.color.rgb = color
        circle.line.width = Pt(1.5)

        ctf = circle.text_frame
        cp = ctf.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        cp.text = num
        cp.font.size = Pt(13)
        cp.font.bold = True
        cp.font.color.rgb = color

        # Gap text
        g_box = s2.shapes.add_textbox(Inches(6.75), Inches(y_pos - 0.05), Inches(5.75), Inches(1.3))
        gtf = g_box.text_frame
        gtf.word_wrap = True

        gp1 = gtf.paragraphs[0]
        gp1.text = title
        gp1.font.size = Pt(13)
        gp1.font.bold = True
        gp1.font.color.rgb = TEXT_TITLE

        gp2 = gtf.add_paragraph()
        gp2.text = desc
        gp2.font.size = Pt(11)
        gp2.font.color.rgb = TEXT_MUTED
        gp2.space_before = Pt(3)

        # Thin divider between rows
        if num != "03":
            div = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.75), Inches(y_pos + 1.25), Inches(5.75), Inches(0.01))
            div.fill.solid()
            div.fill.fore_color.rgb = PANEL_BORDER
            div.line.fill.background()

        y_pos += 1.45

    # Bottom Callout Strip
    bot_strip = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.55), Inches(11.7), Inches(0.45))
    bot_strip.fill.solid()
    bot_strip.fill.fore_color.rgb = PANEL_DARK
    bot_strip.line.color.rgb = ACCENT_CORAL
    bot_strip.line.width = Pt(1)

    bstf = bot_strip.text_frame
    bp = bstf.paragraphs[0]
    bp.alignment = PP_ALIGN.CENTER
    bp.text = "MID-EVALUATION MISSION: Unify semantic contract intelligence with high-precision time-series forecasting."
    bp.font.size = Pt(10.5)
    bp.font.bold = True
    bp.font.color.rgb = ACCENT_CORAL

    # =========================================================================
    # SLIDE 3: SYSTEM STRUCTURE (HORIZONTAL ARCHITECTURE BANDS + FLOW CONNECTORS)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_bg(s3)
    add_slide_header(s3, "System Structure", "Decoupled 3-Tier Enterprise Architecture", 
                     "Modular microservice layers separating reactive presentation, orchestration gateway, and intelligence engines", ACCENT_BLUE)

    tiers = [
        ("TIER 1: PRESENTATION & REAL-TIME CLIENT", ACCENT_CYAN, "Next.js 14 Web Application",
         "React 18 Server Components (RSC) for instantaneous dashboard hydration.",
         "Server-Sent Events (SSE) streaming listener for live stockout notifications and AI risk reasoning.",
         "TailwindCSS responsive design with dynamic code-splitting and asset optimization."),
        
        ("TIER 2: ORCHESTRATION & SECURITY GATEWAY", ACCENT_BLUE, "FastAPI Async Gateway (Port 8000)",
         "High-throughput non-blocking asynchronous REST endpoints with Pydantic v2 strict schema validation.",
         "In-memory LRU caching layer reducing repeat forecasting and inventory query latency by 169x.",
         "Cross-Origin Resource Sharing (CORS) controls, error boundaries, and background job coordination."),
        
        ("TIER 3: ANALYTICAL & VECTOR SERVICES", ACCENT_INDIGO, "Dual ML Engines & Qdrant Vector DB",
         "Forecasting Engine: Facebook Prophet (Fourier Seasonality) & LightGBM (Quantile GBDT Regression).",
         "Vector Store: Qdrant Vector DB executing sub-12ms Cosine similarity queries over HNSW graphs.",
         "LLM Grounding: Groq Llama 3.3 70B generating zero-hallucination compliance citations.")
    ]

    y_pos = 1.75
    for tag, color, headline, pt1, pt2, pt3 in tiers:
        # Tier Left Accent Strip
        t_bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y_pos), Inches(0.08), Inches(1.3))
        t_bar.fill.solid()
        t_bar.fill.fore_color.rgb = color
        t_bar.line.fill.background()

        # Background Tint Panel (Not a box with borders, just an elegant slate ribbon)
        ribbon = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.88), Inches(y_pos), Inches(11.62), Inches(1.3))
        ribbon.fill.solid()
        ribbon.fill.fore_color.rgb = PANEL_DARK
        ribbon.line.fill.background()

        # Content inside ribbon
        t_box = s3.shapes.add_textbox(Inches(1.05), Inches(y_pos + 0.05), Inches(11.3), Inches(1.2))
        ttf = t_box.text_frame
        ttf.word_wrap = True

        p1 = ttf.paragraphs[0]
        p1.text = tag
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = color

        p2 = ttf.add_paragraph()
        p2.text = f"{headline}  —  "
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = TEXT_TITLE

        r1 = p2.add_run()
        r1.text = f"1) {pt1}  "
        r1.font.bold = False
        r1.font.color.rgb = TEXT_BODY

        r2 = p2.add_run()
        r2.text = f"2) {pt2}  "
        r2.font.bold = False
        r2.font.color.rgb = TEXT_MUTED

        r3 = p2.add_run()
        r3.text = f"3) {pt3}"
        r3.font.bold = False
        r3.font.color.rgb = TEXT_BODY

        # Connector between tiers
        if tag != tiers[-1][0]:
            conn = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.5), Inches(y_pos + 1.3), Inches(0.03), Inches(0.2))
            conn.fill.solid()
            conn.fill.fore_color.rgb = ACCENT_BLUE
            conn.line.fill.background()

        y_pos += 1.5

    # Bottom summary tag
    bot_note = s3.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.4))
    bntf = bot_note.text_frame
    bnp = bntf.paragraphs[0]
    bnp.alignment = PP_ALIGN.CENTER
    bnp.text = "Communication Protocols: HTTP/2 REST for control plane  •  Server-Sent Events (SSE) for data plane  •  ONNX Runtime for local vector execution"
    bnp.font.size = Pt(10)
    bnp.font.bold = True
    bnp.font.color.rgb = ACCENT_CYAN

    # =========================================================================
    # SLIDE 4: END-TO-END DATA PIPELINE (HORIZONTAL PIPELINE FLOW WITH CHEVRONS)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_bg(s4)
    add_slide_header(s4, "Data Pipeline", "End-to-End Pipeline: Ingestion to Executive Advisory", 
                     "Four continuous stages transforming unstructured PDFs and time-series data into actionable risk metrics", ACCENT_CYAN)

    # 4 Pipeline Stages (Horizontal Process Ribbon)
    stages = [
        ("STAGE 01", "INGESTION & CLEANING", ACCENT_EMERALD, [
            "Vendor PDF Parsing: PyMuPDF extracts text, headings & tables.",
            "Time-Series Sales: Daily sales CSV parsed & validated.",
            "Schema Enforcement: Missing value forward-fill & date normalization."
        ]),
        ("STAGE 02", "VECTOR & FEATURE PIPELINE", ACCENT_CYAN, [
            "Semantic Chunking: 512-token chunks with 64-token overlap.",
            "FastEmbed Vectorization: 384-d dense vectors generated on ONNX.",
            "Lag Features: 7, 14, 30-day moving averages and rolling std dev."
        ]),
        ("STAGE 03", "DUAL INFERENCE ENGINES", ACCENT_BLUE, [
            "Contract RAG: Qdrant HNSW cosine search retrieves top-k clauses.",
            "Demand Forecast: Prophet (seasonality) & LightGBM (quantiles).",
            "Uncertainty Bounds: P10 (pessimistic), P50, and P90 (surge) outputs."
        ]),
        ("STAGE 04", "SYNTHESIS & ADVISORY", ACCENT_AMBER, [
            "Risk Scoring: Lead-time demand vs. effective stock formula.",
            "Penalty Assessment: LLM extracts liquidated damage penalty %.",
            "Executive Action: Reorder recommendations streamed to Next.js."
        ])
    ]

    col_w = Inches(2.7)
    gap = Inches(0.28)
    left_start = Inches(0.8)

    for i, (stage_num, stage_title, color, bullets) in enumerate(stages):
        x = left_start + i * (col_w + gap)

        # Top Accent Header Bar
        top_bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, Inches(1.8), col_w, Inches(0.08))
        top_bar.fill.solid()
        top_bar.fill.fore_color.rgb = color
        top_bar.line.fill.background()

        # Step Number Badge
        num_badge = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.95), Inches(1.1), Inches(0.32))
        num_badge.fill.solid()
        num_badge.fill.fore_color.rgb = PANEL_DARK
        num_badge.line.color.rgb = color
        num_badge.line.width = Pt(1)

        ntf = num_badge.text_frame
        np = ntf.paragraphs[0]
        np.alignment = PP_ALIGN.CENTER
        np.text = stage_num
        np.font.size = Pt(9)
        np.font.bold = True
        np.font.color.rgb = color

        # Stage Title
        t_box = s4.shapes.add_textbox(x, Inches(2.35), col_w, Inches(0.6))
        ttf = t_box.text_frame
        ttf.word_wrap = True
        tp = ttf.paragraphs[0]
        tp.text = stage_title
        tp.font.size = Pt(12)
        tp.font.bold = True
        tp.font.color.rgb = TEXT_TITLE

        # Content List
        c_box = s4.shapes.add_textbox(x, Inches(3.05), col_w, Inches(3.2))
        ctf = c_box.text_frame
        ctf.word_wrap = True

        for j, b in enumerate(bullets):
            bp = ctf.add_paragraph() if j > 0 else ctf.paragraphs[0]
            bp.text = f"▸ {b}"
            bp.font.size = Pt(10)
            bp.font.color.rgb = TEXT_BODY
            bp.space_before = Pt(6)

        # Right arrow connector between columns
        if i < 3:
            arrow = s4.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x + col_w + Inches(0.06), Inches(2.0), Inches(0.16), Inches(0.2))
            arrow.fill.solid()
            arrow.fill.fore_color.rgb = ACCENT_INDIGO
            arrow.line.fill.background()

    # Bottom Pipeline Summary
    bot_pipe = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.45))
    bot_pipe.fill.solid()
    bot_pipe.fill.fore_color.rgb = PANEL_DARK
    bot_pipe.line.color.rgb = ACCENT_CYAN
    bot_pipe.line.width = Pt(1)

    bptf = bot_pipe.text_frame
    bpp = bptf.paragraphs[0]
    bpp.alignment = PP_ALIGN.CENTER
    bpp.text = "Pipeline Speed: < 50ms total inference pipeline execution  •  Deterministic Schemas  •  End-to-End Type Safety"
    bpp.font.size = Pt(10.5)
    bpp.font.bold = True
    bpp.font.color.rgb = ACCENT_CYAN

    # =========================================================================
    # SLIDE 5: PIPELINE DEEP DIVE 1 — FORECASTING (SPLIT PILLARS + SYNTHESIS)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_bg(s5)
    add_slide_header(s5, "Pipeline Deep Dive 1", "Demand Forecasting: Prophet vs. LightGBM Quantile GBDT", 
                     "A hybrid approach coupling macroeconomic seasonality with high-frequency quantile regression", ACCENT_PURPLE)

    # Left Pillar: Facebook Prophet
    lp_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.8), Inches(0.08), Inches(4.3))
    lp_bar.fill.solid()
    lp_bar.fill.fore_color.rgb = ACCENT_CYAN
    lp_bar.line.fill.background()

    l_box = s5.shapes.add_textbox(Inches(1.05), Inches(1.8), Inches(5.3), Inches(4.3))
    ltf = l_box.text_frame
    ltf.word_wrap = True

    p = ltf.paragraphs[0]
    p.text = "FACEBOOK PROPHET ENGINE"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_CYAN

    prophet_items = [
        ("Fourier Harmonic Decomposition", "Captures recurring weekly and yearly seasonal patterns: y(t) = g(t) + s(t) + h(t) + ε_t."),
        ("Automated Changepoint Detection", "Identifies shifts in sales velocity due to marketing campaigns or macroeconomic shocks."),
        ("Missing Data Resilience", "Natively interpolates missing dates without requiring artificial synthetic zero-fill."),
        ("Primary Role in System", "Macro-level quarterly capacity planning and baseline demand trend estimation.")
    ]
    for h, d in prophet_items:
        bp = ltf.add_paragraph()
        bp.text = f"• {h}: "
        bp.font.bold = True
        bp.font.size = Pt(10.5)
        bp.font.color.rgb = TEXT_TITLE
        bp.space_before = Pt(8)
        r = bp.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Right Pillar: LightGBM Quantile GBDT
    rp_bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.0), Inches(1.8), Inches(0.08), Inches(4.3))
    rp_bar.fill.solid()
    rp_bar.fill.fore_color.rgb = ACCENT_PURPLE
    rp_bar.line.fill.background()

    r_box = s5.shapes.add_textbox(Inches(7.25), Inches(1.8), Inches(5.3), Inches(4.3))
    rtf = r_box.text_frame
    rtf.word_wrap = True

    p = rtf.paragraphs[0]
    p.text = "LIGHTGBM QUANTILE GBDT"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE

    lgbm_items = [
        ("Quantile Loss Formulation", "Trained on pinball loss to output calibrated intervals: P10 (conservative), P50 (median), P90 (surge)."),
        ("Engineered Lag Features", "7-day, 14-day, and 30-day rolling averages, rolling standard deviations, and day-of-week indicators."),
        ("Sub-Millisecond Inference", "Executes tree-based inference in under 5ms, ideal for live dashboard interactive sliders."),
        ("Primary Role in System", "High-frequency operational replenishment and dynamic safety buffer sizing.")
    ]
    for h, d in lgbm_items:
        bp = rtf.add_paragraph()
        bp.text = f"• {h}: "
        bp.font.bold = True
        bp.font.size = Pt(10.5)
        bp.font.color.rgb = TEXT_TITLE
        bp.space_before = Pt(8)
        r = bp.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # Bottom Synthesis Banner
    bot_syn = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.35), Inches(11.7), Inches(0.65))
    bot_syn.fill.solid()
    bot_syn.fill.fore_color.rgb = PANEL_DARK
    bot_syn.line.color.rgb = ACCENT_INDIGO
    bot_syn.line.width = Pt(1)

    bstf = bot_syn.text_frame
    bsp = bstf.paragraphs[0]
    bsp.alignment = PP_ALIGN.CENTER
    bsp.text = "ENSEMBLE DECISION: Prophet establishes the seasonal baseline; LightGBM P90 sets the risk-adjusted replenishment ceiling."
    bsp.font.size = Pt(10.5)
    bsp.font.bold = True
    bsp.font.color.rgb = ACCENT_CYAN

    # =========================================================================
    # SLIDE 6: PIPELINE DEEP DIVE 2 — RAG (PROCESS TIMELINE & GROUNDING GUARDRAIL)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_bg(s6)
    add_slide_header(s6, "Pipeline Deep Dive 2", "Contract Compliance RAG: PDF to Grounded Citations", 
                     "Zero-hallucination semantic retrieval architecture with strict contextual citation constraints", ACCENT_CYAN)

    # 4 Horizontal Pipeline Step Tiles (Not boxed, minimalist tiles with color tops)
    rag_steps = [
        ("01", "PyMuPDF Extraction", ACCENT_CYAN, "Extracts raw text, table structures, and page coordinates from vendor agreements."),
        ("02", "FastEmbed ONNX", ACCENT_BLUE, "Generates 384-d dense vectors locally using BAAI/bge-small-en-v1.5 with zero external API calls."),
        ("03", "Qdrant HNSW Graph", ACCENT_INDIGO, "Cos-similarity vector indexing delivering top-k semantic matches in < 12ms."),
        ("04", "Groq Llama 3.3 70B", ACCENT_EMERALD, "Reasoning model constrained to retrieved text; extracts SLA %, lead-time, and penalties.")
    ]

    tile_w = Inches(2.7)
    tile_gap = Inches(0.28)
    for i, (num, title, color, desc) in enumerate(rag_steps):
        tx = Inches(0.8) + i * (tile_w + tile_gap)
        
        # Color top line
        t_line = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, tx, Inches(1.8), tile_w, Inches(0.06))
        t_line.fill.solid()
        t_line.fill.fore_color.rgb = color
        t_line.line.fill.background()

        # Step number & title box
        s_box = s6.shapes.add_textbox(tx, Inches(1.95), tile_w, Inches(1.5))
        stf = s_box.text_frame
        stf.word_wrap = True

        sp1 = stf.paragraphs[0]
        sp1.text = f"STEP {num}"
        sp1.font.size = Pt(10)
        sp1.font.bold = True
        sp1.font.color.rgb = color

        sp2 = stf.add_paragraph()
        sp2.text = title
        sp2.font.size = Pt(12)
        sp2.font.bold = True
        sp2.font.color.rgb = TEXT_TITLE
        sp2.space_before = Pt(2)

        sp3 = stf.add_paragraph()
        sp3.text = desc
        sp3.font.size = Pt(10)
        sp3.font.color.rgb = TEXT_MUTED
        sp3.space_before = Pt(4)

        # Arrow connector
        if i < 3:
            arr = s6.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, tx + tile_w + Inches(0.06), Inches(2.2), Inches(0.16), Inches(0.2))
            arr.fill.solid()
            arr.fill.fore_color.rgb = ACCENT_INDIGO
            arr.line.fill.background()

    # Grounding Guardrail Callout (Distinct dark slate banner with cyan left accent)
    g_bar = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.9), Inches(0.08), Inches(2.8))
    g_bar.fill.solid()
    g_bar.fill.fore_color.rgb = ACCENT_CYAN
    g_bar.line.fill.background()

    callout_box = s6.shapes.add_textbox(Inches(1.05), Inches(3.85), Inches(11.4), Inches(2.8))
    ctf = callout_box.text_frame
    ctf.word_wrap = True

    cp1 = ctf.paragraphs[0]
    cp1.text = "STRICT CITATION & ZERO-HALLUCINATION ARCHITECTURE"
    cp1.font.size = Pt(12)
    cp1.font.bold = True
    cp1.font.color.rgb = ACCENT_CYAN

    guardrails = [
        ("Citation Requirement", "Every extracted penalty or SLA threshold must link back to an exact clause and page number (e.g., Section 7.2, Page 14)."),
        ("Explicit Fallback Mechanism", "If a contract clause is ambiguous or absent from retrieved chunks, the prompt forces the LLM to output 'Clause Not Specified' rather than guessing."),
        ("Speed & Cost Optimization", "Local ONNX FastEmbed generates vectors in 8ms with zero API token cost, ensuring confidential supplier agreements never leave the enterprise boundary.")
    ]
    for h, d in guardrails:
        bp = ctf.add_paragraph()
        bp.text = f"• {h}: "
        bp.font.bold = True
        bp.font.size = Pt(11)
        bp.font.color.rgb = TEXT_TITLE
        bp.space_before = Pt(6)
        r = bp.add_run()
        r.text = d
        r.font.bold = False
        r.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 7: PIPELINE DEEP DIVE 3 — RISK & CAPITAL FORMULATIONS (FORMULA STRIPS)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_bg(s7)
    add_slide_header(s7, "Pipeline Deep Dive 3", "Inventory Risk Engine & Financial Formulations", 
                     "Deterministic mathematical formulas transforming forecast quantiles into operational risk scores", ACCENT_AMBER)

    formulas = [
        ("01", ACCENT_CYAN, "Effective Net Inventory (I_eff)", 
         "I_eff = I_on_hand + I_in_transit - Backorders",
         "Considers pipeline shipments already dispatched while deducting unfulfilled purchase commitments to prevent false stockout panics."),
        
        ("02", ACCENT_BLUE, "Lead-Time Demand Buffer (D_LT)", 
         "D_LT = (μ_daily × L) + (Z × σ_daily × √L)",
         "Calculates safety stock buffer scaled to supplier lead-time variance (L) and statistical service level Z (e.g., Z = 1.65 for 95% service level)."),
        
        ("03", ACCENT_AMBER, "Normalized Stockout Risk Score (0 - 100)", 
         "Risk = min( 100, max( 0, ((D_LT - I_eff) / D_LT) × 100 ) )",
         "Scores urgency dynamically: Score < 30 (Safe - Emerald), 30-70 (Moderate - Amber), > 70 (Critical Stockout Danger - Coral)."),
        
        ("04", ACCENT_CORAL, "Capital at Risk / Penalty Exposure ($)", 
         "Capital Exposure = Penalty Rate × Deficit Units × Unit Price",
         "Directly multiplies legal SLA breach penalties extracted by RAG against forecasted unfulfilled unit volumes.")
    ]

    y_pos = 1.75
    for num, color, name, math, logic in formulas:
        # Left Accent Strip
        f_strip = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(y_pos), Inches(0.06), Inches(1.05))
        f_strip.fill.solid()
        f_strip.fill.fore_color.rgb = color
        f_strip.line.fill.background()

        # Content Box
        f_box = s7.shapes.add_textbox(Inches(1.0), Inches(y_pos - 0.05), Inches(11.5), Inches(1.1))
        ftf = f_box.text_frame
        ftf.word_wrap = True

        fp1 = ftf.paragraphs[0]
        fp1.text = f"{num}. {name.upper()}"
        fp1.font.size = Pt(11)
        fp1.font.bold = True
        fp1.font.color.rgb = color

        fp2 = ftf.add_paragraph()
        fp2.text = f"FORMULA:  {math}"
        fp2.font.size = Pt(12)
        fp2.font.bold = True
        fp2.font.color.rgb = TEXT_TITLE
        fp2.space_before = Pt(2)

        fp3 = ftf.add_paragraph()
        fp3.text = f"LOGIC: {logic}"
        fp3.font.size = Pt(10)
        fp3.font.color.rgb = TEXT_MUTED
        fp3.space_before = Pt(2)

        # Divider between formulas
        if num != "04":
            div = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(y_pos + 1.15), Inches(11.5), Inches(0.01))
            div.fill.solid()
            div.fill.fore_color.rgb = PANEL_BORDER
            div.line.fill.background()

        y_pos += 1.25

    # =========================================================================
    # SLIDE 8: MID-TERM IMPLEMENTATION STATUS & BENCHMARKS (HERO KPIS + CHECKLIST)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_bg(s8)
    add_slide_header(s8, "Mid-Term Milestones", "Implementation Status & Verified Benchmarks", 
                     "Current functional milestone verification, test coverage, and latency benchmarks", ACCENT_EMERALD)

    # 3 Big Hero KPI Blocks (Open Minimalist Stats - No Clunky Boxes)
    kpis = [
        ("28 / 28", ACCENT_EMERALD, "Automated Tests Passing", "100% test coverage across RAG pipeline, forecasting modules, and API route schemas."),
        ("169×", ACCENT_CYAN, "Cache Acceleration", "In-memory LRU cache reduces recurring inventory calculation latency from 380ms down to 2.2ms."),
        ("< 12ms", ACCENT_INDIGO, "Vector Retrieval Latency", "Local ONNX FastEmbed embedding generation and Qdrant HNSW cosine similarity search.")
    ]

    kw = Inches(3.6)
    kgap = Inches(0.45)
    for i, (val, color, title, desc) in enumerate(kpis):
        kx = Inches(0.8) + i * (kw + kgap)

        k_box = s8.shapes.add_textbox(kx, Inches(1.8), kw, Inches(1.8))
        ktf = k_box.text_frame
        ktf.word_wrap = True

        kp1 = ktf.paragraphs[0]
        kp1.text = val
        kp1.font.size = Pt(36)
        kp1.font.bold = True
        kp1.font.color.rgb = color

        kp2 = ktf.add_paragraph()
        kp2.text = title
        kp2.font.size = Pt(12)
        kp2.font.bold = True
        kp2.font.color.rgb = TEXT_TITLE
        kp2.space_before = Pt(2)

        kp3 = ktf.add_paragraph()
        kp3.text = desc
        kp3.font.size = Pt(10)
        kp3.font.color.rgb = TEXT_MUTED
        kp3.space_before = Pt(4)

    # Divider Line
    mid_div = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.9), Inches(11.7), Inches(0.02))
    mid_div.fill.solid()
    mid_div.fill.fore_color.rgb = PANEL_BORDER
    mid_div.line.fill.background()

    # Live Working Capabilities Checklist
    c_header = s8.shapes.add_textbox(Inches(0.8), Inches(4.1), Inches(11.7), Inches(0.4))
    ch_tf = c_header.text_frame
    ch_p = ch_tf.paragraphs[0]
    ch_p.text = "FUNCTIONAL SYSTEM CAPABILITIES (DEPLOYED & DEMONSTRABLE TODAY)"
    ch_p.font.size = Pt(11)
    ch_p.font.bold = True
    ch_p.font.color.rgb = ACCENT_EMERALD

    capabilities = [
        "Dynamic Ingestion: Automatic parsing of multi-page PDF contracts and tabular sales history CSVs.",
        "Real-Time Risk Engine: Live recalculation of effective stock, lead-time buffers, and stockout scores.",
        "Interactive UI Dashboard: Next.js 14 interface with interactive Prophet & LightGBM forecast charts.",
        "Contract Question-Answering: Semantic search over indexed clauses with exact page references.",
        "Streaming AI Insights: Server-Sent Events (SSE) pipe streaming executive recommendations directly to UI."
    ]

    for i, cap in enumerate(capabilities):
        row_y = Inches(4.55 + i * 0.42)

        # Checkmark icon badge
        chk = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), row_y, Inches(0.32), Inches(0.32))
        chk.fill.solid()
        chk.fill.fore_color.rgb = PANEL_DARK
        chk.line.color.rgb = ACCENT_EMERALD
        chk.line.width = Pt(1)

        ctf = chk.text_frame
        cp = ctf.paragraphs[0]
        cp.alignment = PP_ALIGN.CENTER
        cp.text = "✓"
        cp.font.size = Pt(12)
        cp.font.bold = True
        cp.font.color.rgb = ACCENT_EMERALD

        # Capability description
        r_box = s8.shapes.add_textbox(Inches(1.25), row_y - Inches(0.05), Inches(11.2), Inches(0.35))
        rtf = r_box.text_frame
        rp = rtf.paragraphs[0]
        rp.text = cap
        rp.font.size = Pt(10.5)
        rp.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 9: MID-TO-FINAL EVALUATION ROADMAP (HORIZONTAL TIMELINE TRACK)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_bg(s9)
    add_slide_header(s9, "Project Roadmap", "Path to Final Evaluation & Production Readiness", 
                     "Phased development timeline from working mid-term foundation to autonomous multi-agent production", ACCENT_INDIGO)

    # Horizontal Timeline Connecting Rail
    track = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.2), Inches(2.2), Inches(10.9), Inches(0.06))
    track.fill.solid()
    track.fill.fore_color.rgb = PANEL_BORDER
    track.line.fill.background()

    phases = [
        ("PHASE 01 (COMPLETED)", "Mid-Term Milestone", ACCENT_EMERALD, [
            "Core 3-tier architecture operational.",
            "FastEmbed local ONNX vector pipeline.",
            "Prophet & LightGBM dual inference.",
            "28 automated unit tests passing.",
            "Next.js 14 reactive dashboard live."
        ]),
        ("PHASE 02 (IN PROGRESS)", "Multi-Agent Simulation", ACCENT_CYAN, [
            "Supplier negotiation simulator agent.",
            "Multi-contract conflicting clause analysis.",
            "Real-time ERP webhook listeners.",
            "Automated reorder PO generation.",
            "Dynamic SLA threshold alerts."
        ]),
        ("PHASE 03 (FINAL PHASE)", "Production Deployment", ACCENT_INDIGO, [
            "Live maritime AIS port tracking API.",
            "Multi-modal inspection image ingestion.",
            "Enterprise OAuth2 / SSO RBAC.",
            "Docker Compose & Helm production charts.",
            "End-to-end user evaluation study."
        ])
    ]

    pw = Inches(3.6)
    pgap = Inches(0.4)
    for i, (phase_tag, phase_title, color, items) in enumerate(phases):
        px = Inches(0.8) + i * (pw + pgap)

        # Circular milestone node on the timeline rail
        node = s9.shapes.add_shape(MSO_SHAPE.OVAL, px + Inches(0.2), Inches(2.05), Inches(0.36), Inches(0.36))
        node.fill.solid()
        node.fill.fore_color.rgb = color
        node.line.fill.background()

        # Phase tag
        p_box = s9.shapes.add_textbox(px, Inches(2.55), pw, Inches(0.6))
        ptf = p_box.text_frame
        ptf.word_wrap = True

        pp1 = ptf.paragraphs[0]
        pp1.text = phase_tag
        pp1.font.size = Pt(10)
        pp1.font.bold = True
        pp1.font.color.rgb = color

        pp2 = ptf.add_paragraph()
        pp2.text = phase_title
        pp2.font.size = Pt(13)
        pp2.font.bold = True
        pp2.font.color.rgb = TEXT_TITLE
        pp2.space_before = Pt(2)

        # Phase checklist
        c_box = s9.shapes.add_textbox(px, Inches(3.25), pw, Inches(3.5))
        ctf = c_box.text_frame
        ctf.word_wrap = True

        for j, it in enumerate(items):
            ip = ctf.add_paragraph() if j > 0 else ctf.paragraphs[0]
            ip.text = f"• {it}"
            ip.font.size = Pt(10.5)
            ip.font.color.rgb = TEXT_BODY
            ip.space_before = Pt(6)

    # Save outputs to target directories
    out_dir_projects = r"C:\Users\hp\OneDrive\Desktop\Projects\Rag project"
    out_dir_desktop = r"C:\Users\hp\OneDrive\Desktop"
    out_dir_rag = r"C:\Users\hp\OneDrive\Desktop\Rag project"
    out_dir_brain = r"C:\Users\hp\.gemini\antigravity\brain\40bddb9e-75df-4888-bd68-bb8e478c154c"

    filename = "ContractIQ_Mid_Evaluation_Pipeline.pptx"

    for d in [out_dir_desktop, out_dir_projects, out_dir_brain, out_dir_rag]:
        if os.path.exists(d):
            target = os.path.join(d, filename)
            try:
                prs.save(target)
                print(f"Saved successfully: {target}")
            except Exception as e:
                print(f"Warning: Could not save to {target}: {e}")

if __name__ == "__main__":
    build_v2_presentation()
    print("V2 Mid-Evaluation presentation built successfully!")
