# SDD 02 — UML va ER diagrammalar

**Hujjat:** Cyber Guardian AI SDD  
**Bo‘lim:** 2 — Diagrams  
**Versiya:** 1.0.0-draft  
**Format:** Mermaid + 2–3 jumlali izoh

---

## 2.1 Use Case diagram

```mermaid
flowchart LR
  U[Oddiy foydalanuvchi]
  A[Admin]
  T[Threat Analyst]

  U --> UC1[URL/QR/Fayl tekshirish]
  U --> UC2[Dashboard ko‘rish]
  U --> UC3[Ogohlantirishga javob]
  U --> UC4[Shubhali xabar yuborish]
  U --> UC5[Parol/Email tekshiruv]
  U --> UC6[Sozlamalar va consent]
  U --> UC7[SMS himoya Android]

  A --> UC8[Foydalanuvchi/qurilma boshqaruvi]
  A --> UC9[Audit jurnalini ko‘rish]
  A --> UC10[Notification siyosati]
  A --> UC2

  T --> UC11[Threat feed holati]
  T --> UC12[Qoida versiyalarini boshqarish]
  T --> UC13[Hisobot eksport]
  T --> UC14[MITRE bo‘yicha filtr]
  T --> UC1
```

**Izoh:** Uch asosiy aktor — oddiy foydalanuvchi (himoya va tekshiruv), admin (boshqaruv/audit), threat-analyst (intel va qoidalar). Barcha use case’lar faqat aniqlash, ogohlantirish, bloklash va hisobotga qaratilgan.

---

## 2.2 Class diagram (core domain)

```mermaid
classDiagram
  class User {
    +UUID id
    +String emailHash
    +Locale locale
    +Role role
    +Instant createdAt
  }
  class Device {
    +UUID id
    +UUID userId
    +Platform platform
    +String appVersion
    +Instant lastSeenAt
  }
  class ConsentRecord {
    +UUID id
    +UUID userId
    +ConsentType type
    +Boolean granted
    +Instant changedAt
  }
  class ScanResult {
    +UUID id
    +UUID userId
    +ScanType type
    +Int score
    +Json reasons
    +Instant createdAt
  }
  class ThreatEvent {
    +UUID id
    +UUID deviceId
    +String category
    +Severity severity
    +Json mitreTags
    +Instant detectedAt
  }
  class RiskScoreHistory {
    +UUID id
    +UUID subjectId
    +Int score
    +Instant at
  }
  class RuleDefinition {
    +UUID id
    +RuleKind kind
    +String version
    +Bytes signature
  }
  class ThreatFeedSource {
    +UUID id
    +String name
    +LicenseStatus license
    +Instant lastSyncAt
  }
  class Subscription {
    +UUID id
    +UUID userId
    +Plan plan
    +Instant expiresAt
  }
  class Notification {
    +UUID id
    +UUID userId
    +Level level
    +String bodyKey
    +Boolean read
  }
  class AuditLog {
    +UUID id
    +UUID actorId
    +String action
    +Json meta
    +Instant at
  }

  User "1" --> "*" Device
  User "1" --> "*" ConsentRecord
  User "1" --> "*" ScanResult
  User "1" --> "0..1" Subscription
  User "1" --> "*" Notification
  Device "1" --> "*" ThreatEvent
  ScanResult --> RiskScoreHistory
  ThreatEvent --> RiskScoreHistory
  ThreatFeedSource --> RuleDefinition
  User --> AuditLog
```

**Izoh:** Domen modeli himoya artefaktlarini (skan, tahdid hodisasi, qoida, feed) va maxfiylik artefaktlarini (consent, audit) birlashtiradi. PII maydonlar hash/shifrlangan holda saqlanadi (`03-api-and-database.md`).

---

## 2.3 Sequence diagramlar

### 2.3.1 Ilova ochilishi

