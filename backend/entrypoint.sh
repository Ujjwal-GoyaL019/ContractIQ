#!/bin/sh
set -e

echo "[ContractIQ Backend] Starting initialization..."

if [ "${AUTO_SEED:-true}" = "true" ]; then
  python -c "
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.models.supplier import Supplier
import app.db.models

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    count = db.query(Supplier).count()
finally:
    db.close()

if count == 0:
    print('[ContractIQ Backend] Empty database detected — seeding sample PDFs, suppliers, and forecasts...')
    from scripts.seed_database import seed_database
    seed_database()
else:
    print(f'[ContractIQ Backend] Database already initialized with {count} suppliers.')
"
fi

echo "[ContractIQ Backend] Launching Uvicorn server on 0.0.0.0:8000..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "${UVICORN_WORKERS:-1}"
