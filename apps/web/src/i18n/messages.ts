export type Locale = "uz" | "ru" | "en";

const messages = {
  uz: {
    brand: "Cyber Guardian AI",
    tagline: "O‘zbekiston uchun mudofaa xavfsizlik skaneri",
    support:
      "URL ni tekshiring — phishing, soxta to‘lov va hukumat niqobidagi firibgarliklarga qarshi ogohlantirish.",
    cta: "Tekshirish",
    placeholder: "https://misol.uz/sahifa",
    guestNote: "Mehmon skan — hisob shart emas. Faqat mudofaa tahlili.",
    privacy: "Maxfiylik: URL hash saqlanadi; shaxsiy chat/SMS yuborilmaydi.",
    result: "Natija",
    score: "Xavf balli",
    verdict: "Hukm",
    action: "Tavsiya",
    reasons: "Sabablar",
    mitre: "MITRE",
    family: "Scam oilasi",
    dashboard: "Kabinet",
    dashboardHint: "V1 qobiq: skan tarixi va roziliklar keyingi sprintlarda to‘ldiriladi.",
    consentTitle: "Rozilik",
    consentBody:
      "Monitoring va favqulodda xabarlar faqat sizning yozma roziligingiz bilan yoqiladi.",
    lang: "Til",
    scanning: "Tekshirilmoqda…",
    error: "Skan muvaffaqiyatsiz. Keyinroq urinib ko‘ring.",
    clean: "Toza",
    suspicious: "Shubhali",
    malicious: "Zararli",
    unknown: "Noma’lum",
  },
  ru: {
    brand: "Cyber Guardian AI",
    tagline: "Защитный сканер безопасности для Узбекистана",
    support:
      "Проверьте URL — предупреждения о фишинге, поддельных платежах и гос. масках.",
    cta: "Проверить",
    placeholder: "https://primer.uz/page",
    guestNote: "Гостевое сканирование — аккаунт не обязателен. Только защита.",
    privacy: "Конфиденциальность: хранится hash URL; личные SMS/чаты не отправляются.",
    result: "Результат",
    score: "Оценка риска",
    verdict: "Вердикт",
    action: "Рекомендация",
    reasons: "Причины",
    mitre: "MITRE",
    family: "Семейство скама",
    dashboard: "Кабинет",
    dashboardHint: "Оболочка V1: история и согласия появятся в следующих спринтах.",
    consentTitle: "Согласие",
    consentBody:
      "Мониторинг и экстренные уведомления включаются только с вашего письменного согласия.",
    lang: "Язык",
    scanning: "Проверка…",
    error: "Сканирование не удалось. Попробуйте позже.",
    clean: "Чистый",
    suspicious: "Подозрительный",
    malicious: "Вредоносный",
    unknown: "Неизвестно",
  },
  en: {
    brand: "Cyber Guardian AI",
    tagline: "Defensive security scanner for Uzbekistan",
    support:
      "Check a URL for phishing, fake payment, and government-impersonation lures.",
    cta: "Scan",
    placeholder: "https://example.uz/page",
    guestNote: "Guest scan — no account required. Defensive analysis only.",
    privacy: "Privacy: URL hash may be stored; personal SMS/chats are never uploaded.",
    result: "Result",
    score: "Risk score",
    verdict: "Verdict",
    action: "Recommended action",
    reasons: "Reasons",
    mitre: "MITRE",
    family: "Scam family",
    dashboard: "Dashboard",
    dashboardHint: "V1 shell: scan history and consents land in later sprints.",
    consentTitle: "Consent",
    consentBody:
      "Monitoring and emergency alerts are enabled only with your prior written consent.",
    lang: "Language",
    scanning: "Scanning…",
    error: "Scan failed. Please try again later.",
    clean: "Clean",
    suspicious: "Suspicious",
    malicious: "Malicious",
    unknown: "Unknown",
  },
} as const;

export type MessageKey = keyof (typeof messages)["uz"];

export function t(locale: Locale, key: MessageKey): string {
  return messages[locale][key] ?? messages.en[key];
}

export const locales: Locale[] = ["uz", "ru", "en"];
