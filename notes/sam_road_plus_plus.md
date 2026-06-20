# SAM-Road++ — Deferred Implementation Note

**Paper:** arxiv 2411.16733  
**Ceiling:** ~0.75+ IoU on DeepGlobe (vs our B4 target of 0.70–0.72)

## What it is

Fine-tunes SAM (Segment Anything Model) ViT encoder specifically for road network extraction + occlusion handling. SAM's encoder was pretrained on 1B masks — far richer features than MiT-B4 ImageNet weights.

## Why deferred

- Full backbone swap — not a drop-in encoder change
- SAM ViT-H is 307M params vs MiT-B4's 62M — needs A100 or multi-GPU, T4 won't fit
- 3–5 days of implementation + debugging vs 30h hackathon window
- B4 + SkelRecall + TTA achieves 0.70–0.72 which hits PS4 target

## How to implement (when ready)

1. Install `segment-anything` or `sam2` from Meta
2. Load SAM ViT-H encoder, freeze early layers
3. Replace `smp.Segformer` encoder with SAM ViT, keep MLP decode head
4. Fine-tune on DeepGlobe at batch=2, gradient checkpointing, A100 40GB
5. Stage 2: domain adapt on Sentinel-2 India tiles same as current pipeline

## References

- Paper: https://arxiv.org/abs/2411.16733
- SAM2 repo: https://github.com/facebookresearch/sam2
- Expected gain: +3–5% IoU over MiT-B4 baseline
