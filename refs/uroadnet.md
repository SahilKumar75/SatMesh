# URoadNet — Dual Sparse Attentive U-Net for Multiscale Road Extraction

**Citation.** *URoadNet: Dual Sparse Attention U-Net for road extraction from remote sensing imagery* (2024). Multiscale connectivity-aware road segmentation.

**Core claim.** Roads need both *local* continuity (a lane stays a lane) and *global* connectivity (a highway crosses the whole tile); a dual sparse-attention U-Net models connectivity and integrality jointly, beating single-scale CNNs on long-range road continuity.

## Key ideas

- **Sparse connectivity attention** restricts attention to a sparse neighborhood along road direction, so the model propagates "this is the same road" over long distances at tractable cost (full dense attention over a tile is `O(N²)` in pixels — infeasible at 10 m/512 px).

- **Dual branches** — a connectivity branch (long, thin structure) and an integrality branch (filling the road body) — fused at the decoder:
  ```
  out = Decoder( f_connectivity ⊕ f_integrality )
  ```

- Attention complexity reduced from dense `O(N²)` to sparse `O(N·k)` for `k` selected tokens.

## What it changes in SatMesh

URoadNet motivates the **multiscale receptive field** decision: our D-LinkNet ASPP center block (dilation `[1,6,12,18]` + global pool) is the lightweight stand-in for sparse long-range attention — it captures the same multiscale road context without the attention machinery, which matters under a hackathon T4 budget. It is the fallback/comparison architecture documented for the slide deck; D-LinkNet is what we actually train.

## Judge talking point

We chose D-LinkNet's dilated context over a full attention model deliberately: same multiscale benefit, a fraction of the compute, trainable on a free Kaggle T4 in ~25 min. URoadNet is where we'd go with more GPU — naming it shows we know the frontier and made a defensible budget trade-off, not an ignorant one.

See also [[dlinknet-cvpr2018]] (the architecture we ship) and [[sam-road-graph-2024]] (the other extraction paradigm we evaluated).
