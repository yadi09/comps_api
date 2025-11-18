# Comps Project

## Quick start (local)

1. Create venv and install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000