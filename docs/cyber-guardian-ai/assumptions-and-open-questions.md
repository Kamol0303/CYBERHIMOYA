# Taxminlar va ochiq savollar

**Hujjat:** Cyber Guardian AI SRS/SDD  
**Versiya:** 1.0.0-draft  
**Qoida:** Noaniq joylar **o‘ylab topilmaydi**. Qaror qabul qilinmaguncha AQ/A sifatida qoladi.

---

## A — Ishchi taxminlar (hozircha qabul qilingan)

| ID | Taxmin | Agar noto‘g‘ri bo‘lsa |
|----|--------|------------------------|
| A-01 | Backend asosan PostgreSQL + Redis + object storage | Boshqa stack tanlansa SDD 03 yangilanadi |
| A-02 | Clientlar REST `/v1` bilan gaplashadi (gRPC ichki ixtiyoriy) | Ichki gRPC bo‘lsa gateway mapping qo‘shiladi |
| A-03 | MVP da deepfake va to‘liq Sigma yo‘q | V3/V2 ga mos |
| A-04 | Accessibility Service Android MVP da ishlatilmaydi | AQ-014 qarori |
| A-05 | Breach-check tashqi API orqali | Provayder yo‘q bo‘lsa modul kechiktiriladi |
| A-06 | Uch til: uz, ru, en yetarli MVP uchun | Boshqa tillar roadmap |
| A-07 | Web monitoring Emas — faqat tekshiruv/panel | O‘zgarmas cheklov |

---

## AQ — Ochiq savollar (qaror kerak)

| ID | Savol | Ta’sir | Kim |
|----|-------|--------|-----|
| AQ-001 | Brend nomi: «Cyber Guardian AI» vs «CyberHimoya»? | UI, store listing | Product |
| AQ-002 | Auth identifikator: email, telefon, yoki ikkalasi? | FR-001, PII | Product + Privacy |
| AQ-003 | Tariflar: faqat free yoki Plus pullik? Narx? | FR-111, V3 monetizatsiya | Business |
| AQ-004 | Web fayl upload limitti 25 MB qabul qilinadimi? | NFR-002 | Eng + Product |
| AQ-005 | Prod multi-AZ / qaysi cloud (UZ data residency)? | NFR-012, qonun | Infra + Legal |
| AQ-006 | Certificate pinning pin ro‘yxati va rotatsiya? | NFR-020 | Security |
| AQ-007 | FP/FN gold set kim yig‘adi va qayerda saqlanadi? | NFR-072 | TI + QA |
| AQ-008 | Extension brauzerlari: Chrome/Edge/Firefox qaysilari V1/V2? | FR-062 | Product |
| AQ-009 | On-call / incident runbook egasi? | NFR-081 | DevOps |
| AQ-010 | API va marketing domenlari? | SDD API | Infra |
| AQ-011 | OAuth2 grant turlari (password vs code + PKCE)? | Auth | Eng |
| AQ-012 | Service mesh / mTLS ichki tarmoqda bormi? | HLD | Infra |
| AQ-013 | Deepfake audio retention aniq soat (24 vs 72)? | Privacy | Privacy |
| AQ-014 | Accessibility Service umuman rejalashtiriladimi? | Android compliance | Mobile Sec |
| AQ-015 | Breach/TI provayderlar DPA holati? | Compliance | Legal |
| AQ-016 | `security@` domani va disclosure sahifa? | Responsible disclosure | Security |
| AQ-017 | UZCERT feed texnik formati va kelishuv? | Local TI | TI + Legal |
| AQ-018 | Windows agent va UI versiyalash strategiyasi? | CI/CD | Windows Eng |
| AQ-019 | Push: FCM o‘rniga boshqa (Huawei va h.k.) kerakmi? | Notification | Mobile |
| AQ-020 | Korporativ SSO (SAML/OIDC) V1 da kerakmi? | Auth | Business |
| AQ-021 | UZCERT ga avtomatik hisobot API yoki qo‘lda yuklash? | FR-122 | TI + Legal |
| AQ-022 | Actor cluster taxallusini oddiy foydalanuvchiga ko‘rsatish? | FR-121/123 | Product |
| AQ-023 | Deepfake video hajm/davomiylik limitti? | FR-046 | Eng + Privacy |
| AQ-024 | Rasmiy CGA Telegram bot (forward→tekshiruv) qilinadimi? | FR-045 | Product |
| AQ-025 | TAKB actor alias nomlash konvensiyasi (UZ-SCAM-###)? | FR-201 | TI Lead |
| AQ-026 | Hunting telemetry default: opt-in yoki opt-out? | FR-209 | Privacy |
| AQ-027 | Actor Knowledge Graph: Neo4j vs managed alternative? | FR-300 | Infra |
| AQ-028 | LLM TTP summarization vendor / self-host? | NFR-205 | AI + Privacy |
| AQ-029 | Passive anomaly: qaysi EDR callback/provider? | FR-306 | Windows Eng |
| AQ-030 | Dark web OSINT: litsenziyalangan provayder bormi yoki faqat clearnet? | FR-308 | Legal + TI |
| AQ-031 | V4 national early-warning: qaysi davlat API/shartnoma? | FR-310 | Legal + Product |
| AQ-032 | Playbook `isolate_device`: majburiy agent izolyatsiya yoki faqat tavsiya? | FR-302 | Product + Privacy |
| AQ-033 | Stream bus: Kafka vs Pulsar vs cloud-native? | FR-400 | Infra |
| AQ-034 | RU/CN SE pattern kutubxonasi manbasi va litsenziya? | FR-408 | TI + Legal |
| AQ-035 | Immutable audit: hash-chain vs WORM storage? | FR-411 | Infra + Compliance |
| AQ-036 | Regional Edge PoP kerakmi (MVP da yo‘q)? | SDD-08 | Infra |
| AQ-037 | Vector DB tanlovi (pgvector / milvus / other)? | SDD-08 | Eng |
| AQ-038 | V5 autonomous defense: human-in-the-loop majburiy darajasi? | Roadmap V5 | Ethics |

---

## Qaror qabul qilish tartibi

1. AQ ni sprint grooming da ochish.  
2. Qaror → tegishli FR/NFR/SDD ga patch.  
3. Ushbu faylda AQ → `Resolved: …` deb yopish.  
4. Hallucinate qilingan «taxminiy vendor» yoki «taxminiy qonun bandi» kiritilmasin.
