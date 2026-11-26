import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import random
import pandas as pd
import numpy as np

# Ensure app is importable
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.models.user import User
from app.db.models.supplier import Supplier
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.db.models.order import PurchaseOrder, PurchaseOrderItem
from app.db.models.sales_history import SalesHistory
from app.db.models.document import SupplierDocument
from app.core.security import hash_password
from app.services.rag.ingestion import ingestion_service
from app.services.rag.retrieval import vector_store
from app.workers.forecast_jobs import run_sku_forecast_job, run_all_forecasts_job
from app.core.logging import logger
from scripts.generate_sample_pdfs import generate_all_sample_pdfs

DATA_DIR = os.path.join(os.path.dirname(backend_dir), "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
DOCS_DATA_DIR = os.path.join(DATA_DIR, "supplier_docs")

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DATA_DIR, exist_ok=True)


USERS_DATA = [
    {
        "email": "admin@contractiq.ai",
        "password": "Admin@12345",
        "full_name": "Sarah Chen",
        "role": "admin",
    },
    {
        "email": "analyst@contractiq.ai",
        "password": "Analyst@12345",
        "full_name": "Marcus Vance",
        "role": "procurement_analyst",
    },
    {
        "email": "demo@contractiq.ai",
        "password": "Demo@12345",
        "full_name": "Alex Rivera",
        "role": "viewer",
    },
]

SUPPLIERS_DATA = [
    {
        "code": "SUP-APEX",
        "name": "Apex Microelectronics Corp",
        "contact_email": "orders@apexmicro.com",
        "contact_phone": "+1-408-555-0182",
        "country": "Taiwan",
        "base_lead_time_days": 21,
        "reliability_score": 0.94,
        "quality_score": 0.99,
        "disruption_risk_score": 15.0,
        "payment_terms": "Net 30",
        "notes": "Primary supplier for 32-bit MCUs and power management ICs. Reliable fabrication schedule."
    },
    {
        "code": "SUP-NORDIC",
        "name": "Nordic Silicon Solutions",
        "contact_email": "supply@nordicsilicon.eu",
        "contact_phone": "+47-22-555-0199",
        "country": "Norway",
        "base_lead_time_days": 14,
        "reliability_score": 0.98,
        "quality_score": 0.995,
        "disruption_risk_score": 8.0,
        "payment_terms": "Net 45",
        "notes": "Low-power Bluetooth/RF SoC provider. Consistently meets delivery milestones."
    },
    {
        "code": "SUP-PACIFIC",
        "name": "Pacific Precision Optics",
        "contact_email": "sales@pacificoptics.sg",
        "contact_phone": "+65-6789-0123",
        "country": "Singapore",
        "base_lead_time_days": 35,
        "reliability_score": 0.78,
        "quality_score": 0.91,
        "disruption_risk_score": 65.0,
        "payment_terms": "Net 15",
        "notes": "Subject to maritime freight backlogs. Price revision notice issued in recent addendum."
    },
    {
        "code": "SUP-TITAN",
        "name": "Titan Precision Polymers",
        "contact_email": "b2b@titanpolymers.com",
        "contact_phone": "+1-312-555-0144",
        "country": "US",
        "base_lead_time_days": 10,
        "reliability_score": 0.96,
        "quality_score": 0.98,
        "disruption_risk_score": 12.0,
        "payment_terms": "Net 30",
        "notes": "Domestic molding and enclosure parts. Quick turnaround."
    },
    {
        "code": "SUP-EUROOPTICS",
        "name": "EuroOptics Precision GmbH",
        "contact_email": "contracts@eurooptics.de",
        "contact_phone": "+49-3641-555-0177",
        "country": "Germany",
        "base_lead_time_days": 18,
        "reliability_score": 0.97,
        "quality_score": 0.996,
        "disruption_risk_score": 10.0,
        "payment_terms": "Net 30",
        "notes": "Qualified secondary optical lens supplier (ISO Class 5 cleanroom). Air-freight corridor immune to Asian maritime delays."
    },
]

