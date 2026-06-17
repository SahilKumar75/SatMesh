# PS13 — Air-Gapped Predictive Copilot for Secure MPLS Operations

**Mentors:** Pravin Kumar Choudhary, Pavan Kumar Bhairavarasu, Mithilesh Kumar
**Explainer:** Video 2, 33:22–37:03
**Slides:** Captured.
**Tagline:** "An offline AI **NOC Copilot** that predicts network failures before they impact users — and explains why."

> The outlier statement — **networking/security, not space-data ML.** No satellite data involved.

## The problem (slide)
- **Reactive detection:** NOC tools raise alerts only **after a performance threshold is breached** — by then users are already affected and there's no time to act.
- **Air-gap constraints:** regulated and government networks **cannot use cloud-connected AI**, leaving the most security-sensitive sites without any intelligent guidance.
- **The goal:** build an **autonomous, fully offline AI NOC Copilot** that forecasts failures with enough **lead time to act**, explains its reasoning in **plain language**, and **never depends on the internet or cloud APIs**.

## What you'll build — 4 building blocks (slide)
1. **Simulated SD-WAN / MPLS network** — a reproducible multi-site topology (**branch, hub, datacenter**) with **MPLS, VPNs, BGP/OSPF, IPSec tunnels** and **fault injection**.
2. **Predictive fault analytics** — ML models that catch **precursors** (congestion buildup, route flaps, tunnel degradation) **before** a failure occurs.
3. **Offline LLM NOC Copilot** — a **self-hosted, quantized LLM** using **RAG over local runbooks and topology data** to explain predictions in plain language.
4. **Integrated workflow automation** — **event correlation**, **confidence-scored alert prioritization**, and **automated playbook suggestions** for operators.

## Detail from the talk
- Simulate the network in software (a tool is named in the proposal; any other is fine; can run **vIOS**-type open-source router OS). Multi-site MPLS topology.
- Fault analysis from parameters: **route flapping, router queueing, tunnel up/down/flapping** as precursors of downtime.
- The LLM does RAG over local playbooks/runbooks + topology map (e.g. given an IP, find which router/location it belongs to).
- Logs collected via **SNMP, syslog, config files, or NMS tools**.

## Q&A
- (1:06) Use logs from either the **same simulated MPLS network** or **already-available data** integrated into the simulation.
- (1:11) You **build your own demo network** with open-source simulation tools; public datasets OK for training. End deliverable = a **chatbot/copilot** that you query and that returns **explainable** answers.

## Official description (website) — authoritative additions
- **Topology detail:** branch/hub/datacenter sites with **CE/PE/P device roles**, MPLS forwarding, VPN segmentation, traffic engineering, SD-WAN IPSec overlays, BGP/OSPF, QoS policies, configurable fault injection.
- **Operator must answer three questions:** Q1 what's likely to fail next and when; Q2 why is risk elevated / which signals contributed; Q3 what corrective action before SLA or security impact.
- **Named tools:** simulation — **EVE-NG / GNS3 / Containerlab**; telemetry — **Telegraf, Prometheus, Elasticsearch, Kafka**; predictive — **LSTM, Prophet, graph-based anomaly detection, ensembles**; offline LLM — **Mistral 7B / LLaMA 3 8B / Phi-3 (quantized)**; local RAG vector DB. Data: SNMP, syslog, BGP/OSPF events, **NetFlow/IPFIX**, SD-WAN controller telemetry, injected-fault ground-truth labels.
- **Evaluation weights (explicit):** Technical Merit **35%** (prediction accuracy + lead time), Copilot Effectiveness **35%** (correct, grounded, no hallucination), Security & Offline Compliance **20%** (verifiable zero outbound at runtime), Documentation **10%**.

## Our take
Not our lane and not space-tech — network engineering + an offline/quantized LLM with RAG. No imagery or remote-sensing component, so none of our CV/geospatial skills transfer. The deck is well-scoped (clear 4-block build), which will attract networking/security teams; likely a smaller, specialised applicant pool. Skip unless the team has strong networking + local-LLM/RAG experience.
