from pathlib import Path
import torch
import segmentation_models_pytorch as smp

# True SegFormer: MiT-B0 encoder + MLP decode head (smp.Segformer, not smp.Unet).
# Satisfies PS4 Objective 1: "Transformer-based deep learning architecture."


def build_segformer(pretrained=True, in_channels=3, encoder_name="mit_b0"):
    return smp.Segformer(
        encoder_name=encoder_name,
        encoder_weights="imagenet" if pretrained else None,
        in_channels=in_channels,
        classes=1,
    )


# patch_embed1.proj.weight key is identical across MiT-B0 through B5.
_PATCH1_KEY = "encoder.patch_embed1.proj.weight"


def build_segformer_multiclass(num_classes=4, checkpoint_binary=None,
                               device="cpu", encoder_name="mit_b0"):
    """SegFormer with num_classes output channels for semantic segmentation.

    If checkpoint_binary is given (a 1-class binary road model), transfers all
    encoder + decoder weights and reinitialises the segmentation head randomly.
    This gives a warm encoder start without shape mismatch on the head.
    """
    model = smp.Segformer(
        encoder_name=encoder_name,
        encoder_weights=None,
        in_channels=3,
        classes=num_classes,
    )
    if checkpoint_binary and Path(checkpoint_binary).exists():
        state = torch.load(checkpoint_binary, map_location=device, weights_only=True)
        # Drop segmentation head keys (shape [1,…] won't match [num_classes,…])
        state = {k: v for k, v in state.items()
                 if not k.startswith("segmentation_head")}
        model.load_state_dict(state, strict=False)
        print(f"[multiclass] loaded encoder+decoder from {checkpoint_binary}; head reinit")
    return model


def build_segformer_4ch(checkpoint_3ch=None, device="cpu", encoder_name="mit_b0"):
    """Load Stage-1 (3-ch) checkpoint into 4-ch Stage-2 SegFormer.

    Transfers patch_embed1 RGB weights exactly; inits NIR channel from their mean.
    strict=False load reports exactly 1 missing key (patch_embed1), 0 unexpected — verified.
    """
    model = smp.Segformer(
        encoder_name=encoder_name,
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
