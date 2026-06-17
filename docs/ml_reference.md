# ML Reference Guide — SatMesh

Compiled from two sources:
- Google Machine Learning Crash Course (MLCC): https://developers.google.com/machine-learning/crash-course
- Zero to Mastery: Learn PyTorch (learnpytorch.io): https://www.learnpytorch.io

This file covers the concepts directly relevant to the SatMesh pipeline:
satellite image loading → segmentation model → training loop → evaluation.

---

## Part 1 — Foundations (MLCC)

### How a model learns

A model has two kinds of parameters: **weights** (how much each input matters)
and a **bias** (a baseline offset). During training, only these are updated —
the input data is never touched.

The basic update cycle every epoch:
1. Forward pass — run input through the model, get a prediction.
2. Compute loss — measure how wrong the prediction is.
3. Backpropagation — compute the gradient of loss w.r.t. every weight.
4. Gradient descent step — nudge weights in the direction that reduces loss.

### Loss functions

| Situation | Loss to use | Notes |
|---|---|---|
| Regression (continuous output) | MSE / L1 | Penalises distance from target value |
| Binary classification (one class) | BCEWithLogitsLoss | Combines sigmoid + BCE, numerically stable |
| Multi-class classification | CrossEntropyLoss | Applies softmax internally |
| Road segmentation (pixel-wise binary) | Dice + BCE | Dice handles class imbalance (roads are rare pixels) |

**Why Dice loss for segmentation:**
Roads occupy a small fraction of pixels. Plain BCE would let the model score
well by predicting "no road" everywhere. Dice loss computes overlap between
prediction and target, so it forces the model to actually find the roads.

### Overfitting and generalisation

"Data trumps all. The quality and size of the dataset matters much more than
which algorithm you use."

ML practitioners spend roughly 80% of project time on data — not on models.

**The three-split rule:**
- Training set: model learns from this.
- Validation set: tune hyperparameters here. Never let the model optimise for this.
- Test set: evaluate once at the very end. Touch it only once.

**Signs of overfitting:**
- Training loss keeps falling; validation loss stops falling or rises.
- Large gap between training accuracy and validation accuracy.

**Fixes:**
- More training data (or augmentation — synthetic occlusions in our case).
- L2 regularisation: add a penalty proportional to the square of every weight.
- Dropout: randomly zero out neurons during training.
- Early stopping: save the checkpoint where validation loss was lowest.

### Normalisation

Neural networks are sensitive to the scale of inputs. Always normalise image
pixels before training. Standard approach for ImageNet-pretrained models:

```
mean = [0.485, 0.456, 0.406]   # per-channel means
std  = [0.229, 0.224, 0.225]   # per-channel standard deviations
normalised = (pixel / 255 - mean) / std
```

Albumentations `A.Normalize()` applies this automatically.

### Classification metrics

For binary segmentation each pixel is a binary prediction.

```
Precision = TP / (TP + FP)     how many predicted road pixels are actually road
Recall    = TP / (TP + FN)     how many actual road pixels did we find
F1        = 2 * P * R / (P+R)  harmonic mean

IoU (Jaccard) = TP / (TP + FP + FN)   standard segmentation metric
Dice          = 2*TP / (2*TP + FP + FN)  = F1 score for binary masks
```

PS4 specifically rewards **Occlusion-Recall** — how well you recover roads
hidden under tree canopy or shadows. That is just Recall computed only on
pixels that were occluded in the input. The clDice loss targets this directly.

---

## Part 2 — PyTorch Patterns (learnpytorch.io)

### Tensors — the data container

Everything in PyTorch is a tensor.

```python
import torch

# Shape, dtype, device — always check these three when debugging
t = torch.rand(3, 4)
print(t.shape)   # torch.Size([3, 4])
print(t.dtype)   # torch.float32
print(t.device)  # cpu

# Permute image from HWC (numpy/PIL) to CHW (PyTorch)
img = torch.rand(224, 224, 3)
img = img.permute(2, 0, 1)   # -> (3, 224, 224)

# Add/remove a batch dimension
img = img.unsqueeze(0)        # -> (1, 3, 224, 224)
img = img.squeeze(0)          # -> (3, 224, 224)
```

