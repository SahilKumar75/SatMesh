import torch
import torch.nn.functional as F
import segmentation_models_pytorch as smp


def _soft_erode(x):
    return -F.max_pool2d(-x, kernel_size=3, stride=1, padding=1)


def _soft_dilate(x):
    return F.max_pool2d(x, kernel_size=3, stride=1, padding=1)


def soft_skel(x, iters=5):
    skel = F.relu(x - _soft_dilate(_soft_erode(x)))
    for _ in range(iters - 1):
        x = _soft_erode(x)
        delta = F.relu(x - _soft_dilate(_soft_erode(x)))
        skel = skel + F.relu(delta - skel * delta)
    return skel


def skeleton_recall_loss(pred_logits, target, iters=5):
    """Skeleton Recall Loss (Shit et al., ECCV 2024 — arxiv 2404.03010).

    One-directional: GT skeleton × pred. Better than clDice for road connectivity.
    Only activate after epoch 10 — early random predictions destabilize training.
    """
    pred = torch.sigmoid(pred_logits)
    st = soft_skel(target, iters)
    recall = (st * pred).sum() / (st.sum() + 1e-6)
    return 1.0 - recall


_dice = smp.losses.DiceLoss(mode="binary")


def combined_loss(logits, target, use_skelrecall=True,
                  w_dice=0.40, w_bce=0.30, w_skelrecall=0.30):
    pw = torch.tensor([5.0], device=logits.device)
    bce = F.binary_cross_entropy_with_logits(logits, target, pos_weight=pw)
    loss = w_dice * _dice(logits, target) + w_bce * bce
    if use_skelrecall:
        loss = loss + w_skelrecall * skeleton_recall_loss(logits, target)
    return loss
