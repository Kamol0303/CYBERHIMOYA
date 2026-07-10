# SRS 03 — Funksiyalar × Platforma matritsasi

**Hujjat:** Cyber Guardian AI SRS  
**Bo‘lim:** 3 — Feature × Platform Matrix (majburiy birinchi ishlab chiqiladigan hujjat)  
**Versiya:** 1.0.0-draft  
**Rol:** Security Architect + Mobile + Windows + Web leads

**Belgilar:**  
✅ To‘liq qo‘llab-quvvatlanadi  
⚠️ Cheklangan / qisman  
❌ Imkonsiz yoki ma’nosiz  
N/A Platformaga tegishli emas  

---

## 3.1 Asosiy matritsa

| # | Funksiya | Android | Windows | Web | Cheklov / izoh |
|---|----------|:-------:|:-------:|:---:|----------------|
| 1 | Threat Intelligence integratsiyasi | ✅ | ✅ | ✅ | Markaziy cloud feed; clientlar delta-sync |
| 2 | Risk Scoring algoritmi | ✅ | ✅ | ✅ | Umumiy backend model; clientda engil cache |
| 3 | Behavior Analysis Engine | ✅ | ✅ | ⚠️ | Webda faqat sessiya/extension darajasida |
| 4 | URL Reputation Engine | ✅ | ✅ | ✅ | Local cache + cloud lookup |
| 5 | SMS Scam Detection | ✅ | ❌ | ❌ | Faqat Android SMS API; xom matn cloudga yo‘q |
| 6 | Telegram Scam Detection | ✅ | ✅ | ✅ | Faqat forward/bot/ulashilgan kontent; shaxsiy chat o‘qilmaydi |
| 7 | QR Code Analysis | ✅ | ✅ | ✅ | Kamera / webcam / rasm yuklash |
| 8 | Deepfake Voice Detection | ✅ | ✅ | ✅ | Faqat rozilik bilan yuklangan audio; jonli yozib olish yo‘q |
| 9 | Wi-Fi Security Analyzer | ✅ | ✅ | ❌ | Brauzer tarmoq qatlamiga kira olmaydi |
| 10 | Browser Protection | ⚠️ | ✅ | ✅ | Android: overlay emas, xavfsiz in-app browser; W/Web: extension |
| 11 | Password Health Checker | ✅ | ✅ | ✅ | k-anonymity; parol serverga ochiq yuborilmaydi |
| 12 | Email Breach Checker | ✅ | ✅ | ✅ | Hash/normalizatsiya + tashqi breach API (ToS) |
| 13 | USB Protection | ❌ | ✅ | ❌ | Faqat Windows’da mantiqiy (device control) |
| 14 | Ransomware Monitoring | ⚠️ | ✅ | ❌ | Android sandbox tufayli cheklangan; W: honeypot+entropiya |
| 15 | File Reputation | ✅ | ✅ | ✅ | Web: yuklab tekshirish rejimi |
| 16 | Process Monitoring | ❌ | ✅ | ❌ | OS 3-tomon ilovaga Android/Webda ruxsat bermaydi |
| 17 | Registry Monitoring | N/A | ✅ | N/A | Windows-only tushuncha |
| 18 | Browser Extension Analyzer | N/A | ✅ | ✅ | Bitta umumiy extension kod bazasi |
| 19 | Network Monitoring | ✅ | ✅ | ⚠️ | A: VpnService/DNS; W: driver/ETW; Web: joriy sahifa |
| 20 | DNS Security | ✅ | ✅ | ✅ | VpnService / system DNS hook / extension |
| 21 | YARA Rule Engine | ✅ | ✅ | ❌ | Web UI orqali backend file-upload skanerida ishlaydi |
| 22 | Sigma Rule Engine | ❌ | ✅ | N/A | Windows agent + backend threat pipeline |
| 23 | MITRE ATT&CK Mapping | ✅ | ✅ | ✅ | Alohida engine emas — dashboard tasnifi |
| 24 | Advanced Threat Actor Fingerprinting | ✅ | ✅ | ✅ | Behavior + infrastructure + code similarity |
| 25 | Campaign Correlation Engine | ✅ | ✅ | ✅ | Ko‘p hodisa bog‘lanishi |
| 26 | Automated TTP Mapping & Attribution | ⚠️ | ✅ | ✅ | MITRE + custom UZ TTP base |
| 27 | Suspicious Infrastructure Detection (C2/phishing kit/scam panel) | ✅ | ✅ | ✅ | Domain, IP, ASN, certificate — aniqlash |
| 28 | Memory & Process Ancestry Analysis | ❌ | ✅ | ❌ | Windows killer feature (detection-only) |
| 29 | Cross-platform IOC Sweeping | ✅ | ✅ | ✅ | Real-time sweep engine |
| 30 | Threat Actor Persona & Group Tracking | ❌ | ✅ | ✅ | Qonuniy OSINT; dark web — AQ-030 |
| 31 | Threat Hunting Pipeline | ⚠️ | ⚠️ | ✅ | Real-time + scheduled (BE) |
| 32 | Actor Knowledge Graph / TAKB | ❌ | ❌ | ✅ | Neo4j yoki ekvivalent |
| 33 | Intelligence Fusion Engine | ❌ | ❌ | ✅ | OSINT + feeds + telemetry |
| 34 | Automated Playbook Engine (defensive) | ⚠️ | ✅ | ✅ | Blok/karantin/xabar; hack-back yo‘q |
| 35 | Attacker Intent / LOLBin-Injection Detection | ⚠️ | ✅ | ⚠️ | Windows IOA; exploit qo‘llanma yo‘q |
| 36 | Predictive Threat Actor Behavior Modeling | ⚠️ | ⚠️ | ✅ | ML forecast; client hint |
| 37 | Automated Infrastructure Take-down Intelligence | ⚠️ | ⚠️ | ✅ | Organlarga IOC paket; o‘zimiz take-down yo‘q |
| 38 | Deep Memory & Behavioral Forensics | ❌ | ✅ | ⚠️ | W agent; Web case UI |
| 39 | Graph-based Relationship Analysis | ⚠️ | ⚠️ | ✅ | actor–tool–victimPattern–campaign |
| 40 | Multi-Language Scam & SE (uz/ru/en + slang) | ✅ | ✅ | ✅ | + ixtiyoriy RU/CN pattern lib |
| 41 | Live Phishing Kit & Scam Panel Hunting | ✅ | ✅ | ✅ | Detection only |
| 42 | Zero-Day Behavior Anomaly Detection | ⚠️ | ✅ | ⚠️ | Signature’siz; W kuchli |

