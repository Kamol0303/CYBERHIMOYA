# Cyber Guardian AI — Texnik Spetsifikatsiya (SRS + SDD)
## Threat Hunter Edition

**Versiya:** 2.0.0-threat-hunter  
**Sana:** 2026-07-10  
**Holat:** Sprint-planning uchun tayyor draft  
**Til:** O‘zbek (texnik atamalar inglizcha saqlanadi)  
**Branch siyosati:** Bitta ishchi branch (ushbu PR); mahsulotlar bo‘yicha parallel branchlar ochilmaydi  

---

## Himoya-only nizom (majburiy)

1. **Faqat mudofaa va intellektual aniqlash** — aniqlash, monitoring, ogohlantirish, bloklash, threat actor kuzatish.  
2. **Maqsad:** shubhali faoliyat va potensial actor/kampaniyani **belgilari** bo‘yicha topish.  
3. **Taqiqlanadi:** hujum/ekspluatatsiya qo‘llanmasi, zararli kod, exploit PoC, hack-back, ruxsatsiz kuzatuv.  
4. **Yozish qoidasi:** «qanday buziladi» emas — «qanday **aniqlanadi / kuzatiladi / bloklanadi**».  
5. **Hunting ma’lumoti:** anonim + consent; actor batafsili — rasmiy organlarga disclosure.  
6. **Test:** himoya labi; red team **simulation** (detektor mashqi); repoga malware/exploit yo‘q.

---

## Hujjatlar indeksi

| # | Hujjat | Joylashuv | Mazmun |
|---|--------|-----------|--------|
| 0 | Ushbu indeks | `README.md` | Navigatsiya |
| 1 | SRS — Kirish | [`srs/01-introduction.md`](srs/01-introduction.md) | Missiya (Threat Hunter) |
| 2 | SRS — Umumiy tavsif | [`srs/02-overall-description.md`](srs/02-overall-description.md) | 3 mahsulot + hunting |
| 3 | SRS — Funksiya × Platforma | [`srs/03-feature-platform-matrix.md`](srs/03-feature-platform-matrix.md) | #1–35 matritsa |
| 4 | SRS — Funksional talablar | [`srs/04-functional-requirements.md`](srs/04-functional-requirements.md) | FR-001… |
| 4b | SRS — Scam + attribution | [`srs/06-universal-scam-and-attribution.md`](srs/06-universal-scam-and-attribution.md) | Scam oilalari |
| 4c | **SRS — Threat Hunting** | [`srs/07-threat-hunting-requirements.md`](srs/07-threat-hunting-requirements.md) | FR-200…210, NFR-100… |
| 5 | SRS — Nofunksional | [`srs/05-non-functional-requirements.md`](srs/05-non-functional-requirements.md) | NFR-001… |
| 6 | SDD — Arxitektura | [`sdd/01-system-architecture.md`](sdd/01-system-architecture.md) | HLD + Hunt/TAKB |
| 6b | **SDD — Hunting Architecture** | [`sdd/06-threat-hunting-architecture.md`](sdd/06-threat-hunting-architecture.md) | Pipeline, TAKB, oqim |
| 7 | SDD — UML/ER | [`sdd/02-uml-er-diagrams.md`](sdd/02-uml-er-diagrams.md) | Diagrammalar |
| 8 | SDD — API/DB | [`sdd/03-api-and-database.md`](sdd/03-api-and-database.md) | REST `/v1` |
| 9 | SDD — AI/Detection | [`sdd/04-ai-detection-modules.md`](sdd/04-ai-detection-modules.md) | Attribution/Campaign/Intent/APK |
| 10 | SDD — UX/UI | [`sdd/05-ux-ui-design-system.md`](sdd/05-ux-ui-design-system.md) | Dizayn + hunt UX |
| 11 | Compliance | [`compliance/01-security-privacy-compliance.md`](compliance/01-security-privacy-compliance.md) | Maxfiylik + hunting |
| 12 | UZ tahdid modeli | [`compliance/02-uzbekistan-threat-model.md`](compliance/02-uzbekistan-threat-model.md) | Actor patternlari |
| 13–15 | Operations | `operations/` | Ops, QA (red team sim), roadmap |
| 16 | Ochiq savollar | [`assumptions-and-open-questions.md`](assumptions-and-open-questions.md) | AQ |
| 17 | Qabul | [`acceptance-checklist.md`](acceptance-checklist.md) | Sprint-ready |

---

## Virtual ekspert jamoa

| Rol | Asosiy hujjatlar |
|-----|------------------|
| Principal Security Architect | `sdd/01`, `sdd/06`, `srs/07` |
| **Proactive Threat Hunter** | `srs/07`, `sdd/06`, `sdd/04` (Attribution) |
| Senior Malware Researcher & Threat Hunter | `sdd/04`, APK similarity, YARA |
| AI/ML Engineer | Attribution, Intent, Scoring |
| Mobile Security Specialist | Android hunting signals |
| Windows Security Engineer | Ancestry, IOA, anomaly |
| SOC / Threat Intel & Hunting Lead | TAKB, MITRE, UZ model |
| Senior Full-Stack Developer | API, hunt cases |
| UX/UI Product Designer | `sdd/05` |
| Privacy & Compliance Officer | Hunting anonimlik, FR-210 |
| QA/DevOps Lead | Red team simulation (defensive) |

---

## Qabul mezonlari (qisqa)

1. Bo‘limlar to‘liq; Threat Hunting qismi majburiy joylarda bor.  
2. `FR-xxx` / `NFR-xxx` + hunting FR-200…  
3. Mermaid diagrammalar ishlaydi.  
4. Ochiq savollar alohida.  
5. Faqat mudofaa / aniqlash / kuzatish.

**Sprint-planning?** → [`acceptance-checklist.md`](acceptance-checklist.md).
