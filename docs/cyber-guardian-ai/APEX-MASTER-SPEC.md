# Cyber Guardian AI — APEX MASTER SPECIFICATION
## IEEE 830 SRS + SDD (Yagona sprint-planning hujjati)

**Versiya:** 5.0.0-apex-master  
**Sana:** 2026-07-10  
**Holat:** Professional jamoa sprint-planning uchun tayyor  
**Til:** O‘zbek (texnik atamalar EN)  
**Branch siyosati:** Bitta ishchi branch  

**Qat’iy cheklov:** Faqat mudofaa, threat hunting, intelligence va avtomatlashtirilgan **himoya**. Hujum, ekspluatatsiya, exploit, payload, weaponization, hack-back — **taqiqlangan**.

**Satellite chuqur hujjatlar:** `srs/*`, `sdd/*`, `compliance/*`, `operations/*` — ushbu master ularni birlashtiradi va sprint uchun yetarli o‘zini o‘zi yetarli qiladi.

---

# 0. Foydalanish va muvaffaqiyat mezoni

| Mezon | Holat |
|-------|-------|
| Har bo‘lim alohida, chuqur, amaliy | ✅ |
| FR-XXX / NFR-XXX | ✅ |
| Ishlaydigan Mermaid | ✅ |
| Taxminlar/AQ alohida | ✅ §15 + `assumptions-and-open-questions.md` |
| Savolsiz sprint-planning | ✅ §15 baholash |

**Disruption / zararsizlantirish** = blok, karantin, DNS deny, foydalanuvchi ogohlantirishi, organlarga intelligence paketi. Mustaqil infra buzish/DDoS/hack-back — yo‘q.

---

# 1. Rol va ekspert jamoa

| Rol | Mas’uliyat | Asosiy artefakt |
|-----|------------|-----------------|
| Principal Security Architect & Hunt Lead | Arxitektura, threat model, hunting framework | §5, §6, `sdd/08` |
| Senior Malware Researcher & RE | Deep analysis, similarity, binary fingerprint | §8 File/YARA |
| AI/ML & Data Science Engineer | Graph ML, LLM TTP, predictive | §8, `sdd/04c` |
| APT & Nation-State Threat Hunter | Persistent tracking, infra hunting | §4 #27/#41, §11 |
| Mobile & Desktop EDR/XDR Specialist | Telemetry, memory forensics | §3 Android/Windows |
| Threat Intelligence Fusion & Attribution | OSINT + telemetry fusion | §5 Fusion, §8 Attribution |
| Cyber Forensics & IR Lead | Automated forensics, RCA | Evidence Vault §5/§7 |
| Senior Secure Full-Stack Engineer | Zero-trust backend, API | §7 |
| Privacy, Ethics & Legal Officer | Ethical hunting, O‘zR qonun | §10 |
| QA/DevOps & Red Team Simulation Lead | Test, CI/CD, adversarial (defensive) | §13 |

### Threat Hunting & Actor Disruption Strategy
Jamoa faqat detection/attribution/protective response loyihalaydi; red team simulation — detektorlarni sinash, exploit tarqatish emas.

---

# 2. Missiya va muammo konteksti

## 2.1 Muammo
O‘zbekistonda zararli APK, Telegram/QR fishing, voice scam va boshqa SE hujumlari o‘smoqda; oddiy foydalanuvchi texnik himoyasiz.

## 2.2 Missiya
**Cyber Guardian AI** — oddiy foydalanuvchilarni kundalik himoya qilish bilan birga, kiberhujum tayyorlayotgan yoki amalga oshirayotgan threat actorlarni erta aniqlaydigan, kuzatadigan, atributlashtiradigan va **zararsizlantirishga yordam beradigan** (himoya + rasmiy intel) apex mudofaa va threat hunting ekotizimi.

## 2.3 Tamoyil
Faqat defensive hunting, intelligence, avtomatlashtirilgan mudofaa. Hujum/ekspluatatsiya/zararli kod yo‘q.

## 2.4 Asosiy FR/NFR (missiya darajasi)

| ID | Talab |
|----|-------|
| FR-M01 | 3 platformada proaktiv ogohlantirish |
| FR-M02 | Actor/campaign attribution (confidence + explainability) |
| FR-M03 | Defensive playbook response |
| FR-M04 | Authority intelligence package |
| NFR-M01 | TLS 1.3, AES-256 PII, consent-gated hunting |
| NFR-M02 | Offensive capability CI blocklist |

### Threat Hunting & Actor Disruption Strategy
Erta aniqlash → korrelyatsiya → himoya to‘xtatish (delivery/install/C2 indikatorlari) → CERT.

---

# 3. Mahsulot portfeli

