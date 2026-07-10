# SDD 04b — Killer Edition AI / Detection Modules

**Hujjat:** Cyber Guardian AI SDD  
**Bo‘lim:** AI Modules — Killer Set  
**Versiya:** 3.0.0-killer  
**Printsip:** Har bir modul chiqishi: risk score + explainability + confidence + possible actor/group link. Exploit/weaponization yo‘q.

Asosiy modullar ham `sdd/04-ai-detection-modules.md` da; ushbu fayl **killer to‘plam**ni to‘liq shablon bilan beradi.

---

## Threat Hunting & Actor Detection (majburiy)

Bu to‘plam hunting pipeline, knowledge graph va playbooklarni xususiyatlar bilan oziqlantiradi.

---

### Risk Scoring + Intent Prediction
- **Kirish ma’lumoti:** Barcha detektor featurelari, campaign/actor hint, infra score, IOA hitlari. Xom PII yo‘q.
- **Feature extraction:** Agregat skorlar, `scam_family`, `intent_tags`, graph centrality proxy, time decay.
- **Model/Heuristika:** Gradient boosting + qoida floor/ceiling + intent classifier (multi-label TTP/scam intent).
- **Chiqish:** risk score (0–100) + explainability + confidence + possible actor/group link + recommended_action.
- **False positive strategiyasi:** Allowlist, unknown zona, analyst feedback, kalibratsiya.
- **Ma’lumot manbalari:** Ichki labeled events, UZ kampaniyalar, MITRE map.
- **On-device/Cloud:** Engil on-device; to‘liq cloud.
- **Yangilanish:** Haftalik model; kunlik qoida.

---

### Behavior Analysis & Anomaly Detection
- **Kirish ma’lumoti:** W ancestry/network/registry meta; A app/DNS; Web session; baseline profil.
- **Feature extraction:** Burst rates, rare parent-child, deviation from baseline, cross-signal chains.
- **Model/Heuristika:** Baseline + IOA/Sigma + engil ONNX/TFLite anomaly; cloudda og‘irroq korrelyatsiya.
- **Chiqish:** anomaly_score + reasons + confidence + actor/campaign link (agar bor).
- **False positive strategiyasi:** 3 kunlik baseline, publisher allowlist, quiet hours.
- **Ma’lumot manbalari:** Consent telemetry, defensive lab.
- **On-device/Cloud:** Yengil on-device; og‘ir cloud.
- **Yangilanish:** IOA haftalik; baseline oylik.

---

### URL / Domain / IP Reputation + Live Infrastructure Hunting
- **Kirish ma’lumoti:** URL/domain/IP, cert fingerprint, ASN, DNS tarix proxy.
- **Feature extraction:** TI hit, age proxy, ASN anomaly, cert reuse across scam domains, sinkhole/passive DNS (litsenziyalangan).
- **Model/Heuristika:** IOC + ML + infra graph neighborhood.
- **Chiqish:** reputation_score + infra_tags (phishing_panel_suspected, c2_suspected) + confidence + actor link.
- **False positive strategiyasi:** Shared hosting careful weighting; rasmiy allowlist.
- **Ma’lumot manbalari:** Feeds, fusion OSINT, cert transparency (ochiq).
- **On-device/Cloud:** Cache on-device; live hunt cloud.
- **Yangilanish:** IOC soatlik/kunlik; infra job soatlik.

---

### SMS / Telegram Scam + Actor Group Linking
- **Kirish ma’lumoti:** On-device SMS features (matn cloudga yo‘q); ulashilgan Telegram matn/bot; group OSINT meta.
- **Feature extraction:** Money-offer patterns, bot id, script fingerprint, campaign overlap.
- **Model/Heuristika:** On-device SMS TFLite; cloud group linking via bot/IOC.
- **Chiqish:** scam_score + scam_family + confidence + possible group/actor link.
- **False positive strategiyasi:** Official shortcode/channel allowlist; past confidence soft warn.
- **Ma’lumot manbalari:** Annotatsiya, foydalanuvchi hisobot, OSINT.
- **On-device/Cloud:** SMS on-device; linking cloud.
- **Yangilanish:** Lug‘at haftalik; group graph kunlik.

---

### QR & Deepfake Detection
- **Kirish ma’lumoti:** QR image/payload; consent audio/image/video.
- **Feature extraction:** QR→URL features; spectral/face artefacts; SE transcript hits.
- **Model/Heuristika:** Decode + URL engine; cloud deepfake models.
- **Chiqish:** score + media_synthetic_prob + confidence + campaign link (URL orqali).
- **False positive strategiyasi:** Low-quality → inconclusive; consent gate.
- **Ma’lumot manbalari:** Mahalliy QR scam, ochiq deepfake korpus (litsenziya).
- **On-device/Cloud:** Decode on-device; deepfake cloud.
- **Yangilanish:** Qoida haftalik; model oylik.

---

### Advanced File & Memory Analysis
- **Kirish ma’lumoti:** File hash/bytes meta; W memory anomaly indicators (not full raw dump by default); packer/entropy signals; YARA.
- **Feature extraction:** Entropy, section anomaly, packer heuristics, fuzzy hash, YARA hits, cert.
- **Model/Heuristika:** YARA + heuristics + similarity index; memory IOA (W).
- **Chiqish:** file_score + packer_suspected + memory_anomaly + confidence + family/actor link.
- **False positive strategiyasi:** Signed publisher allowlist; packer≠malware alone.
- **Ma’lumot manbalari:** TI, ichki oilalar, Sigma/YARA.
- **On-device/Cloud:** Hash/YARA local (A/W); heavy cloud; memory meta local.
- **Yangilanish:** YARA haftalik.

