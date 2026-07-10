# SRS 01 — Kirish (Introduction)

**Hujjat:** Cyber Guardian AI Software Requirements Specification  
**Bo‘lim:** 1 — Introduction (IEEE 830)  
**Versiya:** 2.0.0-threat-hunter  
**Rol:** Principal Security Architect + Privacy Officer + Proactive Threat Hunter

---

## 1.1 Maqsad (Purpose)

Ushbu SRS «Cyber Guardian AI» (**Threat Hunter Edition**) ekotizimining funksional va nofunksional talablarini belgilaydi. Maqsad — jamoa **savol bermasdan** sprint-planningni boshlashi.

Hujjat quyidagilarni qamrab oladi:

- Uchta mustaqil mahsulot: Android, Windows Desktop, Web Platforma.
- Markaziy cloud + **Threat Hunting Pipeline** + **Threat Actor Knowledge Base**.
- Faqat **mudofaa va intellektual aniqlash**: aniqlash, monitoring, ogohlantirish, bloklash, threat actor kuzatish.

Hujjat quyidagilarni **qamrab olmaydi**:

- Hujum, ekspluatatsiya, ruxsatsiz kirish, zararli kod namunalari, «qanday buzish» tavsifi.
- Hack-back yoki ruxsatsiz kuzatuv.
- iOS (faqat roadmap «kelajakda»).

### Threat Hunting va Actor Detection (majburiy)

Har bir asosiy bo‘limda hunting/actor qismi bor. Markaziy talablar: `srs/07-threat-hunting-requirements.md`.

---

## 1.2 Doira (Scope)

### 1.2.1 Mahsulot nomi

**Cyber Guardian AI** (ichki kod nomi: `CGA`; brend ko‘rinishi: mahalliy bozorda «CyberHimoya» bilan moslashtirilishi mumkin — ochiq savol AQ-001).

### 1.2.2 Muammo konteksti

O‘zbekiston foydalanuvchilari orasida quyidagi tahdidlar ko‘paymoqda:

| Tahdid toifasi | Qisqa tavsif (himoya nuqtai nazaridan) |
|----------------|----------------------------------------|
| Zararli APK | Bank/to‘lov ilovasini taqlid qiluvchi o‘rnatiladigan paketlar |
| Telegram firibgarligi | Soxta ish, lotereya, investitsiya takliflari |
| Fishing sahifalar | Davlat portali yoki to‘lov shlyuzini taqlid |
| Ijtimoiy muhandislik qo‘ng‘iroqlari | «Qo‘llab-quvvatlash» niqobida kod/karta so‘rash |
| QR to‘lov firibgarligi | Noto‘g‘ri manzilga yo‘naltiruvchi QR |

Ko‘pchilik foydalanuvchi texnik bilimga ega emas; hujum **sodir bo‘lishidan oldin** ogohlantiruvchi vosita yetishmaydi.

### 1.2.3 Missiya

**Apex missiya:** oddiy foydalanuvchilarni kundalik himoya qilish bilan birga, kiberhujum tayyorlayotgan/amalga oshirayotgan/rejalashtirayotgan threat actorlarni erta aniqlash, real-time kuzatish, infratuzilma attribution (qonuniy korrelyatsiya), kampaniyalarni **himoya choralar**i bilan to‘xtatish va milliy intellekt ta’minlash.

### 1.2.4 Asosiy printsip (butun loyiha)

> Faqat defensive hunting, intelligence va automated **himoya** response. Offensive capability, exploit, C2-as-weapon, payload, weaponization — yo‘q. Qonuniy, rozilik asosida, faqat himoya.

### Threat Hunting & Actor Disruption Strategy (majburiy)

Disruption = blok/karantin/DNS deny/CERT intel. Hack-back yo‘q. Talablar: `srs/09` (Apex), `srs/08`, `srs/07`.

### 1.2.5 Mahsulot chegaralari

| Nima KIRADI | Nima KIRMAYDI |
|-------------|----------------|
| URL/fayl/QR reputatsiya tekshiruvi | Offensive security tooling |
| SMS/Telegram scam **aniqlash** (ruxsat doirasida) | Shaxsiy chatlarni o‘qish (Telegram private) |
| On-device SMS tahlili | SMS xom matnini cloudga yuborish |
| Windows EDR-uslubidagi monitoring | Androidda to‘liq process/registry monitoring |
| Web: tekshiruv + ta’lim + panel | Webda OS-darajasida monitoring |
| Deepfake: faqat rozilik bilan yuklangan audio | Jonli qo‘ng‘iroqni yashirincha yozib olish |
| Threat feed sync (ochiq + litsenziyalangan) | Threat feedlarni qayta sotish (ToS buzilishi) |

