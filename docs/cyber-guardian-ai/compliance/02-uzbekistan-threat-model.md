# Compliance 02 — O‘zbekiston tahdid modeli va mahalliylashtirish

**Hujjat:** Cyber Guardian AI  
**Bo‘lim:** Local Threat Model (Uzbekistan)  
**Versiya:** 1.0.0-draft  
**Rol:** SOC / Threat Intel Lead + Privacy Officer

---

## 11.1 Maqsad

Threat Intelligence va detection qoidalarini O‘zbekiston foydalanuvchilari duch keladigan **proaktiv** tahdid toifalariga ustuvor moslashtirish. Faqat aniqlash/ogohlantirish/bloklash.

---

## 11.2 Ustuvor tahdid toifalari

| ID | Toifa | Aniqlash yondashuvi (himoya) | Asosiy modullar |
|----|-------|------------------------------|-----------------|
| UZ-T1 | Soxta bank/to‘lov APK | Hash/TI, APK meta heuristika, YARA meta-qoidalar | File Reputation, YARA, Risk Scoring |
| UZ-T2 | Telegram ish/lotoreya/investitsiya firibgarligi | Ulashilgan matn lug‘ati + URL | Telegram Scam, URL |
| UZ-T3 | Davlat portali / to‘lov shlyuzi fishing | Domen spoof, punycode, brend token, TI | URL, Browser Protection |
| UZ-T4 | «Qo‘llab-quvvatlash» qo‘ng‘iroq SE | Foydalanuvchi yuklagan audio + yo‘riqnoma; SMS kod so‘rovi | Deepfake (V3), SMS (V2), ta’lim kontenti |
| UZ-T5 | QR to‘lov firibgarligi | QR decode + URL/payment qoidalar | QR Analysis |
| UZ-T6 | Favqulodda/xavfsizlik ogohlantirishi niqobidagi soxta saytlar | Urgency + official brand spoof qoidalari | URL, Browser, TI |

---

## 11.3 MITRE mapping (himoya tasnifi)

| Toifa | Tipik ATT&CK teglari (dashboard) |
|-------|----------------------------------|
| UZ-T1 | T1204 (User Execution) — aniqlash konteksti |
| UZ-T2/T3/T5/T6 | T1566 (Phishing) |
| UZ-T4 | T1566 / Social Engineering teglari (ichki) |

Eslatma: mapping — tasniflash; hujum bosqichlarini o‘rgatish emas.

---

## 11.4 Mahalliy threat feed

| Manba | Holat | Izoh |
|-------|-------|------|
| UZCERT ogohlantirishlari | Tavsiya etiladi | API/import formati AQ-017 |
| Kiberxavfsizlik markazi | Tavsiya etiladi | Rasmiy kanal kelishuvi |
| Ichki foydalanuvchi hisobotlari | P0 | FR-043 → analyst queue |
| Ochiq global IOC | P0 | ToS inventar |

**Pipeline:** manba → normalizatsiya → `license_status` → imzolangan delta → client.

---

## 11.5 Lokalizatsiya (uz / ru / en)

### 11.5.1 Talab

- Interfeys **to‘liq parallel** uch tilda (FR-101).  
- Faqat mashina tarjimasi yetarli emas — **madaniy kontekstli misollar**.

### 11.5.2 Misollar (ogohlantirish matnlari)

| Til | Namuna (UZ-T3) |
|-----|----------------|
| uz | «Bu sahifa my.gov.uz ni taqlid qilayotgandek. Parolingizni kiritmang.» |
| ru | «Эта страница похожа на подделку my.gov.uz. Не вводите пароль.» |
| en | «This page appears to mimic my.gov.uz. Do not enter your password.» |

| Til | Namuna (UZ-T2) |
|-----|----------------|
| uz | «Telegramdagi “kafolatlangan daromad” odatda firibgarlik. Pul o‘tkazmang.» |
| ru | «“Гарантированный доход” в Telegram часто мошенничество. Не переводите деньги.» |
| en | “Guaranteed income” messages on Telegram are often scams. Do not send money.» |

### 11.5.3 Ta’lim kontenti

Web/Android «Kibergigiyena» bo‘limi:

- Rasmiy bank ilovasini faqat Play/rasmiy manbadan o‘rnatish.  
- Qo‘llab-quvvatlash telefon orqali kod so‘ramasligini tushuntirish.  
- QR ni to‘lovdan oldin tekshirish odatini shakllantirish.

---

## 11.6 Detection qoida teglari (ichki)

```
tag: uz.fake_bank_apk
tag: uz.telegram_job_scam
tag: uz.gov_portal_phish
tag: uz.support_call_se
tag: uz.qr_payment_fraud
tag: uz.emergency_alert_phish
```

Har bir teg `reasons[].code` va MITRE map ga bog‘lanadi.

---

## 11.7 Muvaffaqiyat o‘lchovi (mahalliy)

| Metrika | Tavsif |
|---------|--------|
| UZ-T* coverage | Gold setda har toifa uchun aniqlash darajasi |
| Localization QA | Uch tilda kritik ogohlantirishlar review |
| Feed freshness | UZCERT import kechikishi (kelishuvga qarab) |
