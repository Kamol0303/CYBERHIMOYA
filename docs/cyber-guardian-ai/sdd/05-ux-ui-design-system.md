# SDD 05 — UX/UI va Frontend dizayn tizimi

**Hujjat:** Cyber Guardian AI SDD  
**Bo‘lim:** 5 — UX/UI Design System  
**Versiya:** 1.0.0-draft  
**Rol:** UX/UI Product Designer  
**Eslatma:** Mavjud brend tizimi yo‘q — yangi dizayn yo‘nalishi. Vahima uyg‘otmaydigan, tinch himoya estetikasi.

---

## 5.1 Dizayn printsiplari

1. **Bir kompozitsiya** — birinchi ekran «dashboard clutter» emas; holat + bitta asosiy CTA.
2. **Brend birinchi** — «Cyber Guardian AI» / mahalliy brend nomi hero-darajada (nav emas).
3. **Tinch xavf ranglari** — yashil/sariq/qizil, lekin pastel-tinch; neon/glow yo‘q.
4. **Dark pattern yo‘q** — ruxsat majburlash, soxta countdown, «hozir bloklanasiz» manipulyatsiyasi taqiqlanadi.
5. **Bir bo‘lim — bir ish**.
6. **Motion** — 2–3 maqsadli: holat o‘zgarishi, ogohlantirish paydo bo‘lishi, skan progress.

**Avoid (AI-klaster):** binafsha-indigo gradient, krem+#terracotta serif, broadsheet hairline layout.

---

## 5.2 Dizayn tokenlari

### 5.2.1 Rang palitrasi (CSS o‘zgaruvchilari)

```css
:root {
  /* Brand — deep teal / slate (tinch, texnik) */
  --brand-900: #0B3D3A;
  --brand-700: #14635D;
  --brand-500: #1F8A80;
  --brand-100: #D8F0ED;

  /* Surface — soft cool gray, flat emas: subtle gradient/noise */
  --bg-0: #F3F6F7;
  --bg-1: #E7EEF0;
  --ink-900: #142126;
  --ink-700: #3A4A52;
  --ink-500: #5C6E76;
  --line: #C9D5DA;

  /* Risk — tinch */
  --risk-safe: #2F7D4A;
  --risk-safe-bg: #E6F4EA;
  --risk-warn: #A67C2D;
  --risk-warn-bg: #F8F0DE;
  --risk-crit: #A33B3B;
  --risk-crit-bg: #F8E8E8;
  --focus: #1F8A80;
}
```

| Token | Qiymat | Ma’nosi |
|-------|--------|---------|
| `--brand-900` | `#0B3D3A` | Asosiy brend |
| `--brand-500` | `#1F8A80` | CTA |
| `--bg-0` | `#F3F6F7` → gradient `#EAF3F2` | Fon atmosferasi |
| `--ink-900` | `#142126` | Matn |
| `--risk-safe` | `#2F7D4A` / bg `#E6F4EA` | Xavfsiz |
| `--risk-warn` | `#A67C2D` / bg `#F8F0DE` | Ogohlantirish |
| `--risk-crit` | `#A33B3B` / bg `#F8E8E8` | Kritik |
| `--focus` | `#1F8A80` | Fokus halqasi |

**Dark mode:** fon `#0E1719`, sirt `#162226`, matn `#E7EEF0`; risk ranglari yorqinligi biroz oshiriladi, lekin neon emas.

### 5.2.2 Tipografiya

| Rol | Font | Izoh |
|-----|------|------|
| Display / brend | **Manrope** yoki **Sora** | Expressive, Inter emas |
| Body | **Source Sans 3** | O‘qilishi yuqori; uz/ru/en |
| Mono (hash) | **IBM Plex Mono** | Texnik qiymatlar |

O‘lchamlar: Display 32/40, H1 24, H2 20, Body 16, Caption 13. Katta shrift rejimi: +2–4 px scale.

### 5.2.3 Ikon tizimi

- Chiziqli 1.5px, 24 grid; lucide-uslubidagi custom set.
- Xavf ikonlari: qalqon, havola, QR, xabar — emoji yo‘q.
- Holat: filled soft square emas, oddiy glyph + rang.

### 5.2.4 Kartochkalar

Default: **kartsiz**. Kartochka faqat interaktiv konteyner kerak bo‘lganda (skan natijasi harakatlari). Hero da kartochka yo‘q.

---

## 5.3 Wireframe tavsiflari (matn)

### 5.3.1 Onboarding (ruxsatlar bilan)

