# Cyber Guardian AI — Texnik Spetsifikatsiya (SRS + SDD)

**Versiya:** 1.0.0-draft  
**Sana:** 2026-07-10  
**Holat:** Sprint-planning uchun tayyor draft  
**Til:** O‘zbek (texnik atamalar inglizcha saqlanadi)  
**Printsip:** Faqat himoya (defensive) funksiyalar — hujum/ekspluatatsiya tavsifi yo‘q

---

## Hujjatlar indeksi

| # | Hujjat | Joylashuv | Mazmun |
|---|--------|-----------|--------|
| 0 | Ushbu indeks | `README.md` | Navigatsiya, qabul mezonlari |
| 1 | SRS — Kirish | [`srs/01-introduction.md`](srs/01-introduction.md) | Maqsad, doira, ta'riflar, printsiplar |
| 2 | SRS — Umumiy tavsif | [`srs/02-overall-description.md`](srs/02-overall-description.md) | Mahsulot portfeli, foydalanuvchilar, cheklovlar |
| 3 | SRS — Funksiya × Platforma | [`srs/03-feature-platform-matrix.md`](srs/03-feature-platform-matrix.md) | Majburiy matritsa + asoslash |
| 4 | SRS — Funksional talablar | [`srs/04-functional-requirements.md`](srs/04-functional-requirements.md) | FR-001… raqamlangan talablar |
| 5 | SRS — Nofunksional talablar | [`srs/05-non-functional-requirements.md`](srs/05-non-functional-requirements.md) | NFR-001… |
| 6 | SDD — Tizim arxitekturasi | [`sdd/01-system-architecture.md`](sdd/01-system-architecture.md) | HLD, on-device vs cloud, trust boundaries |
| 7 | SDD — UML va ER diagrammalar | [`sdd/02-uml-er-diagrams.md`](sdd/02-uml-er-diagrams.md) | Use Case, Class, Sequence, Component, Deployment, ER |
| 8 | SDD — API va ma'lumotlar bazasi | [`sdd/03-api-and-database.md`](sdd/03-api-and-database.md) | REST `/v1`, sxemalar, retention |
| 9 | SDD — AI/Detection modullari | [`sdd/04-ai-detection-modules.md`](sdd/04-ai-detection-modules.md) | 15+ modul shablon bo‘yicha |
| 10 | SDD — UX/UI dizayn tizimi | [`sdd/05-ux-ui-design-system.md`](sdd/05-ux-ui-design-system.md) | Dizayn tizimi, wireframe, a11y |
| 11 | Compliance | [`compliance/01-security-privacy-compliance.md`](compliance/01-security-privacy-compliance.md) | Android ruxsatlar, maxfiylik, disclosure |
| 12 | Mahalliy tahdid modeli | [`compliance/02-uzbekistan-threat-model.md`](compliance/02-uzbekistan-threat-model.md) | UZCERT, mahalliy firibgarlik toifalari |
| 13 | Operatsion talablar | [`operations/01-operational-requirements.md`](operations/01-operational-requirements.md) | Notification, offline, update, audit |
| 14 | QA va DevOps | [`operations/02-qa-devops.md`](operations/02-qa-devops.md) | Test, CI/CD, performance |
| 15 | Yo‘l xaritasi | [`operations/03-roadmap.md`](operations/03-roadmap.md) | V1/V2/V3 |
| 16 | Taxminlar va ochiq savollar | [`assumptions-and-open-questions.md`](assumptions-and-open-questions.md) | Hallucinate qilinmagan ochiq nuqtalar |
| 17 | Sifat tekshiruvi | [`acceptance-checklist.md`](acceptance-checklist.md) | Sprint-planning tayyorligi |

---

## Virtual ekspert jamoa (rol → hujjat)

| Rol | Asosiy hujjatlar |
|-----|------------------|
| Principal Security Architect | `sdd/01`, `compliance/01`, `compliance/02` |
| Senior Malware Researcher | `sdd/04` (YARA/File/URL), `srs/03` |
| AI/ML Engineer | `sdd/04`, `sdd/01` (on-device vs cloud) |
| Mobile Security Specialist | `compliance/01`, `srs/03` (Android) |
| Windows Security Engineer | `sdd/04` (Process/Registry/USB/Ransomware) |
| SOC / Threat Intel Lead | `compliance/02`, MITRE mapping |
| Senior Full-Stack Developer | `sdd/03`, `sdd/01` |
| UX/UI Product Designer | `sdd/05` |
| Privacy & Compliance Officer | `compliance/01` |
| QA/DevOps Lead | `operations/02` |

---

## Qabul mezonlari (qisqa)

1. Har bir bo‘lim to‘liq — `...` yoki bo‘sh joylar yo‘q.
2. Talablar `FR-xxx` / `NFR-xxx` formatida.
3. Diagrammalar ishlaydigan Mermaid kodida.
4. Noaniqliklar faqat `assumptions-and-open-questions.md` da.
5. Faqat defensive funksiyalar tasvirlangan.

**Yakuniy savol:** jamoa ushbu spetsifikatsiya asosida darhol sprint-planning boshlay oladimi? → javob: [`acceptance-checklist.md`](acceptance-checklist.md).
