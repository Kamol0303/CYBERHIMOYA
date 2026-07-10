# SRS 07 — Threat Hunting & Actor Detection (Threat Hunter Edition)

**Hujjat:** Cyber Guardian AI SRS  
**Bo‘lim:** 7 — Proactive Threat Hunting Requirements  
**Versiya:** 2.0.0-threat-hunter  
**Rol:** Principal Security Architect + Proactive Threat Hunter + SOC/TI Lead  
**Printsip:** Faqat mudofaa, aniqlash, monitoring, ogohlantirish, bloklash va **intellektual kuzatish**. Hack-back / exploit / «qanday buzish» — taqiqlangan.

---

## 0. Threat Hunting va Actor Detection (majburiy qism)

Ushbu bo‘lim Cyber Guardian AI ni oddiy antivirus/scam-checker dan **Threat Hunter Edition** ga ko‘taradi:

| Qobiliyat | Ma’nosi (himoya) |
|-----------|------------------|
| **Threat Hunting** | IOC/IOA va xatti-harakat belgilari bo‘yicha erta qidiruv |
| **Actor Profiling** | Infratuzilma + behavior korrelyatsiyasi orqali cluster/taxallus |
| **Campaign Tracking** | Bir nechta hodisani bitta kampaniyaga bog‘lash |
| **Intent Detection** | «Hujumchi niyati» belgilarini TTP (ATT&CK) darajasida **aniqlash** (o‘rgatish emas) |
| **APK Similarity** | Shubhali APK larni o‘xshashlik bo‘yicha oilaga bog‘lash |

**Ma’lumot oqimi (majburiy):**

```text
Foydalanuvchi signali → local scan → cloud correlation
  → possible actor attribution → ogohlantirish / bloklash
  → (analyst) Threat Actor KB + rasmiy disclosure
```

---

## 1. Yangi / kengaytirilgan funksional talablar

### FR-200 — Threat Hunting Pipeline
- **P1** | [BE] (+ signallar A/W)
- Signal ingest → normalize → correlate → hunt hypothesis → alert/case.
- **Qabul:** har bir hunt case auditlanadi; PII anonim; exploit yo‘q.

### FR-201 — Threat Actor Knowledge Base (TAKB)
- **P1** | [BE][Web-analyst]
- Actor cluster, kampaniya, IOC/IOA, TTP teglari, ishonch, first/last seen.
- **Qabul:** oddiy foydalanuvchiga to‘liq KB ochilmaydi (AQ-022); analyst RBAC.

### FR-202 — Threat Actor Profiling (IOC/IOA + behavior)
- **P1** | [BE]
- IOC (hash, domen, bot, cert) + IOA (xatti-harakat qoidalari) + behavior score → profil.
- **Qabul:** confidence < threshold da «taxminiy»; doxing yo‘q.

### FR-203 — Campaign Tracking
- **P0** (asos V1 IOC) / **P1** to‘liq | [BE][Web]
- Bir nechta skan/hodisani `campaign_id` ga bog‘lash.
- **Qabul:** FR-120 bilan mos; explainability (qaysi IOC).

### FR-204 — Behavioral Anomaly & Attacker Intent Detection
- **P1** | [W] kuchli; [A] cheklangan; [Web] sessiya
- Process ancestry, noodatiy tarmoq, TTP-mapped IOA (Sigma/qoida).
- **Qabul:** «intent» = ATT&CK teg + tushuntirish; hujum qo‘llanmasi emas.
- **Windows:** lateral movement **belgilarini aniqlash** (himoya ogohlantirishi) — lateral movement qanday qilinishi o‘rgatilmaydi.

### FR-205 — Suspicious APK / Similarity Search
- **P1** | [A][BE][Web-upload]
- APK meta + cert + package + fuzzy hash / embedding o‘xshashlik → oila/kampaniya.
- **Qabul:** o‘xshash zararli oilaga hit → critical; noma’lum → unknown.

