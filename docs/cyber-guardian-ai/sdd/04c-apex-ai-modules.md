# SDD 04c — Apex AI / Detection Modules (kengaytirilgan shablon)

**Versiya:** 4.0.0-apex  
**Cheklov:** Chiqishda recommended actions faqat defensive. Evasion bypass = **detektor mustahkamlash**, hujumchini o‘rgatish emas.

Har bir modul shablon:

- Kirish ma’lumoti  
- Feature extraction & Enrichment  
- Model / Algoritm  
- Chiqish: risk + explainability + confidence + linked actors + recommended actions  
- False positive / evasion **resilience** strategiyasi  
- Ma’lumot manbalari  
- On-device / Edge / Cloud  
- Yangilanish / retraining  
- Integration with kill-chain stage  

---

## Threat Hunting & Actor Disruption Strategy (majburiy)

Modullar kill-chain bosqichlariga map qilinadi; disruption = blok/karantin/CERT intel.

---

### Unified Risk & Intent Scoring
- **Kirish ma’lumoti:** Barcha detektor chiqishlari, graph hints, forecast score, playbook context.
- **Feature extraction & Enrichment:** Weighted aggregates, intent multi-label, stage tag, source trust.
- **Model / Algoritm turi:** Ensemble (GBDT + rules) + calibrator.
- **Chiqish:** risk score + explainability + confidence + linked actors + recommended actions (block/warn/report).
- **False positive / evasion resilience:** Allowlist, adversarial example monitoring on features (defensive), unknown band.
- **Ma’lumot manbalari:** Telemetry + TI + analyst labels.
- **On-device / Edge / Cloud:** Engil on-device; to‘liq cloud.
- **Yangilanish / retraining:** Haftalik; drift alert.
- **Kill-chain stage:** Barcha bosqichlar — yakuniy qaror.

---

### Advanced Behavioral & Anomaly Detection
- **Kirish:** Process/network/app/session sequences; baseline profil.
- **Feature extraction & Enrichment:** Sequence embeddings, rare transitions, burstiness, peer-group deviation.
- **Model / Algoritm:** Transformer/sequence model (cloud) + on-device threshold heuristics.
- **Chiqish:** anomaly_score + explainability + confidence + linked actors + actions.
- **FP / evasion resilience:** Dual-signal critical; concept-drift retraining; obfuscation-tolerant features (counts, not brittle strings only).
- **Manbalar:** Consent telemetry, lab.
- **On-device / Edge / Cloud:** Yengil device; og‘ir cloud.
- **Yangilanish:** IOA haftalik; model oylik.
- **Kill-chain:** Installation / C2 indicators / Actions.

---

### Multi-Vector Reputation Engine (URL, File, IP, Domain, ASN, Cert)
- **Kirish:** URL/file hash/IP/domain/ASN/cert FP.
- **Feature extraction & Enrichment:** TI hits, cert reuse graph, ASN risk, CT logs, passive DNS (licensed).
- **Model / Algoritm:** Ensemble + graph neighborhood features.
- **Chiqish:** multi-vector scores + explainability + confidence + linked actors + actions.
- **FP / evasion resilience:** Newly registered domain caution; shared hosting down-weight; homoglyph detection.
- **Manbalar:** OSINT + private feeds + telemetry.
- **On-device / Edge / Cloud:** Cache device; live cloud.
- **Yangilanish:** IOC hourly/daily.
- **Kill-chain:** Delivery / C2.

---

### SMS / Messenger / VoIP Scam Detection + Actor Linking
- **Kirish:** On-device SMS features; shared messenger text; VoIP metadata (consent; no covert recording).
- **Feature extraction & Enrichment:** uz/ru/en slang, money scripts, bot ids, call-pattern meta (duration/frequency — not audio by default).
- **Model / Algoritm:** TFLite text + cloud linking; optional deepfake audio if user uploads.
- **Chiqish:** scam_score + family + confidence + linked actors/groups + actions.
- **FP / evasion resilience:** Official shortcodes; multilingual thresholds; adversarial spam paraphrases in training.
- **Manbalar:** Telemetry meta, OSINT groups, reports.
- **On-device / Edge / Cloud:** SMS on-device; linking cloud.
- **Yangilanish:** Lexicon weekly; model biweekly.
- **Kill-chain:** Delivery / Actions (fraud).

---

