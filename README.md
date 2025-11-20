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
```

2 Docker
```bash
docker pull yadi09/comps-app:latest
docker run -p 8001:8001 yadi09/comps-app:latest
```

3 How to use
- Using Api /comps endpoint
- using Frontend / endpoing