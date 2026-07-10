# Compliance 01 — Xavfsizlik, maxfiylik va muvofiqlik

**Hujjat:** Cyber Guardian AI  
**Bo‘lim:** Security, Privacy, Compliance  
**Versiya:** 1.0.0-draft  
**Rol:** Privacy & Compliance Officer + Mobile Security + Security Architect

---

## 10.1 Qat’iy Mudofaa Prinsipi

| Qoida | Majburiy |
|-------|----------|
| No active attack | Platforma hech qachon faol hujum qila olmaydi |
| Read-only monitoring | Barcha monitoring read-only / passive |
| Response | Faqat bloklash, ogohlantirish, lokal izolyatsiya, rasmiy organlarga xabar |
| Forbidden | C2, payload, exploit, active probing, hack-back |

> Ushbu modul/funksiya hech qanday holatda hujum yoki faol ekspluatatsiya imkoniyatini yaratmaydi — faqat aniqlash va mudofaa choralari bilan cheklanadi.

## 10.2 Android ruxsatlar siyosati (kritik)

### 10.1.1 Muammo chegarasi

Ba’zi zararli ilovalar keng ruxsat to‘plamini (SMS + Accessibility + yashirin overlay) suiiste’mol qiladi. Cyber Guardian AI **shu suiiste’mol naqshidan ongli farqlanadi**: minimal ruxsat, SMS faqat on-device, yashirin overlay yo‘q, ogohlantirish faqat ko‘rinadigan tizim UI orqali. Hujjatda suiiste’molni qanday amalga oshirish tavsiflanmaydi — faqat himoya chegarasi belgilanadi.

### 10.1.2 Qoidalar

| # | Qoida | Talab ID |
|---|-------|----------|
| 1 | Minimal ruxsat — har bir ruxsat uchun foydalanuvchiga ko‘rinadigan asos | FR-004, FR-103, NFR-026 |
| 2 | SMS tahlili **faqat qurilmada**; xom matn serverga **hech qachon** | FR-040, NFR-030 |
| 3 | Yashirin overlay **ishlatilmaydi** | FR-091, NFR-026 |
| 4 | Ogohlantirish — yopib bo‘lmaydigan **tizim bildirishnomasi** / in-app UI | FR-091 |
| 5 | Accessibility Service — faqat agar himoya uchun muqobil yo‘q va Play siyosatiga mos; default MVP da **o‘chiq/no-use** (AQ-014) | — |
| 6 | VpnService — faqat DNS/filtr; marketing «VPN» deb chalg‘itilmasin; consent | FR-060 |

### 10.1.3 Ruxsat → foyda jadvali (foydalanuvchi matni)

| Ruxsat | Foyda (ko‘rsatiladi) | Nima qilinMAYDI |
|--------|----------------------|-----------------|
| SMS | Firibgar SMS larni telefonda aniqlash | Matnni bulutga yuborish |
| Kamera | QR tekshirish | Fon rejimida kuzatish |
| Bildirishnoma | Xavf haqida ogohlantirish | Spam marketing |
| VpnService (ixtiyoriy) | Zararli domenlarni DNS da to‘xtatish | Trafikni sotish / yashirin tunnel marketing |
| Fayl (ixtiyoriy) | Tanlangan faylni tekshirish | Butun xotirani skanlash (keraksiz) |

### 10.1.4 Google Play Restricted Permissions

**Reja:**

1. Play Console da Restricted Permissions Declaration.  
2. Namoyish videosi: onboarding → SMS consent → scam SMS simulyatsiyasi → **on-device** ogohlantirish → sozlamalarda o‘chirish.  
3. Privacy Policy URL (uz/ru/en).  
4. Data safety form: SMS processed on-device; not shared.

---

## 10.2 Ma’lumotlar maxfiyligi

### 10.2.1 O‘zbekiston qonunchiligi

O‘zR «Shaxsga doir ma’lumotlar to‘g‘risida»gi qonuniga muvofiqlik:

| Printsip | Amal |
|----------|------|
| Qonuniylik | Privacy Policy + consent |
| Maqsad cheklovi | Faqat himoya xizmati |
| Minimallashtirish | SMS cloudga yo‘q; hash afzal |
| Saqlash muddati | NFR-040…043 |
| Subyekt huquqlari | Ko‘rish/o‘chirish (FR-005) |
| Xavfsizlik | TLS 1.3, AES-256 at-rest |

### 10.2.2 Deepfake / ovoz

- Aniq rozilik oqimi (FR-042).  
- Faqat foydalanuvchi yuklagan audio.  
- Jonli qo‘ng‘iroqni yashirincha yozib olish — **YO‘Q**.  
- Qisqa retention (AQ-013).

### 10.2.3 Uchinchi tomon

- PII/telemetry **sotilmaydi** (NFR-033).  
- Breach/TI provayderlar — ToS va DPA (AQ-015).

### 10.2.4 Shifrlash standartlari

