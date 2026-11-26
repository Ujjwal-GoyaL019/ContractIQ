import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide

    # Color Palette: Obsidian / Cyan / Sky / Indigo
    BG_COLOR = RGBColor(10, 15, 29)          # Deep Obsidian Navy
    CARD_BG = RGBColor(17, 24, 39)           # Slate 900
    CARD_BORDER = RGBColor(30, 41, 59)       # Slate 800
    CYAN = RGBColor(6, 182, 212)             # Brand Cyan
    SKY = RGBColor(56, 189, 248)             # Brand Sky Blue
    INDIGO = RGBColor(99, 102, 241)          # Brand Indigo
    WHITE = RGBColor(255, 255, 255)
    MUTED = RGBColor(148, 163, 184)          # Slate 400
    LIGHT_MUTED = RGBColor(203, 213, 225)    # Slate 300
    GREEN = RGBColor(16, 185, 129)           # Emerald Green
    ROSE = RGBColor(244, 63, 94)             # Rose Red
    GOLD = RGBColor(245, 158, 11)            # Amber Gold

    def set_slide_background(slide):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

    def add_header(slide, tag_text, title_text, subtitle_text=None):
        # Header Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        tf_tag.margin_left = tf_tag.margin_top = tf_tag.margin_right = tf_tag.margin_bottom = 0
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = CYAN

        # Header Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_top = tf_title.margin_right = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        if subtitle_text:
            p_sub = tf_title.add_paragraph()
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = MUTED
            p_sub.space_before = Pt(4)

    def add_card(slide, left, top, width, height, title=None, border_color=CARD_BORDER, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Accent decorative glow rectangle
    glow = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(0.15), Inches(4.8))
    glow.fill.solid()
    glow.fill.fore_color.rgb = CYAN
    glow.line.fill.background()

    # Title box
    tbox = s1.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11.3), Inches(2.2))
    tf1 = tbox.text_frame
    tf1.word_wrap = True
    
    p = tf1.paragraphs[0]
    p.text = "CONTRACTIQ"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = WHITE

    p2 = tf1.add_paragraph()
    p2.text = "Autonomous AI Supply Chain & Risk Advisor"
    p2.font.size = Pt(26)
    p2.font.bold = True
    p2.font.color.rgb = SKY
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "A Unified Framework for Dual Time-Series Demand Forecasting (Prophet + LightGBM), Multi-Factor Risk Assessment, and Grounded Supplier Contract RAG Intelligence"
    p3.font.size = Pt(14)
    p3.font.color.rgb = MUTED
    p3.space_before = Pt(12)

    # Evaluation Card
    add_card(s1, Inches(1.2), Inches(3.8), Inches(11.3), Inches(2.8), border_color=CYAN)
    
    eval_box = s1.shapes.add_textbox(Inches(1.5), Inches(4.0), Inches(5.0), Inches(2.4))
    etf = eval_box.text_frame
    etf.word_wrap = True
    
    ep1 = etf.paragraphs[0]
    ep1.text = "PROJECT EVALUATION PHASE"
    ep1.font.size = Pt(12)
    ep1.font.bold = True
    ep1.font.color.rgb = GOLD
    
    ep2 = etf.add_paragraph()
    ep2.text = "Domain: Artificial Intelligence / Supply Chain & Operations"
    ep2.font.size = Pt(13)
    ep2.font.color.rgb = WHITE
    ep2.space_before = Pt(6)

    ep3 = etf.add_paragraph()
    ep3.text = "Architecture: Next.js 14 • FastAPI • Qdrant HNSW • Groq Llama 3.3 70B"
    ep3.font.size = Pt(12)
    ep3.font.color.rgb = MUTED
    ep3.space_before = Pt(4)

    ep4 = etf.add_paragraph()
    ep4.text = "Status: 100% Verified (28/28 Unit & System Tests Passing)"
    ep4.font.size = Pt(12)
    ep4.font.bold = True
    ep4.font.color.rgb = GREEN
    ep4.space_before = Pt(6)

    # Team Roll Numbers Box
    team_box = s1.shapes.add_textbox(Inches(7.0), Inches(4.0), Inches(5.0), Inches(2.4))
    ttf = team_box.text_frame
    ttf.word_wrap = True

    tp1 = ttf.paragraphs[0]
    tp1.text = "PROJECT TEAM (ROLL NUMBERS):"
    tp1.font.size = Pt(12)
    tp1.font.bold = True
    tp1.font.color.rgb = CYAN

    roll_numbers = [
        ("U23AI074", "Demand Forecasting & Feature Engineering Pipeline"),
        ("U23AI079", "Retrieval-Augmented Generation (RAG) & Vector Database"),
        ("U23AI094", "Supply Chain Multi-Factor Risk & Prioritization Engine"),
        ("U23AI072", "Full-Stack System Architecture, RBAC & API Gateway")
    ]

    for roll, role in roll_numbers:
        rp = ttf.add_paragraph()
        rp.text = f"•  {roll}  —  {role}"
        rp.font.size = Pt(12)
        rp.font.bold = True
        rp.font.color.rgb = WHITE
        rp.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: MOTIVATION & PROBLEM STATEMENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Context & Motivation", "The Enterprise Supply Chain Challenge", "Why modern manufacturing and distribution networks face catastrophic stockouts")

    cards_data = [
        ("Siloed Unstructured Contracts", "Legal & Procurement Blindspot", 
         ["Master supply agreements, force majeure notices, and delivery SLAs are trapped in static PDFs.", 
          "Procurement teams miss lead-time extension notices (e.g. 21 to 42 days) until assembly lines halt.",
          "Lack of semantic linking between contractual obligations and active inventory."], ROSE),
        ("Unreliable Demand Forecasting", "Over-Reliance on Moving Averages",
         ["Spreadsheet-based models fail to capture weekly/yearly seasonality and promotion spikes.",
          "Single-point forecasts ignore downside prediction bounds (quantile variance).",
          "Result: Either millions in trapped working capital or sudden out-of-stock shortages."], GOLD),
        ("Disjointed Risk Evaluation", "Reactive Instead of Proactive",
         ["Stock levels, vendor reliability, and demand velocity are evaluated in isolated dashboards.",
          "No automated quantification of 'Capital at Risk' across critical SKUs.",
          "Decisions are made after stockouts occur rather than during lead-time windows."], SKY)
    ]

    for i, (title, sub, bullets, color) in enumerate(cards_data):
        left = Inches(0.8 + i * 3.95)
        add_card(s2, left, Inches(1.8), Inches(3.8), Inches(4.9), border_color=color)
        
        box = s2.shapes.add_textbox(left + Inches(0.25), Inches(2.0), Inches(3.3), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = WHITE
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = color
        p_sub.space_before = Pt(3)

        for b in bullets:
            bp = tf.add_paragraph()
            bp.text = f"• {b}"
            bp.font.size = Pt(11)
            bp.font.color.rgb = LIGHT_MUTED
            bp.space_before = Pt(10)

    # =========================================================================
    # SLIDE 3: OBJECTIVES & SCOPE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Scope & Goals", "Project Objectives & Technical Deliverables", "Targeted capabilities engineered to bridge procurement contracts with predictive demand")

    objs = [
        ("1. Dual Time-Series Engine", "Implement and benchmark Prophet (additive seasonality) vs. LightGBM (Quantile GBDT) to output 30-day demand trajectories with 95% confidence intervals."),
        ("2. Grounded Contract RAG Pipeline", "Ingest unstructured PDF/text agreements into Qdrant vector database via BGE embeddings, delivering cited answers with zero hallucination via Groq Llama 3.3 70B."),
        ("3. Composite Multi-Factor Risk Engine", "Quantify operational vulnerability into a 0-100 score combining inventory runway, supplier SLA compliance, lead-time variance, and monetary capital exposure."),
        ("4. Role-Based Access Control (RBAC)", "Implement JWT-authenticated roles (Admin, Procurement Analyst, Viewer) with secure bcrypt hashing, session persistence, and endpoint guards."),
        ("5. Enterprise-Grade System Performance", "Achieve sub-5ms cached response times, asynchronous forecasting worker deduplication, binary PDF magic-byte validation, and real-time SSE streaming.")
    ]

    for i, (head, desc) in enumerate(objs):
        top = Inches(1.8 + i * 1.0)
        card = add_card(s3, Inches(0.8), top, Inches(11.7), Inches(0.85), border_color=CARD_BORDER)
        
        box = s3.shapes.add_textbox(Inches(1.0), top + Inches(0.08), Inches(11.3), Inches(0.7))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = head
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = CYAN
        
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = LIGHT_MUTED
        p2.space_before = Pt(2)

    # =========================================================================
    # SLIDE 4: SYSTEM ARCHITECTURE
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "System Design", "End-to-End High-Performance Architecture", "Modular micro-service architecture separating client presentation, REST gateway, and analytical engines")

    arch_blocks = [
        ("Presentation Layer", "Next.js 14 & Tailwind CSS", 
         ["Client-side TanStack Query for cache-aside data retrieval",
          "Dynamic code-splitting for heavy Recharts visualizers (46% bundle size drop)",
          "Obsidian Glassmorphism design tokens with responsive data tables",
          "1-Click Demo Login pills with JWT localStorage synchronization"], CYAN),
        ("API & Gateway Layer", "FastAPI & Middleware Pool", 
         ["GZip compression middleware reducing JSON payloads by 75-85%",
          "Sliding-window IP rate limiter preventing DoS & token depletion",
          "RBAC authorization dependencies (require_admin, require_analyst)",
          "Server-Sent Events (SSE) streaming engine for real-time AI tokens"], SKY),
        ("Intelligence & Compute", "Dual ML & RAG Engine", 
         ["Prophet: Additive Fourier seasonal modeling",
          "LightGBM: Quantile loss regression with lag-window features",
          "FastEmbed: BGE-small-en-v1.5 local embedding with LRU cache",
          "Groq Llama 3.3 70B: High-speed grounded legal reasoning"], INDIGO),
        ("Persistence & Vector DB", "Relational & HNSW Storage", 
         ["SQLite / PostgreSQL with composite B-Tree indexes (0 N+1 overhead)",
          "Qdrant Vector Database with HNSW cosine graph search",
          "In-Memory Thread-Safe Cache with tag-based invalidation",
          "UUID-scoped sanitized file storage with magic-byte validation"], GREEN)
    ]

    for i, (title, sub, items, col) in enumerate(arch_blocks):
        left = Inches(0.8 + i * 2.95)
        add_card(s4, left, Inches(1.8), Inches(2.85), Inches(4.9), border_color=col)
        
        box = s4.shapes.add_textbox(left + Inches(0.15), Inches(1.95), Inches(2.55), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = WHITE
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = col
        p_sub.space_before = Pt(2)

        for it in items:
            p_it = tf.add_paragraph()
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = LIGHT_MUTED
            p_it.space_before = Pt(8)

    # =========================================================================
    # SLIDE 5: COMPONENT 1 - DEMAND FORECASTING
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "Forecasting Module", "Dual Time-Series Demand Forecasting", "Combining interpretable seasonal baselines with non-linear gradient-boosted trees")

    # Prophet Card
    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.7), Inches(3.2), border_color=SKY)
    pb = s5.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(2.9))
    ptf = pb.text_frame
    ptf.word_wrap = True
    p = ptf.paragraphs[0]
    p.text = "Model 1: Facebook Prophet (Generalized Additive Model)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = SKY
    prophet_points = [
        "Mathematical Formula: y(t) = g(t) + s(t) + h(t) + ε_t",
        "g(t): Piecewise linear trend with changepoint detection.",
        "s(t): Fourier series modeling weekly & yearly demand cycles.",
        "h(t): Holiday and promotional impulse regressors.",
        "Key Advantage: Highly robust to missing observations and outlier demand surges without extensive normalization."
    ]
    for pt in prophet_points:
        pp = ptf.add_paragraph()
        pp.text = f"• {pt}"
        pp.font.size = Pt(10)
        pp.font.color.rgb = LIGHT_MUTED
        pp.space_before = Pt(4)

    # LightGBM Card
    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.7), Inches(3.2), border_color=CYAN)
    lb = s5.shapes.add_textbox(Inches(7.0), Inches(1.95), Inches(5.3), Inches(2.9))
    ltf = lb.text_frame
    ltf.word_wrap = True
    p = ltf.paragraphs[0]
    p.text = "Model 2: LightGBM (Quantile Gradient Boosted Trees)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = CYAN
    lgb_points = [
        "Feature Engineering: Lag windows (t-1, t-7, t-14, t-30), rolling mean/std (7d, 28d), day-of-week, month, and promo flags.",
        "Pinball Loss Optimization: Quantiles α ∈ [0.05, 0.50, 0.95].",
        "α = 0.50 yields median forecasted demand.",
        "α = 0.05 & 0.95 generate rigorous 95% confidence bounds.",
        "Key Advantage: Captures complex non-linear promotional interactions and delivers 25-35% lower RMSE under high volatility."
    ]
    for pt in lgb_points:
        pp = ltf.add_paragraph()
        pp.text = f"• {pt}"
        pp.font.size = Pt(10)
        pp.font.color.rgb = LIGHT_MUTED
        pp.space_before = Pt(4)

    # Backtesting Metrics Card
    add_card(s5, Inches(0.8), Inches(5.2), Inches(11.7), Inches(1.7), border_color=GOLD)
    mb = s5.shapes.add_textbox(Inches(1.0), Inches(5.3), Inches(11.3), Inches(1.5))
    mtf = mb.text_frame
    mtf.word_wrap = True
    p = mtf.paragraphs[0]
    p.text = "Backtesting Protocol & Model Evaluation Metrics"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = GOLD
    
    mp = mtf.add_paragraph()
    mp.text = "Rolling-Origin Cross Validation (Expanding Window) evaluates performance on holdout data without lookahead bias:"
    mp.font.size = Pt(10)
    mp.font.color.rgb = WHITE
    mp.space_before = Pt(2)

    mp2 = mtf.add_paragraph()
    mp2.text = "• MAPE (Mean Absolute Percentage Error)  |  • RMSE (Root Mean Squared Error)  |  • MAE (Mean Absolute Error)  |  • WAPE (Weighted Absolute Percentage Error)"
    mp2.font.size = Pt(10)
    mp2.font.bold = True
    mp2.font.color.rgb = CYAN
    mp2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 6: COMPONENT 2 - RAG CONTRACT INTELLIGENCE
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Semantic Intelligence", "Supplier Contract RAG Architecture", "Grounded legal & SLA question-answering with citation tracing and zero hallucination")

    rag_steps = [
        ("1. Extraction & Ingestion", "PyMuPDF / Chunking", 
         ["High-speed parsing of PDF, TXT, and Markdown files.",
          "Recursive token-aware chunking (chunk_size=512, overlap=64) preserving clause semantics.",
          "Automatic metadata binding: supplier_id, doc_type, effective_date, page_number."]),
        ("2. Dense Embeddings", "FastEmbed BGE-small", 
         ["384-dimensional dense semantic vector space.",
          "ONNX-runtime execution (zero PyTorch dependency overhead).",
          "2,048-entry in-memory LRU vector cache for repeated query lookups (<0.8ms)."]),
        ("3. Vector Retrieval", "Qdrant HNSW Graph", 
         ["Cosine similarity with Hierarchical Navigable Small World index.",
          "Payload metadata filtering: Restricts search strictly to a target supplier or doc_type.",
          "Verified 100% Top-1 accuracy in benchmark retrieval evaluations."]),
        ("4. Grounded Synthesis", "Groq Llama 3.3 70B", 
         ["Strict system prompt forcing direct citations: [Doc: Agreement, Page X].",
          "Automatic operational risk keyword extractor (surcharges, force majeure, penalties).",
          "Streaming token generator via Server-Sent Events (SSE)."])
    ]

    for i, (title, sub, items) in enumerate(rag_steps):
        left = Inches(0.8 + i * 2.95)
        add_card(s6, left, Inches(1.8), Inches(2.85), Inches(4.9), border_color=INDIGO)
        
        box = s6.shapes.add_textbox(left + Inches(0.15), Inches(1.95), Inches(2.55), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = WHITE
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(10)
        p_sub.font.bold = True
        p_sub.font.color.rgb = SKY
        p_sub.space_before = Pt(2)

        for it in items:
            p_it = tf.add_paragraph()
            p_it.text = f"• {it}"
            p_it.font.size = Pt(10)
            p_it.font.color.rgb = LIGHT_MUTED
            p_it.space_before = Pt(8)

    # =========================================================================
    # SLIDE 7: COMPONENT 3 - COMPOSITE RISK ENGINE
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "Mathematical Engine", "Multi-Factor Supply Chain Risk Formulation", "Mathematical modeling translating physical stock, demand volatility, and contract risk into business indices")

    # Stockout risk box
    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=ROSE)
    sb = s7.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(4.6))
    stf = sb.text_frame
    stf.word_wrap = True
    
    p = stf.paragraphs[0]
    p.text = "1. Stockout Vulnerability Score (S_risk ∈ [0, 100])"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = ROSE

    points = [
        "Projected Net Pipeline: Stock_net = Stock_current - Stock_allocated + Stock_incoming",
        "Lead-Time Demand: D_LT = Forecast_daily × LeadTime_days",
        "Safety Buffer Ratio: R_buffer = (Stock_net - D_LT) / SafetyStock_min",
        "Risk Formulation:",
        "  • If R_buffer < 0 (Impending stockout): Score = min(100, 60 + |R_buffer| × 40)",
        "  • If 0 ≤ R_buffer < 1 (Buffer depleted): Score = 30 + (1 - R_buffer) × 30",
        "  • If R_buffer ≥ 1 (Healthy buffer): Score = max(0, 30 - (R_buffer - 1) × 15)",
        "Capital at Risk: If Stock_net < D_LT, Exposure = (D_LT - Stock_net) × UnitCost"
    ]
    for pt in points:
        pp = stf.add_paragraph()
        pp.text = pt
        pp.font.size = Pt(10.5)
        pp.font.color.rgb = LIGHT_MUTED
        pp.space_before = Pt(6)

    # Supplier Disruption & Composite box
    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=GOLD)
    db = s7.shapes.add_textbox(Inches(7.0), Inches(1.95), Inches(5.3), Inches(4.6))
    dtf = db.text_frame
    dtf.word_wrap = True

    p = dtf.paragraphs[0]
    p.text = "2. Supplier Disruption & Composite Index"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GOLD

    points2 = [
        "Supplier Disruption Score (V_risk ∈ [0, 100]):",
        "  V_risk = w_1(1 - Reliability) + w_2(DelayedRatio) + w_3(ClauseRiskFlag)",
        "  • Clause Flags: 25 pts for force majeure; 15 pts for port congestion notices.",
        "Composite Risk Formulation:",
        "  C_risk = 0.55 × S_risk + 0.30 × V_risk + 0.15 × FinancialWeight",
        "Automated Severity Classification:",
        "  • CRITICAL (Score ≥ 70): Immediate emergency PO & expedite",
        "  • HIGH (50 ≤ Score < 70): Reorder point breach warning",
        "  • MEDIUM (25 ≤ Score < 50): Standard operational tracking",
        "  • HEALTHY (Score < 25): Fully covered safety runway"
    ]
    for pt in points2:
        pp = dtf.add_paragraph()
        pp.text = pt
        pp.font.size = Pt(10.5)
        pp.font.color.rgb = LIGHT_MUTED
        pp.space_before = Pt(6)

    # =========================================================================
    # SLIDE 8: COMPONENT 4 - SECURITY & RBAC
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "Security & Governance", "Role-Based Access Control & Security Hardening", "Enterprise security posture protecting intellectual property, document uploads, and API endpoints")

    sec_cards = [
        ("Role-Based Access Control (RBAC)", "3-Tier Permission Hierarchy",
         ["Admin (Full Access): Manage users, upload/delete contracts, trigger global model retrains.",
          "Procurement Analyst: Calibrate inventory levels, run forecast comparisons, query RAG assistant.",
          "Viewer: Read-only access to risk matrix, forecast charts, and executive scorecards.",
          "Enforcement: FastAPI dependency injection (require_admin, require_analyst_or_admin)."], CYAN),
        ("Authentication & Session Protocol", "JWT + Native Bcrypt",
         ["Bcrypt Hashing: Salted password hashing with automatic 72-byte truncation protection.",
          "Cryptographic JWT: HS256 signed access tokens with 24-hour expiration carrying role claims.",
          "Axios Interceptors: Automatic Authorization: Bearer token injection on client HTTP requests.",
          "Local Persistence: Automatic session restore and background profile verification (/me)."], SKY),
        ("File Ingestion Security Guardrails", "Multi-Layer Boundary Defense",
         ["Extension Whitelist: Restricts document upload strictly to .pdf, .txt, .md formats.",
          "Magic-Byte Verification: Inspects initial 1KB stream for binary %PDF- header to prevent spoofing.",
          "Strict Size Ceiling: 15MB file size limit enforced chunk-by-chunk to prevent DoS attacks.",
          "Path Traversal Containment: UUID prefixing & directory boundary verification."], ROSE)
    ]

    for i, (title, sub, bullets, color) in enumerate(sec_cards):
        left = Inches(0.8 + i * 3.95)
        add_card(s8, left, Inches(1.8), Inches(3.8), Inches(4.9), border_color=color)
        
        box = s8.shapes.add_textbox(left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = WHITE
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = color
        p_sub.space_before = Pt(3)

        for b in bullets:
            bp = tf.add_paragraph()
            bp.text = f"• {b}"
            bp.font.size = Pt(10)
            bp.font.color.rgb = LIGHT_MUTED
            bp.space_before = Pt(8)

    # =========================================================================
    # SLIDE 9: RESULTS, BENCHMARKS & VERIFICATION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Empirical Validation", "Testing, Benchmark & Evaluation Metrics", "Quantitative performance benchmarks and test suite execution results")

    # Left: Test Results
    add_card(s9, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=GREEN)
    tb = s9.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(4.6))
    ttf = tb.text_frame
    ttf.word_wrap = True

    p = ttf.paragraphs[0]
    p.text = "Automated Test Suite: 28 / 28 Tests Passing (100%)"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GREEN

    tests = [
        "test_auth.py (7 Tests): Bcrypt hashing, JWT generation/decoding, registration, duplicate rejection, login auth, /me profile, RBAC restrictions.",
        "test_forecasting.py (4 Tests): 30-day feature engineering, Prophet model fitting, LightGBM quantile regression, MAPE/RMSE metric evaluator.",
        "test_performance_and_cache.py (6 Tests): TTL expiration, tag-based invalidation, LRU eviction, job deduplication, vector query caching.",
        "test_rag.py & retrieval_quality.py (7 Tests): FastEmbed indexing, chunking service, Qdrant HNSW vector search, Top-1 semantic relevance, supplier metadata isolation.",
        "test_risk_engine.py (4 Tests): Critical stockout calculations, healthy buffer modeling, supplier disruption scoring, priority queue."
    ]
    for t in tests:
        tp = ttf.add_paragraph()
        tp.text = f"✔ {t}"
        tp.font.size = Pt(9.5)
        tp.font.color.rgb = LIGHT_MUTED
        tp.space_before = Pt(6)

    # Right: Latency & Speedup Table
    add_card(s9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=CYAN)
    lb = s9.shapes.add_textbox(Inches(7.0), Inches(1.95), Inches(5.3), Inches(4.6))
    ltf = lb.text_frame
    ltf.word_wrap = True

    p = ltf.paragraphs[0]
    p.text = "Performance Benchmarks & Optimizations"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = CYAN

    benchmarks = [
        "Endpoint Acceleration (GET /api/v1/risk):",
        "  • Cold / DB Query Time: 583.40 ms (3N+1 queries)",
        "  • Eager-Loaded + Cache Hit: 3.44 ms (169x Speedup / 99.4% drop)",
        "Bandwidth Compression (GZip Middleware):",
        "  • Payload reduction: 70% to 85% on large inventory arrays",
        "Frontend Route Code-Splitting:",
        "  • Dynamic chunking of Recharts visualizer",
        "  • Initial JS reduced from 225 kB to 121 kB (46% reduction)",
        "Asynchronous Model Training:",
        "  • Background ASGI worker execution with job deduplication",
        "  • Zero blocking of main event loop during 10,000-iter fits"
    ]
    for b in benchmarks:
        bp = ltf.add_paragraph()
        bp.text = b
        bp.font.size = Pt(10)
        bp.font.color.rgb = LIGHT_MUTED
        bp.space_before = Pt(4)

    # =========================================================================
    # SLIDE 10: USER WORKFLOWS & DEMONSTRATION
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "Product Walkthrough", "Key User Workflows & Live Demonstration", "End-to-end operational workflows supported by ContractIQ")

    flows = [
        ("1. 1-Click Demo Login", "Instant Persona Switching", 
         ["Access /login and select Admin, Analyst, or Viewer.", 
          "Immediately loads role-specific permissions and auth token.",
          "Dynamic profile pill with initials avatar and colored role badge."]),
        ("2. Executive Overview", "Unified Operational Matrix",
         ["Real-time telemetry showing critical vulnerabilities, high-risk items, and total capital at risk.",
          "Dynamic personalized greeting according to authenticated user profile.",
          "Quick action shortcuts directly to risk matrix and RAG chatbot."]),
        ("3. Inventory Calibration", "Interactive Warehouse Ledger",
         ["Filter SKUs by urgency (CRITICAL, HIGH, HEALTHY) or text search.",
          "Open Stock Adjustment Modal to simulate on-hand / incoming stock changes.",
          "Instantaneous automatic cache invalidation across the dashboard."]),
        ("4. Demand Forecasting", "Prophet vs LightGBM Analysis",
         ["Switch between 4 seeded SKUs across semiconductors, optics, and RF modules.",
          "Toggle between Prophet baseline and LightGBM Quantile GBDT.",
          "Inspect 95% confidence intervals and holdout error metrics (MAPE, RMSE)."]),
        ("5. Contract RAG Intelligence", "Grounded Decision Support",
         ["Query supplier agreements, SLA delivery terms, and force majeure notices.",
          "Live Server-Sent Events (SSE) streaming token output.",
          "Clickable citation cards with document title and page references."])
    ]

    for i, (f_title, f_sub, f_items) in enumerate(flows):
        top = Inches(1.8 + i * 1.0)
        card = add_card(s10, Inches(0.8), top, Inches(11.7), Inches(0.85), border_color=CARD_BORDER)
        
        box = s10.shapes.add_textbox(Inches(1.0), top + Inches(0.06), Inches(11.3), Inches(0.72))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = f"{f_title}  —  {f_sub}"
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = SKY
        
        p2 = tf.add_paragraph()
        p2.text = "   • " + "   • ".join(f_items)
        p2.font.size = Pt(10)
        p2.font.color.rgb = LIGHT_MUTED
        p2.space_before = Pt(2)

    # =========================================================================
    # SLIDE 11: TECHNICAL STACK
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "Engineering Tooling", "Complete Technology Stack", "Production-grade open-source and modern enterprise software tools")

    stack_cats = [
        ("Frontend & UI", CYAN, [
            ("Next.js 14", "App Router & SSR/SSG"),
            ("TypeScript", "Strict type safety"),
            ("Tailwind CSS", "Glassmorphic design system"),
            ("TanStack Query v5", "Client-side cache-aside"),
            ("Recharts", "Interactive quantile plotting"),
            ("Lucide React", "Consistent icon ecosystem")
        ]),
        ("Backend & API", SKY, [
            ("FastAPI 0.111", "Asynchronous ASGI framework"),
            ("Uvicorn", "High-performance ASGI server"),
            ("Pydantic v2", "Data validation & schemas"),
            ("SQLAlchemy 2.0", "Declarative ORM + joinedload"),
            ("PyJWT & Bcrypt", "Cryptographic authentication"),
            ("GZip & RateLimit", "Transport optimization")
        ]),
        ("AI, ML & Vector DB", INDIGO, [
            ("Prophet", "Fourier additive seasonal model"),
            ("LightGBM", "Quantile gradient boosted trees"),
            ("FastEmbed", "BGE-small-en-v1.5 embeddings"),
            ("Qdrant", "HNSW cosine vector database"),
            ("Groq Cloud", "Llama 3.3 70B inference engine"),
            ("PyMuPDF", "Binary document text extraction")
        ]),
        ("Data & DevSecOps", GREEN, [
            ("SQLite / Postgres", "Relational database"),
            ("Alembic", "Automated schema migrations"),
            ("Pytest", "28-test automated suite"),
            ("Pandas & NumPy", "Feature engineering & lags"),
            ("CmdStanPy", "Underlying Stan C++ compiler"),
            ("Docker", "Containerized deployment")
        ])
    ]

    for i, (cat_name, cat_col, tools) in enumerate(stack_cats):
        left = Inches(0.8 + i * 2.95)
        add_card(s11, left, Inches(1.8), Inches(2.85), Inches(4.9), border_color=cat_col)
        
        box = s11.shapes.add_textbox(left + Inches(0.15), Inches(1.95), Inches(2.55), Inches(4.6))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = cat_name
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = cat_col
        
        for tool_name, tool_desc in tools:
            tp = tf.add_paragraph()
            tp.text = f"• {tool_name}"
            tp.font.size = Pt(11)
            tp.font.bold = True
            tp.font.color.rgb = WHITE
            tp.space_before = Pt(6)

            dp = tf.add_paragraph()
            dp.text = f"   {tool_desc}"
            dp.font.size = Pt(9.5)
            dp.font.color.rgb = MUTED

    # =========================================================================
    # SLIDE 12: CONCLUSION & FUTURE ROADMAP
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "Summary & Future Roadmap", "Project Conclusion & Scalability Roadmap", "Summary of project milestones and planned enterprise extensions")

    # Conclusion Card
    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=GREEN)
    cb = s12.shapes.add_textbox(Inches(1.0), Inches(1.95), Inches(5.3), Inches(4.6))
    ctf = cb.text_frame
    ctf.word_wrap = True

    p = ctf.paragraphs[0]
    p.text = "Key Project Achievements"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = GREEN

    concl = [
        "Unified Architecture: Successfully solved the supply chain visibility gap by bridging unstructured contract clauses with machine-learned demand forecasts.",
        "Quantified Risk & Capital: Transformed abstract risk into a mathematically sound composite index with dollar-denominated exposure ($ at risk).",
        "High-Speed Performance: Benchmarked 169x speedup via multi-tier caching and 0 N+1 query overhead.",
        "Robust Security Posture: Fully governed with JWT authentication, RBAC, magic-byte upload inspection, and path traversal protection.",
        "Verified & Evaluated: 28 automated tests passing across feature engineering, RAG semantic precision, and security modules."
    ]
    for c in concl:
        cp = ctf.add_paragraph()
        cp.text = f"✔ {c}"
        cp.font.size = Pt(10.5)
        cp.font.color.rgb = LIGHT_MUTED
        cp.space_before = Pt(8)

    # Future Scope Card
    add_card(s12, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), border_color=CYAN)
    fb = s12.shapes.add_textbox(Inches(7.0), Inches(1.95), Inches(5.3), Inches(4.6))
    ftf = fb.text_frame
    ftf.word_wrap = True

    p = ftf.paragraphs[0]
    p.text = "Future Scope & Enterprise Roadmap"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = CYAN

    future = [
        "1. ERP Direct Connectors: Pre-built bi-directional webhooks and adapters for SAP S/4HANA, Oracle NetSuite, and Microsoft Dynamics 365.",
        "2. Multi-Agent Autonomous Negotiation: Deploying LangGraph / AutoGen agents to automatically draft purchase order amendments and negotiate discounts based on SLA breach credits.",
        "3. Live Macro & Port Telemetry: Ingesting AIS satellite ship tracking and customs freight delay APIs to dynamically adjust supplier lead-time parameters in real-time.",
        "4. Multi-Modal Vision RAG: Extraction of technical schematics, engineering CAD drawings, and ISO inspection certificates via vision-language models."
    ]
    for f in future:
        fp = ftf.add_paragraph()
        fp.text = f
        fp.font.size = Pt(10.5)
        fp.font.color.rgb = LIGHT_MUTED
        fp.space_before = Pt(8)

    # Save outputs
    output_path1 = os.path.join(r"C:\Users\hp\OneDrive\Desktop\Projects\Rag project", "ContractIQ_Project_Evaluation.pptx")
    prs.save(output_path1)
    print(f"Saved PPTX to {output_path1}")

    # Also save to artifact directory if available
    artifact_dir = r"C:\Users\hp\.gemini\antigravity\brain\40bddb9e-75df-4888-bd68-bb8e478c154c"
    if os.path.exists(artifact_dir):
        output_path2 = os.path.join(artifact_dir, "ContractIQ_Project_Evaluation.pptx")
        prs.save(output_path2)
        print(f"Saved PPTX to {output_path2}")

if __name__ == "__main__":
    create_presentation()
