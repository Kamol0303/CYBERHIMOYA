# Operations 03 — Yo‘l xaritasi (Roadmap)

**Hujjat:** Cyber Guardian AI  
**Bo‘lim:** Roadmap  
**Versiya:** 1.1.0-draft  
**Rol:** Product + Architect  
**Eslatma:** Muddatlar kalendar hafta/kun bilan baholanmagan — sprint-planningda story point/scope bilan.

---

## 14.1 V1 — MVP

**Maqsad:** 3 platformada tezkor tekshiruv + dashboard + maxfiylik + **asosiy scam oilalari** (to‘lov/gov/emergency URL).

| Epik | Asosiy FR | Platforma |
|------|-----------|-----------|
| Auth + Consent + Erasure | FR-001…005 | A/W/Web/BE |
| URL / QR / File (hash+TI) | FR-030…032 | A/W/Web |
| Universal scam skeleti (payment/gov/emergency) | FR-044 (qisman) | BE |
| Password + Email breach | FR-050…051 | A/W/Web |
| Risk score + MITRE oddiy | FR-020, FR-082 | BE |
| Threat feed sync | FR-010…011 | A/W/Web |
| Dashboard + Notification + i18n + a11y | FR-090…102 | A/W/Web |
| Privacy/Play poydevori | NFR-026…035 | A/BE |

**Chiqish mezonlari:** Mehmon Web skan; A/W o‘rnatiladi; imzolangan IOC sync; asosiy fishing/scam URL; SMS xom matn cloudga yo‘q.

---

## 14.2 V2 — Scam qamrovi + kampaniya / «kim?»

| Epik | Asosiy FR |
|------|-----------|
| SMS scam on-device | FR-040 |
| Telegram ulashilgan kontent | FR-041 |
| Pul-taklif bot / ish/lotoreya/invest | FR-044 (to‘liq), FR-045 |
| Cross-channel korrelyatsiya | FR-047 |
| Kampaniya klasterlash + foydalanuvchi tushuntirishi | FR-120, FR-123 |
| Rasmiy organlarga himoya hisoboti | FR-122 |
| Behavior Analysis | FR-080 |
| Browser protection / extension | FR-062 |
| DNS + Wi-Fi | FR-060…061 |
| Windows: Process/Registry/Network/USB/Ransomware | FR-070…074 |
| YARA qisman + File chuqurroq | FR-033 |
| Admin panel asoslari | FR-110…111 |

---

## 14.3 V3 — Deepfake + actor cluster + B2B

| Epik | Asosiy FR |
|------|-----------|
| Deepfake voice (consent) | FR-042 |
| Deepfake face/video (consent) | FR-046 |
| Threat Actor cluster (taxminiy, infratuzilma) | FR-121 |
| To‘liq YARA/Sigma | FR-033, FR-081 |
| MITRE boyitilgan analyst UX | FR-082, FR-093 |
| B2B/SOC threat-feed API monetizatsiya | FR-012 + tijorat (AQ-003) |

---

## 14.4 Kelajakda ko‘rib chiqiladi

| G‘oya | Izoh |
|-------|------|
| iOS versiyasi | Sandbox/ruxsat modeli alohida SRS talab qiladi |
| Enterprise boshqaruv konsoli | MDM/policy, multi-tenant |
| Qo‘shimcha tillar | Qozoq va boshqalar — resource asosida |
| Rasmiy CGA Telegram bot (foydalanuvchi forward qiladi) | AQ-024 |

---

## 14.5 Sprint-planning uchun epik tartibi (tavsiya)

1. BE skeleton: Auth, Scan URL, Feed sync, DB  
2. Scam classifier skeleti (`SCAM_PAYMENT/GOV/EMERGENCY`)  
3. Web mehmon skan + i18n  
4. Android MVP UI + local cache  
5. Windows MVP UI + local cache  
6. Password/Breach  
7. QR  
8. File hash  
9. Hardening: rate limit, retention jobs, audit  
10. Play/Windows signing staging  

V2: bot/pul taklifi, kampaniya klaster, authority report.  
V3: deepfake + actor cluster.

Batafsil: `srs/06-universal-scam-and-attribution.md`.
