# SAM for Road-Network Graph Extraction

**Citation.** *Segment Anything Model (SAM) for road network graph extraction* (arXiv, 2024). Foundation-model-based road extraction and graph vectorization.

**Core claim.** Promptable foundation models (SAM) can segment roads zero-/few-shot, but turning their dense masks into a clean, connected **graph** still requires explicit skeletonization + topology repair — the segmentation model alone does not give you a routable network.

## Key ideas

- **Mask → graph pipeline** is unavoidable regardless of the segmenter: `mask → skeleton (thinning) → nodes (junctions/endpoints) → edges (traced arms) → gap healing`. SAM improves the first box; it does not remove the graph-construction stages.

- **Foundation-model cost.** SAM's ViT-H backbone is heavy; for a fixed inference budget a purpose-trained D-LinkNet on 4-channel Sentinel-2 is faster and domain-adapted, whereas SAM is RGB-only and not tuned for thin 10 m roads.

## What it changes in SatMesh

It validates the architecture split: **segmentation and graph extraction are separate concerns.** SatMesh keeps `src/model/` (segmentation) cleanly decoupled from `src/graph/skeleton.py` + `heal.py` (vectorization + topology repair). That decoupling means the segmenter is swappable — D-LinkNet today, SAM or URoadNet later — without touching the graph engine, criticality, or APLS code.

## Judge talking point

SAM is the obvious "just use a foundation model" suggestion. The paper's own pipeline shows SAM still needs the exact skeleton→heal→graph stages we built — and SAM is RGB-only, heavier, and not tuned for 10 m Indian roads. Our decoupled design means we get SAM's upside for free if we want it: drop it in as the segmenter, keep the entire Track-B engine unchanged.

See also [[uroadnet]] and [[dlinknet-cvpr2018]] (segmentation alternatives) and [[apls-spacenet5]] (how we'd compare them objectively).
