import torch
import torch.nn as nn
import torch.nn.functional as F
import segmentation_models_pytorch as smp


class ASPP(nn.Module):
    def __init__(self, in_ch, out_ch=256):
        super().__init__()
        self.b1 = self._branch(in_ch, out_ch, dilation=1)
        self.b6 = self._branch(in_ch, out_ch, dilation=6)
        self.b12 = self._branch(in_ch, out_ch, dilation=12)
        self.b18 = self._branch(in_ch, out_ch, dilation=18)
        self.gap = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(in_ch, out_ch, 1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(out_ch * 5, out_ch, 1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
        )

    @staticmethod
    def _branch(in_ch, out_ch, dilation):
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=dilation, dilation=dilation, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        h, w = x.shape[-2:]
        gap = F.interpolate(self.gap(x), (h, w), mode="bilinear", align_corners=False)
        return self.fuse(torch.cat([self.b1(x), self.b6(x), self.b12(x), self.b18(x), gap], 1))


class DLinkNet(nn.Module):
    def __init__(self, in_channels=4, pretrained=True):
        super().__init__()
        self.base = smp.Unet(
            encoder_name="resnet34",
            encoder_weights="imagenet" if pretrained else None,
            in_channels=3,
            classes=1,
        )

        if in_channels == 4:
            old = self.base.encoder.conv1
            new = nn.Conv2d(4, old.out_channels, old.kernel_size, old.stride, old.padding, bias=False)
            with torch.no_grad():
                new.weight[:, :3] = old.weight
                new.weight[:, 3:] = old.weight.mean(1, keepdim=True)
            self.base.encoder.conv1 = new

        enc_ch = self.base.encoder.out_channels[-1]
        self.aspp = ASPP(enc_ch, enc_ch)

    def forward(self, x):
        features = self.base.encoder(x)
        features[-1] = self.aspp(features[-1])
        decoder_output = self.base.decoder(*features)
        return self.base.segmentation_head(decoder_output)


def build_dlinknet(pretrained=True, in_channels=4):
    return DLinkNet(in_channels=in_channels, pretrained=pretrained)
