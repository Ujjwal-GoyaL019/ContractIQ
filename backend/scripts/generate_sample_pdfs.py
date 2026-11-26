import os
from typing import List, Dict, Any
from reportlab.lib.pagesizes import LETTER
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak


CONTRACT_SPECS: List[Dict[str, Any]] = [
    {
        "filename": "Apex_Microelectronics_Master_SLA_2025.pdf",
        "title": "Apex Microelectronics Master Supply & SLA Agreement (2025)",
        "supplier_code": "SUP-APEX",
        "doc_type": "contract",
        "doc_number": "MSA-APEX-2025-001",
        "effective_date": "January 1, 2025",
        "parties": "Apex Microelectronics Corp (Hsinchu, Taiwan) & ContractIQ Buyer Operations",
        "pages": [
            {
                "heading": "SECTION 1 & 2: SCOPE, SUPPLY COMMITMENT & LEAD TIME",
                "paragraphs": [
                    "1.1 Scope of Agreement: This Master Supply and Service Level Agreement (MSA-APEX-2025-001) governs the fabrication, quality assurance, packaging, and delivery of High-Performance 32-Bit Cortex-M4 Microcontrollers (SKU-MCU-32B) supplied by Apex Microelectronics Corp.",
                    "2.1 Standard Manufacturing Lead Time: Apex Microelectronics guarantees a standard manufacturing and ocean/air consolidated delivery lead time of twenty-one (21) calendar days from Purchase Order acknowledgment for SKU-MCU-32B.",
                    "2.4 Minimum Order Quantity (MOQ): Standard production batch Minimum Order Quantity is strictly five hundred (500) units per Purchase Order line item. Base unit pricing is established at $6.80 USD per unit FOB Taipei."
                ],
                "table": [
                    ["Parameter", "Contracted Term", "Clause Ref"],
                    ["Covered SKU", "SKU-MCU-32B (Cortex-M4 MCU)", "Section 1.1"],
                    ["Standard Lead Time", "21 Calendar Days", "Section 2.1"],
                    ["Minimum Order Quantity", "500 Units per PO", "Section 2.4"],
                    ["Base Unit Price", "$6.80 USD (FOB Taipei)", "Section 2.4"],
                    ["Payment Terms", "Net 30 Days from B/L", "Section 2.6"],
                ]
            },
            {
                "heading": "SECTION 3 & 4: EXPEDITED ORDERS & FORCE MAJEURE ALLOCATION",
                "paragraphs": [
                    "3.1 Expedited Rush Turnaround: Buyer may request an expedited 10-day turnaround schedule for urgent factory replenishment of SKU-MCU-32B. Expedited orders requested with less than fourteen (14) days advance notice incur a mandatory 20% rush surcharge fee and are subject to semiconductor fab line availability.",
                    "4.2 Capacity & Force Majeure Allocation: In the event of global silicon wafer allocation shortages exceeding 15% industry-wide supply reduction, foundry power interruption, or natural disaster, Supplier reserves the right to implement pro-rata allocation of deliveries across active Tier-1 contract holders.",
                    "4.3 Notice Obligation: Supplier must issue written Force Majeure notice within seventy-two (72) hours of disruption onset, specifying projected recovery milestones and revised shipment schedules."
                ]
            },
            {
                "heading": "SECTION 6 & 7: QUALITY WARRANTY & LIQUIDATED DAMAGES",
                "paragraphs": [
                    "6.1 Quality Defect Guarantee: Apex Microelectronics warrants that delivered semiconductor lots shall maintain an outgoing defect rate of less than 100 DPPM (defects per million). Non-conforming lots verified by incoming QA will be replaced within 14 calendar days at Supplier's sole air-freight expense.",
                    "7.2 Liquidated Damages for Late Delivery: Excluding verified Force Majeure events under Section 4.2, shipments delayed beyond a 3-business-day grace period shall incur liquidated damages equal to 2.0% of the delayed Purchase Order value per week of delay, up to an aggregate cap of 12% of the affected order value.",
                    "7.5 Governing Law & Audit Rights: Buyer retains semi-annual audit rights over ISO 9001 and IATF 16949 fabrication records."
                ]
            }
        ]
    },
    {
        "filename": "Apex_Microelectronics_Addendum_2026_Q2.pdf",
        "title": "Apex Microelectronics Q2 2026 Pricing & Buffer Addendum",
        "supplier_code": "SUP-APEX",
        "doc_type": "addendum",
        "doc_number": "ADD-APEX-2026-Q2",
        "effective_date": "April 1, 2026",
        "parties": "Apex Microelectronics Corp & ContractIQ Buyer Operations",
        "pages": [
            {
                "heading": "AMENDMENT 1: TIERED VOLUME PRICING & REDUCED MOQ PILOT",
                "paragraphs": [
                    "This Contract Addendum (ADD-APEX-2026-Q2) amends Master Supply Agreement MSA-APEX-2025-001 specifically for SKU-MCU-32B during fiscal year 2026.",
                    "1.2 Tiered Volume Discount: To incentivize consolidated quarterly replenishment, Apex Microelectronics grants an automatic 6% volume pricing discount on single Purchase Orders exceeding 1,500 units (reducing net unit cost from $6.80 to $6.39 USD).",
                    "1.3 Dual-Source Flexibility Pilot: For split-order procurement programs, the pilot MOQ floor is temporarily lowered from 500 units to 250 units when Buyer maintains an annual rolling forecast commitment."
                ],
                "table": [
                    ["Order Volume Tier (SKU-MCU-32B)", "Discount", "Net Unit Price"],
                    ["250 - 1,499 Units (Pilot MOQ)", "0%", "$6.80 USD"],
                    ["1,500 - 4,999 Units", "6.0%", "$6.39 USD"],
                    ["5,000+ Units", "9.5%", "$6.15 USD"],
                ]
            },
            {
                "heading": "AMENDMENT 2: BUFFER WAFER BANK & LEAD TIME STABILITY",
                "paragraphs": [
                    "2.1 Dedicated Die Bank: Apex commits to maintaining a rolling 14-day finished die bank in Hsinchu dedicated to SKU-MCU-32B, stabilizing standard fulfillment lead time at 21 calendar days even during Q3 consumer electronics peak demand.",
                    "2.2 Superseding Clause: Where terms of Addendum ADD-APEX-2026-Q2 conflict with Section 2.4 of MSA-APEX-2025-001 regarding MOQ and tiered pricing, this Addendum shall supersede for all orders placed between April 1, 2026 and December 31, 2026."
                ]
            }
        ]
    },
    {
        "filename": "Pacific_Optics_Supply_Notice_Risk_2026.pdf",
        "title": "Pacific Precision Optics - Disruption & Price Revision Notice (2026)",
        "supplier_code": "SUP-PACIFIC",
        "doc_type": "risk_notice",
        "doc_number": "NOTICE-PPO-2026-014",
        "effective_date": "February 10, 2026",
        "parties": "Pacific Precision Optics Pte Ltd (Singapore) -> All Tier-1 Buyers",
        "pages": [
            {
                "heading": "URGENT OPERATIONAL DISRUPTION NOTICE (SKU-LENS-4K)",
                "paragraphs": [
                    "Subject: Lead Time Extension, Maritime Port Congestion & Logistics Surcharge for Optical 4K Sensor Glass Lens Arrays (SKU-LENS-4K).",
                    "1.1 Extended Lead Times: Due to regional raw optical borosilicate glass refining bottlenecks and severe maritime shipping congestion across the Malacca Strait and Port of Singapore, standard delivery lead times for SKU-LENS-4K are temporarily extended from 21 business days to 35-42 calendar days.",
                    "1.2 Logistics Energy Surcharge: Effective for all Purchase Orders placed after March 1, 2026, a temporary 12.5% logistics and fuel energy surcharge shall be added to the base contract price of $18.50 USD (bringing effective landed cost to $20.81 USD per unit)."
                ],
                "table": [
                    ["Risk Factor", "Previous Baseline", "Revised 2026 Condition"],
                    ["Affected SKU", "SKU-LENS-4K", "SKU-LENS-4K (All Batches)"],
                    ["Delivery Lead Time", "21 Business Days", "35 - 42 Calendar Days"],
                    ["Logistics Surcharge", "0.0%", "+12.5% after March 1, 2026"],
                    ["SLA Late Penalty", "2.0% / week", "Temporarily Waived (Force Majeure)"],
                ]
            },
            {
                "heading": "SECTION 2: FORCE MAJEURE WAIVER & BUYER MITIGATION ADVISORY",
                "paragraphs": [
                    "2.1 Temporary SLA Penalty Waiver: Pursuant to Maritime Force Majeure Clause 9.4 of the Pacific Optics Framework Agreement, on-time delivery SLA liquidated damages are temporarily suspended during the active congestion window.",
                    "2.2 Buffer Inventory Recommendation: Pacific Precision Optics urgently advises procurement teams to establish rolling 60-day safety stock buffers or activate qualified secondary optical suppliers immediately to prevent downstream manufacturing line stoppages.",
                    "2.3 Payment Terms: Standard payment terms remain Net 15 days from shipment departure."
                ]
            }
        ]
    },
    {
        "filename": "Nordic_Silicon_Framework_Agreement_2025.pdf",
        "title": "Nordic Silicon Solutions Framework Supply & Dual-Source Agreement",
        "supplier_code": "SUP-NORDIC",
        "doc_type": "contract",
        "doc_number": "FPA-NORDIC-2025-088",
        "effective_date": "March 15, 2025",
        "parties": "Nordic Silicon Solutions AS (Oslo, Norway) & ContractIQ Buyer Operations",
        "pages": [
            {
                "heading": "SECTION 1 & 2: PRODUCT SCOPE & GUARANTEED DELIVERY TERMS",
                "paragraphs": [
                    "1.1 Covered Components: Nordic Silicon Solutions serves as Primary Supplier for Ultra-Low Power BLE 5.3 SoC Modules (SKU-BLE-SOC) at $4.20 USD/unit and Qualified Secondary Dual-Source Supplier for 32-Bit Cortex-M4 MCUs (SKU-MCU-32B) at $7.35 USD/unit.",
                    "2.1 Guaranteed Delivery Lead Time: Delivery is FOB Oslo with a contractually guaranteed 14-day calendar lead time across European and North American distribution hubs.",
                    "2.2 Minimum Order Quantity & Payment Terms: Standard MOQ is 150 units per SKU order. Payment terms are Net 45 days upon verified warehouse receipt."
                ],
                "table": [
                    ["SKU", "Role", "Unit Price", "Lead Time", "MOQ"],
                    ["SKU-BLE-SOC", "Primary", "$4.20 USD", "14 Days", "150 Units"],
                    ["SKU-MCU-32B", "Secondary Qualified", "$7.35 USD", "14 Days", "150 Units"],
                ]
            },
            {
                "heading": "SECTION 3: ON-TIME RELIABILITY SLA & PENALTIES",
                "paragraphs": [
                    "3.1 Reliability Commitment: Nordic Silicon commits to a 98.5% guaranteed on-time-in-full (OTIF) fulfillment rate measured quarterly across all active purchase orders.",
                    "3.2 Late Delivery Penalty Schedule: Any unexcused delivery delay beyond the 14-day SLA incurs an automatic late delivery penalty credit of 1.5% per week of delay, capped at a maximum 10% credit against the delayed invoice.",
                    "3.3 Hardware Replacement Warranty: Standard hardware replacement warranty period is twenty-four (24) months from shipment date."
                ]
            },
            {
                "heading": "SECTION 4: VOLUME DISCOUNTS & CONSIGNMENT WAREHOUSING",
                "paragraphs": [
                    "4.1 Automated Volume Discount: A 5% volume discount is applied automatically on consolidated batch orders exceeding 1,000 units of SKU-BLE-SOC.",
                    "4.2 Consignment Buffer Stock: Nordic Silicon maintains a dedicated 30-day revolving consignment safety stock buffer in regional European warehousing to absorb unexpected 2x demand surges without lead-time slippage."
                ]
            }
        ]
    },
    {
        "filename": "Titan_Polymers_Delivery_Terms_2025.pdf",
        "title": "Titan Precision Polymers Domestic Delivery & Quality Agreement",
        "supplier_code": "SUP-TITAN",
        "doc_type": "contract",
        "doc_number": "DMA-TITAN-2025-042",
        "effective_date": "January 15, 2025",
        "parties": "Titan Precision Polymers LLC (Chicago, IL, USA) & ContractIQ Buyer Operations",
        "pages": [
            {
                "heading": "SECTION 1: DOMESTIC PRODUCTION & RAPID TURNAROUND",
                "paragraphs": [
                    "1.1 Covered Products: IP67 Ruggedized Polycarbonate Industrial Enclosures with silicone gaskets (SKU-ENC-IP67) priced at $11.20 USD per unit (MOQ 100 units).",
                    "1.2 Standard Domestic Lead Time: Ten (10) calendar days for standard injection-molding production runs up to 1,000 units shipped ex-works Chicago.",
                    "1.3 Emergency Overnight Dispatch: Domestic overnight air courier dispatch is available for critical line-down emergencies with same-day tooling prep at a flat $350 expedite fee."
                ]
            },
            {
                "heading": "SECTION 2: QUALITY CERTIFICATIONS & PAYMENT TERMS",
                "paragraphs": [
                    "2.1 Regulatory & Environmental Compliance: All molded enclosures comply strictly with ISO 9001:2015 Quality Management Systems and certified IP67 waterproof/dustproof ingress protection testing.",
                    "2.2 SLA & Late Penalty: On-time fulfillment target is 96.0%, with a 1.0% weekly late delivery credit on orders exceeding 12 calendar days.",
                    "2.3 Payment Terms: Standard invoicing is Net 30 days via ACH transfer."
                ]
            }
        ]
    },
    {
        "filename": "EuroOptics_Secondary_Qualification_SLA_2026.pdf",
        "title": "EuroOptics GmbH Secondary Optical Qualification & Dual-Source SLA",
        "supplier_code": "SUP-EUROOPTICS",
        "doc_type": "compliance",
        "doc_number": "SLA-EURO-2026-009",
        "effective_date": "February 20, 2026",
        "parties": "EuroOptics Precision GmbH (Jena, Germany) & ContractIQ Buyer Operations",
        "pages": [
            {
                "heading": "SECTION 1: SECONDARY DUAL-SOURCE QUALIFICATION FOR SKU-LENS-4K",
                "paragraphs": [
                    "1.1 Strategic Mitigation Role: EuroOptics GmbH is formally qualified as Secondary Backup Supplier for Optical 4K Sensor Glass Lens Arrays (SKU-LENS-4K) to mitigate Asian maritime freight bottlenecks affecting Pacific Precision Optics.",
                    "1.2 Pricing & Surcharge Immunity: Standard contract unit cost is $21.40 USD per unit (MOQ 100 units, monthly capacity 1,200 units) with ZERO maritime or energy surcharge through 2026.",
                    "1.3 Air-Freight Lead Time: Guaranteed door-to-door delivery lead time of eighteen (18) calendar days from Jena, Germany via direct European air cargo corridors."
                ],
                "table": [
                    ["Attribute", "EuroOptics GmbH (Secondary)", "Notes"],
                    ["Qualified SKU", "SKU-LENS-4K", "Full drop-in optical compatibility"],
                    ["Unit Cost", "$21.40 USD (0% Surcharge)", "Fixed through Q4 2026"],
                    ["Lead Time", "18 Calendar Days", "Direct Air Cargo (No Malacca Route)"],
                    ["Reliability / OTD", "97.0% Guaranteed", "2.0%/wk Late Delivery SLA Penalty"],
                ]
            },
            {
                "heading": "SECTION 2: CLEANROOM QUALITY & COMPLIANCE STANDARDS",
                "paragraphs": [
                    "2.1 Cleanroom Compliance: All optical anti-reflective coating and precision glass grinding operates inside certified Cleanroom ISO Class 5 facilities.",
                    "2.2 Optical Defect Tolerance: Maximum allowable batch defect tolerance is strictly 0.02% across all inspected 4K optical lots, backed by automated interferometry certificates shipped with every crate.",
                    "2.3 Payment Terms & SLA: Payment terms are Net 30 days. Late shipments beyond 18 days trigger a binding 2.0% weekly SLA penalty credit with NO maritime force majeure waiver."
                ]
            }
        ]
    }
]


