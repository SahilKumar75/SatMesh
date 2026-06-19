# D-LinkNet — LinkNet with Pretrained Encoder and Dilated Convolution

**Citation.** Zhou, L., Zhang, C., Wu, M. *D-LinkNet: LinkNet with Pretrained Encoder and Dilated Convolution for High Resolution Satellite Imagery Road Extraction.* CVPR Workshops (DeepGlobe), 2018. — Winner, DeepGlobe 2018 Road Extraction Challenge.

**Core claim.** A LinkNet encoder–decoder with an ImageNet-pretrained ResNet backbone and a dilated-convolution center block preserves both fine road detail and large receptive-field context, which is exactly what thin, long, connected roads need.

## Key ideas / equations

- **Dilated convolution** expands receptive field without losing resolution. For dilation rate `r`, the effective kernel size of a `k×k` filter is:
  ```
  k_eff = k + (k - 1)(r - 1)
  ```
  Stacking parallel branches at rates `r ∈ {1, 2, 4, 8}` (cascade + parallel) covers receptive fields from a single pixel up to most of the tile.

- **Encoder skip + residual decoder (LinkNet form).** Each decoder stage adds back the matching encoder feature instead of concatenating, keeping the parameter count low:
  ```
  D_i = Up(D_{i+1}) + E_i
  ```

- **Loss.** BCE + Dice on the road/background mask; Dice counters the heavy class imbalance (roads are a small fraction of pixels).

## What it changes in SatMesh

`src/model/dlinknet.py` builds on an SMP ResNet34 encoder, replaces the bottleneck with an **ASPP** center block (dilation rates `[1, 6, 12, 18]` + global pooling) and wraps each skip with a 1×1 **LinkConv** residual. The first conv is widened to **4 channels (RGB + NIR)**, with the NIR weight initialized as the mean of the pretrained RGB weights to keep ImageNet priors. This is the architectural backbone of Track A.

## Judge talking point

A plain U-Net/ResNet34 has a fixed, small receptive field and breaks long roads into disconnected blobs. D-LinkNet's dilated center block sees the whole road corridor at once — which is the difference between a mask that skeletonizes into a connected graph and one that doesn't. It won DeepGlobe for exactly this reason.