PRODUCTS_DATA = [
    {
        "sku": "SKU-MCU-32B",
        "name": "High-Performance 32-Bit Cortex-M4 MCU",
        "description": "168MHz microcontroller with 1MB Flash and hardware FPU",
        "category": "Semiconductors",
        "unit_of_measure": "units",
        "unit_cost": 6.80,
        "unit_price": 14.50,
        "min_safety_stock": 200,
        "target_service_level": 0.98,
        "lead_time_days": 21,
        "supplier_code": "SUP-APEX",
        "current_stock": 260, # Impending risk under high demand
        "allocated_stock": 80,
        "incoming_stock": 150,
        "reorder_point": 350,
        "reorder_quantity": 500,
    },
    {
        "sku": "SKU-BLE-SOC",
        "name": "Ultra-Low Power BLE 5.3 SoC Module",
        "description": "Multi-protocol Bluetooth LE and Zigbee transceiver module",
        "category": "Wireless Modules",
        "unit_of_measure": "units",
        "unit_cost": 4.20,
        "unit_price": 9.90,
        "min_safety_stock": 150,
        "target_service_level": 0.95,
        "lead_time_days": 14,
        "supplier_code": "SUP-NORDIC",
        "current_stock": 650,
        "allocated_stock": 40,
        "incoming_stock": 200,
        "reorder_point": 250,
        "reorder_quantity": 400,
    },
    {
        "sku": "SKU-LENS-4K",
        "name": "Optical 4K Sensor Glass Lens Array",
        "description": "Anti-reflective coated precision glass lens for vision sensors",
        "category": "Optoelectronics",
        "unit_of_measure": "units",
        "unit_cost": 18.50,
        "unit_price": 42.00,
        "min_safety_stock": 100,
        "target_service_level": 0.95,
        "lead_time_days": 35,
        "supplier_code": "SUP-PACIFIC",
        "current_stock": 45, # Critical shortage!
        "allocated_stock": 20,
        "incoming_stock": 0,
        "reorder_point": 120,
        "reorder_quantity": 250,
    },
    {
        "sku": "SKU-ENC-IP67",
        "name": "IP67 Ruggedized Polycarbonate Enclosure",
        "description": "Waterproof industrial grade enclosure with silicone gasket",
        "category": "Mechanical",
        "unit_of_measure": "units",
        "unit_cost": 11.20,
        "unit_price": 26.00,
        "min_safety_stock": 120,
        "target_service_level": 0.90,
        "lead_time_days": 10,
        "supplier_code": "SUP-TITAN",
        "current_stock": 380,
        "allocated_stock": 30,
        "incoming_stock": 100,
        "reorder_point": 200,
        "reorder_quantity": 300,
    },
]