---

### Process Injection & Living-off-the-Land Detection (Windows)
- **Kirish ma’lumoti:** Process ancestry, module load meta, LOLBin invocation patterns, imzo holati (EDR signals).
- **Feature extraction:** Rare ancestry, suspicious LOLBin+network combo, injection **indicator** flags from OS callbacks.
- **Model/Heuristika:** Sigma/IOA + heuristic correlation. **Detection only** — injection/LOLBin abuse how-to yo‘q.
- **Chiqish:** ioa_score + mitre_tags + confidence + possible actor link.
- **False positive strategiyasi:** Admin tools allowlist, baseline, dual-signal requirement for critical.
- **Ma’lumot manbalari:** Sigma community (license), ichki IOA, defensive lab.
- **On-device/Cloud:** Detection on-device; correlation cloud.
- **Yangilanish:** Sigma/IOA haftalik.

---

### YARA + Sigma + Custom Behavioral Rules
- **Kirish ma’lumoti:** Files / structured events.
- **Feature extraction:** Rule match metadata, severity, tags, uz_ttp tags.
- **Model/Heuristika:** Rule engines + staging/canary.
- **Chiqish:** matches[] + score floor + confidence + campaign/actor tags if present.
- **False positive strategiyasi:** Staging, FP tickets, signed active-only packs.
- **Ma’lumot manbalari:** Internal + licensed open rules.
- **On-device/Cloud:** A/W local; Web upload→BE; Sigma W+BE.
- **Yangilanish:** Imzolangan paket haftalik/hotfix.

---

### Threat Actor Attribution Engine
- **Kirish ma’lumoti:** Graph neighborhood, shared IOC/infra/cert, TTP set, fingerprint vectors.
- **Feature extraction:** Shared observable counts, code similarity, temporal overlap, OSINT persona links.
- **Model/Heuristika:** Graph clustering + optional GNN (cloud) + analyst confirm.
- **Chiqish:** actor_cluster + attribution_score + confidence + explainability + group link.
- **False positive strategiyasi:** High threshold auto-link; CDN noise filter; human merge.
- **Ma’lumot manbalari:** Knowledge graph, fusion, OSINT.
- **On-device/Cloud:** Cloud only.
- **Yangilanish:** Continuous + nightly recompute.

---

### Campaign Tracking & Correlation
- **Kirish ma’lumoti:** Events across devices/channels with shared observables.
- **Feature extraction:** Exact/fuzzy IOC, script fingerprint, infra reuse.
- **Model/Heuristika:** Connected components + time-decay + analyst split/merge.
- **Chiqish:** campaign_id + confidence + actor link + reasons.
- **False positive strategiyasi:** Min IOC count; exclude global popular domains as sole link.
- **Ma’lumot manbalari:** Pipeline, graph.
- **On-device/Cloud:** Cloud; client hint.
- **Yangilanish:** Streaming + daily.

---

### C2 / Phishing Kit / Scam Panel Detection
- **Kirish ma’lumoti:** URL/domain/IP, HTTP response meta (safe fetch), cert, path patterns, panel fingerprint hashes (detection signatures — not kit source code distribution).
- **Feature extraction:** Known panel path/title fingerprints, cert reuse, hosting ASN, redirect chains.
- **Model/Heuristika:** Signature + ML reputation + infra graph. Describes **how to detect**, not how to build kits.
- **Chiqish:** infra_score + panel_family + confidence + actor/campaign link.
- **False positive strategiyasi:** Benign admin panels allowlist; inconclusive on weak signals.
- **Ma’lumot manbalari:** TI, UZCERT, licensed intel, internal reports.
- **On-device/Cloud:** Hint local; confirmation cloud.
- **Yangilanish:** Signature packs weekly.

---

### MITRE ATT&CK Automated Mapping
- **Kirish ma’lumoti:** Rule/event category, IOA, scam_family, uz_ttp.
- **Feature extraction:** Map tables to technique IDs.
- **Model/Heuristika:** Deterministic mapping (+ optional LLM assist for analyst summary, PII-stripped).
- **Chiqish:** mitre_tags[] + confidence + optional actor link context.
- **False positive strategiyasi:** Only high-confidence maps; no speculative tags on weak events.
- **Ma’lumot manbalari:** MITRE, internal uz_ttp base.
- **On-device/Cloud:** Cloud mapping; client display.
- **Yangilanish:** On ATT&CK/uz_ttp updates.

---

## Modul × Roadmap (Killer)

| Modul | V1 | V2 | V3 | V4 |
|-------|----|----|----|-----|
| Risk + Intent | ✅ asos | ✅ | ✅ | ✅ |
| Behavior & Anomaly | — | ✅ | ✅ | ✅ |
| URL/Infra hunting | ✅ rep | ✅ | ✅ live | ✅ national feed |
| SMS/Telegram + group link | — | ✅ | ✅ | ✅ |
| QR & Deepfake | QR ✅ | — | Deepfake ✅ | ✅ |
| File & Memory | hash ✅ | YARA+mem ⚠️ | ✅ | ✅ |
| Injection/LOLBin detect | — | ✅ W | ✅ | ✅ |
| YARA/Sigma/Behavioral | — | qisman | ✅ | ✅ |
| Actor Attribution | IOC ✅ | fingerprint ✅ | GNN ✅ | national |
| Campaign Correlation | hint ✅ | ✅ | ✅ | ✅ |
| C2/Panel detect | — | ⚠️ | ✅ | ✅ |
| MITRE mapping | ✅ | ✅ | ✅ + UZ TTP | ✅ |
| Playbooks | — | asos | ✅ | national EW |