| Mahsulot | Asosiy maqsad | Foydalanuvchi | Texnik |
|----------|---------------|---------------|--------|
| **Android ilova** | Real-time scam + actor detection | Oddiy foydalanuvchi | Minimal ruxsat; local-first; SMS on-device |
| **Windows Desktop (XDR)** | Chuqur hunting va forensics | Uy + biznes | Yuqori imtiyoz; process/memory/IOA |
| **Web + SOC Platforma** | Global intel, dashboard, actor tracking | Har qanday qurilma + tashkilotlar | Brauzer cheklovi; TAKB/Graph UI; mehmon skan |

**FR-P01** Web OS monitoring qilmaydi — tekshiruv + intel + extension boshqaruvi.  
**FR-P02** Windows XDR signal beradi; Android sandbox ichida.  
**FR-P03** SOC rollari: analyst, forensics, admin, national (V4+).

### Threat Hunting & Actor Disruption Strategy
Android — scam/APK signal; Windows — EDR/XDR hunting; Web — attribution dashboard va playbook boshqaruvi.

---

# 4. Funksiyalar × Platforma matritsasi

**Belgilar:** ✅ to‘liq · ⚠️ cheklangan · ❌ yo‘q · N/A

| # | Funksiya | A | W | Web | Cheklov |
|---|----------|:-:|:-:|:---:|---------|
| 1 | Threat Intelligence | ✅ | ✅ | ✅ | Cloud feed + delta |
| 2 | Unified Risk & Intent Scoring | ✅ | ✅ | ✅ | Cloud yakuniy |
| 3 | Behavior / Anomaly | ✅ | ✅ | ⚠️ | Web sessiya |
| 4 | URL/Domain/IP Reputation | ✅ | ✅ | ✅ | Cache+cloud |
| 5 | SMS Scam | ✅ | ❌ | ❌ | On-device only |
| 6 | Telegram Scam (shared) | ✅ | ✅ | ✅ | No private chat |
| 7 | QR Analysis | ✅ | ✅ | ✅ | Camera/upload |
| 8 | Deepfake (consent) | ✅ | ✅ | ✅ | No covert record |
| 9 | Wi-Fi Analyzer | ✅ | ✅ | ❌ | No browser NIC |
| 10 | Browser Protection | ⚠️ | ✅ | ✅ | No overlay A |
| 11 | Password Health | ✅ | ✅ | ✅ | k-anonymity |
| 12 | Email Breach | ✅ | ✅ | ✅ | ToS |
| 13 | USB Protection | ❌ | ✅ | ❌ | W only |
| 14 | Ransomware Monitor | ⚠️ | ✅ | ❌ | W honeypot |
| 15 | File Reputation | ✅ | ✅ | ✅ | Web upload lim |
| 16 | Process Monitoring | ❌ | ✅ | ❌ | W XDR |
| 17 | Registry Monitoring | N/A | ✅ | N/A | W |
| 18 | Extension Analyzer | N/A | ✅ | ✅ | Desktop |
| 19 | Network Monitoring | ✅ | ✅ | ⚠️ | A VPN/DNS |
| 20 | DNS Security | ✅ | ✅ | ✅ | Ext/VPN |
| 21 | YARA | ✅ | ✅ | ❌* | *BE upload |
| 22 | Sigma | ❌ | ✅ | N/A | W+BE |
| 23 | MITRE Mapping | ✅ | ✅ | ✅ | Tasnif |
| 24 | Actor Fingerprinting | ✅ | ✅ | ✅ | Signal→cloud |
| 25 | Campaign Correlation | ✅ | ✅ | ✅ | Graph |
| 26 | TTP Mapping & Attribution | ⚠️ | ✅ | ✅ | UZ TTP |
| 27 | Suspicious Infra Detection | ✅ | ✅ | ✅ | Detect only |
| 28 | Memory & Ancestry | ❌ | ✅ | ❌ | W |
| 29 | IOC Sweeping | ✅ | ✅ | ✅ | Signed delta |
| 30 | Persona/Group OSINT | ❌ | ✅ | ✅ | Legal OSINT |
| 31 | Hunting Pipeline | ⚠️ | ⚠️ | ✅ | BE |
| 32 | Knowledge Graph/TAKB | ❌ | ❌ | ✅ | Analyst |
| 33 | Intelligence Fusion | ❌ | ❌ | ✅ | BE |
| 34 | Defensive Playbooks | ⚠️ | ✅ | ✅ | No offense |
| 35 | LOTL/Injection Detect | ⚠️ | ✅ | ⚠️ | Detect only |
| 36 | Predictive Behavior Modeling | ⚠️ | ⚠️ | ✅ | Forecast |
| 37 | Take-down **Intelligence** | ⚠️ | ⚠️ | ✅ | For authorities |
| 38 | Deep Memory Forensics | ❌ | ✅ | ⚠️ | Vault |
| 39 | Graph Relationship Analysis | ⚠️ | ⚠️ | ✅ | actor-tool-campaign |
| 40 | Multi-lang SE (uz/ru/en+slang) | ✅ | ✅ | ✅ | Bias monitor |
| 41 | Live Panel/Kit Hunting | ✅ | ✅ | ✅ | Detect≠build |
| 42 | Zero-Day Behavior Anomaly | ⚠️ | ✅ | ⚠️ | Soft warn |

