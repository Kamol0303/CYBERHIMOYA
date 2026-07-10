# Operations 03 — Yo‘l xaritasi (Roadmap) — Threat Hunter Edition

**Hujjat:** Cyber Guardian AI  
**Bo‘lim:** Roadmap  
**Versiya:** 2.0.0-threat-hunter  
**Rol:** Product + Architect + Threat Hunter  
**Eslatma:** Muddatlar kalendar bilan baholanmagan — sprint scope bilan.

---

## Threat Hunting va Actor Detection (majburiy)

Roadmap hunting qobiliyatini bosqichma-bosqich kiritadi: V1 da asosiy IOC actor detection, V2 da pipeline/kampaniya/intent, V3 da advanced attribution + B2B sharing.

---

## 14.1 V1 — Asosiy himoya + basic actor IOC

| Epik | Asosiy FR |
|------|-----------|
| Auth + Consent + Erasure | FR-001…005 |
| URL / QR / File (hash+TI) | FR-030…032 |
| Universal scam skeleti | FR-044 qisman |
| Basic actor IOC detection / campaign hint | FR-203 asos, FR-010 |
| Password + Email breach | FR-050…051 |
| Risk score + MITRE oddiy | FR-020, FR-082 |
| Threat feed sync | FR-010…011 |
| Dashboard + i18n + a11y | FR-090…102 |
| Privacy/Play poydevori | NFR-026…035 |

**Chiqish:** 3 platforma skan; IOC sync; fishing/scam URL; skanda `campaign` hint bo‘lishi mumkin (sodda).

---

## 14.2 V2 — Initial Threat Hunting

| Epik | Asosiy FR |
|------|-----------|
| SMS + Telegram scam | FR-040…041, FR-045 |
| Behavior + Intent/IOA | FR-080, FR-204 |
| Ransomware + Windows EDR signals | FR-070…074, FR-206 |
| APK Similarity | FR-205 |
| Hunting Pipeline + TAKB asos | FR-200…201 |
| Campaign Tracking to‘liq | FR-203, FR-047, FR-120 |
| Actor Profiling (boshlang‘ich) | FR-202 |
| Anonymized hunting telemetry | FR-209 |
| Authority report | FR-122, FR-210 |
| Browser/DNS/Wi-Fi | FR-060…062 |
| Admin / Hunt cases asos | FR-110, FR-208 qisman |
| Web intel dashboard | FR-207 |

---

## 14.3 V3 — Advanced Attribution + Deepfake + B2B

| Epik | Asosiy FR |
|------|-----------|
| Deepfake voice/face/video | FR-042, FR-046 |
| Advanced Threat Actor Attribution | FR-121, FR-202 to‘liq |
| To‘liq YARA/Sigma | FR-033, FR-081 |
| Hunt Case Management to‘liq | FR-208 |
| B2B/SOC threat intel sharing | FR-012 + AQ-003 |

---

## 14.4 Kelajakda

| G‘oya | Izoh |
|-------|------|
| iOS | Alohida SRS |
| Enterprise console | Multi-tenant hunting |
| Rasmiy CGA Telegram bot | AQ-024 |

---

## 14.5 Sprint tartibi (tavsiya)

1. BE: Auth, Scan, Feed, DB  
2. Scam classifier + basic IOC campaign hint  
3. Web/Android/Windows MVP clients  
4. Hardening + Play/signing  
5. V2 board: Pipeline, TAKB, Intent, APK similarity, Windows ancestry  

Hujjatlar: `srs/07-…`, `sdd/06-…`.
