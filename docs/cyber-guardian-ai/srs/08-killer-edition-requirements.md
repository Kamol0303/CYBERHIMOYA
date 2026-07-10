# SRS 08 — Killer Edition: Elite Threat Hunting Requirements

**Hujjat:** Cyber Guardian AI SRS  
**Bo‘lim:** 8 — Killer / Elite Mudofaa + Hunting  
**Versiya:** 3.0.0-killer  
**Rol:** Principal Security Architect & Red/Blue Team Lead + APT Hunter + Privacy/Legal  
**Qat’iy cheklov:** Faqat defensive + intelligence. Active exploitation, weaponization, hujum vositasi, exploit, payload, «qanday hujum qilish» — **taqiqlangan**.

---

## 0. Threat Hunting & Actor Detection (majburiy)

| Qobiliyat | Himoya ma’nosi |
|-----------|----------------|
| Fingerprinting | Behavior + infratuzilma + kod o‘xshashligi orqali actor izi |
| Campaign correlation | Ko‘p hodisani bog‘lash |
| TTP mapping | MITRE + mahalliy UZ TTP bazasi (aniqlash) |
| Infrastructure hunting | C2/phishing/scam panel **belgilarini** aniqlash |
| Memory/ancestry (W) | Jarayon zanjiri va xotira anomaliyalarini **aniqlash** |
| IOC sweeping | Real-time IOC tekshiruv |
| Persona/group tracking | OSINT (ochiq manbalar) asosida guruh kuzatuvi |
| Playbooks | Avtomatik **mudofaa** choralari (blok, izolyatsiya, xabar) |

**Avtomatik javob = faqat mudofaa:** DNS/IOC blok, qurilma ogohlantirish, fayl karantin, analyst case, UZCERT hisobot. **Hack-back yo‘q.**

---

## 1. Missiya (Killer)

Cyber Guardian AI — O‘zbekiston foydalanuvchilarini himoya qilish bilan birga, kiberhujum tayyorlayotgan yoki amalga oshirayotgan threat actorlarni **erta bosqichda aniqlaydigan**, ularning infratuzilmasi, TTP, IOC/IOA larini **kuzatadigan** va **zararsizlantiradigan** (bloklash/karantin/rasmiy xabar) elite mudofaa va threat hunting platformasi.

**Printsiplar:**

1. Faqat defensive + intelligence.  
2. Hech qanday active exploitation / weaponization / hujum vositasi.  
3. Barcha harakatlar — aniqlash, monitoring, correlation, attribution, bloklash.

---

## 2. Kuchaytirilgan funksiyalar matritsasi (#24–30)

| # | Funksiya | Android | Windows | Web | Izoh |
|---|----------|:-------:|:-------:|:---:|------|
| 24 | Advanced Threat Actor Fingerprinting | ✅ | ✅ | ✅ | Behavior + infrastructure + code similarity |
| 25 | Campaign Correlation Engine | ✅ | ✅ | ✅ | Ko‘p hujum/hodisa bog‘lanishi |
| 26 | Automated TTP Mapping & Attribution | ⚠️ | ✅ | ✅ | MITRE + custom UZ TTP base |
| 27 | Suspicious Infrastructure Detection (C2 / phishing kit / scam panel) | ✅ | ✅ | ✅ | Domain, IP, ASN, certificate — **aniqlash** |
| 28 | Memory & Process Ancestry Analysis | ❌ | ✅ | ❌ | Windows killer feature (detection-only) |
| 29 | Cross-platform IOC Sweeping | ✅ | ✅ | ✅ | Real-time sweep engine |
| 30 | Threat Actor Persona & Group Tracking | ❌ | ✅ | ✅ | OSINT: ochiq Telegram/forum; dark web — faqat litsenziyalangan/qonuniy OSINT manba (AQ-030) |

**Asoslash (qisqa):**

- **#24:** Client signal + cloud fingerprint model; shaxs doxing emas.  
- **#25:** Graph/union-find kampaniya.  
- **#26:** Androidda cheklangan IOA; W/Web to‘liqroq.  
- **#27:** Reputatsiya + sertifikat/ASN anomal; kit **yaratish** emas, **aniqlash**.  
- **#28:** EDR memory anomaly + ancestry; exploit/injection **qo‘llanmasi yo‘q**.  
- **#29:** Imzolangan IOC delta bo‘yicha sweep.  
- **#30:** Faqat ochiq/qonuniy manbalar; yopiq forumga noqonuniy kirish yo‘q.