**FR-MX01** Har skan natijasida ixtiyoriy: `intent_tags`, `campaign_id`, `actor_hint`, `kill_chain_stage`, `recommended_actions[]` (defensive).

### Threat Hunting & Actor Disruption Strategy
#24–42 hunting qatlami; #1–23 kundalik himoya. Disruption playbooklari #34 orqali.

---

# 5. Tizim arxitekturasi

## 5.1 Yuqori darajadagi arxitektura

```mermaid
flowchart TB
  subgraph Clients
    A[Android App]
    W[Windows XDR Agent]
    WEB[Web + SOC UI]
    EXT[Browser Extension]
  end
  GW[API Gateway REST/GraphQL\nJWT + mTLS + rate limit]
  subgraph Plane
    TEL[Telemetry Ingest]
    HUNT[Real-time Hunting Engine]
    FUS[Intelligence Fusion]
    KG[(Knowledge Graph)]
    VDB[(Vector DB)]
    ATTR[Attribution GNN/LLM assist]
    SCORE[Risk & Intent]
    PB[Playbook Orchestrator]
    EV[(Evidence Vault)]
    NOTIF[Notification]
  end
  FEED[TI / UZCERT / OSINT]
  CERT[Authority packages]

  A --> GW
  W --> GW
  WEB --> GW
  EXT --> GW
  GW --> TEL --> HUNT --> FUS
  FUS --> KG
  FUS --> VDB
  FEED --> FUS
  KG --> ATTR
  VDB --> ATTR
  HUNT --> SCORE
  ATTR --> SCORE
  SCORE --> PB
  PB --> NOTIF
  PB --> EV
  ATTR --> CERT
  EV --> CERT
```

**Izoh:** Web monitoring Emas; Windows eng boy telemetry; Fusion litsenziya/consent gate.

## 5.2 On-device / Edge / Cloud

| Qobiliyat | On-device | Edge | Cloud |
|-----------|:--------:|:----:|:-----:|
| IOC sweep / engil anomaly | ✅ | ⚠️ | sync |
| SMS scam | ✅ | — | ❌ raw |
| URL cache | ✅ | ⚠️ | ✅ |
| Process/memory indicators | ✅ W | — | meta |
| Stream correlation | — | ⚠️ | ✅ |
| Graph + Vector + GNN | — | — | ✅ |
| LLM TTP assist | — | — | ✅ |
| Predictive forecast | — | — | ✅ |
| Playbook local actions | ✅ | — | orch. |
| Evidence Vault | — | — | ✅ |

## 5.3 Ma’lumot oqimi

```mermaid
sequenceDiagram
  participant D as Device
  participant H as Hunting Engine
  participant F as Fusion
  participant G as Graph/Vector
  participant S as Scoring
  participant P as Playbook
  participant U as User/SOC
  D->>H: telemetry/scan meta
  H->>F: enrich
  F->>G: upsert observables
  G->>S: actor/campaign features
  S->>P: score+intent+stage
  P->>U: notify / block / case
  P->>G: authority package queue
```

## 5.4 Trust boundaries

| Zona | Chiqadi | Chiqmaydi |
|------|---------|-----------|
| Device | hash, URL, anon meta | SMS raw, password, covert audio |
| Transport | TLS 1.3 | cleartext |
| Cloud | encrypted PII fields | sold data |
| SOC | redacted IOC | unnecessary PII |
| Authority | signed intel pack | exploit tooling |

### Threat Hunting & Actor Disruption Strategy
Oqim oxiri — defensive playbook + CERT intel; offensive sink yo‘q.

---

# 6. Diagrammalar

## 6.1 Use Case (qisqa)

```mermaid
flowchart LR
  User[Oddiy foydalanuvchi] --> S[Skan/Himoya]
  User --> Al[Alertlarga javob]
  SOC[SOC Analyst] --> H[Hunt cases]
  SOC --> AP[Actor profile]
  FOR[Forensics] --> EV[Evidence Vault]
  ADM[Admin] --> PB[Playbooks]
  NAT[National role V4] --> EW[Early warning]
```

## 6.2 Graph-based Actor Relationship

