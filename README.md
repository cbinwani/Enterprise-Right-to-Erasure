# Enterprise RTBF / Right-to-Erasure

A self-contained demo showing an enterprise Right to Erasure / Right to Be Forgotten control plane across three heterogeneous systems:

1. Modern Web Application - REST API.
2. Legacy Green Screen - no REST API; RTBF uses a terminal-style TCP adapter.
3. COTS CRM - vendor-style privacy endpoint.

## What the demo shows

- RTBF request initiated from a web frontend.
- DELETE or ANONYMIZE choice.
- Live request status polling.
- Enterprise Exclusion List stored as `data/exclusion-list.json`.
- Exclusion List web view and REST API.
- Downstream ingestion decision API that returns BLOCK/ALLOW.
- JSON-backed audit log with a dedicated web view.
- Validation web view showing per-system execution and verification.
- Agentic execution pattern: Observe -> Plan -> Act -> Verify.
- Sample Web, COTS and Green Screen applications that visibly change after execution.
- Idempotent behavior when a record is already absent.

## Run in VS Code

### 1. Requirements

- Python 3.10+
- Visual Studio Code
- Python extension for VS Code

### 2. Open project

Open `rtbf_enterprise_project` in VS Code.

### 3. Create virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 4. Install packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Start

```bash
python run.py
```

Open http://127.0.0.1:8000

## Demo walkthrough

### Step 1 - Open the main RTBF screen

http://127.0.0.1:8000

Use `alice@example.com`.

Select:

- DELETE, or
- ANONYMIZE

Click **Submit RTBF Request**.

The screen polls the request and shows:

- Request status
- System execution status
- Record references
- Verification results
- Agent trace

### Step 2 - Show the sample systems before/after

Modern Web Application:

http://127.0.0.1:8000/demo/web

COTS CRM:

http://127.0.0.1:8000/demo/cots

Green Screen:

http://127.0.0.1:8000/static/green-screen.html

The Green Screen page is a visual representation. The actual RTBF adapter uses the TCP terminal service on port 2323.

### Step 3 - Show the Exclusion List

Main page -> Exclusion List section.

API:

```bash
curl http://127.0.0.1:8000/api/exclusion-list
```

File:

`data/exclusion-list.json`

The subject is stored as a SHA-256 hash plus a masked display value; raw PII is not written to the exclusion file.

### Step 4 - Demonstrate downstream suppression

```bash
curl -X POST http://127.0.0.1:8000/api/ingestion/decision \
  -H 'Content-Type: application/json' \
  -d '{"subject_value":"alice@example.com"}'
```

Expected:

```json
{"allowed":false,"decision":"BLOCK","reason":"RTBF request received"}
```

### Step 5 - Show Audit Log

Main page -> Audit Log.

API:

http://127.0.0.1:8000/api/audit-log

File:

`data/audit-log.json`

### Step 6 - Show Validation

Main page -> Validation. Once the request is complete it displays:

- overall status
- per-system execution status
- per-system verification status
- agent trace
- exclusion record

API:

`/api/validation/{request_id}`

## API quick reference

| Purpose | Method | Endpoint |
|---|---|---|
| Create RTBF | POST | `/api/rtbf/requests` |
| List requests | GET | `/api/rtbf/requests` |
| Request status | GET | `/api/rtbf/requests/{id}` |
| Exclusion list | GET | `/api/exclusion-list` |
| Check exclusion | POST | `/api/exclusion-list/check` |
| Ingestion guard | POST | `/api/ingestion/decision` |
| Audit log | GET | `/api/audit-log` |
| Validation | GET | `/api/validation/{id}` |
| Agent architecture | GET | `/api/agent/architecture` |

## Sample request

```bash
curl -X POST http://127.0.0.1:8000/api/rtbf/requests \
  -H 'Content-Type: application/json' \
  -d '{
    "subject_type":"EMAIL",
    "subject_value":"alice@example.com",
    "action":"DELETE",
    "jurisdiction":"GDPR",
    "reason":"Customer request"
  }'
```

## Anonymization example

Use `bob@example.com` and `ANONYMIZE` in the UI, or:

```bash
curl -X POST http://127.0.0.1:8000/api/rtbf/requests \
  -H 'Content-Type: application/json' \
  -d '{
    "subject_type":"EMAIL",
    "subject_value":"bob@example.com",
    "action":"ANONYMIZE",
    "jurisdiction":"GDPR",
    "reason":"Customer request"
  }'
```

## Run tests

```bash
pytest -q
```

## Architecture

See `architecture.md` for the enterprise target architecture and demo-to-production mapping.

## Important demo note

The three sample systems are intentionally lightweight and in-memory so the project can be run from VS Code with one command. The architecture preserves separate adapter boundaries so the Web adapter can be replaced with a real API integration, the Green Screen adapter with 3270/5250/RPA automation, and the COTS adapter with the actual vendor privacy API.
