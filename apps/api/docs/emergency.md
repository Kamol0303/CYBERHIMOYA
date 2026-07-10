# Emergency reporting foundation (FR-EM01…07)

| Endpoint | Maqsad |
|----------|--------|
| `GET /v1/emergency/allowlist` | AQ-039 holati (destination qiymatlari oshkor etilmaydi) |
| `POST /v1/emergency/consent` | `emergency_law_enforcement` opt-in |
| `POST /v1/emergency/confirm` | ≥3 modul + yuqori confidence → confirm token |
| `POST /v1/emergency/dispatch` | Ikkinchi tasdiq; default **dry-run** |
| `GET /v1/emergency/logs` | Foydalanuvchi kabineti jurnali |

**Qoidalar:** raw PII/SMS/parol yo‘q; allowlist bo‘sh/PENDING bo‘lsa live yuborish yo‘q; faqat mudofaa.