```mermaid
flowchart TB
  ACT[ActorCluster]
  CAMP[Campaign]
  TOOL[Tool/Family]
  VIC[VictimPattern]
  INF[Infrastructure]
  IOC[Observable IOC]
  TTP[TTP/MITRE]

  ACT -->|RUNS| CAMP
  CAMP -->|USES| TOOL
  CAMP -->|TARGETS| VIC
  CAMP -->|HOSTED_ON| INF
  CAMP -->|USES| IOC
  CAMP -->|EXHIBITS| TTP
  ACT -->|SIMILAR| ACT
  TOOL -->|SIMILAR_CODE| TOOL
```

**Izoh:** `VictimPattern` — agregat (kanal/til/region), shaxs emas.

## 6.3 Sequence — URL → attribution → response

```mermaid
sequenceDiagram
  actor U as User
  participant App
  participant API
  participant Hunt
  participant Graph
  participant PB as Playbook
  U->>App: suspicious URL
  App->>API: POST /v1/scan/url
  API->>Hunt: enrich+correlate
  Hunt->>Graph: lookup/link
  Graph-->>Hunt: campaign/actor
  Hunt-->>App: score+actions
  Hunt->>PB: trigger if policy
  PB-->>U: block/warn notification
```

## 6.4 Component

```mermaid
flowchart LR
  UI --> Agent
  Agent --> Gateway
  Gateway --> Hunt
  Gateway --> GraphQL
  Hunt --> Fusion
  Fusion --> KG
  Fusion --> Vec
  Hunt --> Score
  Score --> Playbook
  Playbook --> Vault
  Playbook --> Push
```

## 6.5 Deployment

```mermaid
flowchart TB
  Phone[Android] --> LB
  PC[Windows] --> LB
  Browser --> LB
  LB --> GW
  GW --> Svc[Microservices]
  Svc --> PG[(PostgreSQL)]
  Svc --> Neo[(Neo4j)]
  Svc --> Vec[(Vector DB)]
  Svc --> Obj[(Object/Vault storage)]
  Svc --> Bus[(Event bus)]
```

## 6.6 ER (operatsion + graph projection)

Asosiy OLTP: User, Device, Consent, ScanResult, ThreatEvent, Notification, AuditLog, HuntCase, EvidenceObject, PlaybookRun — batafsil SQL: `sdd/03-api-and-database.md`.  
Graph tugunlari: ActorCluster, Campaign, Observable, Infrastructure, TTP, ToolFamily.

### Threat Hunting & Actor Disruption Strategy
Diagrammalar faqat himoya oqimini ko‘rsatadi; attacker TTP “how-to” yo‘q.

---

# 7. API va ma’lumotlar bazasi

## 7.1 Umumiy

| Band | Qiymat |
|------|--------|
| REST | `/v1/...` |
| GraphQL | `/v1/graphql` (SOC o‘qish/query) |
| Auth | OAuth2 + JWT; service mTLS |
| Rate limit | mehmon/auth tarif |
| Errors | Problem Details |

## 7.2 Asosiy REST

| Endpoint | Maqsad |
|----------|--------|
| `POST /v1/scan/url\|file\|qr\|message` | Skan |
| `POST /v1/risk-score` | Score |
| `GET /v1/threat-feed/sync` | IOC delta |
| `POST /v1/ioc/sweep` | Sweep |
| `GET /v1/campaigns/{id}` | Campaign |
| `GET /v1/actors/{id}` | Actor (RBAC) |
| `POST /v1/playbooks/{id}/run` | Defensive run |
| `POST /v1/evidence` | Vault |
| `POST /v1/authority/takedown-intel` | Intel pack |
| `POST /v1/breach-check` | Breach |
| `GET/POST /v1/consents` | Consent |
| `DELETE /v1/me` | Erasure |

**Scan URL response (namuna):**
```json
{
  "scan_id": "...",
  "score": 88,
  "confidence": 0.81,
  "verdict": "malicious",
  "scam_family": ["SCAM_PAYMENT"],
  "intent_tags": ["phishing"],
  "kill_chain_stage": "delivery",
  "campaign_id": "...",
  "actor_hint": {"alias": "UZ-SCAM-017", "confidence": 0.62},
  "reasons": [{"code": "TI_DOMAIN_HIT", "message_key": "reason.ti_domain_hit"}],
  "recommended_actions": ["block_and_warn", "open_hunt_case"],
  "mitre_tags": ["T1566"]
}
```

## 7.3 GraphQL (SOC)

```graphql
type ActorCluster {
  id: ID!
  alias: String!
  confidence: Float!
  campaigns: [Campaign!]!
}
type Campaign {
  id: ID!
  scamFamily: [String!]!
  observables: [Observable!]!
  ttps: [String!]!
}
type Query {
  actor(id: ID!): ActorCluster
  searchActors(query: String!, limit: Int = 20): [ActorCluster!]!
  campaign(id: ID!): Campaign
}
```