> **Apex #36–42** — `srs/09-apex-edition-requirements.md`. Killer #24–35 saqlanadi.

---

## 3.2 Har bir funksiya uchun asoslash

### 1. Threat Intelligence integratsiyasi — ✅✅✅

Markaziy **Threat Intel Service** tashqi/ichki feedlarni normalizatsiya qiladi (URL, domen, hash, kampaniya teglari). Clientlar `/v1/threat-feed/sync` orqali imzolangan delta oladi. Web ham xuddi shu feeddan foydalanadi (skan vaqtida).

### 2. Risk Scoring — ✅✅✅

Yagona scoring modeli backendda; clientlar offline uchun engil heuristika + oxirgi model versiyasini cache qiladi. Natija: `score 0–100` + `reasons[]`.

### 3. Behavior Analysis — ✅✅⚠️

- **Android:** ilova ichidagi hodisalar (ruxsat o‘zgarishi, shubhali intent, DNS bloklari) — OS cheklovi ichida.  
- **Windows:** jarayon daraxti, registry, tarmoq bog‘lanishlari.  
- **Web:** faqat brauzer sessiyasi / extension hodisalari; OS behavior yo‘q.

### 4. URL Reputation — ✅✅✅

Barcha platformalarda bir xil API: local bloom/cache → cloud reputation → risk score.

