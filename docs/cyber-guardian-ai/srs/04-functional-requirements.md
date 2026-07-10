# SRS 04 — Funksional talablar (Functional Requirements)

**Hujjat:** Cyber Guardian AI SRS  
**Bo‘lim:** 4 — Specific Requirements (Functional)  
**Versiya:** 1.0.0-draft  
**Format:** `FR-xxx` | Prioritet: P0/P1/P2 | Platforma: [A][W][Web][BE]

---

## 4.0 O‘qish qoidasi

Har bir talab:

- **ID**, **Nom**, **Prioritet**, **Platforma**, **Tavsif**, **Qabul mezonlari**, **Bog‘liqlik**.

---

## 4.1 Autentifikatsiya va foydalanuvchi

### FR-001 — Ro‘yxatdan o‘tish va kirish
- **P0** | [A][W][Web][BE]
- Foydalanuvchi email yoki telefon (AQ-002) orqali OAuth2 oqimida hisob yaratadi/kiradi.
- **Qabul:** muvaffaqiyatli login → JWT access + refresh; noto‘g‘ri parolda rate limit.
- **Bog‘liqlik:** NFR-020, NFR-030

### FR-002 — Mehmon rejimi (Web)
- **P0** | [Web]
- Ro‘yxatdan o‘tmasdan URL/QR/email (cheklangan kvota) tekshirish mumkin.
- **Qabul:** mehmon skanlari rate-limit; tarix qurilmada sessionStorage da; sync yo‘q.

### FR-003 — Qurilma bog‘lash
- **P0** | [A][W][BE]
- Qurilma `Device` yozuvi bilan hisobga bog‘lanadi (model, OS, app versiya — PII minimal).
- **Qabul:** bir hisobda bir nechta qurilma; chiqarib yuborish mumkin.

### FR-004 — Rozilik (Consent) yozuvi
- **P0** | [A][W][Web][BE]
- SMS, mikrofon/audio yuklash, VpnService, Accessibility (agar ishlatilsa) uchun alohida consent.
- **Qabul:** `ConsentRecord` saqlanadi; rad etilsa modul o‘chiq; majburiy dark pattern yo‘q.

### FR-005 — Hisobni o‘chirish (Right to erasure)
- **P0** | [Web][BE] (+A/W sozlamalar)
- Foydalanuvchi o‘chirishni so‘raydi; PII retention siyosatiga muvofiq o‘chiriladi/anonimlashtiriladi.
- **Qabul:** so‘rovdan keyin tasdiqlash; audit logda hodisa; muddat NFR-041.

---

## 4.2 Threat Intelligence va sync

### FR-010 — Threat feed sync
- **P0** | [A][W][Web][BE]
- Client imzolangan delta threat DB ni yuklab oladi.
- **Qabul:** imzo noto‘g‘ri bo‘lsa qo‘llanilmaydi; versiya raqami oshadi.

### FR-011 — Mahalliy IOC qo‘llash
- **P0** | [A][W]
- Offline rejimda cache IOC bo‘yicha URL/domen/hash tekshiruvi.
- **Qabul:** tarmoq yo‘qligida ham cache hit ishlaydi.

### FR-012 — Analyst feed boshqaruvi
- **P2** | [Web][BE]
- Threat-analyst ichki IOC qo‘shishi / manba holatini ko‘rishi mumkin.
- **Qabul:** faqat `threat-analyst` / `admin` roli; audit.

---

## 4.3 Risk Scoring

### FR-020 — Yagona risk score
- **P0** | [BE] (+client ko‘rsatish)
- Har bir skan natijasi `0–100` score + `severity` + `reasons[]` + ixtiyoriy MITRE teglari.
- **Qabul:** bir xil kirish → barqaror score (±1); explainability bo‘sh emas.

### FR-021 — Score tarixi
- **P1** | [A][W][Web][BE]
- `RiskScoreHistory` saqlanadi (dashboard trend).
- **Qabul:** oxirgi N yozuv ko‘rinadi; retention NFR-040.

---

## 4.4 URL / QR / File skan

### FR-030 — URL tekshirish
- **P0** | [A][W][Web][BE]
- `POST /v1/scan/url` — URL normalizatsiya, reputation, risk score.
- **Qabul:** fishing/local UZ toifalari uchun teg; bloklash tavsiyasi.

### FR-031 — QR tahlil
- **P0** | [A][W][Web]
- Rasm/kamera → payload → agar URL bo‘lsa FR-030; aks holda ogohlantirish.
- **Qabul:** to‘lov QR firibgarligi qoidalari (mahalliy) ishlaydi.