---

## 1.3 Ta'riflar, qisqartmalar va qoidalar

### 1.3.1 Qisqartmalar

| Qisqartma | Ma’nosi |
|-----------|---------|
| SRS | Software Requirements Specification |
| SDD | Software Design Document |
| EDR | Endpoint Detection and Response (himoya monitoring uslubi) |
| TI | Threat Intelligence |
| IOC | Indicator of Compromise (hash, domen, URL va h.k.) |
| MITRE ATT&CK | Tahdid taktikalarini tasniflash freymvorki |
| YARA | Fayl/xotira namunalarini qoida asosida aniqlash |
| Sigma | Log hodisalarini qoida asosida aniqlash |
| PII | Personally Identifiable Information |
| TLS | Transport Layer Security |
| JWT | JSON Web Token |
| OAuth2 | OAuth 2.0 autentifikatsiya freymvorki |
| TFLite | TensorFlow Lite (on-device ML) |
| VPN Service | Android VpnService (DNS/filtr uchun, VPN marketing emas) |
| UZCERT | O‘zbekiston CERT / kiberxavfsizlik ogohlantirish manbalari |
| FP / FN | False Positive / False Negative |
| WCAG | Web Content Accessibility Guidelines |
| k-anonymity | Parol tekshiruvida maxfiylik usuli (hash prefiks) |

### 1.3.2 Asosiy atamalar

| Atama | Ta’rif |
|-------|--------|
| Risk score | 0–100 oralig‘idagi xavf bahosi + tushuntirish |
| Local-first | Avval qurilmada ishlash; cloud faqat kerak bo‘lganda |
| Trust boundary | Ma’lumot ishonch zonasidan chiqadigan chegarasi |
| Consent record | Foydalanuvchi roziligining auditlanadigan yozuvi |
| Delta-update | Threat DB / qoidalarning faqat o‘zgargan qismini yangilash |
| Safe browser | Ilova ichidagi xavfsiz brauzer (overlay emas) |
| Honeypot file | Ransomware monitoring uchun nazorat fayli (himoya maqsadida) |

### 1.3.3 Hujjat yozish qoidalari

1. Talablar: `FR-xxx` (funksional), `NFR-xxx` (nofunksional).
2. Prioritet: `P0` (MVP majburiy), `P1` (V2), `P2` (V3+).
3. Platforma teglari: `[A]` Android, `[W]` Windows, `[Web]`, `[BE]` Backend.
4. Noaniqlik: taxmin qilinmaydi — `assumptions-and-open-questions.md` ga yoziladi.
5. Himoya-only: har qanday «hujum qanday ishlaydi» tavsifi o‘rniga «qanday aniqlanadi/bloklanadi» yoziladi.

---

## 1.4 Havolalar (References)

| ID | Manba | Izoh |
|----|-------|------|
| REF-01 | IEEE 830-1998 | SRS tuzilishi |
| REF-02 | O‘zR «Shaxsga doir ma’lumotlar to‘g‘risida»gi qonun | Maxfiylik muvofiqligi |
| REF-03 | Google Play Restricted Permissions | SMS/Accessibility siyosati |
| REF-04 | MITRE ATT&CK | Dashboard tasnifi |
| REF-05 | WCAG 2.1 AA | Accessibility |
| REF-06 | OAuth 2.0 / RFC 6749, JWT RFC 7519 | Auth |
| REF-07 | TLS 1.3 | Transport xavfsizligi |
| REF-08 | UZCERT / Kiberxavfsizlik markazi ogohlantirishlari | Mahalliy TI (integratsiya shartlari ochiq) |

---

## 1.5 Hujjat tuzilishi

1. **SRS 01** — Kirish (ushbu fayl)  
2. **SRS 02** — Umumiy tavsif  
3. **SRS 03** — Funksiya × Platforma matritsasi  
4. **SRS 04** — Funksional talablar  
5. **SRS 05** — Nofunksional talablar  
6. **SDD / Compliance / Operations** — dizayn va operatsiya (alohida papkalar)

---

## 1.6 Versiyalash siyosati

| Maydon | Qoida |
|--------|-------|
| Major | Mahsulot doirasi o‘zgarishi (yangi platforma, yangi P0 modul) |
| Minor | Yangi FR/NFR yoki diagramma qo‘shilishi |
| Patch | Tuzatish, aniqlashtirish, tarjima |
| Holat | `draft` → `review` → `approved` → `frozen-for-sprint` |