def _render_pdf(spec: Dict[str, Any], output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=spec["title"],
        author="ContractIQ Legal Procurement System"
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Title"],
        fontSize=15,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=6,
        alignment=0,
    )
    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#475569"),
        spaceAfter=4,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=11,
        textColor=colors.HexColor("#0369A1"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=8,
    )

    story = []
    for page_idx, page_spec in enumerate(spec["pages"]):
        if page_idx == 0:
            story.append(Paragraph(spec["title"].upper(), title_style))
            story.append(Paragraph(f"<b>Document ID:</b> {spec['doc_number']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Effective Date:</b> {spec['effective_date']}", meta_style))
            story.append(Paragraph(f"<b>Parties:</b> {spec['parties']}", meta_style))
            story.append(Spacer(1, 0.15 * inch))
        else:
            story.append(PageBreak())
            story.append(Paragraph(f"{spec['title']} — Page {page_idx + 1} ({spec['doc_number']})", meta_style))
            story.append(Spacer(1, 0.1 * inch))

        story.append(Paragraph(page_spec["heading"], heading_style))
        for p in page_spec["paragraphs"]:
            story.append(Paragraph(p, body_style))

        if "table" in page_spec:
            story.append(Spacer(1, 0.1 * inch))
            tbl = Table(page_spec["table"], repeatRows=1)
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8FAFC"), colors.white]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]))
            story.append(tbl)
            story.append(Spacer(1, 0.15 * inch))

    doc.build(story)


def generate_all_sample_pdfs(output_dir: str) -> List[Dict[str, Any]]:
    """
    Generates all 6 multi-page enterprise PDF contracts/notices into output_dir
    and returns their metadata ready for ingestion.
    """
    os.makedirs(output_dir, exist_ok=True)
    generated = []
    for spec in CONTRACT_SPECS:
        file_path = os.path.join(output_dir, spec["filename"])
        _render_pdf(spec, file_path)
        generated.append({
            "file_path": file_path,
            "filename": spec["filename"],
            "title": spec["title"],
            "supplier_code": spec["supplier_code"],
            "doc_type": spec["doc_type"],
            "pages": len(spec["pages"]),
        })
    return generated


if __name__ == "__main__":
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = os.path.join(base, "data", "supplier_docs")
    docs = generate_all_sample_pdfs(out)
    for d in docs:
        print(f"Generated PDF ({d['pages']} pages): {d['file_path']}")
