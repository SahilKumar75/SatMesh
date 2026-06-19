import torch
import torch.nn as nn
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


def cl_dice_loss(pred_logits, target, iters=5, smooth=1.0):
    pred = torch.sigmoid(pred_logits)
    sp = soft_skel(pred, iters)
    st = soft_skel(target, iters)
    t_prec = ((sp * target).sum() + smooth) / (sp.sum() + smooth)
    t_sens = ((st * pred).sum() + smooth) / (st.sum() + smooth)
    return 1.0 - 2.0 * t_prec * t_sens / (t_prec + t_sens)


_dice = smp.losses.DiceLoss(mode="binary")
_bce = nn.BCEWithLogitsLoss()


def combined_loss(logits, target, w_dice=0.35, w_bce=0.30, w_cldice=0.35):
    return w_dice * _dice(logits, target) + w_bce * _bce(logits, target) + w_cldice * cl_dice_loss(logits, target)