### QR & Visual Phishing Detection
- **Kirish:** QR image; optional screenshot (consent).
- **Feature extraction & Enrichment:** Payload URL features; visual brand spoof embeddings.
- **Model / Algoritm:** Decode + vision similarity + URL engine.
- **Chiqish:** score + explainability + confidence + linked actors + actions.
- **FP / evasion resilience:** Official merchant allowlist; inconclusive on blur.
- **Manbalar:** Local QR scam DB, TI.
- **On-device / Edge / Cloud:** Decode device; vision cloud.
- **Yangilanish:** Weekly.
- **Kill-chain:** Delivery.

---

### Deepfake Audio/Video Detection
- **Kirish:** User-consented uploads only.
- **Feature extraction & Enrichment:** Spectral/face artefacts; SE transcript.
- **Model / Algoritm:** Cloud deepfake classifiers + heuristics.
- **Chiqish:** synthetic_score + confidence + linked SE campaign + actions.
- **FP / evasion resilience:** Low-quality inconclusive; never sole legal proof.
- **Manbalar:** Licensed corpora + internal SE cases.
- **On-device / Edge / Cloud:** Cloud primary.
- **Yangilanish:** Monthly retrain.
- **Kill-chain:** Delivery / Actions (SE).

---

### Memory Forensics & Process Tree Analysis
- **Kirish:** Windows process tree; memory **indicators** (not default full dump).
- **Feature extraction & Enrichment:** Ancestry depth, unsigned modules, hollow/injection **indicators**, entropy hotspots.
- **Model / Algoritm:** IOA/Sigma + heuristic forensics scoring; optional offline dump in Evidence Vault (role-gated).
- **Chiqish:** forensics_score + tree explain + confidence + linked actors + actions (quarantine/isolate_suggest).
- **FP / evasion resilience:** Dev tools allowlist; require corroboration for critical.
- **Manbalar:** EDR telemetry, lab.
- **On-device / Edge / Cloud:** Capture on-device; vault cloud.
- **Yangilanish:** IOA weekly.
- **Kill-chain:** Installation / Actions.

---

### Rootkit / Injection / LOTL Detection
- **Kirish:** Kernel/user telemetry available to agent; LOLBin patterns; persistence IOA.
- **Feature extraction & Enrichment:** Hidden module indicators, unusual parent of LOLBin, network+LOLBin combo.
- **Model / Algoritm:** Behavioral rules + anomaly. **Detection only** — no rootkit/injection how-to.
- **Chiqish:** ioa_score + MITRE + confidence + linked actors + actions.
- **FP / evasion resilience:** Baseline admins; multi-signal; continuous rule tuning.
- **Manbalar:** Sigma, internal IOA, lab.
- **On-device / Edge / Cloud:** Detect device; correlate cloud.
- **Yangilanish:** Weekly packs.
- **Kill-chain:** Installation / C2 / Actions.

---

### YARA + Sigma + Behavioral Rule Engine
- **Kirish:** Files / events.
- **Feature extraction & Enrichment:** Match meta, uz_ttp tags, severity.
- **Model / Algoritm:** Rule engines + canary.
- **Chiqish:** matches + score floor + confidence + linked actors/tags + actions.
- **FP / evasion resilience:** Staging; polymorphic coverage via family rules + fuzzy hash.
- **Manbalar:** Internal + licensed.
- **On-device / Edge / Cloud:** Local A/W; BE for Web upload.
- **Yangilanish:** Signed weekly/hotfix.
- **Kill-chain:** Delivery–Installation.

---

### Threat Actor Attribution & Fingerprinting
- **Kirish:** Graph+vector features, infra, code similarity, OSINT persona.
- **Feature extraction & Enrichment:** Shared IOC, embedding distance, TTP Jaccard, cert clusters.
- **Model / Algoritm:** GNN + clustering + analyst confirm; LLM summary assist.
- **Chiqish:** actor_cluster + score + explainability + confidence + linked actors + actions (CERT package).
- **FP / evasion resilience:** High auto-link threshold; CDN noise filter.
- **Manbalar:** Graph, fusion, OSINT, private TI.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Continuous + nightly.
- **Kill-chain:** Cross-stage attribution.

---

### Campaign Detection & Tracking
- **Kirish:** Multi-event observables.
- **Feature extraction & Enrichment:** Fuzzy/exact links, time decay, channel mix.
- **Model / Algoritm:** Graph components + ML link prediction.
- **Chiqish:** campaign_id + confidence + linked actors + actions.
- **FP / evasion resilience:** Min evidence; human merge/split.
- **Manbalar:** Pipeline, vault refs.
- **On-device / Edge / Cloud:** Cloud; client hint.
- **Yangilanish:** Streaming.
- **Kill-chain:** Campaign-level across stages.

---