### FR-032 — Fayl reputatsiya
- **P0** | [A][W][Web][BE]
- Hash hisoblash (imkon qadar clientda) + TI; Webda upload limitti.
- **Qabul:** ma’lum zararli hash → critical; noma’lum → info + ehtiyot.

### FR-033 — Fayl YARA skani
- **P1** | [A][W][BE]
- Local/backend YARA qoidalari.
- **Qabul:** match → ThreatEvent + tushuntirish; Web faqat BE orqali.

---

## 4.5 SMS / Telegram / Deepfake

### FR-040 — SMS scam aniqlash (on-device)
- **P1** | [A]
- Kelgan SMS on-device klassifikator/heuristika bilan baholanadi; xom matn serverga **yuborilmaydi**.
- **Qabul:** shubhali bo‘lsa tizim notification; cloudga faqat anonim meta (ixtiyoriy, consent bilan): til, score, qoida ID.

### FR-041 — Telegram scam (ulashilgan kontent)
- **P1** | [A][W][Web]
- Forward/bot/paste orqali matn/URL tekshiruvi.
- **Qabul:** shaxsiy chat API ishlatilmaydi.

### FR-042 — Deepfake voice (consent)
- **P2** | [A][W][Web][BE]
- Foydalanuvchi audio yuklaydi; consent majburiy; natija score + tushuntirish.
- **Qabul:** consent yo‘q → modul ishlamaydi; jonli yozib olish yo‘q.

### FR-043 — Shubhali xabar yuborish oqimi
- **P0** | [A][W][Web]
- Foydalanuvchi matn/URL/skrinshot yuboradi (PII filtri bilan).
- **Qabul:** yuborishdan oldin nima ulashilishi ko‘rsatiladi; bekor qilish mumkin.

> **Kengaytma (scam oilalari, bot/pul taklifi, deepfake face, kampaniya/hujumchi klaster, rasmiy hisobot):**  
> `FR-044`…`FR-047`, `FR-120`…`FR-123` — batafsil: [`06-universal-scam-and-attribution.md`](06-universal-scam-and-attribution.md).

---

## 4.6 Parol va breach

### FR-050 — Password health
- **P0** | [A][W][Web]
- Mahalliy kuchlilik + k-anonymity pwned check.
- **Qabul:** to‘liq parol tarmoqda ko‘rinmaydi; natija: weak/pwned/ok.

### FR-051 — Email breach check
- **P0** | [A][W][Web][BE]
- `POST /v1/breach-check` — email tekshiruvi.
- **Qabul:** topilsa tavsiyalar (parol almashtirish, 2FA); email marketingga ishlatilmaydi.

---

## 4.7 Tarmoq / DNS / Wi-Fi / Browser

### FR-060 — DNS Security
- **P1** | [A][W][Web-ext]
- Zararli domenlarni ogohlantirish/bloklash.
- **Qabul:** foydalanuvchi istisno (allowlist) qo‘sha oladi; audit.

### FR-061 — Wi-Fi analyzer
- **P1** | [A][W]
- Ochiq/shifrlanmagan tarmoq, shubhali nomlar haqida ogohlantirish.
- **Qabul:** Webda funksiya yo‘q (matritsa).

### FR-062 — Browser protection (extension)
- **P1** | [W][Web]
- Navigatsiya oldidan URL tekshiruvi; phishing sahifada banner.
- **Qabul:** Androidda in-app safe browser; overlay yo‘q.

### FR-063 — Browser extension analyzer
- **P2** | [W][Web]
- O‘rnatilgan kengaytmalar ruxsatlari tahlili.
- **Qabul:** yuqori ruxsatli noma’lum kengaytma → warning.

---

## 4.8 Windows chuqur himoya

### FR-070 — Process monitoring
- **P1** | [W]
- Yangi jarayon, shubhali parent-child, imzosiz binar ogohlantirishi.
- **Qabul:** faqat aniqlash/ogohlantirish/bloklash siyosati; exploit yo‘q.

### FR-071 — Registry monitoring
- **P1** | [W]
- Himoya qoidalari belgilagan registry kalitlaridagi shubhali o‘zgarishlarga ogohlantirish (aniqlash/bloklash).
- **Qabul:** Sigma/qoida asosida; FP kamaytirish allowlist; qoidalarda hujum qo‘llanmasi yo‘q.

### FR-072 — Network monitoring (endpoint)
- **P1** | [W]
- Jarayon ↔ tashqi ulanish korrelyatsiyasi.
- **Qabul:** TI domen/IP hit → ThreatEvent.

### FR-073 — USB protection
- **P1** | [W]
- Yangi USB; siyosat: so‘rash / bloklash / ruxsat.
- **Qabul:** avto-ishga tushish urinishida critical.