### FR-206 — Process Ancestry Tracking (Windows)
- **P1** | [W]
- Parent→child zanjiri saqlanadi (meta); shubhali ancestry qoidalari.
- **Qabul:** EDR-uslubidagi defensive monitoring; memory exploit yo‘q.

### FR-207 — Global Threat Intel Dashboard (Web)
- **P1** | [Web]
- Kampaniya xaritasi, actor cluster (redacted), mahalliy UZ trendlar, ta’lim.
- **Qabul:** mehmon uchun agregat; batafsil — auth + rol.

### FR-208 — Hunt Case Management
- **P2** | [Web-analyst]
- Hypothesis, evidence IOC, status (open/validated/false), linked campaign.
- **Qabul:** audit; faqat defensive evidence.

### FR-209 — Anonymized hunting telemetry (consent)
- **P1** | [A][W][BE]
- Hunting uchun faqat anonim/pseudonym meta; consent; opt-out.
- **Qabul:** xom SMS/chat/parol ketmaydi; NFR-030 saqlanadi.

### FR-210 — Actor intel → rasmiy organlar
- **P1** | [BE][Web]
- FR-122 kengaytmasi: TAKB dan UZCERT paket (IOC, kampaniya, TTP teglari).
- **Qabul:** responsible disclosure; ommaviy doxing yo‘q.

---

## 2. Funksiya × Platforma (Threat Hunter qo‘shimchalari)

| # | Funksiya | Android | Windows | Web | Cheklov |
|---|----------|:-------:|:-------:|:---:|---------|
| 28 | Threat Actor Profiling | ⚠️ | ⚠️ | ✅ | Signal clientdan; profil BE/analyst |
| 29 | Campaign Tracking | ⚠️ | ⚠️ | ✅ | Clientda natija; bog‘lash BE |
| 30 | Anomaly Detection (Network/Process) | ⚠️ | ✅ | ⚠️ | W eng kuchli; Web sessiya |
| 31 | Suspicious APK Similarity Search | ✅ | ⚠️ | ✅ | W: umumiy fayl; A/Web: APK |
| 32 | Process Ancestry Tracking | ❌ | ✅ | ❌ | Windows-only |
| 33 | Threat Hunting Pipeline | ⚠️ | ⚠️ | ✅ | Orchestration BE |
| 34 | Threat Actor Knowledge Base | ❌ | ❌ | ✅ | Analyst/admin Web |
| 35 | Attacker Intent (TTP/IOA) Detection | ⚠️ | ✅ | ⚠️ | ATT&CK map; exploit yo‘q |

Har bir asosiy himoya funksiyasiga **attacker intent detection** elementi: skan natijasida ixtiyoriy `intent_tags[]` / MITRE + `campaign_id`.

---

## 3. Nofunksional (hunting)

### NFR-100 — Hunting latency
- Cloud correlation p95 < **5 s** (oddiy skan boyitish).
- Batch klasterlash: soatlik job OK.

### NFR-101 — Anonymization
- Hunting datasetda to‘g‘ridan-to‘g‘ri identifikator yo‘q (yoki hash).
- Rozilik yo‘q → hunting telemetry yuborilmaydi.

### NFR-102 — Analyst isolation
- TAKB va hunt case lar RBAC + audit.
- Export imzolangan va TTL li.

### NFR-103 — Red team simulation (defensive)
- QA labda himoya stsenariylari; repoga malware/exploit yo‘q.
- FP/FN hunting gold set (AQ-007 kengaytmasi).

---

## 4. Bog‘liqlik

| Hujjat | Mazmun |
|--------|--------|
| `sdd/06-threat-hunting-architecture.md` | Pipeline + TAKB + oqim |
| `sdd/04-ai-detection-modules.md` | Attribution / Campaign / Intent modullari |
| `srs/06-universal-scam-and-attribution.md` | Scam oilalari + FR-120…123 |
| `compliance/02-uzbekistan-threat-model.md` | Mahalliy actor patternlari |
| `operations/03-roadmap.md` | V1–V3 hunting bosqichlari |
