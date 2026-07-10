# Cyber Guardian AI — Hujjatlar indeksi

**Joriy nashr:** Apex Master **v5.3.0-emergency-reporting** (passive hunting, read-only monitoring, lokal mudofaa response)  
**Sprint-planning KIRISH NUQTASI:** [`APEX-MASTER-SPEC.md`](APEX-MASTER-SPEC.md)

Ushbu fayl — master spetsifikatsiyaga yo‘l ko‘rsatgich.

---

## Nizom (eng qat’iy)

Faqat **mudofaa**. Active probing, hujum, exploit, C2/payload, boshqa tizimga faol aralashuv — taqiqlangan.  
Avtomatik javob: lokal bloklash, izolyatsiya, ogohlantirish, rasmiy organlarga xabar.  
Bitta branch.

Ushbu fayl — master spetsifikatsiyaga yo‘l ko‘rsatgich. Barcha 15 bo‘lim masterda; quyida chuqur satellite hujjatlar.

---

## Nizom

Faqat mudofaa, threat hunting, intelligence, avtomatlashtirilgan **himoya**.  
Hujum / ekspluatatsiya / exploit / payload / weaponization / hack-back — taqiqlangan.  
Bitta branch.

---

## Master

| Hujjat | Mazmun |
|--------|--------|
| **[`APEX-MASTER-SPEC.md`](APEX-MASTER-SPEC.md)** | IEEE 830 SRS+SDD — §0…§15 (**v5.1.0** yangilangan rollar/matritsa/arch) |
| [`acceptance-checklist.md`](acceptance-checklist.md) | «Sprint planning boshlay oladimi?» |
| [`assumptions-and-open-questions.md`](assumptions-and-open-questions.md) | AQ-001…041 |
| `operations/04-aq039-allowlist-runbook.md` | Emergency allowlist (Legal) |
| `operations/aq039-allowlist.env.template` | Env shablon (`REPLACE_*`) |
| `operations/05-v1-release-checklist.md` | Merge/release checklist |

---

## Satellite (chuqurlashtirish)

| Papka | Mazmun |
|-------|--------|
| `srs/01`…`05` | Asosiy SRS |
| `srs/06` | Universal scam |
| `srs/07` | Threat hunting FR-200 |
| `srs/08` | Killer Edition |
| `srs/09` | Apex FR-400 |
| `sdd/01`…`03` | Arch, UML, API/DB |
| `sdd/04` + `04b` + `04c` | AI modullar |
| `sdd/05` | UX |
| `sdd/06`…`08` | Hunting / Fusion / Apex arch |
| `compliance/` | Privacy, UZ model |
| `operations/` | Ops, QA, roadmap V1–V5 |

---

## Jamoa (qisqa)

Defensive Hunt Lead · Defensive Malware Analyst · AI/ML (predictive defense) · Blue Team Hunter · XDR Specialist · TI & Attribution · Forensics (defensive) · Zero-trust Full-Stack · Privacy & Ethics