### 5. SMS Scam Detection — ✅❌❌

Faqat Androidda `RECEIVE_SMS` / `READ_SMS` (Play Restricted). Tahlil **faqat on-device**. Windows/Webda SMS API yo‘q.

### 6. Telegram Scam Detection — ✅✅✅

Shaxsiy chatlarga kirish **taqiqlangan**. Qo‘llab-quvvatlanadigan kirishlar:

- Foydalanuvchi forward qilgan xabar  
- Rasmiy bot orqali yuborilgan matn/URL  
- «Shubhali xabarni yuborish» oqimi (copy-paste)

### 7. QR Code Analysis — ✅✅✅

Dekodlash → URL/payload → URL Reputation + mahalliy to‘lov firibgarligi qoidalari.

### 8. Deepfake Voice Detection — ✅✅✅

Faqat foydalanuvchi **aniq rozilik** berib yuklagan audio. Jonli qo‘ng‘iroqni fon rejimida yozib olish **YO‘Q** (qonuniy va Play siyosati).

### 9. Wi-Fi Security Analyzer — ✅✅❌

SSID/xavfsizlik turi/ochiq tarmoq ogohlantirishi — OS API orqali. Brauzer buni ko‘ra olmaydi.

### 10. Browser Protection — ⚠️✅✅

- **Android:** tizim-keng overlay **ishlatilmaydi**; xavfsiz in-app browser + intent intercept (mumkin bo‘lgan darajada).  
- **Windows/Web:** umumiy browser extension (Chrome/Edge/Firefox — AQ-008).

### 11. Password Health Checker — ✅✅✅

Mahalliy kuchlilik + k-anonymity range query (masalan, HIBP Pwned Passwords usuli). Ochiq parol serverga ketmaydi.

### 12. Email Breach Checker — ✅✅✅

Email normalizatsiya + tashqi breach API. Natija: topilgan/topilmagan + tavsiyalar. Marketing maqsadida email sotilmaydi.

### 13. USB Protection — ❌✅❌

Windows: yangi USB qurilma, avto-run o‘xshash xatti-harakatlar, siyosat (ruxsat/blok). Android/Webda ekvivalent yo‘q (yoki ma’nosiz).

### 14. Ransomware Monitoring — ⚠️✅❌

- **Windows:** honeypot fayllar + mass-encrypt entropiya/heuristika + jarayon bog‘lash.  
- **Android:** sandbox tufayli cheklangan (faqat o‘z app storage / MediaStore doirasida ogohlantirish).  
- **Web:** imkonsiz.

### 15. File Reputation — ✅✅✅

Hash (SHA-256) + TI lookup + (W/A) YARA. Web: foydalanuvchi yuklagan fayl backend skanerida.

### 16. Process Monitoring — ❌✅❌

Faqat Windows agent (yuqori imtiyoz). Android/Web OS buni 3-tomon ilovaga bermaydi.

### 17. Registry Monitoring — N/A ✅ N/A

Faqat Windows.

### 18. Browser Extension Analyzer — N/A ✅✅

O‘rnatilgan kengaytmalar ro‘yxati, ruxsatlar, noma’lum manba ogohlantirishi. Android brauzerida cheklangan; asosan desktop extension + Web boshqaruv.

### 19. Network Monitoring — ✅✅⚠️

- A: VpnService asosida DNS/filtr (foydalanuvchiga tushuntirilgan).  
- W: tarmoq ulanishlari monitoring.  
- Web: faqat joriy sahifa / extension ko‘radigan so‘rovlar.

### 20. DNS Security — ✅✅✅

Zararli domenlarni bloklash/ogohlantirish. Webda extension DNS/host tekshiruvi orqali.

### 21. YARA Rule Engine — ✅✅❌ (Web UI → BE ✅)

Clientda (A/W) local engine; Web sahifasida fayl yuklash → **backend** YARA. Brauzerda native YARA yo‘q.

### 22. Sigma Rule Engine — ❌✅ N/A