**NFR-API01** GraphQL faqat RBAC; mutation playbook — audit.

## 7.4 Knowledge Graph model

| Node | Asosiy maydonlar |
|------|------------------|
| ActorCluster | alias, confidence, region_focus |
| Campaign | scam_family, first/last_seen |
| Observable | type, value_hash |
| Infrastructure | asn, cert_fp, domain_hash |
| ToolFamily | name, similarity_index_ref |
| TTP | mitre_id / uz_ttp_id |
| VictimPattern | channel, lang, sector (aggregate) |

## 7.5 Shifrlash / retention

| Ma’lumot | At-rest | Retention |
|----------|---------|-----------|
| email/phone | AES-256-GCM | erasure 30k |
| Evidence blob | AES-256 + KMS | case TTL |
| Audit | append-only | 365k+ |
| Scan results | 180k | NFR-040 |
| Deepfake media | qisqa TTL | AQ-013 |

### Threat Hunting & Actor Disruption Strategy
API da `recommended_actions` faqat defensive enum; offensive qiymatlar validatsiyada rad.

---

# 8. AI / Detection modullari

**To‘liq shablon har modulda.** Batafsil: `sdd/04c-apex-ai-modules.md`. Quyida sprint uchun majburiy qisqa+to‘liq shablon.

### Threat Hunting & Actor Disruption Strategy
Har modul `kill_chain_stage` va defensive `recommended_actions` qaytaradi.

---

### Unified Risk & Intent Scoring Engine
- **Kirish:** Barcha detektor chiqishlari, graph/forecast hint.
- **Feature extraction & Enrichment:** Weighted aggregates, intent multi-label, stage, source trust.
- **Model:** Ensemble GBDT + rules + calibrator.
- **Chiqish:** risk + explainability + confidence + linked actors + recommended actions.
- **FP / evasion resilience:** Allowlist, unknown band, drift monitor.
- **Manbalar:** Telemetry + TI + labels.
- **On-device / Edge / Cloud:** Engil device; to‘liq cloud.
- **Yangilanish / retraining:** Haftalik.
- **Kill-chain:** Yakuniy qaror (barcha stage).

### Advanced Behavioral Anomaly & Predictive Detection
- **Kirish:** Process/app/session sequences, baseline.
- **Feature extraction & Enrichment:** Embeddings, rare transitions, peer deviation.
- **Model:** Sequence/Transformer (cloud) + on-device thresholds; predictive head ixtiyoriy.
- **Chiqish:** anomaly/forecast scores + explain + confidence + actors + actions.
- **FP / evasion resilience:** Dual-signal critical; soft warn on zero-day-like.
- **Manbalar:** Consent telemetry, lab.
- **On-device / Edge / Cloud:** Yengil device; og‘ir cloud.
- **Yangilanish:** IOA haftalik; model oylik.
- **Kill-chain:** Installation / C2 ind. / Actions / Pre-delivery (predict).

### Multi-Vector Reputation & Live Infrastructure Hunting
- **Kirish:** URL/file/IP/domain/ASN/cert.
- **Feature extraction & Enrichment:** TI, cert reuse, ASN, CT, passive DNS (licensed).
- **Model:** Ensemble + graph neighborhood.
- **Chiqish:** multi-vector scores + infra tags + confidence + actors + actions.
- **FP / evasion resilience:** Shared hosting down-weight; new domain caution.
- **Manbalar:** OSINT + private + telemetry.
- **On-device / Edge / Cloud:** Cache device; live cloud.
- **Yangilanish:** IOC soatlik/kunlik.
- **Kill-chain:** Delivery / C2.

### SMS / Telegram / Voice Scam + Actor Linking
- **Kirish:** On-device SMS features; shared messenger; VoIP meta (consent); optional uploaded audio.
- **Feature extraction & Enrichment:** uz/ru/en slang, money scripts, bot ids.
- **Model:** TFLite text + cloud linking + optional deepfake.
- **Chiqish:** scam_score + family + confidence + actors + actions.
- **FP / evasion resilience:** Official shortcodes; multilingual thresholds.
- **Manbalar:** Meta, OSINT, reports.
- **On-device / Edge / Cloud:** SMS on-device; link cloud.
- **Yangilanish:** Lexicon haftalik.
- **Kill-chain:** Delivery / Actions.

### QR & Visual Phishing Analysis
- **Kirish:** QR / screenshot (consent).
- **Feature extraction & Enrichment:** Payload URL + visual brand embeddings.
- **Model:** Decode + vision + URL engine.
- **Chiqish:** score + explain + confidence + actors + actions.
- **FP / evasion resilience:** Merchant allowlist; blur→inconclusive.
- **Manbalar:** Local QR DB, TI.
- **On-device / Edge / Cloud:** Decode device; vision cloud.
- **Yangilanish:** Haftalik.
- **Kill-chain:** Delivery.

