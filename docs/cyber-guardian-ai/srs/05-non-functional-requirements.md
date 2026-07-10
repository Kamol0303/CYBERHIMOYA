# SRS 05 — Nofunksional talablar (Non-Functional Requirements)

**Hujjat:** Cyber Guardian AI SRS  
**Bo‘lim:** 5 — NFR  
**Versiya:** 1.0.0-draft  
**Format:** `NFR-xxx`

---

## 5.1 Ishlash tezligi (Performance)

### NFR-001 — URL skan kechikishi
- Cloud online: p95 < **2.0 s** (tarmoq normal).
- Local cache hit: p95 < **200 ms**.

### NFR-002 — Fayl hash + TI
- ≤ 50 MB fayl: hash clientda; TI lookup p95 < **3.0 s**.
- Web upload limitti: **25 MB** (MVP; AQ-004).

### NFR-003 — On-device model resursi
- Android SMS/URL engil model: CPU o‘rtacha qo‘shimcha < **5%** 1 daqiqalik oynada; batareya ta’siri kuniga < **2%** (benchmark qurilmada).
- Model hajmi (SMS/URL): < **15 MB** (uncompressed on-disk).

### NFR-004 — Windows agent overhead
- Idle CPU < **3%**; RAM (agent) < **150 MB** tipik.
- Disk I/O monitoring: foydalanuvchi sezilarli sekinlashmasligi (benchmark stsenariy).

### NFR-005 — Dashboard ochilishi
- Asosiy dashboard cold start: Android < **2.5 s**, Windows < **2.0 s**, Web FCP < **2.0 s** (3G emas, broadband).

---

## 5.2 Ishonchlilik (Reliability)

### NFR-010 — Offline degradatsiya
- Tarmoq yo‘q: A/W local skan + cache ishlaydi; navbatga qo‘yilgan sync qayta urinadi.
- Web: oxirgi natijalar; yangi skan xato xabari aniq.

### NFR-011 — Sync yaxlitligi
- Threat delta imzo tekshiruvisiz qo‘llanilmaydi.
- Yarim yuklangan delta rollback.

### NFR-012 — Mavjudlik (backend)
- API oylik uptime maqsadi: **99.5%** (MVP); rejalashtirilgan texnik ishlar bundan mustasno.
- Multi-AZ (AQ-005) — ochiq.

### NFR-013 — Xato xabarlari
- Foydalanuvchiga texnik stack trace ko‘rsatilmaydi; lokalizatsiyalangan xabar + qayta urinish.

---

## 5.3 Xavfsizlik (Security NFR)

### NFR-020 — Transport
- Barcha client↔server: **TLS 1.3**.
- Certificate pinning: Android/Windows (AQ-006 — pin ro‘yxati).

### NFR-021 — At-rest shifrlash
- PII maydonlar: **AES-256** (yoki cloud KMS ekvivalenti).
- Qurilmada sezgir cache: platforma keystore/DPAPI.

### NFR-022 — Auth
- OAuth2 + JWT; access token TTL qisqa; refresh rotatsiyasi.
- Brute-force: rate limit + lockout siyosati.

### NFR-023 — API rate limiting
- Mehmon: qat’iy kvota (masalan, 10 URL/soat/IP — sozlanadi).
- Autentifikatsiyalangan: tarif bo‘yicha.

### NFR-024 — Himoya-only
- Kod bazasida offensive modul, exploit PoC, «qanday buzish» hujjati bo‘lmasligi — PR checklist.

### NFR-025 — Sirlar
- API kalitlari, signing keylar CI secret store da; repoda yo‘q.

### NFR-026 — Android ruxsatlar
- Minimal ruxsat; SMS on-device; overlay yo‘q; Play declaration + demo video.

### NFR-027 — Supply chain
- Dependency scanning (SCA); imzolangan Windows binary; Play App Signing.

---

## 5.4 Maxfiylik (Privacy)

### NFR-030 — SMS xom matn
- Hech qachon serverga yuborilmaydi.