def create_sample_contracts():
    """Generates realistic text/PDF contract and notice documents."""
    docs = [
        {
            "filename": "Apex_Microelectronics_Master_SLA_2025.txt",
            "title": "Apex Microelectronics Master Supply & SLA Agreement",
            "supplier_code": "SUP-APEX",
            "doc_type": "contract",
            "content": """MASTER SUPPLY & SERVICE LEVEL AGREEMENT
Supplier: Apex Microelectronics Corp (Taiwan)
Buyer: Smart Inventory Solutions Inc.
Effective Date: January 1, 2025

1. SUPPLY COMMITMENT & LEAD TIME:
Apex Microelectronics guarantees standard manufacturing lead times of 21 calendar days for Cortex-M4 MCU components (SKU-MCU-32B). Minimum order quantity (MOQ) is 500 units per purchase order.

2. EXPEDITED ORDERS & SURCHARGES:
Buyer may request an expedited 10-day turnaround subject to a 20% surcharge and fab line availability.

3. CAPACITY & FORCE MAJEURE:
In the event of global silicon wafer allocation shortages exceeding 15% industry supply reduction, Supplier reserves the right to pro-rata allocate deliveries across active tier-1 contract holders.

4. WARRANTY & QUALITY STANDARDS:
Defect rate guarantee is maintained at less than 100 DPPM (defects per million). Rejections will be replaced within 14 calendar days at Supplier's sole freight cost."""
        },
        {
            "filename": "Pacific_Optics_Supply_Notice_Risk.txt",
            "title": "Pacific Precision Optics - Disruption & Price Revision Notice",
            "supplier_code": "SUP-PACIFIC",
            "doc_type": "risk_notice",
            "content": """URGENT OPERATIONAL NOTICE & CONTRACT AMENDMENT
Supplier: Pacific Precision Optics (Singapore)
Date: February 10, 2026
Subject: Lead Time Extension & Raw Material Surcharge for Lens Arrays (SKU-LENS-4K)

Please be advised that due to regional raw optical glass refining disruptions and ongoing maritime shipping congestion in the Malacca Strait:
1. Standard lead times for all 4K Sensor Lens Arrays (SKU-LENS-4K) are temporarily extended from 21 business days to 35-42 calendar days.
2. A temporary logistics energy surcharge of 12.5% will apply to all purchase orders placed after March 1, 2026.
3. Pacific Precision Optics urges all procurement teams to place rolling 60-day buffer orders immediately to prevent factory line stockouts.
4. On-time delivery SLA penalties are temporarily waived during this force majeure period."""
        },
        {
            "filename": "Nordic_Silicon_Framework_Agreement.txt",
            "title": "Nordic Silicon Solutions Framework Supply Terms",
            "supplier_code": "SUP-NORDIC",
            "doc_type": "contract",
            "content": """FRAMEWORK PURCHASE AGREEMENT
Supplier: Nordic Silicon Solutions (Norway)
Product Category: Wireless Modules & Bluetooth SoCs (SKU-BLE-SOC)

TERMS & CONDITIONS:
1. Standard Delivery: FOB Oslo with guaranteed 14-day lead time across European and North American distribution hubs.
2. Reliability Commitment: 98.5% guaranteed on-time fulfillment rate with late delivery penalty of 1.5% per week of delay up to a maximum 10% credit.
3. Volume Discount: 5% discount applied automatically on batch orders exceeding 1,000 units.
4. Inventory Consignment: Nordic maintains a 30-day revolving safety stock buffer in regional European warehousing."""
        },
        {
            "filename": "Titan_Polymers_Standard_Delivery_Terms.txt",
            "title": "Titan Precision Polymers Enclosure Delivery Agreement",
            "supplier_code": "SUP-TITAN",
            "doc_type": "contract",
            "content": """DOMESTIC MANUFACTURING & SUPPLY AGREEMENT
Supplier: Titan Precision Polymers (Chicago, US)
Products: Industrial Enclosures (SKU-ENC-IP67)

1. LEAD TIME: 10 calendar days for standard production runs up to 1,000 units.
2. EMERGENCY SHIPMENTS: Domestic overnight courier dispatch available with same-day tooling prep.
3. PAYMENT TERMS: Net 30 days.
4. QUALITY COMPLIANCE: ISO 9001:2015 and IP67 waterproof certification compliance."""
        }
    ]

    saved_docs = []
    for doc in docs:
        file_path = os.path.join(DOCS_DATA_DIR, doc["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc["content"])
        saved_docs.append({
            "file_path": file_path,
            "filename": doc["filename"],
            "title": doc["title"],
            "supplier_code": doc["supplier_code"],
            "doc_type": doc["doc_type"]
        })
    return saved_docs


def generate_synthetic_sales_history(product_id: str, base_daily: float, volatility: float = 0.25, days: int = 400) -> List[SalesHistory]:
    """Generates 400 days of realistic daily sales history with day-of-week seasonality, trend, and holiday surges."""
    records = []
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    current_date = start_date
    day_idx = 0

    while current_date < end_date:
        dow = current_date.weekday()
        # Weekend slight reduction or increase based on B2B
        dow_factor = 1.2 if dow in [1, 2, 3] else (0.8 if dow in [5, 6] else 1.0)
        
        # Monthly seasonality + slight upward trend
        trend_factor = 1.0 + (day_idx / days) * 0.2
        season_factor = 1.0 + 0.15 * np.sin(2 * np.pi * current_date.timetuple().tm_yday / 365.0)

        # Occasional promotions
        is_promo = random.random() < 0.08
        promo_factor = 1.8 if is_promo else 1.0

        # Random noise
        noise = np.random.normal(1.0, volatility)
        qty = int(max(1, round(base_daily * dow_factor * trend_factor * season_factor * promo_factor * noise)))

        # Occasional historical stockout mark
        had_stockout = False
        if qty > base_daily * 2.2 and random.random() < 0.15:
            had_stockout = True

        records.append(
            SalesHistory(
                product_id=product_id,
                sales_date=current_date,
                quantity_sold=qty,
                unit_price=round(base_daily * 1.5, 2),
                is_promotion=is_promo,
                is_holiday=(current_date.month == 12 and current_date.day >= 20),
                had_stockout=had_stockout
            )
        )
        current_date += timedelta(days=1)
        day_idx += 1

    return records


def seed_database():
    logger.info("Starting database initialization and seeding...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Seed Default Demo Users
        for u_data in USERS_DATA:
            user = User(
                email=u_data["email"],
                hashed_password=hash_password(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                is_active=True
            )
            db.add(user)
        db.commit()
        logger.info(f"Seeded {len(USERS_DATA)} demo users.")

        # 2. Seed Suppliers
        supplier_map = {}
        for s_data in SUPPLIERS_DATA:
            supplier = Supplier(**s_data)
            db.add(supplier)
            db.flush()
            supplier_map[s_data["code"]] = supplier

        logger.info(f"Seeded {len(supplier_map)} suppliers.")

        # 3. Seed Products and Inventory
        product_map = {}
        all_sales_records = []

        for p_raw in PRODUCTS_DATA:
            p_data = p_raw.copy()
            sup_code = p_data.pop("supplier_code")
            supplier = supplier_map.get(sup_code)
            
            c_stock = p_data.pop("current_stock")
            a_stock = p_data.pop("allocated_stock")
            i_stock = p_data.pop("incoming_stock")
            r_point = p_data.pop("reorder_point")
            r_qty = p_data.pop("reorder_quantity")

            product = Product(**p_data, supplier_id=supplier.id if supplier else None)
            db.add(product)
            db.flush()
            product_map[product.sku] = product

            # Create Inventory record
            inventory = Inventory(
                product_id=product.id,
                warehouse_code="WH-MAIN",
                current_stock=c_stock,
                allocated_stock=a_stock,
                incoming_stock=i_stock,
                reorder_point=r_point,
                reorder_quantity=r_qty,
                days_of_supply=round(c_stock / 15.0, 1),
                urgency_status="HEALTHY"
            )
            db.add(inventory)

            # Generate ~400 days sales history per SKU
            base_sales = 20.0 if "MCU" in product.sku else (14.0 if "BLE" in product.sku else (8.0 if "LENS" in product.sku else 16.0))
            sales = generate_synthetic_sales_history(product_id=product.id, base_daily=base_sales)
            all_sales_records.extend(sales)

        db.bulk_save_objects(all_sales_records)
        db.commit()
        logger.info(f"Seeded {len(product_map)} products with {len(all_sales_records)} historical demand entries.")

        # 3. Create Sample Purchase Orders
        po_records = [
            PurchaseOrder(
                order_number="PO-2026-001",
                supplier_id=supplier_map["SUP-APEX"].id,
                order_date=date.today() - timedelta(days=10),
                expected_delivery_date=date.today() + timedelta(days=11),
                status="SHIPPED",
                total_amount=3400.0,
                delay_days=0,
                notes="Standard weekly batch order for MCU microcontrollers"
            ),
            PurchaseOrder(
                order_number="PO-2026-002",
                supplier_id=supplier_map["SUP-PACIFIC"].id,
                order_date=date.today() - timedelta(days=25),
                expected_delivery_date=date.today() - timedelta(days=4), # Overdue!
                status="DELAYED",
                total_amount=4625.0,
                delay_days=4,
                notes="Optics batch delayed at port customs due to congestion notice"
            )
        ]
        db.add_all(po_records)
        db.commit()

        # 4. Generate & Ingest Multi-Page Enterprise Supplier PDFs into Qdrant + BM25 Hybrid Store
        logger.info("Generating and ingesting multi-page supplier contract PDFs into hybrid vector store...")
        vector_store.reset_collection()
        doc_files = generate_all_sample_pdfs(DOCS_DATA_DIR)
        for doc_item in doc_files:
            supplier = supplier_map.get(doc_item["supplier_code"])
            import uuid
            doc_id = str(uuid.uuid4())

            ingest_res = ingestion_service.ingest_document(
                file_path=doc_item["file_path"],
                doc_id=doc_id,
                title=doc_item["title"],
                supplier_id=supplier.id if supplier else None,
                supplier_name=supplier.name if supplier else "General Supplier",
                doc_type=doc_item["doc_type"]
            )

            db_doc = SupplierDocument(
                id=doc_id,
                title=doc_item["title"],
                filename=doc_item["filename"],
                file_path=doc_item["file_path"],
                doc_type=doc_item["doc_type"],
                supplier_id=supplier.id if supplier else None,
                file_size_bytes=ingest_res["file_size"],
                chunk_count=ingest_res["chunk_count"],
                content_hash=ingest_res["file_hash"],
                summary=f"Key terms and agreements with {supplier.name if supplier else 'supplier'}."
            )
            db.add(db_doc)

        db.commit()
        logger.info(f"Ingested {len(doc_files)} supplier documents.")

        # 5. Run initial demand forecasting and risk calculations
        logger.info("Computing initial demand forecasts and risk indices...")
        for sku in product_map.keys():
            # Run both Prophet and LightGBM
            run_sku_forecast_job(sku=sku, model_type="prophet", horizon_days=30, db=db)
            run_sku_forecast_job(sku=sku, model_type="lightgbm", horizon_days=30, db=db)

        logger.info("[SUCCESS] Database seeded and forecasts calculated successfully!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