### Deepfake Detection
- **Kirish:** Consent upload audio/image/video only.
- **Feature extraction & Enrichment:** Artefacts + SE transcript.
- **Model:** Cloud classifiers.
- **Chiqish:** synthetic_score + confidence + campaign link + actions.
- **FP / evasion resilience:** Low quality inconclusive.
- **Manbalar:** Licensed corpora.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Oylik.
- **Kill-chain:** Delivery / SE Actions.

### Memory Forensics & Process Tree Analysis
- **Kirish:** W process tree; memory indicators (full dump default off).
- **Feature extraction & Enrichment:** Ancestry, unsigned modules, injection indicators.
- **Model:** IOA/Sigma + forensics scoring.
- **Chiqish:** forensics_score + tree explain + confidence + actors + actions.
- **FP / evasion resilience:** Dev allowlist; corroboration.
- **Manbalar:** EDR telemetry, lab.
- **On-device / Edge / Cloud:** Capture device; vault cloud.
- **Yangilanish:** IOA haftalik.
- **Kill-chain:** Installation / Actions.

### Rootkit / Injection / LOTL Detection
- **Kirish:** Agent telemetry; LOLBin patterns.
- **Feature extraction & Enrichment:** Hidden module ind., LOLBin+network combo.
- **Model:** Behavioral rules + anomaly (**detection only**).
- **Chiqish:** ioa_score + MITRE + confidence + actors + actions.
- **FP / evasion resilience:** Baseline admins; multi-signal.
- **Manbalar:** Sigma, internal IOA.
- **On-device / Edge / Cloud:** Detect device; correlate cloud.
- **Yangilanish:** Haftalik.
- **Kill-chain:** Installation / C2 / Actions.

### YARA + Sigma + Behavioral Rule Engine
- **Kirish:** Files / events.
- **Feature extraction & Enrichment:** Match meta, uz_ttp.
- **Model:** Rule engines + canary.
- **Chiqish:** matches + floor score + confidence + actors/tags + actions.
- **FP / evasion resilience:** Staging; family+fuzzy.
- **Manbalar:** Internal + licensed.
- **On-device / Edge / Cloud:** Local A/W; BE web upload.
- **Yangilanish:** Signed packs.
- **Kill-chain:** Delivery–Installation.

### Threat Actor Attribution & Fingerprinting Engine
- **Kirish:** Graph+vector, infra, code similarity, OSINT.
- **Feature extraction & Enrichment:** Shared IOC, embedding distance, TTP Jaccard.
- **Model:** GNN + clustering + LLM assist.
- **Chiqish:** actor_cluster + score + explain + confidence + linked actors + CERT actions.
- **FP / evasion resilience:** High threshold; CDN filter.
- **Manbalar:** Graph, fusion, OSINT, private TI.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Continuous.
- **Kill-chain:** Cross-stage.

### Campaign Detection & Tracking
- **Kirish:** Multi-event observables.
- **Feature extraction & Enrichment:** Exact/fuzzy links, time decay.
- **Model:** Graph components + link prediction.
- **Chiqish:** campaign_id + confidence + actors + actions.
- **FP / evasion resilience:** Min evidence; human merge.
- **Manbalar:** Pipeline, vault refs.
- **On-device / Edge / Cloud:** Cloud; client hint.
- **Yangilanish:** Streaming.
- **Kill-chain:** Campaign-level.

### Infrastructure & C2 Hunting
- **Kirish:** Domains/IPs/certs/safe fingerprints.
- **Feature extraction & Enrichment:** Panel FP, ASN, CT, redirects.
- **Model:** Signatures + ML + graph (detect≠build kits).
- **Chiqish:** infra_score + family + confidence + actors + deny/intel actions.
- **FP / evasion resilience:** Benign allowlist.
- **Manbalar:** TI, UZCERT, licensed.
- **On-device / Edge / Cloud:** Hint local; confirm cloud.
- **Yangilanish:** Weekly.
- **Kill-chain:** Delivery / C2.

### Graph-based Relationship Analysis
- **Kirish:** KG + embeddings.
- **Feature extraction & Enrichment:** Paths, communities, NN similarity.
- **Model:** Graph algos + vector + GNN.
- **Chiqish:** paths + similarity + confidence + actors + actions.
- **FP / evasion resilience:** Path limits; thresholds.
- **Manbalar:** Neo4j + vector DB.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Continuous index.
- **Kill-chain:** Investigation.