**Three most common tensor bugs:**
1. Wrong dtype — model expects float32, data is uint8.
2. Wrong device — model on GPU, data on CPU (or vice versa).
3. Wrong shape — batch dimension missing, or channels in wrong position.

### Device handling

```python
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():   # Apple Silicon
    device = "mps"
else:
    device = "cpu"

# Move model and data to the same device
model = model.to(device)
x, y  = x.to(device), y.to(device)

# Move back to CPU before converting to numpy
arr = tensor.cpu().numpy()
```

### Building a model

Every model subclasses `nn.Module` and implements `forward()`.

```python
import torch.nn as nn

class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.relu = nn.ReLU()

    def forward(self, x):
        return self.relu(self.conv(x))
```

For SatMesh we use `segmentation_models_pytorch` instead of building from
scratch, but the same pattern applies:

```python
import segmentation_models_pytorch as smp

model = smp.Unet(
    encoder_name="resnet34",
    encoder_weights="imagenet",
    in_channels=3,
    classes=1            # one output channel: road probability
).to(device)
```

### Transfer learning — how the ResNet34 encoder works

The pretrained ResNet34 has already learned to detect edges, textures, and
shapes from 1.2 million ImageNet photos. We keep those weights and only train
the decoder (the upsampling path) on road masks.

```python
# Freeze encoder — only decoder will update
for param in model.encoder.parameters():
    param.requires_grad = False

# Later: unfreeze for fine-tuning
for param in model.encoder.parameters():
    param.requires_grad = True
```

With `segmentation_models_pytorch`, the default is to train everything
end-to-end. Freezing the encoder is useful in the early epochs to stabilise
the decoder, then you unfreeze for fine-tuning.

### Custom Dataset

Subclass `torch.utils.data.Dataset` and implement three methods:

```python
from torch.utils.data import Dataset
import cv2

class RoadDS(Dataset):
    def __init__(self, pairs, transform):
        self.pairs = pairs       # list of (image_path, mask_path)
        self.transform = transform

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, i):
        img_path, msk_path = self.pairs[i]

        img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
        msk = cv2.imread(msk_path, cv2.IMREAD_GRAYSCALE)
        msk = (msk > 127).astype("float32")   # binarise: road=1, background=0

        result = self.transform(image=img, mask=msk)
        return result["image"], result["mask"].unsqueeze(0)   # mask -> (1,H,W)
```

```python
from torch.utils.data import DataLoader

train_dl = DataLoader(
    RoadDS(train_pairs, train_transform),
    batch_size=8,
    shuffle=True,
    num_workers=2,
    pin_memory=True    # faster CPU->GPU transfer
)
```

### Training loop

The five-step loop — in this exact order every batch:

```python
model.train()

for x, y in train_dataloader:
    x, y = x.to(device), y.to(device)

    # 1. Forward pass
    logits = model(x)

    # 2. Compute loss
    loss = loss_fn(logits, y)

    # 3. Zero gradients (must come before backward)
    optimizer.zero_grad()

    # 4. Backward pass
    loss.backward()

    # 5. Update weights
    optimizer.step()
```

A common mistake is forgetting `optimizer.zero_grad()`. Gradients accumulate
by default in PyTorch, so skipping this adds gradients from previous batches.

### Evaluation loop

```python
model.eval()

with torch.inference_mode():   # disables gradient tracking, faster than no_grad
    for x, y in val_dataloader:
        x, y = x.to(device), y.to(device)
        logits = model(x)
        # compute metrics here
```

`model.eval()` switches off dropout and batch-norm running stats.
`torch.inference_mode()` disables the autograd engine entirely — use this
during validation and inference, not during training.

