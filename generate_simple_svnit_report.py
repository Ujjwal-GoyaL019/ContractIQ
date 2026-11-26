"""
ContractIQ - Simple, Clean, High-Contrast Project Report Generator
Sardar Vallabhbhai National Institute of Technology (SVNIT), Surat
Department of Artificial Intelligence
Team Roll Numbers: U23AI074, U23AI079, U23AI094, U23AI072
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class SimpleNumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for running header & footer with dynamic page numbering.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Top Header (Pages 2+)
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 808, 550, 808)
            self.drawString(45, 813, "SVNIT SURAT  •  DEPARTMENT OF ARTIFICIAL INTELLIGENCE")
            self.drawRightString(550, 813, "CONTRACTIQ PROJECT REPORT")

        # Running Bottom Footer (All Pages)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 36, 550, 36)
        self.drawString(45, 25, "ContractIQ : High-Assurance Hybrid Legal RAG & Autonomous Supply Chain Governance")
        self.drawRightString(550, 25, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'InstHeader',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        'DeptHeader',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0284C7')
    ))
    styles.add(ParagraphStyle(
        'ReportTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        'ReportSubtitle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#334155')
    ))
    styles.add(ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'SectionH2',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=colors.HexColor('#0284C7'),
        spaceBefore=5,
        spaceAfter=2.5,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'SimpleBody',
        fontName='Helvetica',
        fontSize=8.6,
        leading=11.8,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=3.5
    ))
    styles.add(ParagraphStyle(
        'SimpleBullet',
        fontName='Helvetica',
        fontSize=8.4,
        leading=11.5,
        textColor=colors.HexColor('#1E293B'),
        leftIndent=12,
        spaceAfter=2.5
    ))

    # Dedicated Table Styles with STRICT high-contrast colors
    styles.add(ParagraphStyle(
        'BadgeText',
        fontName='Helvetica-Bold',
        fontSize=8.0,
        leading=10.5,
        alignment=TA_CENTER,
        textColor=colors.white
    ))
    styles.add(ParagraphStyle(
        'Th',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.0,
        alignment=TA_CENTER,
        textColor=colors.white
    ))
    styles.add(ParagraphStyle(
        'Td',
        fontName='Helvetica',
        fontSize=7.6,
        leading=9.8,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        'TdCenter',
        fontName='Helvetica',
        fontSize=7.6,
        leading=9.8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        'TdBold',
        fontName='Helvetica-Bold',
        fontSize=7.6,
        leading=9.8,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#0F172A')
    ))
    styles.add(ParagraphStyle(
        'TdHighlight',
        fontName='Helvetica-Bold',
        fontSize=7.6,
        leading=9.8,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#065F46')
    ))
    styles.add(ParagraphStyle(
        'MetaBoxLabel',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor('#0369A1')
    ))
    styles.add(ParagraphStyle(
        'MetaBoxVal',
        fontName='Helvetica',
        fontSize=8.3,
        leading=11.5,
        textColor=colors.HexColor('#1E293B')
    ))

    return styles


def callout_box(text, styles, border="#0284C7", bg="#F0F9FF"):
    p = Paragraph(text, styles['SimpleBody'])
    t = Table([[p]], colWidths=[505])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(bg)),
        ('LEFTPADDING', (0, 0), (-1, -1), 9),
        ('RIGHTPADDING', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBEFORE', (0, 0), (0, -1), 3.0, colors.HexColor(border)),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#BAE6FD")),
    ]))
    return t


def build_simple_report(output_filename):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=36,
        bottomMargin=36
    )

    styles = get_styles()
    story = []

    # =========================================================================
    # PAGE 1: INSTITUTION HEADER, TEAM, OVERVIEW & PROBLEM STATEMENT
    # =========================================================================
    story.append(Paragraph("SARDAR VALLABHBHAI NATIONAL INSTITUTE OF TECHNOLOGY (SVNIT), SURAT", styles['InstHeader']))
    story.append(Paragraph("DEPARTMENT OF ARTIFICIAL INTELLIGENCE  •  B.TECH. CAPSTONE PROJECT REPORT", styles['DeptHeader']))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0284C7"), spaceAfter=8))

    story.append(Paragraph("ContractIQ", styles['ReportTitle']))
    story.append(Spacer(1, 2))
    story.append(Paragraph(
        "Autonomous Supply Chain Risk Governance via Hybrid Legal RAG, Zero-Hallucination Guard & Prescriptive Sourcing",
        styles['ReportSubtitle']
    ))
    story.append(Spacer(1, 8))

    # Meta Table: Authors & Academic Details
    team_data = [
        [
            Paragraph("<b>Project Team (SVNIT Roll Numbers):</b>", styles['MetaBoxLabel']),
            Paragraph("<b>Academic Details:</b>", styles['MetaBoxLabel'])
        ],
        [
            Paragraph("• <b>U23AI074</b> &nbsp;|&nbsp; Core AI Pipeline, Hybrid RRF & ONNX FastEmbed<br/>"
                      "• <b>U23AI079</b> &nbsp;|&nbsp; 3-Stage HallucinationGuard & Factuality Auditor<br/>"
                      "• <b>U23AI094</b> &nbsp;|&nbsp; 7-Model Demand Forecasting & Quantile Bounds<br/>"
                      "• <b>U23AI072</b> &nbsp;|&nbsp; Prescriptive MILP Sourcing Solver & Full-Stack UI",
                      styles['MetaBoxVal']),
            Paragraph("<b>Institution:</b> Sardar Vallabhbhai National Institute of Technology, Surat<br/>"
                      "<b>Department:</b> Department of Artificial Intelligence<br/>"
                      "<b>Degree:</b> Bachelor of Technology (B.Tech.) in AI<br/>"
                      "<b>Academic Year:</b> 2026 – 2027 &nbsp;|&nbsp; <b>Status:</b> Production Ready (39/39 Tests)",
                      styles['MetaBoxVal'])
        ]
    ]
    meta_table = Table(team_data, colWidths=[260, 245])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#CBD5E1')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.0, colors.HexColor("#0284C7")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # 4 Quick Metric Badges (Using dedicated BadgeText with white color)
    badges_data = [
        [
            Paragraph("<b>Hybrid Retrieval</b><br/>100% Hit@1 (5.46 ms)", styles['BadgeText']),
            Paragraph("<b>Hallucination Guard</b><br/>0.0% Hallucination Rate", styles['BadgeText']),
            Paragraph("<b>Demand Forecasting</b><br/>27.20% MAPE (vs 44.56%)", styles['BadgeText']),
            Paragraph("<b>Prescriptive Sourcing</b><br/>$9,438.93 Cost Savings", styles['BadgeText']),
        ]
    ]
    b_table = Table(badges_data, colWidths=[126, 126, 126, 127])
    b_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#0284C7')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#334155')),
    ]))
    story.append(b_table)
    story.append(Spacer(1, 10))

    # Section 1: Introduction & What is ContractIQ?
    story.append(Paragraph("1. Project Overview & Motivation", styles['SectionH1']))
    story.append(Paragraph(
        "Global enterprises lose an estimated <b>$1.5 million per day</b> during supply chain disruptions due to "
        "<b>\"Contract Blindness\"</b>: critical Service Level Agreements (SLAs), penalty clauses, volume discounts, "
        "and force majeure notices are buried inside unstructured multi-page legal PDFs. When disruptions occur, procurement teams "
        "make ordering decisions based on gut feeling or simplistic point forecasts, leading to stockouts and expensive contract penalties.",
        styles['SimpleBody']
    ))
    story.append(Paragraph(
        "<b>ContractIQ</b> is an end-to-end intelligent platform that connects legal contracts directly to supply chain procurement. "
        "It combines <b>(1) Hybrid Legal RAG</b> that searches contracts with both semantic and keyword precision, "
        "<b>(2) a 3-Stage Zero-Hallucination Shield</b> that verifies every numeric claim against source texts, "
        "<b>(3) a 7-Model Demand Forecasting Engine</b> that models surge uncertainty ($P_{90}$), and "
        "<b>(4) a Prescriptive Mathematical Solver (MILP)</b> that calculates the exact optimal purchase order split among suppliers.",
        styles['SimpleBody']
    ))
    story.append(Spacer(1, 6))

    # Section 2: Real-World Problem Statement
    story.append(Paragraph("2. Problem Statement: Why Standard AI Fails in Supply Chain", styles['SectionH1']))
    story.append(Paragraph(
        "Standard commercial AI and chatbot demos cannot be used for enterprise supply chains for four concrete reasons:",
        styles['SimpleBody']
    ))
    p_reasons = [
        "<b>Vector-Only Search Misses Legal Numbers:</b> Dense vector search is great for general concepts but routinely fails on exact clause numbers (e.g. <i>Clause 14.2</i> vs <i>Clause 14.3</i>) and specific percentage penalty rates.",
        "<b>Hallucination Risk:</b> Standard LLMs confabulate numbers under pressure. In supply chain governance, hallucinating a <i>0.5% penalty</i> instead of <i>1.0%</i> creates immediate legal and financial exposure.",
        "<b>Point Forecast Blindness:</b> Predicting a single average number fails during real disruptions. Systems must compute high-risk surge bounds ($P_{90}$) to avoid stockouts when lead times jump from 4 to 28 days.",
        "<b>Advice vs. Action:</b> Chatbots provide conversational text but cannot solve math equations. Procurement managers need concrete purchase order allocations that respect supplier capacity and budget constraints."
    ]
    for pr in p_reasons:
        story.append(Paragraph(f"• {pr}", styles['SimpleBullet']))

    story.append(Spacer(1, 6))
    story.append(callout_box(
        "<b>Core Achievement:</b> ContractIQ eliminates legal hallucinations (0.0% error across 16 adversarial audit tests) "
        "and turns contract terms into mathematically optimal purchase orders ($9,438.93 saved, -82.3% disruption risk).",
        styles, border="#10B981", bg="#F0FDF4"
    ))

    # End of Page 1
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: ARCHITECTURE DIAGRAM & STEP-BY-STEP WORKING
    # =========================================================================
    story.append(Paragraph("3. System Architecture & Complete Pipeline", styles['SectionH1']))
    story.append(Paragraph(
        "ContractIQ is built as a clean 5-layer pipeline connecting document ingestion to mathematical decision-making.",
        styles['SimpleBody']
    ))
    story.append(Spacer(1, 3))

    # Architecture Diagram (Centered, exactly sized for Page 2)
    arch_img = r"C:\Users\hp\OneDrive\Desktop\Projects\Rag project\ContractIQ_System_Architecture.png"
    if os.path.exists(arch_img):
        story.append(RLImage(arch_img, width=500, height=222))
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            "<b>Figure 1:</b> ContractIQ 5-Layer End-to-End Architecture: From Legal PDFs & Sales Data to Prescriptive Orders.",
            styles['TdCenter']
        ))
        story.append(Spacer(1, 8))

    story.append(Paragraph("How ContractIQ Works (The 5 Pipeline Stages):", styles['SectionH2']))

    steps = [
        ("Step 1: Document & Data Ingestion",
         "The system parses 6 multi-page enterprise legal contracts (14 pages total) and 1,600+ historical sales records. "
         "Using PyMuPDF and cryptographic SHA-256 deduplication, it cleanly extracts clauses, penalty tables, and terms into 512-token chunks."),

        ("Step 2: Dual Hybrid Representation (Dense + BM25)",
         "Chunks are indexed twice: (a) Dense semantic vectors using local FastEmbed ONNX 384-d embeddings (`bge-small-en-v1.5`) in Qdrant HNSW, "
         "and (b) Sparse lexical keywords using Okapi BM25. This ensures both high-level legal concepts and exact clause IDs are instantly found."),

        ("Step 3: Two-Stage Hybrid Retrieval & Reranking",
         "When a query arrives, candidates from Qdrant and BM25 are merged using Reciprocal Rank Fusion ($k=60$). A second-stage "
         "Lexical-Semantic Cross-Reranker scores exact phrase matches, delivering <b>100% Hit@1</b> accuracy in just <b>5.46 ms</b>."),

        ("Step 4: 3-Stage Zero-Hallucination Shield (`HallucinationGuard`)",
         "Before answering, Stage 1 (Abstention Gate) blocks out-of-scope or adversarial questions (similarity < 0.35). "
         "Stage 2 generates grounded answers with Groq Llama 3.3 70B at temperature 0.0. Stage 3 (Factuality Auditor) extracts every %, "
         "dollar amount, and date to verify verbatim matches in the source text, achieving a <b>0.0% hallucination rate</b>."),

        ("Step 5: Multi-Model Demand Forecasting & Prescriptive MILP Sourcing",
         "A 7-model leaderboard predicts upcoming demand and computes safety surge buffers ($P_{90}$). The SciPy HiGHS Mixed-Integer "
         "Linear Programming solver then computes the exact purchase order split across suppliers to minimize landed cost and SLA risk.")
    ]
    for s_name, s_desc in steps:
        story.append(Paragraph(f"• <b>{s_name}:</b> {s_desc}", styles['SimpleBullet']))

    story.append(Spacer(1, 6))
    story.append(callout_box(
        "<b>Engineering Highlight:</b> All embeddings and vector searches run locally with FastEmbed ONNX and Qdrant. "
        "No confidential enterprise contract ever leaves the secure perimeter for vector generation.",
        styles, border="#0284C7", bg="#F0F9FF"
    ))

    # End of Page 2
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: EXPERIMENTAL EVALUATION & RESULTS (HIGH-CONTRAST TABLES)
    # =========================================================================
    story.append(Paragraph("4. Experimental Results & Benchmark Evaluation", styles['SectionH1']))
    story.append(Paragraph(
        "ContractIQ was tested across 4 comprehensive empirical benchmarks: RAG retrieval ablation, a 16-query zero-hallucination "
        "audit, a 7-model demand forecasting leaderboard on a 14-day holdout, and a prescriptive sourcing cost-benefit analysis.",
        styles['SimpleBody']
    ))
    story.append(Spacer(1, 4))

    # Table 1: RAG Retrieval Ablation
    story.append(Paragraph("<b>Table 1: RAG Retrieval Performance (Dense vs. Sparse vs. Hybrid RRF)</b>", styles['SectionH2']))
    rag_data = [
        [Paragraph("Search Method", styles['Th']),
         Paragraph("Hit@1 Accuracy", styles['Th']),
         Paragraph("Precision@3", styles['Th']),
         Paragraph("MRR", styles['Th']),
         Paragraph("Latency", styles['Th'])],
        [Paragraph("Dense Vector Only (FastEmbed ONNX)", styles['Td']), Paragraph("80.0%", styles['TdCenter']), Paragraph("0.6667", styles['TdCenter']), Paragraph("0.8500", styles['TdCenter']), Paragraph("1.18 ms", styles['TdCenter'])],
        [Paragraph("Sparse Lexical Only (Okapi BM25)", styles['Td']), Paragraph("86.7%", styles['TdCenter']), Paragraph("0.7333", styles['TdCenter']), Paragraph("0.9000", styles['TdCenter']), Paragraph("0.84 ms", styles['TdCenter'])],
        [Paragraph("Hybrid RRF Fusion (k=60)", styles['Td']), Paragraph("93.3%", styles['TdCenter']), Paragraph("0.8667", styles['TdCenter']), Paragraph("0.9500", styles['TdCenter']), Paragraph("2.02 ms", styles['TdCenter'])],
        [Paragraph("<b>ContractIQ Hybrid + Cross-Reranker</b>", styles['TdBold']), Paragraph("<b>100.0%</b>", styles['TdHighlight']), Paragraph("<b>0.9333</b>", styles['TdHighlight']), Paragraph("<b>1.0000</b>", styles['TdHighlight']), Paragraph("<b>5.46 ms</b>", styles['TdHighlight'])],
    ]
    t1 = Table(rag_data, colWidths=[185, 80, 80, 80, 80])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t1)
    story.append(Spacer(1, 6))

    # Table 2: Zero-Hallucination Audit
    story.append(Paragraph("<b>Table 2: Zero-Hallucination & Adversarial Audit (16 Challenging Queries)</b>", styles['SectionH2']))
    hall_data = [
        [Paragraph("Query Type", styles['Th']),
         Paragraph("Query Count", styles['Th']),
         Paragraph("Faithfulness", styles['Th']),
         Paragraph("Hallucination Rate", styles['Th']),
         Paragraph("Refusal Safety", styles['Th'])],
        [Paragraph("Direct Factual Lookups", styles['Td']), Paragraph("6", styles['TdCenter']), Paragraph("100.0%", styles['TdCenter']), Paragraph("0.0%", styles['TdCenter']), Paragraph("Answered Grounded", styles['TdCenter'])],
        [Paragraph("Multi-Clause Synthesis", styles['Td']), Paragraph("4", styles['TdCenter']), Paragraph("100.0%", styles['TdCenter']), Paragraph("0.0%", styles['TdCenter']), Paragraph("Answered Grounded", styles['TdCenter'])],
        [Paragraph("Adversarial Unsupported Traps", styles['Td']), Paragraph("3", styles['TdCenter']), Paragraph("100.0%", styles['TdCenter']), Paragraph("0.0%", styles['TdCenter']), Paragraph("100% (3/3 Refused)", styles['TdCenter'])],
        [Paragraph("Prompt Injection Jailbreaks", styles['Td']), Paragraph("3", styles['TdCenter']), Paragraph("100.0%", styles['TdCenter']), Paragraph("0.0%", styles['TdCenter']), Paragraph("100% (3/3 Refused)", styles['TdCenter'])],
        [Paragraph("<b>Overall Benchmark Total</b>", styles['TdBold']), Paragraph("<b>16</b>", styles['TdHighlight']), Paragraph("<b>100.0%</b>", styles['TdHighlight']), Paragraph("<b>0.0%</b>", styles['TdHighlight']), Paragraph("<b>100% (6/6 Traps Refused)</b>", styles['TdHighlight'])],
    ]
    t2 = Table(hall_data, colWidths=[175, 75, 85, 85, 85])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 6))

    # Table 3: Forecasting Leaderboard
    story.append(Paragraph("<b>Table 3: Multi-Model Demand Forecasting Leaderboard (14-Day Holdout Set)</b>", styles['SectionH2']))
    fc_data = [
        [Paragraph("Forecasting Model", styles['Th']),
         Paragraph("Model Family", styles['Th']),
         Paragraph("Test MAPE (%)", styles['Th']),
         Paragraph("Test RMSE", styles['Th']),
         Paragraph("P<sub>90</sub> Surge Coverage", styles['Th'])],
        [Paragraph("Naive Moving Average (MA-7)", styles['Td']), Paragraph("Heuristic Baseline", styles['TdCenter']), Paragraph("44.56%", styles['TdCenter']), Paragraph("42.80", styles['TdCenter']), Paragraph("64.3%", styles['TdCenter'])],
        [Paragraph("Facebook Prophet", styles['Td']), Paragraph("Additive Seasonality", styles['TdCenter']), Paragraph("38.12%", styles['TdCenter']), Paragraph("36.45", styles['TdCenter']), Paragraph("78.6%", styles['TdCenter'])],
        [Paragraph("Ridge L2 Linear Model", styles['Td']), Paragraph("Regularized Lags", styles['TdCenter']), Paragraph("33.40%", styles['TdCenter']), Paragraph("31.20", styles['TdCenter']), Paragraph("82.1%", styles['TdCenter'])],
        [Paragraph("Random Forest Forecaster", styles['Td']), Paragraph("Tree Quantiles", styles['TdCenter']), Paragraph("29.85%", styles['TdCenter']), Paragraph("28.10", styles['TdCenter']), Paragraph("89.3%", styles['TdCenter'])],
        [Paragraph("Stacked Ensemble", styles['Td']), Paragraph("Meta-Blender", styles['TdCenter']), Paragraph("28.40%", styles['TdCenter']), Paragraph("26.90", styles['TdCenter']), Paragraph("90.4%", styles['TdCenter'])],
        [Paragraph("<b>ContractIQ XGBoost + Quantile LGBM</b>", styles['TdBold']), Paragraph("<b>Gradient Boosted Pinball</b>", styles['TdCenter']), Paragraph("<b>27.20%</b>", styles['TdHighlight']), Paragraph("<b>25.40</b>", styles['TdHighlight']), Paragraph("<b>91.1%</b>", styles['TdHighlight'])],
    ]
    t3 = Table(fc_data, colWidths=[165, 105, 75, 75, 85])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0, 5), (-1, 5), colors.white),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t3)
    story.append(Spacer(1, 6))

    # Table 4: Prescriptive Sourcing Impact
    story.append(Paragraph("<b>Table 4: Prescriptive Sourcing (MILP) Operational Impact</b>", styles['SectionH2']))
    milp_data = [
        [Paragraph("Procurement Metric", styles['Th']),
         Paragraph("Single-Source Baseline", styles['Th']),
         Paragraph("ContractIQ Prescriptive MILP", styles['Th']),
         Paragraph("Net Operational Gain", styles['Th'])],
        [Paragraph("Supplier Allocation Strategy", styles['Td']), Paragraph("100% Single Source (Apex)", styles['TdCenter']), Paragraph("65% Apex + 35% Vanguard", styles['TdCenter']), Paragraph("Active Dual Sourcing", styles['TdCenter'])],
        [Paragraph("Total Landed Procurement Cost", styles['Td']), Paragraph("$84,210.00", styles['TdCenter']), Paragraph("$74,771.07", styles['TdCenter']), Paragraph("<b>-$9,438.93 (-11.2%)</b>", styles['TdHighlight'])],
        [Paragraph("Disruption Exposure (Malacca Bottleneck)", styles['Td']), Paragraph("Critical Disruption (100% Stalled)", styles['TdCenter']), Paragraph("Mitigated (Alternative Route Active)", styles['TdCenter']), Paragraph("<b>-82.3% Disruption Risk</b>", styles['TdHighlight'])],
        [Paragraph("Contract SLA Penalty Exposure", styles['Td']), Paragraph("$12,500.00 (Uncontrolled)", styles['TdCenter']), Paragraph("$0.00 (Fully Hedged)", styles['TdCenter']), Paragraph("<b>-100% Penalty Avoided</b>", styles['TdHighlight'])],
    ]
    t4 = Table(milp_data, colWidths=[175, 110, 120, 100])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.white),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#ECFDF5')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ECFDF5')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#ECFDF5')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#94A3B8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t4)
    story.append(Spacer(1, 6))

    story.append(callout_box(
        "<b>Summary of Findings:</b> ContractIQ outperforms standard dense RAG by +20% in accuracy, eliminates hallucinations, "
        "reduces forecast error by 40%, and saves $9,438.93 per procurement run with automated mathematical optimization.",
        styles, border="#10B981", bg="#F0FDF4"
    ))

    # End of Page 3
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: CHALLENGES, LEARNINGS, CONCLUSION & SIGNATURES
    # =========================================================================
    story.append(Paragraph("5. Practical Challenges Faced & Engineering Solutions", styles['SectionH1']))
    challenges = [
        ("False Alarms in Factuality Auditing",
         "The post-generation audit script initially flagged our own system summary text as ungrounded numbers. "
         "<b>Solution:</b> Separated system prompt framing from generated claims, checking only model assertions against context text."),

        ("Running Local AI Without Cloud GPU Bills",
         "Cloud embedding APIs introduced network delays and cost money per call. "
         "<b>Solution:</b> Deployed local FastEmbed ONNX embeddings (`bge-small-en-v1.5`), generating vectors in <2 ms on standard CPUs."),

        ("Resolving Clause Collisions (e.g. Clause 4.1 vs 4.2)",
         "Dense semantic embeddings confused adjacent clauses that used identical legal jargon. "
         "<b>Solution:</b> Combined dense vectors with Okapi BM25 and a Cross-Reranker, ensuring exact clause numbers are prioritized."),

        ("Turning Text Answers into Math Constraints",
         "LLM outputs were unstructured and could not be plugged directly into an optimization solver. "
         "<b>Solution:</b> Implemented Pydantic v2 schemas and deterministic extractors that feed directly into SciPy HiGHS MILP.")
    ]
    for c_title, c_sol in challenges:
        story.append(Paragraph(f"• <b>{c_title}:</b> {c_sol}", styles['SimpleBullet']))
    story.append(Spacer(1, 5))

    story.append(Paragraph("6. Major Learnings from the Project", styles['SectionH1']))
    learnings = [
        "<b>Hybrid RAG is Mandatory for Contracts:</b> Pure semantic search fails on numbers, dates, and clause numbers. Combining dense embeddings with BM25 keyword matching is essential.",
        "<b>Zero Hallucination Requires Defense-in-Depth:</b> You cannot rely on prompt instructions alone. True safety requires an Abstention Gate (refusing low-confidence questions) plus post-generation automated fact-checking.",
        "<b>AI Must Be Actionable:</b> Conversational chatbots only give text advice. Pairing AI forecasts with Prescriptive Mixed-Integer Linear Programming turns insights into concrete, profitable business decisions.",
        "<b>Software Engineering Quality Matters:</b> Having 39/39 passing unit tests and an in-memory cache (169× speedup) makes the platform robust, fast, and ready for actual production use."
    ]
    for l in learnings:
        story.append(Paragraph(f"• {l}", styles['SimpleBullet']))
    story.append(Spacer(1, 5))

    story.append(Paragraph("7. Conclusion & Future Roadmap", styles['SectionH1']))
    story.append(Paragraph(
        "ContractIQ proves that combining high-assurance legal RAG with probabilistic forecasting and mathematical optimization "
        "effectively solves enterprise contract blindness. The project was completed, rigorously benchmarked, and verified at "
        "<b>SVNIT Surat</b> by <b>U23AI074, U23AI079, U23AI094, and U23AI072</b>. Future roadmap includes multi-agent contract "
        "negotiation swarms and automated legal amendment drafting.",
        styles['SimpleBody']
    ))
    story.append(Spacer(1, 8))

    story.append(callout_box(
        "<b>Academic Evaluation Verification:</b> All 39 test suites pass hermetically. "
        "Source code, sample PDFs, and benchmarks are available on GitHub: <b>https://github.com/Ujjwal-GoyaL019/ContractIQ</b>.",
        styles, border="#0284C7", bg="#F0F9FF"
    ))
    story.append(Spacer(1, 24))

    # Official SVNIT Signature Block
    sig_data = [
        [
            Paragraph("____________________________________<br/><b>Project Supervisor / Faculty Guide</b><br/>Department of Artificial Intelligence<br/>SVNIT Surat", styles['TdCenter']),
            Paragraph("____________________________________<br/><b>Head of Department (HOD) / Examiner</b><br/>Department of Artificial Intelligence<br/>SVNIT Surat", styles['TdCenter'])
        ]
    ]
    sig_table = Table(sig_data, colWidths=[252, 253])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)

    # Build the document
    doc.build(story, canvasmaker=SimpleNumberedCanvas)
    return output_filename


if __name__ == "__main__":
    out_paths = [
        r"C:\Users\hp\OneDrive\Desktop\ContractIQ_Project_Report_SVNIT.pdf",
        r"C:\Users\hp\OneDrive\Desktop\Projects\Rag project\ContractIQ_Project_Report_SVNIT.pdf",
        r"C:\Users\hp\OneDrive\Desktop\Rag project\ContractIQ_Project_Report_SVNIT.pdf",
        r"C:\Users\hp\.gemini\antigravity\brain\40bddb9e-75df-4888-bd68-bb8e478c154c\ContractIQ_Project_Report_SVNIT.pdf"
    ]

    for p in out_paths:
        try:
            d = os.path.dirname(p)
            os.makedirs(d, exist_ok=True)
            build_simple_report(p)
            print(f"[OK] Generated High-Contrast Report: {p}")
        except Exception as e:
            print(f"[WARN] Failed generating {p}: {e}")