Windows log/ETW hodisalari + backend pipeline. Androidda Sigma ma’nosiz; Webda N/A (lekin analyst UI orqali qoidalarni boshqarish mumkin).

### 23. MITRE ATT&CK Mapping — ✅✅✅

Aniqlangan hodisaga tactic/technique teglari qo‘yish — alohida ML engine emas, tasniflash qatlami.

### 24. Advanced Threat Actor Fingerprinting — ✅✅✅

Behavior + infrastructure + code/APK similarity → fingerprint. Doxing emas.

### 25. Campaign Correlation Engine — ✅✅✅

Ko‘p hodisani kampaniyaga bog‘lash (graph).

### 26. Automated TTP Mapping & Attribution — ⚠️✅✅

MITRE + `uz_ttp_*`. Androidda cheklangan IOA.

### 27. Suspicious Infrastructure Detection — ✅✅✅

Domain/IP/ASN/cert orqali C2/phishing/scam panel **ehtimolini aniqlash** (yaratish emas).

### 28. Memory & Process Ancestry — ❌✅❌

Windows EDR: ancestry + memory anomaly indicators. Detection-only.

### 29. Cross-platform IOC Sweeping — ✅✅✅

Imzolangan IOC bo‘yicha real-time/scheduled sweep.

### 30. Threat Actor Persona & Group Tracking — ❌✅✅

Qonuniy OSINT; Web/Windows analyst. Androidda to‘liq persona UI yo‘q.

### 31–34. Pipeline / Graph / Fusion / Playbooks

BE markaziy; playbook faqat defensive.

### 35. Intent / LOLBin-Injection Detection — ⚠️✅⚠️

Windows IOA; «qanday qilish» yo‘q.

### 36–42. Apex kengaytmalar

Predictive modeling, take-down **intelligence** (organlarga), memory forensics, graph relationships, multi-lang SE, live panel hunting, zero-day anomaly — batafsil `srs/09`. Disruption faqat defensive.

> Scam classifier, deepfake, APK similarity — `srs/06`, `sdd/04b`/`04c`.

---

## 3.3 Cross-cutting funksiyalar

| Funksiya | Android | Windows | Web | Izoh |
|----------|:-------:|:-------:|:---:|------|
| Security Dashboard | ✅ | ✅ | ✅ | Platformaga mos widgetlar |
| Notification tizimi | ✅ | ✅ | ✅ | info/warning/critical |
| Log tizimi | ✅ | ✅ | ⚠️ | Web: server audit + client session |
| Audit tizimi | ⚠️ | ✅ | ✅ | Admin asosan Web |
| Ko‘p tillilik (uz/ru/en) | ✅ | ✅ | ✅ | Madaniy kontekstli misollar |
| Accessibility | ✅ | ✅ | ✅ | WCAG 2.1 AA |
| Offline rejim | ✅ | ✅ | ⚠️ | Web: oxirgi natijalar |

---

## 3.4 MVP (V1) kesimi

V1 da **P0** bo‘lganlar (barcha 3 platformada, imkon qadar):

| # | Funksiya | V1 holati |
|---|----------|-----------|
| 1 | Threat Intelligence | P0 — asosiy IOC sync |
| 2 | Risk Scoring | P0 — qoida+ML engil |
| 4 | URL Reputation | P0 |
| 7 | QR Analysis | P0 |
| 11 | Password Health | P0 |
| 12 | Email Breach | P0 |
| 15 | File Reputation | P0 (hash+TI; YARA V2/V3) |
| 23 | MITRE Mapping | P0 — oddiy teglar |
| 24 | Universal Scam (qisman) | P0 — payment/gov/emergency |
| — | Dashboard / Notification / i18n | P0 |

V2/V3: `operations/03-roadmap.md`.

---

## 3.5 Talab bog‘lanishi

Har bir matritsa qatori `FR-xxx` ga bog‘lanadi (`04-functional-requirements.md`). Platforma imkonsizligi `NFR` yoki cheklov sifatida qayd etiladi, «keyinroq qo‘shamiz» deb yashirilmaydi.
