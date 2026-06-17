# Session Knowledge Graph — Report
### Bharatiya Antariksh Hackathon 2026 working session

A hand-built, graphify-style map of everything we covered. Open `graph.html` for the interactive version.

> Note: this is the *equivalent* of running the `graphify` Claude Code skill, produced by hand — the real `/graphify` skill runs inside Claude Code and isn't available in this Cowork session.

## God nodes (what everything connects through)
1. **PS4 Route Resilience** — the chosen problem; the hub linking data, both tracks, and strategy.
2. **BAH 2026** — the event; connects to all 15 problem statements and the logistics.
3. **Idea Proposal / Deck** — the actual deliverable that gets you shortlisted by 1 Jul.
4. **Data (3 jobs)** — the spine of execution; teach the model, check it, run it.
5. **Track B — Graph** — your differentiator; 50% of the score lives here.

## Communities (clusters)
- **Logistics:** BAH 2026, ISRO, Hack2skill, deadlines, team, finale, proposal.
- **15 Problem Statements:** PS1–PS15, with PS4 chosen.
- **PS4 pipeline:** Track A (U-Net + clDice) and Track B (skeletonize → MST heal → betweenness → Resilience Index → dashboard).
- **Data:** raster vs vector; DeepGlobe, SpaceNet, OSM, Sentinel-2, LISS-IV, Cartosat-3.
- **Tools / workflow:** osmnx, NetworkX, segmentation-models-pytorch, Kaggle/Colab GPU, Albumentations, the NotebookLM loop.
- **Strategy:** scorecard, top-4 comparison, judging criteria, proof of concept.

## Surprising / high-value connections
- **clDice loss ↔ the graph half.** The connectivity-preserving loss isn't just a CV trick — it directly improves the graph you build in Track B. Better-connected masks → fewer gaps to heal → a more trustworthy Resilience Index. One loss function links the two halves.
- **OpenStreetMap ↔ two jobs at once.** OSM is both the *answer key* for training Track A and the *ready-made graph* for Track B. It de-risks both halves with one free, login-free source.
- **Proof of Concept ↔ DeepGlobe + osmnx.** The whole "impress the scientists" move reduces to two scripts: a road prediction (DeepGlobe) and a city graph with a Resilience Index (osmnx). Small inputs, big credibility.
- **NotebookLM ↔ the proposal's technical core.** The research loop is what surfaced clDice and URoadNet — the two ideas that upgraded the approach beyond a generic U-Net.
- **Judging criteria ↔ scope.** "Innovation > scalability" plus "avoid overscoping" is why PS4 (one pilot city, both halves) beat tempting-but-vast options like PS5 (climate twin).

## Questions this graph is positioned to answer
1. What's the single highest-value technical upgrade for PS4, and why does it touch both halves? *(clDice)*
2. What two artifacts turn the deck from idea-only into a proof of concept, and where does their data come from?
3. Which datasets do I need now vs at the finale, and which need logins?
4. Why PS4 over PS8/PS10/PS11 for this specific team?
5. What does each 30-hour sub-team build in parallel?

## The one-line story
**Learn on DeepGlobe → check against OSM → extract roads with U-Net + clDice → heal into a graph → score critical nodes → simulate disasters (Resilience Index) → show it in a dashboard.** That's PS4, and the proposal pitches exactly this.
