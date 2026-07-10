# SDD 04 — AI / Detection modullari

**Hujjat:** Cyber Guardian AI SDD  
**Bo‘lim:** 4 — Detection Modules  
**Versiya:** 1.0.0-draft  
**Rol:** AI/ML Engineer + Malware Researcher + Windows/Mobile Security  
**Printsip:** Faqat aniqlash, ogohlantirish, bloklash — exploit/hujum qo‘llanmasi yo‘q

Har bir modul majburiy shablon bo‘yicha.

---

### Risk Scoring
- **Kirish ma’lumoti:** Boshqa modullardan kelgan feature vektorlari (URL score, TI hit soni, behavior score, fayl hit, qoida ID lari, platforma konteksti). Xom SMS/parol kelmaydi.
- **Feature extraction:** Raqamli agregatlar + kategorik teglar (`UZ_FAKE_PAYMENT`, `TI_DOMAIN_HIT`, `YARA_MATCH`); missing-value sentinel; model_version.
- **Model/heuristika turi:** Gradient boosting (masalan, LightGBM) + qoida asosidagi floor/ceiling (kritik TI hit → minimal score).
- **Chiqish:** risk score (0–100) + `reasons[]` (explainability) + `confidence` + ixtiyoriy MITRE teglari.
- **False positive kamaytirish strategiyasi:** allowlist (rasmiy bank/davlat domenlari), kalibratsiya, «unknown» zonasi (40–60), inson-analyst feedback loop (V2+).
- **Ma’lumot manbalari:** Ichki labeled skanlar, ochiq fishing to‘plamlari, mahalliy UZ kampaniya teglari (PII’siz).
- **On-device / Cloud:** Yakuniy score — cloud; offline engil heuristika — on-device.
- **Yangilanish chastotasi:** Model paketi haftalik yoki kerak bo‘lganda; qoida floor kunlik.

---

### Behavior Analysis Engine
- **Kirish ma’lumoti:** Qurilma hodisalari (W: process/network/registry signal meta; A: app-level events, DNS block events; Web: extension navigation/session events).
- **Feature extraction:** Vaqt oynasidagi hodisa chastotasi, nodir ruxsat o‘zgarishi, parent-child g‘ayrioddiylik skori (W), sessiyadagi takroriy phishing urinishlari (Web).
- **Model/heuristika turi:** Qoida + engil anomaly (isolation-style yoki thresholded counters); chuqur RL yo‘q (MVP).
- **Chiqish:** behavior_score (0–100) + tushuntirish («qisqa vaqt ichida ko‘p shubhali domen»).
- **False positive kamaytirish strategiyasi:** Ilova/jarayon allowlist, o‘rganish davri (3 kun baseline), faqat korrelyatsiyalangan ogohlantirish.
- **Ma’lumot manbalari:** Telemetriya meta (consent), ichki red-team himoya stsenariylari (defensive).
- **On-device / Cloud:** Signal yig‘ish on-device; og‘ir korrelyatsiya cloud (W agent online bo‘lsa).
- **Yangilanish chastotasi:** Qoidalar kunlik; baseline model oylik.

---

### URL Reputation Engine
- **Kirish ma’lumoti:** URL/domen (normalizatsiya qilingan); referrer/source (manual, QR, SMS-meta, extension).
- **Feature extraction:** Domen yoshi proxy (agar mavjud), TLD, punycode, yo‘l entropiyasi, brend spoof tokenlari (bank/gov UZ), TI hit, redirect zanjiri uzunligi (cloud fetch — ehtiyot).
- **Model/heuristika turi:** Bloom/cache IOC + gradient boosting + regex/heuristika qoidalari.
- **Chiqish:** url_score (0–100) + reasons + verdict.
- **False positive kamaytirish strategiyasi:** Rasmiy allowlist, homoglyph faqat yuqori confidence da, foydalanuvchi «noto‘g‘ri ogohlantirish» tugmasi.
- **Ma’lumot manbalari:** Threat feed IOC, UZCERT ogohlantirishlari, ichki hisobotlar.
- **On-device / Cloud:** Cache on-device; boyitish cloud.
- **Yangilanish chastotasi:** IOC delta kuniga ≥1; kritik soatlik.