### Infrastructure Hunting (C2, phishing, scam panels)
- **Kirish:** Domains/IPs/certs/paths; safe response fingerprints.
- **Feature extraction & Enrichment:** Panel fingerprints, ASN, CT, redirect graphs.
- **Model / Algoritm:** Signatures + ML + graph. Detect panels — do not publish kit build guides.
- **Chiqish:** infra_score + family + confidence + linked actors + actions (deny + takedown-intel).
- **FP / evasion resilience:** Benign panel allowlist; weak→inconclusive.
- **Manbalar:** TI, UZCERT, licensed intel.
- **On-device / Edge / Cloud:** Hint local; confirm cloud.
- **Yangilanish:** Weekly signatures.
- **Kill-chain:** Delivery / C2.

---

### Predictive Attack Forecasting
- **Kirish:** Actor/campaign histories, seasonality, channel shifts.
- **Feature extraction & Enrichment:** Time-series features, graph growth rate, language/channel mix.
- **Model / Algoritm:** Time-series + graph features ensemble; uncertainty estimates.
- **Chiqish:** forecast windows + probability + explainability + confidence + linked actors + prep actions (raise sensitivity, pre-block related IOC).
- **FP / evasion resilience:** Never present as certainty; calibration metrics.
- **Manbalar:** Historical campaigns (PII-free).
- **On-device / Edge / Cloud:** Cloud; optional device policy tighten.
- **Yangilanish:** Weekly retrain.
- **Kill-chain:** Pre-Delivery proactive defense.

---

### Graph-based Relationship & Similarity Analysis
- **Kirish:** Knowledge graph + vector embeddings (tools, samples, personas).
- **Feature extraction & Enrichment:** Path features, community detection, similarity NN.
- **Model / Algoritm:** Graph algorithms + vector search + GNN.
- **Chiqish:** relationship paths + similarity hits + confidence + linked actors + actions.
- **FP / evasion resilience:** Path length limits; evidence thresholds.
- **Manbalar:** Graph DB + vector DB + fusion.
- **On-device / Edge / Cloud:** Cloud.
- **Yangilanish:** Continuous index.
- **Kill-chain:** Cross-stage investigation.

---

### Automated TTP & MITRE Mapping
- **Kirish:** IOA/rules/scam_family/uz_ttp.
- **Feature extraction & Enrichment:** Map tables; optional LLM narrative for analysts.
- **Model / Algoritm:** Deterministic map + LLM assist.
- **Chiqish:** mitre/uz_ttp tags + confidence + linked actors context + actions.
- **FP / evasion resilience:** No speculative tags on weak events.
- **Manbalar:** MITRE + UZ TTP base.
- **On-device / Edge / Cloud:** Cloud map; client display.
- **Yangilanish:** On framework updates.
- **Kill-chain:** Stage labeling for playbooks.

---

## Modul × Roadmap (Apex V1–V5)

| Modul | V1 | V2 | V3 | V4 | V5 |
|-------|----|----|----|----|-----|
| Unified Risk & Intent | ✅ | ✅ | ✅ | ✅ | ✅ autonomous policies |
| Behavior & Anomaly | — | ✅ | ✅ | ✅ | ✅ |
| Multi-Vector Reputation | ✅ | ✅ | ✅ | ✅ | ✅ |
| SMS/Messenger/VoIP + link | — | ✅ | ✅ | ✅ | ✅ |
| QR & Visual | QR ✅ | visual ⚠️ | ✅ | ✅ | ✅ |
| Deepfake | — | — | ✅ | ✅ | ✅ |
| Memory & Process Tree | — | ✅ W | ✅ | ✅ | ✅ |
| Rootkit/Injection/LOTL detect | — | ✅ | ✅ | ✅ | ✅ |
| YARA/Sigma/Behavioral | — | ✅ | ✅ | ✅ | ✅ |
| Attribution & Fingerprint | IOC ✅ | ✅ | GNN ✅ | ✅ | ✅ |
| Campaign Tracking | hint ✅ | ✅ | ✅ | ✅ | ✅ |
| Infra Hunting | — | ⚠️ | ✅ | ✅ | ✅ |
| Predictive Forecasting | — | — | ✅ | ✅ | ✅ |
| Graph Relationship | — | graph ✅ | +vector ✅ | ✅ | ✅ |
| TTP/MITRE | ✅ | ✅ | ✅ | ✅ | ✅ |
| Evidence Vault | — | ✅ | ✅ | ✅ | ✅ |
| National Sentinel | — | — | — | ✅ | ✅ AI ecosystem |
