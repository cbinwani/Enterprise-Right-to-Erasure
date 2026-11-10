# Enterprise RTBF Architecture v3

## 1. Demo target

The demonstration is designed to show a complete enterprise Right to Erasure flow, not just a DELETE API:

`Web Request -> Policy -> Exclusion -> Agentic Orchestration -> 3 Heterogeneous Systems -> Verification -> Audit -> Validation`

## 2. Logical architecture

```text
+--------------------------- EXPERIENCE ----------------------------+
| RTBF Request UI | Exclusion List UI | Audit UI | Validation UI   |
+-------------------------------+---------------------------------+
                                |
                                v
+------------------------- PRIVACY CONTROL PLANE --------------------+
| RTBF API | Identity | Policy Engine | Durable Orchestrator       |
|          |          |               | Agent Tool Registry         |
+-------------------------------+---------------------------------+
                                |
              +-----------------+----------------+
              |                                  |
              v                                  v
+--------------------------+        +-------------------------------+
| EXCLUSION SERVICE       |        | EXECUTION / ADAPTER LAYER     |
| JSON feed / API         |        | Web | Green Screen | COTS     |
| hash + masked subject   |        +-------------------------------+
+-------------+------------+                        |
              |                                     v
              v                           +--------------------------+
+--------------------------+               | Verification Engine     |
| Downstream Guardrails   |               | Search/inspect/confirm   |
| ETL / CRM / AI / MDM    |               +------------+-------------+
| BLOCK or ALLOW          |                            |
+--------------------------+                            v
                                           +--------------------------+
                                           | Audit / Evidence Store  |
                                           +--------------------------+
```

## 3. Exclusion List

The demo stores the authoritative list in:

`data/exclusion-list.json`

Example:

```json
{
  "version": "1.0",
  "records": [
    {
      "exclusion_id": "EXC-20261106-ABC123",
      "request_id": "RTBF-20261106-ABC123",
      "subject_type": "EMAIL",
      "subject_masked": "a***@example.com",
      "subject_hash": "sha256...",
      "status": "ACTIVE",
      "reason": "RTBF request received",
      "created_at": "..."
    }
  ]
}
```

Raw email is deliberately not persisted in this file. The hash supports matching and the masked value supports UI display.

Production should move the authoritative store to a protected database or privacy service while retaining a JSON/event feed for downstream consumers where appropriate.

## 4. Downstream suppression

Every workflow that can create, copy, ingest, vectorize, enrich or otherwise process customer data should call:

`POST /api/ingestion/decision`

before processing.

```text
Customer -> Ingestion Workflow -> Privacy Guard -> BLOCK / ALLOW
                                      |
                                      v
                               Exclusion Service
```

For high-volume systems, publish `PRIVACY_SUBJECT_SUPPRESSED` events to Kafka/Event Hub and maintain a local suppression cache.

## 5. Agentic AI

The demo uses a deterministic tool-calling agent so it runs without an external LLM key.

The pattern is:

`Observe -> Plan -> Act -> Verify`

Tools are constrained to explicit adapter functions:

- WEB.discover
- WEB.delete
- WEB.anonymize
- GREEN_SCREEN.discover
- GREEN_SCREEN.delete
- GREEN_SCREEN.anonymize
- COTS.discover
- COTS.delete
- COTS.anonymize

Production architecture:

```text
LLM / Agent
     |
     v
Tool Registry
     |
     v
Policy / Authorization
     |
     v
Adapter
     |
     v
System
     |
     v
Independent Verification
```

The LLM should never receive unrestricted database credentials or arbitrary SQL execution privileges.

## 6. Heterogeneous system adapters

### Modern Web

REST API adapter discovers the customer and calls DELETE or anonymization endpoint.

### Green Screen

No REST API is assumed. The adapter connects to the terminal service and performs:

`Login -> Search -> Validate -> Delete/Anonymize -> Verify`

The demo uses TCP port 2323. A production implementation can replace it with IBM 3270/5250, terminal emulator, RPA or a supported legacy integration mechanism.

### COTS

The adapter calls a vendor-style privacy endpoint. In production, use the COTS vendor's supported privacy functionality rather than direct database writes.

## 7. Delete vs anonymize

The request contains:

`action = DELETE | ANONYMIZE`

Production policy should be object-aware. For example:

| Data | Action |
|---|---|
| Customer profile | DELETE |
| Marketing profile | DELETE |
| Support ticket | ANONYMIZE |
| Financial transaction | RETAIN/minimize if legally required |
| Audit evidence | RETAIN/minimize |
| Vector embedding | DELETE |
| Agent memory | DELETE |
| Backup | Expire according to backup lifecycle |

## 8. Validation

Validation is independent of the execution response.

The demo verifies each system after execution and shows:

- system
- execution status
- record reference
- verification status
- agent trace

Overall completion requires all in-scope systems to be either ABSENT or ANONYMIZED according to the requested action and policy.

## 9. Audit

The demo stores audit events in `data/audit-log.json`.

Production should use immutable/WORM-capable storage and SIEM integration.

Audit records should prove what happened without unnecessarily creating another PII repository.

## 10. Production evolution

| Demo | Production replacement |
|---|---|
| JSON files | Protected privacy DB / service |
| In-memory sample systems | Real enterprise systems |
| FastAPI | Enterprise API gateway/service mesh |
| Threaded execution | Temporal/Camunda or durable workflow |
| Deterministic agent | Governed LLM agent |
| TCP green screen | 3270/5250/RPA/legacy integration |
| Local audit JSON | Immutable audit/WORM + SIEM |
| Polling UI | Event-driven status + WebSocket/SSE |
| Simple hash match | Enterprise identity resolution / MDM |
| Local suppression | Kafka/Event Hub + distributed suppression cache |

## 11. Key enterprise principle

**Centralized governance, decentralized execution.**

The privacy platform owns request management, identity, policy, exclusion, orchestration, audit and validation. Each system adapter owns the system-specific mechanism for finding and deleting/anonymizing data.