---

## 3. Funksional talablar (Killer)

### FR-300 — Actor Knowledge Graph
- **P2** | [BE]
- Actor–Campaign–IOC–TTP–Infrastructure tugunlari (Neo4j yoki ekvivalent).
- **Qabul:** query API; PII yo‘q; audit.

### FR-301 — Intelligence Fusion Engine
- **P1** | [BE]
- OSINT + private/licensed feeds + on-device telemetry (consent, anonim) birlashtirish.
- **Qabul:** manba `license_status`; konfliktlar confidence bilan.

### FR-302 — Automated Playbook Engine (defensive)
- **P2** | [BE][W][A]
- Trigger: actor/campaign/IOC hit → playbook: `block_dns`, `quarantine_file`, `notify_user`, `open_hunt_case`, `prepare_cert_report`.
- **Qabul:** playbookda offensive action yo‘q; foydalanuvchi/admin siyosati; audit.

### FR-303 — Advanced Threat Actor Fingerprinting
- **P1** | [BE] (+A/W/Web signal)
- Behavior + infra + code/APK similarity → fingerprint_id.
- **Qabul:** explainability; confidence; FR-202 bilan mos.

### FR-304 — Automated TTP Mapping (UZ base)
- **P1** | [BE][W][Web]
- MITRE + `uz_ttp_*` custom teglar.
- **Qabul:** mapping jadvali versiyalanadi; hujum qo‘llanmasi emas.

### FR-305 — Suspicious Infrastructure Detection
- **P1** | [BE][A][W][Web]
- Domain/IP/ASN/cert anomaly → `infra_suspicious` + reasons.
- **Qabul:** C2/phishing/scam panel **ehtimoli** sifatida; false clean emas.

### FR-306 — Memory & Process Ancestry Analysis (Windows)
- **P1** | [W]
- Ancestry zanjiri + memory anomaly indicators (EDR-uslub).
- **Qabul:** detection/alert/block policy; memory dump default cloudga yo‘q; injection **aniqlash** — bajarish yo‘riqnomasi yo‘q.

### FR-307 — Cross-platform IOC Sweeping
- **P0** | [A][W][Web][BE]
- Real-time/scheduled sweep: URL, hash, domen, bot id.
- **Qabul:** imzo tekshiruvi; p95 kechikish NFR.

### FR-308 — Actor Persona & Group Tracking (OSINT)
- **P2** | [BE][Web-analyst]
- Ochiq manbalardan guruh/persona kartochkasi (taxallus, kanallar, IOC).
- **Qabul:** faqat qonuniy OSINT; ToS; Privacy Officer review; dark web — AQ-030.

### FR-309 — Living-off-the-Land / Process Injection **Detection** (Windows)
- **P1** | [W]
- IOA/Sigma: noodatiy LOLBin naqshlari, injection **belgilari**.
- **Qabul:** faqat aniqlash; texnikani o‘rgatuvchi kontent yo‘q.

### FR-310 — National early-warning interface (V4)
- **P2** | [BE]
- Davlat organlari bilan kelishilgan API/portal (AQ-031).
- **Qabul:** alohida shartnoma; ma’lumot minimallashtirish.

---

## 4. Nofunksional (Killer)

| ID | Talab |
|----|-------|
| NFR-200 | Graph query p95 < 2 s (oddiy lookup) |
| NFR-201 | IOC sweep local cache hit < 100 ms |
| NFR-202 | Playbook offensive action lint — CI da fail |
| NFR-203 | Fusion manbalari inventar + ToS |
| NFR-204 | OSINT yig‘ish faqat ochiq/qonuniy; rate-limit etik |
| NFR-205 | GNN/LLM TTP tahlili — faqat cloud; PII strip |

---

## 5. Etika (qisqa — batafsil compliance)

- Hunting: qurilma + rozilik berilgan ma’lumot.  
- Actor intel: **faqat** UZCERT, Milliy Kiberxavfsizlik Markazi yoki tegishli organlarga disclosure.  
- Sotish/uchinchi tomon marketing — yo‘q.

---

## 6. Bog‘liqlik

| Hujjat |
|--------|
| `sdd/07-intelligence-fusion-playbooks.md` |
| `sdd/06-threat-hunting-architecture.md` |
| `srs/07-threat-hunting-requirements.md` |
| `sdd/04-ai-detection-modules.md` (killer modullar) |
| `operations/03-roadmap.md` (V1–V4) |
