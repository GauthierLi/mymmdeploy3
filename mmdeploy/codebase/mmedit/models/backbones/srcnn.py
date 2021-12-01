# Copyright (c) OpenMMLab. All rights reserved.
import torch.nn as nn

from mmdeploy.core import MODULE_REWRITER


@MODULE_REWRITER.register_rewrite_module(
    'mmedit.models.backbones.sr_backbones.SRCNN', backend='tensorrt')
class SRCNN__tensorrt(nn.Module):
    """Rewrite `SRCNN` for tensorrt backend.

    SRCNN has three conv layers. For each layer, we can define the
    `in_channels`, `out_channels` and `kernel_size`.The input image will
    first be upsampled with a bicubic upsampler, and then super-resolved
    in the HR spatial size.
    Because TensorRT doesn't support bicubic operator, when deployment we use
    bilinear instead. According to the experiments, the precision may decrease
    about 4%.
    Paper: Learning a Deep Convolutional Network for Image Super-Resolution.

    Args:
        module (nn.Module): Source SRCNN module.
        channels (tuple[int]): A tuple of channel numbers for each layer
            including channels of input and output . Default: (3, 64, 32, 3).
        kernel_sizes (tuple[int]): A tuple of kernel sizes for each conv layer.
            Default: (9, 1, 5).
        upscale_factor (int): Upsampling factor. Default: 4.
    """

    def __init__(self,
                 module,
                 channels=(3, 64, 32, 3),
                 kernel_sizes=(9, 1, 5),
                 upscale_factor=4):
        super(SRCNN__tensorrt, self).__init__()

        self._module = module

        module.img_upsampler = nn.Upsample(
            scale_factor=module.upscale_factor,
            mode='bilinear',
            align_corners=False)

    def forward(self, *args, **kwargs):
        """Run forward."""
        return self._module(*args, **kwargs)

    def init_weights(self, *args, **kwargs):
        """Initialize weights."""
        return self._module.init_weights(*args, **kwargs)