### NFR-031 — Parol
- Ochiq parol serverga yuborilmaydi; k-anonymity.

### NFR-032 — Audio
- Faqat consent + user upload; avtomatik call recording yo‘q.

### NFR-033 — Ma’lumot sotilmasligi
- PII/threat telemetry uchinchi tomonga sotilmaydi.

### NFR-034 — Maqsad cheklovi
- Yig‘ilgan meta faqat himoya sifatini oshirish va xavfsizlik uchun.

### NFR-035 — Consent audit
- Har bir rozilik `ConsentRecord` da; bekor qilish mumkin.

---

## 5.5 Ma’lumotlarni saqlash (Retention)

### NFR-040 — ScanResult / ThreatEvent
- Standart: **180 kun** (sozlanadi); keyin o‘chirish yoki anonim agregat.

### NFR-041 — Hisob o‘chirish
- So‘rovdan keyin PII **30 kun** ichida o‘chiriladi/anonimlashtiriladi (qonuniy saqlash bundan mustasno — audit).

### NFR-042 — AuditLog
- Admin audit: **365 kun** (o‘zgarmas).

### NFR-043 — Log (mahalliy)
- Qurilma loglari: PII’siz; aylanma hajm limitti (masalan, 50 MB).

---

## 5.6 Foydalanish qulayligi (Usability)

### NFR-050 — Ogohlantirish tili
- Qat’iy, aniq, CTA li; qo‘rqitish/dark pattern yo‘q.

### NFR-051 — Til
- uz/ru/en parallel; madaniy misollar.

### NFR-052 — Accessibility
- WCAG 2.1 AA.

### NFR-053 — Onboarding
- Har bir ruxsat uchun foyda tushuntiriladi; o‘tkazib yuborish mumkin (modul o‘chiq).

---

## 5.7 Moslashuvchanlik va qo‘llab-quvvatlash

### NFR-060 — API versiyalash
- `/v1/...`; breaking change → `/v2`.

### NFR-061 — Client orqaga moslik
- Backend kamida **N-1** client versiyasini qo‘llab-quvvatlaydi.

### NFR-062 — Qoida yangilanishi
- YARA/Sigma/IOC delta: kamida **kuniga 1** marta; kritik IOC — soatlik (imkon qadar).

### NFR-063 — Lokalizatsiya qo‘shish
- Yangi til: resource fayllar orqali; kod o‘zgarishisiz matn.

---

## 5.8 Test va sifat

### NFR-070 — Avtomatik test qamrovi
- Kritik backend: unit ≥ **70%** chiziq (MVP maqsad).
- Client critical paths: integration smoke majburiy.

### NFR-071 — Security testing
- SAST har PR; DAST staging da release oldidan.
- Dependency CVE: high/critical bloklovchi (istisno jarayoni bilan).

### NFR-072 — FP/FN benchmark
- URL to‘plamida FP < **2%**; kritis fishing FN < **5%** (belgilangan gold set; AQ-007).

### NFR-073 — Performance regressiya
- CI da asosiy skan benchmark; >20% yomonlashsa fail.

---

## 5.9 Operatsion

### NFR-080 — Observability
- Metrics, structured logs (PII’siz), tracing (gateway→service).

### NFR-081 — Incident response
- Critical production: on-call runbook (AQ-009).

### NFR-082 — Backup
- DB backup kuniga ≥1; restore drill chorakda.

### NFR-083 — Update imzo
- Threat DB, qoidalar, model paketlar: ed25519 yoki ekvivalent imzo.

---

## 5.10 Muvofiqlik

### NFR-090 — O‘zR PII qonuni
- Privacy policy, consent, erasure, maqsad cheklovi.

### NFR-091 — Play Restricted Permissions
- Declaration, demo video, faqat e’lon qilingan foyda.

### NFR-092 — Threat feed ToS
- Har bir manba litsenziyasi inventarizatsiya qilinadi.

### NFR-093 — Responsible disclosure
- Topilgan uchinchi tomon zaifligi: siyosat bo‘yicha xabar (`compliance/01`).
