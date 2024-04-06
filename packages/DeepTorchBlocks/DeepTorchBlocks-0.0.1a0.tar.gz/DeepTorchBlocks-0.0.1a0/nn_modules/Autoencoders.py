"""
Autoencoders - PyTorch modules (inheriting nn.Module) for Encoders/Decoders layering
(Sphynx Docstrings)
"""

__version__ = "0.0.1"


import torch
import torch.nn as nn
from Standard import ConvBlock

device = 'cuda' if torch.cuda.is_available() else 'cpu'


# ------------------------------------------------------- U-Net --------------------------------------------------------
class UNetEncoder(nn.Module):
    def __init__(self, channels, kernel_size, activation, device=device):
        """Creates a Pytorch module comprising a 2xConvolutional layer, followed by Batch-Normalization
        and an arbitrary activation function, with a MaxPooling stage. It is referred to as the U-Net Encoder.
        (see O. Ronneberger et al. - "U-Net: Convolutional Networks for Biomedical Image Segmentation",
        https://arxiv.org/pdf/1505.04597.pdf)

        :param channels     : Input channels for each encoding stage (including input channels)
        :type channels      : list
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param activation   : Output activation function (w. attributes), defaults to nn.ReLU()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(UNetEncoder, self).__init__()
        self.stages = len(channels)
        self.layers = nn.ModuleDict()

        for stage in range(self.stages - 1):
            self.layers[f'{stage + 1}_ConvBlock_1'] = ConvBlock(in_channels=channels[stage],
                                                                out_channels=channels[stage + 1],
                                                                kernel_size=kernel_size,
                                                                stride=1,
                                                                padding='same',
                                                                activation=activation,
                                                                device=device)
            self.layers[f'{stage + 1}_ConvBlock_2'] = ConvBlock(in_channels=channels[stage + 1],
                                                                out_channels=channels[stage + 1],
                                                                kernel_size=kernel_size,
                                                                stride=1,
                                                                padding='same',
                                                                activation=activation,
                                                                device=device)
            self.layers[f'{stage + 1}_DWN_MaxPool'] = nn.MaxPool2d(kernel_size=2, stride=2)

    def forward(self, x):
        """Forward method

        :param x            : Input Tensor (batch_size, in_channels, height, width)
        :type x             : torch.Tensor
        :return last_x      : Output Tensor (batch_size, channels[-1], height / (2**len(channels)), width / (2**len(channels)))
        :rtype last_x       : torch.Tensor
        :return last_p      : Output Tensor (batch_size, channels[-1], height / (2**len(channels)), width / (2**len(channels)))
        :rtype last_p       : torch.Tensor
        :return stages_out  : List of Convolutional stages outputs (len(channels) torch.Tensor(s))
        :rtype stages_out   : list
        """
        stages_out = []
        for stage in range(self.stages - 1):
            x = self.layers[f'{stage + 1}_ConvBlock_1'](x)
            x = self.layers[f'{stage + 1}_ConvBlock_2'](x)

            # Place output tensor from 2nd Convolutional stage
            last_x = x
            stages_out.append(x)

            # MaxPooling
            x = self.layers[f'{stage + 1}_DWN_MaxPool'](x)

            # Place output tensor from Pooling stage
            last_p = x

        return last_x, last_p, stages_out


class UNetDecoder(nn.Module):
    def __init__(self, channels, kernel_size, activation, device=device):
        """Creates a Pytorch module comprising a de-Convolutional layer, followed by 2xConvBlocks
        w. an arbitrary activation function. It is referred to as the U-Net Decoder.
        (see O. Ronneberger et al. - "U-Net: Convolutional Networks for Biomedical Image Segmentation",
        https://arxiv.org/pdf/1505.04597.pdf)

        :param channels     : Input channels for each encoding stage (including input channels)
        :type channels      : list
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param activation   : Output activation function (w. attributes), defaults to nn.ReLU()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(UNetDecoder, self).__init__()
        self.stages = len(channels)
        self.layers = nn.ModuleDict()

        for stage in range(len(channels) - 1):
            self.layers[f'{stage + 1}_UpConv_Block'] = nn.ConvTranspose2d(channels[stage],
                                                                          channels[stage + 1],
                                                                          kernel_size=2,
                                                                          stride=2,
                                                                          padding=0)

            self.layers[f'{stage + 1}_ConvBlock_1'] = ConvBlock(in_channels=channels[stage],
                                                                out_channels=channels[stage + 1],
                                                                kernel_size=kernel_size,
                                                                stride=1,
                                                                padding='same',
                                                                activation=activation,
                                                                device=device)

            self.layers[f'{stage + 1}_ConvBlock_2'] = ConvBlock(in_channels=channels[stage + 1],
                                                                out_channels=channels[stage + 1],
                                                                kernel_size=kernel_size,
                                                                stride=1,
                                                                padding='same',
                                                                activation=activation,
                                                                device=device)

    def forward(self, x, skip):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :param skip : Intermediate encoding tensors
        :type       : torch.Tensor
        :return x   : Output Tensor (batch_size, channels[-1], input_height, input_width)
        :rtype x    : torch.Tensor
        """
        for stage in range(self.stages):
            x = self.layers[f'{stage + 1}_UpConv_Block'](x)
            x = torch.cat((x, skip[::-1][1:]), axis=1)
            x = self.layers[f'{stage + 1}_ConvBlock_1'](x)
            x = self.layers[f'{stage + 1}_ConvBlock_2'](x)

            return x