```mermaid
sequenceDiagram
  actor U as Foydalanuvchi
  participant App as Client App
  participant SM as sync-manager
  participant Auth as Auth Service
  participant TI as Threat Intel

  U->>App: Ilovani ochadi
  App->>App: local session / biometric
  alt Token muddati o‘tgan
    App->>Auth: refresh token
    Auth-->>App: yangi JWT
  end
  App->>SM: background sync
  SM->>TI: GET /v1/threat-feed/sync?since=ver
  TI-->>SM: delta + signature
  SM->>SM: verify signature
  SM-->>App: cache yangilandi
  App-->>U: Dashboard
```

**Izoh:** Ochilishda avval mahalliy sessiya, keyin imzolangan threat delta. Sync muvaffaqiyatsiz bo‘lsa ham dashboard offline cache bilan ochiladi.

### 2.3.2 URL tekshirish

```mermaid
sequenceDiagram
  actor U as Foydalanuvchi
  participant UI as UI
  participant Local as local-scan
  participant API as Scan API
  participant Score as Scoring

  U->>UI: URL kiritadi
  UI->>Local: normalize + cache lookup
  Local-->>UI: local hint
  UI->>API: POST /v1/scan/url
  API->>Score: compute
  Score-->>API: score+reasons
  API-->>UI: ScanResult
  UI-->>U: Natija ekrani
```

**Izoh:** Local hint darhol ko‘rsatiladi; yakuniy score clouddan keladi. Natija saqlanadi va notification siyosatiga qarab ogohlantiradi.

### 2.3.3 SMS skan (Android, on-device)

```mermaid
sequenceDiagram
  participant OS as Android OS
  participant App as CGA Android
  participant ML as On-device SMS model
  participant N as System Notification

  OS->>App: SMS_RECEIVED broadcast
  App->>App: consent tekshiruvi
  alt Consent yo‘q
    App-->>App: ignore
  else Consent bor
    App->>ML: feature extract (local)
    ML-->>App: score + reasons
    alt score >= threshold
      App->>N: visible system notification
      Note over App: xom matn SERVERGA YO‘Q
    end
  end
```

**Izoh:** SMS tahlili faqat qurilmada. Ogohlantirish yashirin overlay emas — foydalanuvchiga ko‘rinadigan tizim bildirishnomasi (suiiste’molchi overlay naqshidan farq).

### 2.3.4 Ransomware aniqlanishi (Windows)

```mermaid
sequenceDiagram
  participant Mon as Ransomware Monitor
  participant FS as File System hooks
  participant Proc as Process Monitor
  participant UI as Windows UI
  participant API as ThreatEvent API

  FS->>Mon: honeypot file modified
  Mon->>Proc: correlating process
  Mon->>Mon: entropy / mass-write heuristics
  Mon->>UI: CRITICAL alert + CTA
  Mon->>API: POST ThreatEvent meta
  Note over Mon,API: Fayl kontenti yuborilmaydi; faqat meta
```

**Izoh:** Honeypot + entropiya/heuristika orqali himoya ogohlantirishi. Maqsad — foydalanuvchini to‘xtatish va yo‘riqnoma berish; hujum texnikasi o‘rgatilmaydi.

### 2.3.5 Hisobot yuborish

```mermaid
sequenceDiagram
  actor T as Threat Analyst
  participant Web as Web Panel
  participant R as Reports Service
  participant DB as DB
  participant Aud as AuditLog

  T->>Web: Hodisalarni tanlaydi
  Web->>R: POST /v1/reports
  R->>DB: query + PII redact
  R->>Aud: append export action
  R-->>Web: download link / JSON
  Web-->>T: Hisobot
```

**Izoh:** Eksport RBAC va audit ostida. PII redaksiya qilinadi; defensive hisobot formati.

---

## 2.4 Component diagram

```mermaid
flowchart TB
  subgraph Android
    AUI[UI]
    ALS[local-scan-engine]
    ASM[sync-manager]
    ASMS[sms-detector]
  end
  subgraph Windows
    WUI[UI]
    WAG[Agent Service]
    WPM[Process/Registry/Network]
    WR[Ransomware/USB]
  end
  subgraph Web
    WBUI[Web UI]
    EXT[Extension]
  end
  subgraph Backend
    GW[API Gateway]
    AUTH[Auth]
    TI[Threat Intel]
    SCAN[Scan]
    SCR[Scoring]
    NTF[Notification]
    RUL[Rules]
  end
  AUI --> ALS --> ASM --> GW
  ASMS --> ALS
  WUI --> WAG --> GW
  WPM --> WAG
  WR --> WAG
  WBUI --> GW
  EXT --> GW
  GW --> AUTH
  GW --> TI
  GW --> SCAN
  GW --> SCR
  GW --> NTF
  GW --> RUL
```