### Automated TTP & MITRE Mapping
- **Kirish:** IOA/rules/scam_family/uz_ttp.
- **Feature extraction & Enrichment:** Map tables; LLM narrative (analyst).
- **Model:** Deterministic + LLM assist.
- **Chiqish:** tags + confidence + context + playbook stage actions.
- **FP / evasion resilience:** No weak speculative tags.
- **Manbalar:** MITRE + UZ TTP.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Framework updates.
- **Kill-chain:** Stage labeling.

### Predictive Attack Forecasting
- **Kirish:** Campaign/actor histories, channel shifts.
- **Feature extraction & Enrichment:** Time-series + graph growth.
- **Model:** Ensemble + uncertainty.
- **Chiqish:** forecast windows + probability + explain + confidence + actors + prep actions.
- **FP / evasion resilience:** Calibration; never certainty UX.
- **Manbalar:** Historical PII-free.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Weekly.
- **Kill-chain:** Pre-Delivery proactive defense.

---

# 9. UX/UI va Frontend dizayn

## 9.1 Dizayn tizimi
- **Brend:** deep teal `#0B3D3A` / `#1F8A80`
- **Risk:** safe `#2F7D4A`, warn `#A67C2D`, crit `#A33B3B` (tinch)
- **Fon:** soft cool gradient (flat emas); dark `#0E1719`
- **Font:** Manrope/Sora + Source Sans 3 (Inter emas)
- **Kartochka:** default yo‘q; faqat interaktiv zaruratda
- **a11y:** WCAG 2.1 AA

## 9.2 Wireframe ekranlar

### Onboarding
Brend hero → foyda → ruxsatlar ketma-ket (asos + nima qilinMAYDI) → til.

### Dashboard
Holat qatori + bitta CTA «Tekshirish» + oxirgi 1–3 alert (stats clutter yo‘q).

### Skan natijasi
Score + reasons + campaign/actor hint (yumshoq) + defensive CTAs.

### Alert Center
Filtr: info/warn/critical; o‘qish; deep link natija/hunt.

### Hunting View (SOC)
Timeline + IOC jadvali + graph mini-map + case status; **Attack** tugmasi yo‘q.

### Actor Profile (SOC)
Alias, confidence, campaigns, TTP tags, infra (redacted), «Prepare authority pack».

### Playbook Center
Faqat defensive action ro‘yxati; run + audit.

### Settings / Privacy
Consent, modules, erasure, language, large text.

## 9.3 Ogohlantirish UX
Qat’iy, aniq, CTA; dark pattern/timer/qo‘rqitish yo‘q. Overlay taqiqlangan.

### Threat Hunting & Actor Disruption Strategy
Foydalanuvchi: himoya CTA. SOC: intel + playbook. Hech kimga «hujum qil» UI yo‘q.

---

# 10. Xavfsizlik, maxfiylik, muvofiqlik

## 10.1 Android ruxsatlar
- Minimal ruxsat + ko‘rinadigan asos.
- SMS **on-device**; raw cloudga yo‘q.
- Yashirin overlay yo‘q; tizim notification.
- Accessibility default MVP off (AQ-014).
- Play Restricted declaration + demo video.

## 10.2 Maxfiylik
- O‘zR PII qonuni + GDPR-uslub tamoyillar (consent, minimize, erasure, purpose limit).
- Hunting faqat consent + anonim meta.
- TLS 1.3; AES-256 at-rest.
- Sotish yo‘q.

## 10.3 Responsible Disclosure
Topilgan uchinchi tomon zaifligi / actor intel → UZCERT / Milliy Kiberxavfsizlik Markazi / tegishli organlar; muddatli ichki qayd; ommaviy doxing yo‘q.

## 10.4 Ethical Hunting
Explainability majburiy; bias monitoring uz/ru/en; immutable audit; offensive lint.

| ID | Talab |
|----|-------|
| FR-SEC01 | ConsentRecord har modul |
| FR-SEC02 | Authority-only actor detail export |
| NFR-SEC01 | Immutable audit ≥365k |
| NFR-SEC02 | CI blocks offensive playbook actions |

### Threat Hunting & Actor Disruption Strategy
Etik chegara: intel tayyorlash ≠ mustaqil take-down.

---

# 11. Mahalliylashtirish — O‘zbekiston tahdid modeli

| ID | Tahdid | Hunting ustuvor |
|----|--------|------------------|
| UZ-T1 | Soxta bank APK | Similarity/YARA/fingerprint |
| UZ-T2 | Telegram ish/lotoreya/invest | Scam+bot link |
| UZ-T3 | Gov/payment phishing | URL/infra |
| UZ-T4 | Support call SE | SMS+deepfake consent |
| UZ-T5 | QR fraud | QR engine |
| UZ-T6 | Emergency alert phish | URL+SE |
| UZ-T7 | Money-offer bots | Bot detector |
| UZ-T8 | Deepfake SE | Media modules |
| UZ-T9 | Romance scam | Multi-lang SE |
| UZ-T10 | Campaign clusters | Graph attribution |