1. **Ekran A — Brend:** to‘liq fon (yumshoq gradient + himoya atmosferasi illustratsiya/foto). Markazda brend nomi, bitta jumla: «Hujumdan oldin ogohlantiramiz.» Bitta CTA: «Boshlash».
2. **Ekran B — Qanday himoya qiladi:** 3 qator (URL, xabar, qurilma) — statistikasiz.
3. **Ekran C — Ruxsatlar ketma-ket:** har bir ruxsat alohida: nima uchun kerak, nima **qilinmaydi** (masalan, SMS serverga ketmaydi), «Ruxsat berish» / «Hozir emas».
4. **Ekran D — Til tanlash:** uz/ru/en.

Motion: brend fade-up; ruxsat ekranida progress dots.

### 5.3.2 Dashboard / Bosh sahifa

- Yuqorida brend + holat qatori: «Himoya yoqilgan» (yashil) yoki «Cheklangan rejim».
- Bitta bosh CTA: «Tekshirish» (URL/QR/fayl).
- Oxirgi 1–3 ogohlantirish ro‘yxati (chiziqli, kartasiz).
- Pastki nav: Bosh / Tekshir / Tarix / Sozlama.
- Birinchi viewportda: brend, holat, 1 CTA, 1 qisqa jumla — stat strip yo‘q.

### 5.3.3 Skan natijasi

- Katta score (0–100) + verdict rangi (tinch).
- 2–4 ta `reasons` odam tilida.
- CTA guruh: «Havolani ochmaslik», «Allowlistga qo‘shish», «Ulashish (PII’siz)».
- MITRE teglari ikkinchi daraja (analyst uchun; oddiy foydalanuvchida yig‘ilgan).

### 5.3.4 Xavf ogohlantirish (modal / notification)

- **Critical:** tizim notification (Android) + in-app full-screen interrupt (foydalanuvchi yopishi mumkin, lekin birlamchi CTA aniq).
- Sarlavha: nima xavfli (1 qator).
- Tana: nima qilish kerak (1–2 qator).
- CTA: asosiy himoya harakati; ikkinchi: «Batafsil».
- Yashirin overlay / boshqa ilova ustida soxta login — **taqiqlangan**.

### 5.3.5 Sozlamalar

- Modullar yoqish/o‘chirish (toggle + qisqa izoh).
- Ruxsatlar holati.
- Til, mavzu (light/dark/system), katta shrift.
- Maxfiylik: consent, ma’lumotlarni o‘chirish.
- Hisob/tarif.

### 5.3.6 Hisobot / Tarix

- Filtr: turi, sana, severity.
- Ro‘yxat qatori: ikon, qisqa nom, score, vaqt.
- Batafsil: reasons, tavsiya.
- Bo‘sh holat: «Hali tekshiruv yo‘q» + CTA.

### 5.3.7 «Shubhali xabarni yuborish»

1. Matn/URL/skrinshot qo‘shish.
2. **Preview:** nima yuboriladi; PII ogohlantirishi.
3. Tasdiqlash / Bekor.
4. Rahmat + natija kelganda notification.

---

## 5.4 Ogohlantirish UX printsipi

| Yaxshi | Yomon (taqiqlangan) |
|--------|---------------------|
| «Bu havola soxta to‘lov sahifasiga o‘xshaydi. Ochmang.» | «Sizni HACK qilishdi!!!» |
| «SMS da kod so‘ralgan. Bank buni so‘ramaydi.» | Soxta timer / «5 soniya qoldi» |
| Aniq CTA | Ruxsatni yashirin majburlash |
| Noto‘g‘ri ogohlantirish haqida xabar berish | FP ni yashirish |

Til: qat’iy, aniq, harakatga undovchi; qo‘rqitib noto‘g‘ri qaror qildiruvchi emas.

---

## 5.5 Accessibility (WCAG 2.1 AA)

| Talab | Amal |
|-------|------|
| Kontrast | Matn ≥ 4.5:1; katta matn ≥ 3:1 |
| Fokus | Ko‘rinadigan focus ring (`--focus`) |
| Screen reader | Barcha CTA `label`; score `aria-live` |
| Harakat | Faqat rangga tayanmaslik (ikon+matn) |
| Shrift | Tizim/katta shrift rejimi |
| Motion | `prefers-reduced-motion` da animatsiya o‘chiq |
| Klaviatura | Web/Windows to‘liq klaviatura navigatsiyasi |

---

## 5.6 Platformaga xos UI izohlari

| Platforma | Izoh |
|-----------|------|
| Android | Material bilan to‘liq nusxa emas — brend tokenlari; notification channel: `security_critical` |
| Windows | Fluent ta’siri cheklangan; agent tray ikon + asosiy oyna |
| Web | Mehmon skan markaziy; marketing clutter hero da yo‘q |

---

## 5.7 Motion spetsifikatsiyasi (minimal 2–3)

1. **Skan progress** — chiziqli indeterminate → score count-up (300–500 ms).  
2. **Holat badge** — safe↔warn rang crossfade.  
3. **Critical alert** — pastdan/yuqoridan slide + subtle shake **yo‘q** (reduced motion).