**Izoh:** Har platforma o‘zining local komponentlariga ega; umumiy aqllilik backendda. Extension Web bilan bir xil Scan/TI API dan foydalanadi.

---

## 2.5 Deployment diagram

```mermaid
flowchart TB
  subgraph UserDevices
    Phone[Android telefon]
    PC[Windows PC]
    Browser[Brauzer]
  end
  subgraph CloudProd
    LB[Load Balancer TLS]
    GW[API Gateway pods]
    SVC[Microservices pods]
    PG[(PostgreSQL primary/replica)]
    RD[(Redis)]
    S3[(Object Storage)]
  end
  Phone --> LB
  PC --> LB
  Browser --> LB
  LB --> GW --> SVC
  SVC --> PG
  SVC --> RD
  SVC --> S3
```

**Izoh:** Clientlar faqat LB/Gateway ga chiqadi. Ichki servislar private tarmoqda; DB va object storage alohida xavfsizlik guruhida.

---

## 2.6 ER diagram

```mermaid
erDiagram
  USER ||--o{ DEVICE : owns
  USER ||--o{ CONSENT_RECORD : grants
  USER ||--o{ SCAN_RESULT : performs
  USER ||--o| SUBSCRIPTION : has
  USER ||--o{ NOTIFICATION : receives
  USER ||--o{ AUDIT_LOG : actor
  DEVICE ||--o{ THREAT_EVENT : raises
  SCAN_RESULT ||--o{ RISK_SCORE_HISTORY : tracks
  THREAT_EVENT ||--o{ RISK_SCORE_HISTORY : tracks
  THREAT_FEED_SOURCE ||--o{ RULE_DEFINITION : publishes
  USER {
    uuid id PK
    string email_enc
    string role
    string locale
    timestamptz created_at
  }
  DEVICE {
    uuid id PK
    uuid user_id FK
    string platform
    string app_version
    string device_pubkey
    timestamptz last_seen_at
  }
  SCAN_RESULT {
    uuid id PK
    uuid user_id FK
    string scan_type
    int score
    jsonb reasons
    string subject_hash
    timestamptz created_at
  }
  THREAT_EVENT {
    uuid id PK
    uuid device_id FK
    string category
    string severity
    jsonb mitre_tags
    jsonb meta
    timestamptz detected_at
  }
  RISK_SCORE_HISTORY {
    uuid id PK
    uuid subject_id
    string subject_type
    int score
    timestamptz at
  }
  RULE_DEFINITION {
    uuid id PK
    uuid feed_source_id FK
    string kind
    string version
    bytea signature
    boolean active
  }
  THREAT_FEED_SOURCE {
    uuid id PK
    string name
    string license_status
    timestamptz last_sync_at
  }
  SUBSCRIPTION {
    uuid id PK
    uuid user_id FK
    string plan
    timestamptz expires_at
  }
  NOTIFICATION {
    uuid id PK
    uuid user_id FK
    string level
    string body_key
    boolean read
    timestamptz created_at
  }
  AUDIT_LOG {
    uuid id PK
    uuid actor_id FK
    string action
    jsonb meta
    timestamptz at
  }
  CONSENT_RECORD {
    uuid id PK
    uuid user_id FK
    string consent_type
    boolean granted
    timestamptz changed_at
  }
```

**Izoh:** ER majburiy obyektlarni qamrab oladi: User, Device, ScanResult, ThreatEvent, RiskScoreHistory, RuleDefinition, ThreatFeedSource, Subscription, Notification, AuditLog, ConsentRecord. Indekslar va retention `03-api-and-database.md` da.