### FR-074 — Ransomware monitoring
- **P1** | [W] (A: P2 cheklangan)
- Honeypot fayl o‘zgarishi + mass write/entropiya heuristikasi → ogohlantirish.
- **Qabul:** demo stsenariyda aniqlash; foydalanuvchiga tiklash yo‘riqnomasi (backup tavsiyasi).

---

## 4.9 Behavior, YARA/Sigma, MITRE

### FR-080 — Behavior Analysis Engine
- **P1** | [A][W][Web⚠️]
- Hodisalar zanjiridan anomaliya / shubhali naqsh.
- **Qabul:** yakka hodisa emas, korrelyatsiya; explainability.

### FR-081 — Sigma qoidalari
- **P2** | [W][BE]
- Sigma → agent/backend pipeline.
- **Qabul:** qoida versiyalanadi; imzo.

### FR-082 — MITRE ATT&CK mapping
- **P0** | [BE][Web][A][W]
- ThreatEvent ga tactic/technique teglari.
- **Qabul:** dashboardda filtr; alohida «hujum qo‘llanma» yo‘q.

---

## 4.10 Dashboard, notification, hisobot

### FR-090 — Security Dashboard
- **P0** | [A][W][Web]
- Joriy holat, oxirgi ogohlantirishlar, tezkor skan CTA.
- **Qabul:** birinchi ekranda vahima statistikasi to‘plami bo‘lmasin; tinch UX.

### FR-091 — Notification darajalari
- **P0** | [A][W][Web]
- `info` / `warning` / `critical` — matn aniq, CTA bor, dark pattern yo‘q.
- **Qabul:** critical yopib bo‘lmaydigan tizim notification (A); yashirin overlay yo‘q.

### FR-092 — Hisobot / tarix
- **P0** | [A][W][Web]
- ScanResult va ThreatEvent tarixi.
- **Qabul:** filtr, batafsil, ulashish (PII siz).

### FR-093 — Hisobot yuborish (analyst/admin)
- **P1** | [Web][BE]
- Tanlangan hodisalar bo‘yicha eksport (JSON/PDF).
- **Qabul:** audit; PII redaksiya.

---

## 4.11 Sozlamalar, i18n, a11y

### FR-100 — Sozlamalar
- **P0** | [A][W][Web]
- Modul yoqish/o‘chirish, ruxsatlar, til, bildirishnoma, allowlist.
- **Qabul:** har bir xavfli ruxsat uchun tushuntirish ekrani.

### FR-101 — Ko‘p tillilik
- **P0** | [A][W][Web]
- uz / ru / en to‘liq parallel; madaniy misollar.
- **Qabul:** til almashinuvida barcha asosiy ekranlar tarjima.

### FR-102 — Accessibility
- **P0** | [A][W][Web]
- WCAG 2.1 AA; screen reader; katta shrift.
- **Qabul:** kontrast, fokus, label; a11y checklist QA da.

### FR-103 — Onboarding
- **P0** | [A][W][Web]
- Ruxsatlarni tushuntirish + minimal so‘rov ketma-ketligi.
- **Qabul:** «hammasini birga so‘rash» yo‘q; rad etish mumkin.

---

## 4.12 Admin / Analyst

### FR-110 — Admin panel
- **P1** | [Web][BE]
- Foydalanuvchi/qurilma, qoidalar holati, audit ko‘rish.
- **Qabul:** RBAC; admin harakatlari AuditLog da.

### FR-111 — Subscription holati
- **P1** | [A][W][Web][BE]
- Free / Plus (AQ-003) imkoniyatlari.
- **Qabul:** limitlar aniq ko‘rsatiladi; yashirin to‘lov yo‘q.

---

## 4.13 Talablar matritsaga xarita (qisqa)

| Matritsa # | Asosiy FR |
|------------|-----------|
| 1 TI | FR-010–012 |
| 2 Scoring | FR-020–021 |
| 3 Behavior | FR-080 |
| 4 URL | FR-030 |
| 5 SMS | FR-040 |
| 6 Telegram | FR-041 |
| 7 QR | FR-031 |
| 8 Deepfake | FR-042 |
| 9 Wi-Fi | FR-061 |
| 10 Browser | FR-062 |
| 11 Password | FR-050 |
| 12 Breach | FR-051 |
| 13 USB | FR-073 |
| 14 Ransomware | FR-074 |
| 15 File | FR-032–033 |
| 16–17 Process/Registry | FR-070–071 |
| 18 Ext analyzer | FR-063 |
| 19–20 Network/DNS | FR-060, FR-072 |
| 21–22 YARA/Sigma | FR-033, FR-081 |
| 23 MITRE | FR-082 |