| Qatlam | Standart |
|--------|----------|
| Transport | TLS 1.3 |
| At-rest PII | AES-256-GCM + KMS |
| Qurilma | Android Keystore / Windows DPAPI |
| Yangilanish | ed25519 (yoki ekvivalent) imzo |

---

## 10.3 Mas’uliyatli oshkor qilish (Responsible Disclosure)

Agar tahlil jarayonida **boshqa tizimda** zaiflik/xavf ko‘rinsa (masalan, foydalanuvchi yuborgan sahifa orqali):

| Qadam | Muddat | Amal |
|-------|--------|------|
| 1. Ichki qayd | 24 soat | Severity baholash; exploit yo‘riqnomasi yozilmaydi |
| 2. Vendor/egaga xabar | 72 soat (imkon qadar) | Maxfiy kanal; minimal tasdiqlovchi ma’lumot |
| 3. Muvofiqlashtirilgan oshkor | Vendor bilan kelishilgan muddat | Ommaviy blog — faqat himoya maslahati |
| 4. Foydalanuvchi | Darhol | Faqat o‘z xavfini ogohlantirish |

**Ichki:** `security@` manzili (AQ-016), PGP ixtiyoriy.  
**Tashqi tadqiqotchilar** uchun alohida policy sahifasi (Web).

---

## 10.4 Threat feed litsenziyalash

| Talab | Tavsif |
|-------|--------|
| Inventar | Har bir `ThreatFeedSource` uchun ToS/litsenziya holati |
| `license_status` | `ok` / `review` / `blocked` |
| Qayta tarqatish | Client cache — shartnoma ruxsat bersa; qayta sotish yo‘q |
| Attribution | Kerak bo‘lsa UI/Docs da manba |
| Tekshiruv | Huquqiy review har yangi manba oldidan |

Namuna manbalar (integratsiya sharti ochiq): ochiq URL reputation ro‘yxatlari, UZCERT ogohlantirishlari, breach API.

---

## 10.5 Windows agent xavfsizligi

- Code signing majburiy (NFR-027).  
- Least privilege qayerda mumkin; admin kerak bo‘lsa onboarding da tushuntirish.  
- Self-protection: agent o‘chirishga urinishda ogohlantirish (foydalanuvchi paroli bilan).  
- Exploit/offensive tooling agentga kiritilmaydi.

---

## 10.6 Web maxfiyligi

- Mehmon skan: IP asosida rate limit; uzoq muddatli profil yaratilmaydi.  
- Extension: minimal ruxsat (`<all_urls>` faqat kerak bo‘lsa va store review uchun asos).  
- CSP, secure cookies, no third-party tracker (marketing pixel default yo‘q).

## 10.7 Threat Hunting maxfiyligi (Threat Hunter Edition)

| Qoida | Tavsif |
|-------|--------|
| Anonimlashtirish | Hunting ma’lumotlari faqat anonim/pseudonym meta (FR-209) |
| Rozilik | Hunting telemetry opt-in; rad etilsa local himoya ishlayveradi |
| Actor ma’lumoti | Potensial actor/cluster haqidagi batafsil ma’lumot **faqat** rasmiy organlarga responsible disclosure orqali (FR-210); ommaviy doxing yo‘q |
| TAKB | Analyst RBAC + audit; oddiy foydalanuvchiga to‘liq ochilmaydi |
| Taqiqlangan | Hack-back, ruxsatsiz kuzatuv, exploit saqlash |

## 10.8 Killer Edition etika (kuchaytirilgan)

| Qoida | Majburiy amal |
|-------|----------------|
| Hunting asosi | Faqat foydalanuvchi qurilmasi yoki **rozilik** berilgan ma’lumot |
| Actor ma’lumoti | **Faqat** UZCERT, Milliy Kiberxavfsizlik Markazi yoki tegishli organlarga responsible disclosure |
| Sotish | Hech qanday hunting/PII ma’lumot uchinchi shaxslarga sotilmaydi |
| Playbook | Faqat defensive action; offensive CI da blok |
| OSINT | Ochiq/qonuniy manbalar; noqonuniy kirish yo‘q |
| Weaponization | Kod bazasi va hujjatlarda taqiqlangan |

## 10.9 Apex etika va Ethical AI

| Qoida | Amal |
|-------|------|
| Rozilik | Har qanday hunting — foydalanuvchi roziligi |
| Disclosure | Actor ma’lumoti faqat UZCERT, Milliy Kiberxavfsizlik Markazi va tegishli organlar |
| Sotish | Yo‘q |
| Audit | Full immutable trail (FR-411) |
| Explainability | Score/attribution uchun majburiy |
| Bias | uz/ru/en SE detektorlarida monitoring (NFR-310) |
| Take-down | Faqat intelligence paketi; ijro — organlar |
| Autonomous defense (V5) | Faqat himoya siyosatlari; human oversight |

### Threat Hunting & Actor Disruption Strategy (majburiy)

Apex «de-anonimizatsiya» = infratuzilma/kampaniya attribution; fuqarolarni noqonuniy doxing qilish emas.