**Tillar:** uz/ru/en to‘liq; slang; ixtiyoriy RU/CN SE lib (AQ-034).  
**Feed:** UZCERT, Milliy markaz, ochiq/litsenziyalangan TI.

### Threat Hunting & Actor Disruption Strategy
Mahalliy actor cluster → foydalanuvchi ogohlantirishi + organlarga paket.

---

# 12. Operatsion talablar

| Tizim | Talab |
|-------|-------|
| Notification | info/warn/critical; i18n keys; no overlay |
| Offline | A/W full cache; Web last results |
| Auto-update | Delta IOC/rules/models + signature verify |
| Audit | Immutable; playbook/hunt/disclosure |
| Playbooks | Defensive enum only; policy+audit |
| Observability | Metrics/logs/traces PII-free |

**FR-OPS01** Sync imzo fail → discard.  
**FR-OPS02** Playbook run → AuditLog + optional Evidence ref.

### Threat Hunting & Actor Disruption Strategy
Playbook execution = avtomatik himoya; on-call runbook (AQ-009).

---

# 13. Sifat, test, DevOps

## 13.1 Test qatlami
Unit → Integration → SAST/DAST/SCA → FP/FN benchmark → Adversarial/red-team **simulation** (lab, no malware in repo) → Performance → a11y.

## 13.2 Performance (tanlangan)
| Metrika | Maqsad |
|---------|--------|
| URL cloud p95 | < 2s |
| Cache hit | < 200ms |
| Hunt enrich p95 | < 3s |
| Graph lookup p95 | < 2.5s |
| W idle CPU | < 3% |
| SMS model disk | < 15MB |

## 13.3 CI/CD
- Android: Play internal → prod  
- Windows: code-sign gate  
- Web: staging → DAST → prod  
- Backend: migrate + smoke  
- **Gate:** offensive action lint, explainability present, high CVE block

### Threat Hunting & Actor Disruption Strategy
Red team sim — detektor chidamliligi; exploit tarqatish taqiqlangan.

---

# 14. Yo‘l xaritasi

| Versiya | Mazmun |
|---------|--------|
| **V1 MVP** | Core protection + basic hunting + IOC sweep + scam URL/QR/file + dashboard |
| **V2** | Full XDR + behavior + SMS/Telegram + fingerprinting + graph/vault asos |
| **V3** | Predictive + playbooks + infra/panel hunting + deepfake + GNN/LLM assist + B2B |
| **V4 National** | UZCERT/Milliy integratsiya, early-warning, take-down intel at scale |
| **Kelajak** | V5 autonomous **defensive** ecosystem; iOS; enterprise mesh |

### Threat Hunting & Actor Disruption Strategy
V1 dan himoya; V2+ hunting chuqurligi; V4 milliy intel; hech qachon offensive roadmap.

---

# 15. Yakuniy format, taxminlar, qabul

## 15.1 Chiqish tekshiruvi
- Bo‘limlar to‘liq ✅  
- FR/NFR ✅  
- Mermaid ✅  
- Defensive-only ✅  
- Satellite chuqurlik: `srs/09`, `sdd/08`, `sdd/04c`, `srs/08`, `srs/07`, `srs/06`

## 15.2 Taxminlar va ochiq savollar
To‘liq ro‘yxat: [`assumptions-and-open-questions.md`](assumptions-and-open-questions.md) (AQ-001…AQ-038).

Asosiy bloklovchilar: auth ID (AQ-002), cloud residency (AQ-005), Neo4j/vector (AQ-027/037), dark web OSINT (AQ-030), national API (AQ-031), stream bus (AQ-033).

## 15.3 Baholash

### Ushbu spetsifikatsiya asosida professional jamoa darhol sprint planning boshlay oladimi?

**Ha.**

1. V1 epiklari aniq (URL/QR/File, auth/consent, feed sync, dashboard, basic IOC/campaign hint).  
2. Platforma cheklovlari matritsada ochiq.  
3. API/DB/AI shablonlari implementatsiya uchun yetarli.  
4. AQ lar groomingda yopiladi; V4/V5 shartnomaga bog‘liq.  
5. Offensive kontent yo‘q — xavfsizlik review osonlashadi.

**Tavsiya etilgan birinchi sprint board:** Auth → Scan URL → Feed sync → Web mehmon skan → Android/Windows shell → Consent/Privacy → CI gates.

---

*Cyber Guardian AI Apex Master Spec v5.0.0 — defensive hunting only.*