---

### SMS Scam Detection
- **Kirish ma’lumoti:** Android SMS matni (faqat qurilmada), yuboruvchi raqam/shortcode, vaqt.
- **Feature extraction:** URL borligi, shoshilinchlik lug‘ati (uz/ru), pul/kod so‘rash naqshlari, qisqa havola, yuboruvchi reputatsiyasi (local).
- **Model/heuristika turi:** On-device TFLite matn klassifikatori + regex/heuristika.
- **Chiqish:** score (0–100) + reasons; critical da tizim notification.
- **False positive kamaytirish strategiyasi:** Bank rasmiy shortcode allowlist (foydalanuvchi tasdiqlagan), faqat URL yoki kod so‘rovi bo‘lsa yuqori score, til bo‘yicha alohida threshold.
- **Ma’lumot manbalari:** Sintetik/annotatsiya qilingan scam SMS (PII tozalangan), foydalanuvchi opt-in meta.
- **On-device / Cloud:** **Faqat on-device** (xom matn cloudga yo‘q).
- **Yangilanish chastotasi:** Model paketi 2 haftada; lug‘at/qoida haftalik (imzolangan).

---

### Telegram Scam Detection
- **Kirish ma’lumoti:** Foydalanuvchi forward/bot/paste qilgan matn yoki URL; shaxsiy chat o‘qilmaydi.
- **Feature extraction:** «ish taklifi», «lotoreya», «investitsiya», kafolatlangan foyda lug‘atlari; URL features; kontaktga yozish CTA naqshlari.
- **Model/heuristika turi:** Regex+heuristika + matn klassifikatori (on-device yoki cloud — matn foydalanuvchi ulashganda).
- **Chiqish:** score + reasons + tavsiya («havolani ochmang», «pul o‘tkazmang»).
- **False positive kamaytirish strategiyasi:** Rasmiy kanallar allowlist; faqat ulashilgan kontent; past confidence da «ehtiyot» emas «firibgar».
- **Ma’lumot manbalari:** Ommaviy scam namunalari, UZ mahalliy kampaniyalar, foydalanuvchi hisobotlari.
- **On-device / Cloud:** Matn — local yoki consent bilan cloud; URL — URL engine.
- **Yangilanish chastotasi:** Lug‘at haftalik; model oylik.

---

### QR Code Analysis
- **Kirish ma’lumoti:** Kamera kadr / yuklangan rasm / clipboard payload.
- **Feature extraction:** Decode turi (URL/text/payment), URL features, to‘lov maydonlari anomaliyasi (summa, receiver nomida brend spoof).
- **Model/heuristika turi:** QR decode (ZXing yoki ekvivalent) + URL Reputation + mahalliy to‘lov firibgarligi qoidalari.
- **Chiqish:** score + qr_type + reasons; to‘lov oldidan ogohlantirish.
- **False positive kamaytirish strategiyasi:** Rasmiy merchant allowlist; noaniq QR da «tekshirib bo‘lmadi» (false clean emas).
- **Ma’lumot manbalari:** Mahalliy QR scam hisobotlari, TI URL.
- **On-device / Cloud:** Decode on-device; reputation cloud.
- **Yangilanish chastotasi:** Qoidalar haftalik.

---

