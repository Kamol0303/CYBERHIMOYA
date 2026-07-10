# Operations 03 — Yo‘l xaritasi (Roadmap)

**Hujjat:** Cyber Guardian AI  
**Bo‘lim:** Roadmap  
**Versiya:** 1.0.0-draft  
**Rol:** Product + Architect  
**Eslatma:** Muddatlar kalendar hafta/kun bilan baholanmagan — sprint-planningda story point/scope bilan.

---

## 14.1 V1 — MVP

**Maqsad:** 3 platformada tezkor tekshiruv + asosiy dashboard + maxfiylik poydevori.

| Epik | Asosiy FR | Platforma |
|------|-----------|-----------|
| Auth + Consent + Erasure | FR-001…005 | A/W/Web/BE |
| URL / QR / File (hash+TI) | FR-030…032 | A/W/Web |
| Password + Email breach | FR-050…051 | A/W/Web |
| Risk score + MITRE oddiy | FR-020, FR-082 | BE |
| Threat feed sync | FR-010…011 | A/W/Web |
| Dashboard + Notification + i18n + a11y | FR-090…102 | A/W/Web |
| Privacy/Play poydevori | NFR-026…035 | A/BE |

**Chiqish mezonlari:** Mehmon Web skan ishlaydi; A/W o‘rnatiladi; imzolangan IOC sync; SMS xom matn cloudga yo‘q (SMS moduli hali V2).

---

## 14.2 V2

| Epik | Asosiy FR |
|------|-----------|
| SMS scam on-device | FR-040 |
| Telegram ulashilgan kontent | FR-041 |
| Behavior Analysis | FR-080 |
| Browser protection / extension | FR-062 |
| DNS + Wi-Fi | FR-060…061 |
| Windows: Process/Registry/Network/USB/Ransomware | FR-070…074 |
| YARA qisman + File chuqurroq | FR-033 |
| Admin panel asoslari | FR-110…111 |

---

## 14.3 V3

| Epik | Asosiy FR |
|------|-----------|
| Deepfake voice (consent) | FR-042 |
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

---

## 14.5 Sprint-planning uchun epik tartibi (tavsiya)

1. BE skeleton: Auth, Scan URL, Feed sync, DB  
2. Web mehmon skan + i18n  
3. Android MVP UI + local cache  
4. Windows MVP UI + local cache  
5. Password/Breach  
6. QR  
7. File hash  
8. Hardening: rate limit, retention jobs, audit  
9. Play/Windows signing staging  

V2+ epiklar alohida boardda.