### Binary segmentation output

The model outputs raw **logits** (unbounded real numbers). To get a mask:

```python
probs = torch.sigmoid(logits)      # -> [0, 1] probability per pixel
mask  = (probs > 0.5).float()      # -> binary road mask
```

Do not apply sigmoid before passing logits to `BCEWithLogitsLoss` —
that loss applies sigmoid internally, and applying it twice will break training.

### IoU and Dice — computing them in PyTorch

```python
def iou_dice(logits, target, threshold=0.5):
    pred  = (torch.sigmoid(logits) > threshold).float()
    inter = (pred * target).sum((1, 2, 3))
    union = ((pred + target) > 0).float().sum((1, 2, 3))
    iou   = ((inter + 1e-6) / (union + 1e-6)).mean()
    dice  = ((2 * inter + 1e-6) /
             (pred.sum((1,2,3)) + target.sum((1,2,3)) + 1e-6)).mean()
    return iou.item(), dice.item()
```

The `1e-6` smoothing term prevents division by zero on empty masks.

### Saving and loading checkpoints

```python
# Save — store state_dict, not the whole model object
torch.save(model.state_dict(), "best_model.pth")

# Load
model.load_state_dict(torch.load("best_model.pth", map_location=device))
model.eval()
```

Never save the full model object (`torch.save(model, ...)`). The state dict
is portable; the object is tied to the exact file structure at save time.

### Reproducibility

```python
import random, numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)   # if using GPU
```

Set these at the top of every script before any tensor operations.

### Optimisers and LR schedules

```python
# AdamW — Adam with decoupled weight decay, better than plain Adam for CV
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

# OneCycleLR — starts low, peaks, then decays; converges faster in fewer epochs
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer,
    max_lr=1e-3,
    steps_per_epoch=len(train_dataloader),
    epochs=EPOCHS
)

# Call scheduler.step() after optimizer.step() inside the batch loop
optimizer.step()
scheduler.step()
```

---

## Part 3 — Augmentation with Albumentations

Albumentations applies the same transform to both the image and its mask,
which is critical for segmentation (a random flip must flip both).

```python
import albumentations as A
from albumentations.pytorch import ToTensorV2

train_transform = A.Compose([
    A.Resize(256, 256),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomRotate90(p=0.5),
    # Occlusion simulation (SatMesh-specific)
    A.RandomShadow(p=0.4),           # simulates building / hill shadows
    A.CoarseDropout(max_holes=8, max_height=32, max_width=32,
                    fill_value=0, p=0.5),   # simulates tree canopy blackouts
    # Colour jitter
    A.ColorJitter(brightness=0.2, contrast=0.2,
                  saturation=0.2, hue=0.1, p=0.4),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
    A.Normalize(),     # applies ImageNet mean/std
    ToTensorV2(),
])

# Apply to image+mask pair
result = train_transform(image=img_array, mask=mask_array)
image_tensor = result["image"]   # (3, H, W) float32
mask_tensor  = result["mask"]    # (H, W) float32
```

---

## Part 4 — Quick reference: what goes where in SatMesh

| Pipeline step | Concept | Where in code |
|---|---|---|
| Load image + mask | Custom Dataset | `track_a/road_segmentation.py` → `RoadDS` |
| Augmentation | Albumentations Compose | `train_tf` in `road_segmentation.py` |
| Model | U-Net + ResNet34 | `smp.Unet(...)` |
| Loss | Dice + BCE + clDice | `cl_dice_loss()` + `smp.losses.DiceLoss` |
| Optimiser | AdamW + OneCycleLR | after model init |
| Training loop | 5-step pattern | `for ep in range(EPOCHS)` |
| Evaluation | IoU + Dice, `model.eval()` + `inference_mode` | val loop |
| Checkpoint | `torch.save(model.state_dict(), ...)` | on best val IoU |
| Inference | `torch.sigmoid(logits) > 0.5` | visualisation block |