### Deepfake Voice Detection
- **Kirish ma’lumoti:** Foydalanuvchi **rozilik** bilan yuklagan audio fayl (qo‘ng‘iroq yozuvi ixtiyoriy yuklash — yashirin yozib olish yo‘q).
- **Feature extraction:** Spektral/artefakt featurelar, asr-transcript ixtiyoriy (consent), «qo‘llab-quvvatlash / karta / kod» lug‘ati transcript da.
- **Model/heuristika turi:** Cloud chuqur audio model + transcript heuristika; ixtiyoriy engil on-device prefilter.
- **Chiqish:** score (0–100) + «sintetik ehtimoli» tushuntirishi + ijtimoiy muhandislik matn hitlari.
- **False positive kamaytirish strategiyasi:** Past sifatli audio da «aniqlanmadi»; hech qachon yagona dalil sifatida sud/ayblov; FAQ tushuntirish.
- **Ma’lumot manbalari:** Ochiq deepfake korpuslar + sintetik UZ/RU ovozlar (litsenziya tekshiruvi).
- **On-device / Cloud:** Asosan cloud; audio retention qisqa.
- **Yangilanish chastotasi:** Model oylik; lug‘at haftalik.

---

### Wi-Fi Security Analyzer
- **Kirish ma’lumoti:** OS beradigan SSID, xavfsizlik turi (open/WPA2/…), signal (agar mavjud).
- **Feature extraction:** Open network flag, captive portal shubhasi (nom), «bank/airport» o‘xshash bait nomlar.
- **Model/heuristika turi:** Qoida asosidagi klassifikator (ML shart emas).
- **Chiqish:** score + «ochiq tarmoqda banking qilmang» tavsiyasi.
- **False positive kamaytirish strategiyasi:** Foydalanuvchi uy tarmog‘ini ishonchli deb belgilashi; faqat info/warning.
- **Ma’lumot manbalari:** Ichki qoidalar, mahalliy bait SSID ro‘yxati.
- **On-device / Cloud:** Faqat on-device; Webda yo‘q.
- **Yangilanish chastotasi:** Qoida oylik.

---

### Browser Protection
- **Kirish ma’lumoti:** Navigatsiya URL (extension) yoki in-app browser URL (Android); sahifa sarlavhasi (ixtiyoriy).
- **Feature extraction:** URL reputation features; brend spoof title; login formasi + shubhali domen korrelyatsiyasi (extension DOM — minimal, maxfiylik bilan).
- **Model/heuristika turi:** URL engine + sahifa heuristikasi; block/warn banner.
- **Chiqish:** score + on-page banner / block interstitial + reasons.
- **False positive kamaytirish strategiyasi:** «Davom etish» (warning da) audit bilan; allowlist; Androidda overlay yo‘q.
- **Ma’lumot manbalari:** TI, foydalanuvchi hisobotlari.
- **On-device / Cloud:** Tekshiruv local cache + cloud.
- **Yangilanish chastotasi:** IOC kunlik; extension qoida haftalik.

---

### Password Health Checker
- **Kirish ma’lumoti:** Foydalanuvchi kiritgan parol (faqat xotira/UI); hech qachon logga yozilmaydi.
- **Feature extraction:** Uzunlik, complexity, common-password hit (local list), k-anonymity hash prefiks (pwned API).
- **Model/heuristika turi:** Heuristika + remote k-anonymity range query.
- **Chiqish:** score/yoki holat: weak|pwned|ok + tushuntirish.
- **False positive kamaytirish strategiyasi:** «Pwned» faqat API tasdiqlasa; kuchlilik ogohlantirishi yumshoq til.
- **Ma’lumot manbalari:** Local top-N common passwords; HIBP yoki ekvivalent (ToS).
- **On-device / Cloud:** Strength on-device; pwned range — cloud.
- **Yangilanish chastotasi:** Common list oylik.

---

### Email Breach Checker
- **Kirish ma’lumoti:** Email manzili.
- **Feature extraction:** Normalizatsiya (lowercase, unicode); provider domeni.
- **Model/heuristika turi:** Tashqi breach API integratsiyasi (qoida emas).
- **Chiqish:** found true/false + breach meta + tavsiyalar; risk score ixtiyoriy (masalan, topilsa 60–80).
- **False positive kamaytirish strategiyasi:** API noaniqligida «tekshirib bo‘lmadi»; spam breach nomlarini filtrlash.
- **Ma’lumot manbalari:** Litsenziyalangan breach xizmati.
- **On-device / Cloud:** Cloud.
- **Yangilanish chastotasi:** Tashqi manba; lokal cache TTL 24 soat.

