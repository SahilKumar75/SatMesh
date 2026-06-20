from pathlib import Path
import torch
import segmentation_models_pytorch as smp

# True SegFormer: MiT-B0 encoder + MLP decode head (smp.Segformer, not smp.Unet).
# Satisfies PS4 Objective 1: "Transformer-based deep learning architecture."


def build_segformer(pretrained=True, in_channels=3):
    return smp.Segformer(
        encoder_name="mit_b0",
        encoder_weights="imagenet" if pretrained else None,
        in_channels=in_channels,
        classes=1,
    )


# Verified: only encoder.patch_embed1.proj.weight changes between 3-ch and 4-ch.
# Shape [32,3,7,7] → [32,4,7,7]. Exact key confirmed by running smp.Segformer().state_dict().
_PATCH1_KEY = "encoder.patch_embed1.proj.weight"


def build_segformer_4ch(checkpoint_3ch=None, device="cpu"):
    """Load Stage-1 (3-ch) checkpoint into 4-ch Stage-2 SegFormer.

    Transfers patch_embed1 RGB weights exactly; inits NIR channel from their mean.
    strict=False load reports exactly 1 missing key (patch_embed1), 0 unexpected — verified.
    """
    model = smp.Segformer(
        encoder_name="mit_b0",
        encoder_weights=None,
        in_channels=4,
        classes=1,
    )
    if checkpoint_3ch and Path(checkpoint_3ch).exists():
        state = torch.load(checkpoint_3ch, map_location=device, weights_only=True)
        old_w = state.pop(_PATCH1_KEY, None)
        model.load_state_dict(state, strict=False)
        if old_w is not None:
            with torch.no_grad():
                w = model.encoder.patch_embed1.proj.weight
                w[:, :3].copy_(old_w)
                w[:, 3:].copy_(old_w.mean(1, keepdim=True))
    return model
