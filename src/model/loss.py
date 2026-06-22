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
    """One-directional skeleton recall (GT skeleton x pred). Kept for reference;
    superseded by soft_cldice_loss which also penalises hallucinated roads."""
    pred = torch.sigmoid(pred_logits)
    st = soft_skel(target, iters)
    recall = (st * pred).sum() / (st.sum() + 1e-6)
    return 1.0 - recall


def soft_cldice_loss(pred_logits, target, iters=6, smooth=1e-5):
    """Soft clDice — topology-preserving connectivity loss (Shit et al., CVPR 2021,
    arxiv 2003.07311). Bidirectional: Tprec (pred skeleton inside GT) penalises
    hallucinated roads, Tsens (GT skeleton inside pred) penalises broken roads.
    Stable from epoch 1; ~-24% topology error on road datasets. iters should exceed
    the max road half-width in px.
    """
    pred = torch.sigmoid(pred_logits)
    sp = soft_skel(pred, iters)
    st = soft_skel(target, iters)
    tprec = (sp * target).sum() / (sp.sum() + smooth)
    tsens = (st * pred).sum() / (st.sum() + smooth)
    cldice = 2.0 * tprec * tsens / (tprec + tsens + smooth)
    return 1.0 - cldice


_dice = smp.losses.DiceLoss(mode="binary")


def combined_loss(logits, target, use_topo=True,
                  w_dice=0.40, w_bce=0.30, w_topo=0.30):
    """Dice + weighted-BCE + soft-clDice. clDice runs every epoch (it is bounded
    and stable), replacing the old epoch-10 skeleton-recall switch that spiked loss."""
    pw = torch.tensor([5.0], device=logits.device)
    bce = F.binary_cross_entropy_with_logits(logits, target, pos_weight=pw)
    loss = w_dice * _dice(logits, target) + w_bce * bce
    if use_topo:
        loss = loss + w_topo * soft_cldice_loss(logits, target)
    return loss