---

### USB Protection
- **Kirish ma’lumoti:** Windows USB qurilma ulanish hodisasi, qurilma sinfi, avto-ishga tushish urinishi signalı.
- **Feature extraction:** Qurilma turi, birinchi marta ko‘rilgan, siyosat holati, executable launch urinishi flag.
- **Model/heuristika turi:** Siyosat + qoida (ML shart emas).
- **Chiqish:** score/severity + foydalanuvchi so‘rovi (ruxsat/blok) + critical notification.
- **False positive kamaytirish strategiyasi:** Ishonchli qurilmalar ro‘yxati; klaviatura/sichqoncha default allow.
- **Ma’lumot manbalari:** Ichki siyosat, Windows xavfsizlik baselinelari.
- **On-device / Cloud:** On-device; meta ixtiyoriy cloud.
- **Yangilanish chastotasi:** Siyosat paket oylik.

---

### Ransomware Monitoring
- **Kirish ma’lumoti:** Honeypot fayl o‘zgarishlari, qisqa vaqtda ko‘p fayl yozish, entropiya o‘sishi, bog‘langan jarayon meta (Windows). Androidda cheklangan app-storage signal.
- **Feature extraction:** Vaqt birligida modify rate, entropiya delta, honeypot hit, jarayon imzo holati.
- **Model/heuristika turi:** Heuristika + threshold; ixtiyoriy engil klassifikator.
- **Chiqish:** critical score + jarayon nomi + «fayllarni saqlash/to‘xtatish» CTA (himoya yo‘riqnomasi).
- **False positive kamaytirish strategiyasi:** Backup/indexer allowlist; honeypot hit majburiy korrelyatsiya; test rejimi.
- **Ma’lumot manbalari:** Himoya stsenariy testlari, ochiq ransomware oilalari **aniqlash** belgilari (YARA) — exploit yo‘q.
- **On-device / Cloud:** Aniqlash on-device real-time; event meta cloud.
- **Yangilanish chastotasi:** Qoida/YARA haftalik.

---

### File Reputation
- **Kirish ma’lumoti:** Fayl hash (SHA-256), hajm, MIME/tur, ixtiyoriy YARA match, paket meta (APK package name — Android).
- **Feature extraction:** TI hash hit, APK ruxsat to‘plami anomaliyasi (A), imzo yo‘qligi (W), YARA hit.
- **Model/heuristika turi:** TI lookup + YARA + engil APK heuristika.
- **Chiqish:** score + verdict + reasons; «ochmang/o‘chirib tashlang» tavsiyasi.
- **False positive kamaytirish strategiyasi:** Imzolangan nashriyot allowlist; noma’lum fayl = unknown (clean deb yozmaslik).
- **Ma’lumot manbalari:** Threat feed hash, ichki APK namunalar (himoya lab), YARA qoidalar.
- **On-device / Cloud:** Hash local; TI/YARA local yoki cloud (Web upload).
- **Yangilanish chastotasi:** Hash IOC kunlik; YARA haftalik.

---

### Process / Registry / Network Monitoring (Windows)
- **Kirish ma’lumoti:** Jarayon yaratilishi, raqamli imzo holati, himoya qoidalari kuzatadigan registry o‘zgarishlari, tashqi ulanishlar (IP/domen).
- **Feature extraction:** Parent–child bog‘lanish anomaliyasi, imzosiz binar, kuzatuvdagi registry kalit o‘zgarishi, TI domen hit bilan korrelyatsiya.
- **Model/heuristika turi:** Sigma qoidalari + heuristika; EDR-uslubidagi **defensive** monitoring (faqat aniqlash/ogohlantirish/bloklash).
- **Chiqish:** ThreatEvent severity + MITRE teg + score; bloklash siyosati (foydalanuvchi/admin sozlamasi).
- **False positive kamaytirish strategiyasi:** Microsoft/ishonchli publisher allowlist, sigma tuning, quiet hours faqat info uchun.
- **Ma’lumot manbalari:** Sigma community (litsenziya), ichki himoya qoidalari, TI. Qoidalarda exploit yo‘riqnomasi bo‘lmaydi.
- **On-device / Cloud:** Monitoring on-device; qoida sync cloud; xotira dump cloudga default yo‘q.
- **Yangilanish chastotasi:** Sigma/IOC kunlik-haftalik.

