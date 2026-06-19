# clDice — Topology-Preserving Loss for Tubular Structure Segmentation

**Citation.** Shit, S., Paetzold, J. C., et al. *clDice — A Novel Topology-Preserving Loss Function for Tubular Structure Segmentation.* CVPR 2021.

**Core claim.** Optimizing overlap (Dice/IoU) alone lets a network leave tiny gaps that wreck connectivity; measuring overlap between predicted/ground-truth **skeletons** instead directly rewards an unbroken centerline, guaranteeing topological correctness for tube-like structures (roads, vessels).

## Key equations

- **Topology precision / sensitivity** between a mask `V` and a skeleton `S`:
  ```
  Tprec(S_P, V_L) = |S_P ∩ V_L| / |S_P|
  Tsens(S_L, V_P) = |S_L ∩ V_P| / |S_L|
  ```
  (`P` = prediction, `L` = label/ground truth.)

- **clDice** is their harmonic mean:
  ```
  clDice = 2 · (Tprec · Tsens) / (Tprec + Tsens)
  ```

- **Differentiable skeleton** via iterative soft morphology (min/max-pool surrogates of erosion/dilation), so the whole thing is trainable end-to-end:
  ```
  soft_skel(I) = Σ_k  relu( I_k − maxpool(minpool(I_k)) )
  ```

## What it changes in SatMesh

`src/model/loss.py` ports `soft_skel` and `cl_dice_loss` and combines them:
```
combined = w_dice·Dice + w_bce·BCE + w_cldice·clDice   (default 0.35 / 0.30 / 0.35)
```
clDice is upweighted vs a naive baseline because **topology, not pixel overlap, is what the graph metric (APLS) and Occlusion-Recall actually measure.** A single healed gap is worth more to the score than a few extra correct pixels.

## Judge talking point

Two masks can have identical IoU but one has a 2-pixel break that severs a road and the other doesn't. clDice penalizes that break explicitly — it optimizes the same thing the Track-B graph is built on. This is why our masks skeletonize into connected graphs with high APLS instead of fragmented stubs.

See also [[apls-spacenet5]] (the graph metric clDice indirectly optimizes) and [[dlinknet-cvpr2018]] (the architecture it trains).
