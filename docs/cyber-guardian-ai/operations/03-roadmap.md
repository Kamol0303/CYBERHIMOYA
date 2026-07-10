# Operations 03 — Roadmap (Killer Edition)

**Versiya:** 3.0.0-killer  
**Rol:** Product + Architect + APT Hunter  

---

## Threat Hunting & Actor Detection (majburiy)

V1 dan boshlab asosiy IOC hunting; V2 EDR+fingerprint; V3 attribution+playbooks; V4 milliy early-warning.

---

## V1 — Core protection + basic hunting + IOC

- Auth, consent, URL/QR/File, scam skeleti  
- IOC sync + sweep (FR-307 asos)  
- Basic campaign hint / actor IOC  
- 3 platforma dashboard  

## V2 — Full EDR + Behavior + Actor fingerprinting

- Windows ancestry, IOA, LOLBin/injection **detection**, ransomware  
- Behavior & anomaly, SMS/Telegram, APK similarity  
- Fingerprinting (FR-303), Fusion asos, TAKB/Graph asos  
- Hunting pipeline real-time + scheduled  

## V3 — Advanced Attribution + Campaign + Playbooks + B2B

- Full Attribution Engine (+ optional GNN)  
- Campaign tracking to‘liq  
- C2/phishing/scam panel detection  
- Automated **defensive** Playbooks  
- Deepfake  
- B2B Threat Intel Platform  
- OSINT persona/group tracking (qonuniy)  

## V4 — National-level early warning

- Davlat bilan hamkorlikda early-warning (FR-310, AQ-031)  
- Milliy feed exchange (UZCERT / Milliy Kiberxavfsizlik Markazi)  
- Kengaytirilgan playbook siyosatlari (kelishilgan)  

---

## Sprint tartibi (qisqa)

1. V1 core (mavjud SRS 04 + feed + sweep)  
2. V2 EDR + fingerprint board  
3. V3 graph + playbooks + B2B  
4. V4 faqat shartnoma/legal tayyor bo‘lgach  

Hujjatlar: `srs/08`, `sdd/07`, `sdd/04b`.