---

### YARA / Sigma Rule Engine
- **Kirish ma’lumoti:** Fayl baytlari / meta (YARA); strukturalangan log hodisasi (Sigma→agent).
- **Feature extraction:** Qoida match metadata (rule id, tags, severity); fayl ofsetlari logda PII’siz.
- **Model/heuristika turi:** Aniq qoida dvigateli (YARA lib; Sigma compiler→agent query).
- **Chiqish:** match list + mapped score floor + explain (qoida tavsifi).
- **False positive kamaytirish strategiyasi:** Qoida staging, canary, FP ticket, imzo bilan faqat `active` qoidalar.
- **Ma’lumot manbalari:** Ichki qoidalar, ochiq litsenziyalangan to‘plamlar, UZ APK oilalari uchun meta-qoidalar.
- **On-device / Cloud:** A/W local engine; Web upload → backend YARA; Sigma asosan W + BE pipeline.
- **Yangilanish chastotasi:** Paket imzolangan holda haftalik; hotfix istalgan vaqt.

---

### MITRE ATT&CK avtomatik tasniflash
- **Kirish ma’lumoti:** ThreatEvent/ScanResult teglari, qoida `mitre` maydoni, kategoriya.
- **Feature extraction:** Mapping jadvali: `category|rule_id → tactic/technique`.
- **Model/heuristika turi:** Lug‘at/qoida asosida tasnif (alohida ML engine emas).
- **Chiqish:** `mitre_tags[]` (masalan, `T1566`) + dashboard filtri; **hujum qo‘llanmasi emas**.
- **False positive kamaytirish strategiyasi:** Faqat yuqori ishonchli map; noaniq → teg qo‘yilmasin.
- **Ma’lumot manbalari:** MITRE ATT&CK (iqtibos), ichki map jadvali.
- **On-device / Cloud:** Asosan cloud/backend; clientda ko‘rsatish.
- **Yangilanish chastotasi:** Map jadvali oylik yoki ATT&CK versiya chiqqanda.

---

## Modul × Roadmap

| Modul | V1 | V2 | V3 |
|-------|----|----|-----|
| Risk Scoring | ✅ | ✅ | ✅ |
| URL Reputation | ✅ | ✅ | ✅ |
| QR Analysis | ✅ | ✅ | ✅ |
| Password Health | ✅ | ✅ | ✅ |
| Email Breach | ✅ | ✅ | ✅ |
| File Reputation | ✅ hash/TI | +YARA | ✅ |
| MITRE mapping | ✅ oddiy | ✅ | ✅ |
| Universal Scam Classifier | ✅ qisman | ✅ to‘liq | ✅ |
| Money-Offer Bot Detector | — | ✅ | ✅ |
| SMS Scam | — | ✅ | ✅ |
| Telegram Scam | — | ✅ | ✅ |
| Campaign & Actor Attribution | — | ✅ kampaniya | ✅ actor cluster |
| Behavior | — | ✅ | ✅ |
| Browser Protection | ⚠️ asos | ✅ | ✅ |
| DNS / Wi-Fi | — | ✅ | ✅ |
| USB / Ransomware / Process | — | ✅ W | ✅ |
| YARA/Sigma | — | qisman | ✅ |
| Deepfake Voice | — | — | ✅ |
| Deepfake Face/Video | — | — | ✅ |

> Yangi modullar tavsifi: `srs/06-universal-scam-and-attribution.md` §6.
