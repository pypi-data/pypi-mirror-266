"""
Inception - PyTorch modules (inheriting nn.Module) for Inception (GoogLeNet) blocks layering
(Sphynx Docstrings)
"""

__version__ = "0.0.1"


import torch
import torch.nn as nn
from Standard import ConvBlock

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class V1Block(nn.Module):
    def __init__(self, in_channels, in_5x5, out_5x5, in_3x3, out_3x3, out_1x1_pool, out_1x1, activation, device=device):
        """Creates a Pytorch module consisting of parallelized ConvBlock instances. It is called Inception Block V1.
        (see C. Szegedy - "Going Deeper with Convolutions", https://arxiv.org/pdf/1409.4842.pdf)

        :param in_channels      : Input tensor channels
        :type in_channels       : int
        :param in_5x5           : 1st branch feature map input channels
        :type in_5x5            : int
        :param out_5x5          : 1st branch feature map output channels
        :type out_5x5           : int
        :param in_3x3           : 2nd branch feature map input channels
        :type in_3x3            : int
        :param out_3x3          : 2nd branch feature map output channels
        :type out_3x3           : int
        :param out_1x1_pool     : 3rd branch feature map output channels
        :type out_1x1_pool      : int
        :param out_1x1          : 4th branch feature map output channels
        :type out_1x1           : int
        :param activation       : Common output activation function (w. attributes), defaults to nn.ReLU()
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(V1Block, self).__init__()
        self.branch_1 = nn.ModuleDict()
        self.branch_2 = nn.ModuleDict()
        self.branch_3 = nn.ModuleDict()
        self.branch_4 = nn.ModuleDict()

        # Branch n.1: 1D_Conv (k=1, s=1, p=0) --> 5x5_Conv (k=5, s=1, p=2)
        self.branch_1['1D_2_5x5Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                out_channels=in_5x5,
                                                                kernel_size=1,
                                                                stride=1,
                                                                padding=0,
                                                                activation=activation,
                                                                device=device),
                                                      ConvBlock(in_channels=in_5x5,
                                                                out_channels=out_5x5,
                                                                kernel_size=5,
                                                                stride=1,
                                                                padding=2,
                                                                activation=activation,
                                                                device=device))

        # Branch n.2: 1D_Conv (k=1, s=1, p=0) --> 3x3_Conv (k=3, s=1, p=1)
        self.branch_2['1D_2_3x3Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                out_channels=in_3x3,
                                                                kernel_size=1,
                                                                stride=1,
                                                                padding=0,
                                                                activation=activation,
                                                                device=device),
                                                      ConvBlock(in_channels=in_3x3,
                                                                out_channels=out_3x3,
                                                                kernel_size=3,
                                                                stride=1,
                                                                padding=1,
                                                                activation=activation,
                                                                device=device))

        # Branch n.3: MaxPooling (k=3, s=1, p=1) --> 1D_Conv (k=1, s=1, p=0)
        self.branch_3['pool_2_1D_Conv'] = nn.Sequential(nn.MaxPool2d(kernel_size=3,
                                                                     stride=1,
                                                                     padding=1,
                                                                     return_indices=False,
                                                                     ceil_mode=False).to(device),
                                                        ConvBlock(in_channels,
                                                                  out_channels=out_1x1_pool,
                                                                  kernel_size=1,
                                                                  stride=1,
                                                                  padding=0,
                                                                  activation=activation,
                                                                  device=device))

        # Branch n.4: 1D Conv (k=1, s=1, p=0)
        self.branch_4['1D_Conv'] = ConvBlock(in_channels,
                                             out_channels=out_1x1,
                                             kernel_size=1,
                                             stride=1,
                                             padding=0,
                                             activation=activation,
                                             device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output Tensor (batch_size, out_5x5 + out_3x3 + out_1x1_pool + out_1x1, height, width)
        :rtype      : torch.Tensor
        """
        out_1 = self.branch_1['1D_2_5x5Conv'](x)
        out_2 = self.branch_2['1D_2_3x3Conv'](x)
        out_3 = self.branch_3['pool_2_1D_Conv'](x)
        out_4 = self.branch_4['1D_Conv'](x)

        # Output concatenation
        out = torch.cat([out_1, out_2, out_3, out_4], dim=1)

        return out


class V25Block(nn.Module):
    def __init__(self, in_channels, in_3x3, int_3x3, out_3x3, in2_3x3, out2_3x3, out_1x1_pool, out_1x1, activation, device=device):
        """Creates a Pytorch module consisting of refactored parallelized ConvBlock instances.
        It is referred to as Inception Block V2.5 (Figure 5).
        (see C. Szegedy - "Rethinking the Inception Architecture for Computer Vision", https://arxiv.org/pdf/1512.00567v3.pdf)

        :param in_channels      : Input tensor channels
        :type in_channels       : int
        :param in_3x3           : 1st branch feature map input channels
        :type in_3x3            : int
        :param int_3x3          : 1st branch feature map intermediate channels
        :type int_3x3           : int
        :param out_3x3          : 1st branch feature map output channels
        :type out_3x3           : int
        :param in2_3x3          : 2nd branch feature map input channels
        :type in2_3x3           : int
        :param out2_3x3         : 2nd branch feature map output channels
        :type out2_3x3          : int
        :param out_1x1_pool     : 3rd branch feature map output channels
        :type out_1x1_pool      : int
        :param out_1x1          : 4th branch feature map output channels
        :type out_1x1           : int
        :param activation       : Common output activation function (w. attributes), defaults to nn.ReLU()
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(V25Block, self).__init__()
        self.branch_1 = nn.ModuleDict()
        self.branch_2 = nn.ModuleDict()
        self.branch_3 = nn.ModuleDict()
        self.branch_4 = nn.ModuleDict()

        # Branch n.1: 1D_Conv (k=1, s=1, p=0) --> 3x3_Conv (k=3, s=1, p=1) --> 3x3_Conv (k=3, s=1, p=1)
        self.branch_1['1D_to_3x3_to_3x3Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                        out_channels=in_3x3,
                                                                        kernel_size=1,
                                                                        stride=1,
                                                                        padding=0,
                                                                        activation=activation,
                                                                        device=device),
                                                              ConvBlock(in_channels=in_3x3,
                                                                        out_channels=int_3x3,
                                                                        kernel_size=3,
                                                                        stride=1,
                                                                        padding=1,
                                                                        activation=activation,
                                                                        device=device),
                                                              ConvBlock(in_channels=int_3x3,
                                                                        out_channels=out_3x3,
                                                                        kernel_size=3,
                                                                        stride=1,
                                                                        padding=1,
                                                                        activation=activation,
                                                                        device=device))

        # Branch n.2: 1D_Conv (k=1, s=1, p=0) --> 3x3_Conv (k=3, s=1, p=1)
        self.branch_2['1D_to_3x3Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                 out_channels=in2_3x3,
                                                                 kernel_size=1,
                                                                 stride=1,
                                                                 padding=0,
                                                                 activation=activation,
                                                                 device=device),
                                                       ConvBlock(in_channels=in2_3x3,
                                                                 out_channels=out2_3x3,
                                                                 kernel_size=3,
                                                                 stride=1,
                                                                 padding=1,
                                                                 activation=activation,
                                                                 device=device))

        # Branch n.3: MaxPooling (k=3, s=1, p=1) --> 1D_Conv (k=1, s=1, p=0)
        self.branch_3['MaxPooling_to_1D_Conv'] = nn.Sequential(nn.MaxPool2d(kernel_size=3,
                                                                            stride=1,
                                                                            padding=1,
                                                                            return_indices=False,
                                                                            ceil_mode=False).to(device),
                                                               ConvBlock(in_channels,
                                                                         out_channels=out_1x1_pool,
                                                                         kernel_size=1,
                                                                         stride=1,
                                                                         padding=0,
                                                                         activation=activation,
                                                                         device=device))

        # Branch n.4: 1D Conv (k=1, s=1, p=0)
        self.branch_4['1D_Conv'] = ConvBlock(in_channels,
                                             out_channels=out_1x1,
                                             kernel_size=1,
                                             stride=1,
                                             padding=0,
                                             activation=activation,
                                             device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return out : Output Tensor (batch_size, out_3x3 + out2_3x3 + out_1x1_pool + out_1x1, height, width)
        :rtype out  : torch.Tensor
        """
        out_1 = self.branch_1['1D_to_3x3_to_3x3Conv'](x)
        out_2 = self.branch_2['1D_to_3x3Conv'](x)
        out_3 = self.branch_3['MaxPooling_to_1D_Conv'](x)
        out_4 = self.branch_4['1D_Conv'](x)

        # Concatenation on dim=1
        out = torch.cat([out_1, out_2, out_3, out_4], dim=1)

        return out


# (Could be progressively generalized finding how many ConvBlocks are required w.r.t. kernel size (now 7x7)
class V26Block(nn.Module):
    def __init__(self, in_channels, int_channels, out_channels, kernel_size, activation, device=device):
        """Creates a Pytorch module consisting of a generalized kernel-dependent refactored parallelized ConvBlock instances.
        It is referred to as Inception Block V2.6 (Figure 6).
        (see C. Szegedy - "Rethinking the Inception Architecture for Computer Vision", https://arxiv.org/pdf/1512.00567v3.pdf)

        :param in_channels      : Input tensor channels
        :type in_channels       : int
        :param int_channels     : Intermediate feature map channels
        :type int_channels      : int
        :param out_channels     : Output tensor channels
        :type out_channels      : int
        :param kernel_size      : Convolutional linear kernel (filter) dimension, default should be 7
        :type kernel_size       : int
        :param activation       : Common output activation function (w. attributes), defaults to nn.ReLU()
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(V26Block, self).__init__()
        self.branch_1 = nn.ModuleDict()
        self.branch_2 = nn.ModuleDict()
        self.branch_3 = nn.ModuleDict()
        self.branch_4 = nn.ModuleDict()

        # Branch n.1: Short term features map
        self.branch_1['1D_to_2x(1xN_to_Nx1Conv)'] = nn.Sequential(ConvBlock(in_channels,
                                                                            out_channels=int_channels,
                                                                            kernel_size=1,
                                                                            stride=1,
                                                                            padding=0,
                                                                            activation=activation,
                                                                            device=device),
                                                                  ConvBlock(in_channels=int_channels,
                                                                            out_channels=int_channels,
                                                                            kernel_size=(1, kernel_size),
                                                                            stride=1,
                                                                            padding='same',
                                                                            activation=activation,
                                                                            device=device),
                                                                  ConvBlock(in_channels=int_channels,
                                                                            out_channels=int_channels,
                                                                            kernel_size=(kernel_size, 1),
                                                                            stride=1,
                                                                            padding='same',
                                                                            activation=activation,
                                                                            device=device),
                                                                  ConvBlock(in_channels=int_channels,
                                                                            out_channels=int_channels,
                                                                            kernel_size=(1, kernel_size),
                                                                            stride=1,
                                                                            padding='same',
                                                                            activation=activation,
                                                                            device=device),
                                                                  ConvBlock(in_channels=int_channels,
                                                                            out_channels=out_channels,
                                                                            kernel_size=(kernel_size, 1),
                                                                            stride=1,
                                                                            padding='same',
                                                                            activation=activation,
                                                                            device=device))

        # Branch n.2: Midterm features map
        self.branch_2['1D_to_1xN_to_Nx1Conv'] = nn.Sequential(ConvBlock(in_channels=in_channels,
                                                                        out_channels=int_channels,
                                                                        kernel_size=1,
                                                                        stride=1,
                                                                        padding=0,
                                                                        activation=activation,
                                                                        device=device),
                                                              ConvBlock(in_channels=int_channels,
                                                                        out_channels=int_channels,
                                                                        kernel_size=(1, kernel_size),
                                                                        stride=1,
                                                                        padding='same',
                                                                        activation=activation,
                                                                        device=device),
                                                              ConvBlock(in_channels=int_channels,
                                                                        out_channels=out_channels,
                                                                        kernel_size=(kernel_size, 1),
                                                                        stride=1,
                                                                        padding='same',
                                                                        activation=activation,
                                                                        device=device))

        # Branch n.3: Max Pooling (k=3, s=1, p=1) --> 1D_Conv: (k=1, s=1, p=0)
        self.branch_3['MaxPooling_to_1D_Conv'] = nn.Sequential(nn.MaxPool2d(kernel_size=3,
                                                                            stride=1,
                                                                            padding=1,
                                                                            return_indices=False,
                                                                            ceil_mode=False).to(device),
                                                               ConvBlock(in_channels=in_channels,
                                                                         out_channels=out_channels,
                                                                         kernel_size=1,
                                                                         stride=1,
                                                                         padding=0,
                                                                         activation=activation,
                                                                         device=device))

        # Branch n.4: 1D Conv: (k=1, s=1, p=0)
        self.branch_4['1D_Conv'] = ConvBlock(in_channels=in_channels,
                                             out_channels=out_channels,
                                             kernel_size=1,
                                             stride=1,
                                             padding=0,
                                             activation=activation,
                                             device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return out : Output Tensor (batch_size, out_channels, height, width)
        :rtype out  : torch.Tensor
        """
        out_1 = self.branch_1['1D_to_2x(1xN_to_Nx1Conv)'](x)
        out_2 = self.branch_2['1D_to_1xN_to_Nx1Conv'](x)
        out_3 = self.branch_3['MaxPooling_to_1D_Conv'](x)
        out_4 = self.branch_4['1D_Conv'](x)

        # Concatenation on dim=1 (dim=0 represents batch_size)
        out = torch.cat([out_1, out_2, out_3, out_4], dim=1)

        return out


class V27Block(nn.Module):
    def __init__(self, in_channels, in_3x3, int_3x3, out1_3x3, out2_3x3, red_3x3, out_3x3, out_1x1_pool, out_1x1, activation, device=device):
        """Creates a Pytorch module consisting of a generalized V1Block with expansion kernels.
        It is referred to as Inception Block V2.7 (Figure 7).
        (see C. Szegedy - "Rethinking the Inception Architecture for Computer Vision", https://arxiv.org/pdf/1512.00567v3.pdf)

        :param in_channels      : Input tensor channels
        :type in_channels       : int
        :param in_3x3           : 1st branch feature map input channels
        :type in_3x3            : int
        :param int_3x3          : 1st branch intermediate feature map channels
        :type int_3x3           : int
        :param out1_3x3         : 1st branch expansion (3x1) filter channels
        :type out1_3x3          : int
        :param out2_3x3         : 1st branch expansion (1x3) filter channels
        :type out2_3x3          : int
        :param red_3x3          : 2nd branch feature map input channels
        :type in_3x3            : int
        :param out_3x3          : 2nd branch feature map (expansion filters) output channels
        :type out_3x3           : int
        :param out_1x1_pool     : 3rd branch feature map output channels
        :type out_1x1_pool      : int
        :param out_1x1          : 4th branch feature map output channels
        :type out_1x1           : int
        :param activation       : Common output activation function (w. attributes), defaults to nn.ReLU()
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(V27Block, self).__init__()
        self.branch_1 = nn.ModuleDict()
        self.branch_2 = nn.ModuleDict()
        self.branch_3 = nn.ModuleDict()
        self.branch_4 = nn.ModuleDict()

        # Branch n.1: 1D_Conv (k=1, s=1, p=0) --> 3x3_Conv (k=3, s=1, p=1) --> Expansion_filters (1x3 & 3x1)
        self.branch_1['1D_to_3x3Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                 out_channels=in_3x3,
                                                                 kernel_size=1,
                                                                 stride=1,
                                                                 padding=0,
                                                                 activation=activation,
                                                                 device=device),
                                                       ConvBlock(in_channels=in_3x3,
                                                                 out_channels=int_3x3,
                                                                 kernel_size=3,
                                                                 stride=1,
                                                                 padding=1,
                                                                 activation=activation,
                                                                 device=device))
        self.branch_1['exp_1x3Conv'] = ConvBlock(in_channels=int_3x3,
                                                 out_channels=out1_3x3,
                                                 kernel_size=(1, 3),
                                                 stride=1,
                                                 padding=(0, 1),
                                                 activation=activation,
                                                 device=device)
        self.branch_1['exp_3x1Conv'] = ConvBlock(in_channels=int_3x3,
                                                 out_channels=out2_3x3,
                                                 kernel_size=(3, 1),
                                                 stride=1,
                                                 padding=(1, 0),
                                                 activation=activation,
                                                 device=device)

        # Branch n.2: 1D_Conv (k=1, s=1, p=0) --> Expansion_filters (1x3 & 3x1)
        self.branch_2['1D_Conv'] = ConvBlock(in_channels,
                                             out_channels=red_3x3,
                                             kernel_size=1,
                                             stride=1,
                                             padding=0,
                                             activation=activation,
                                             device=device)
        self.branch_2['exp_1x3Conv'] = ConvBlock(in_channels=red_3x3,
                                                 out_channels=out_3x3,
                                                 kernel_size=(1, 3),
                                                 stride=1,
                                                 padding=(0, 1),
                                                 activation=activation,
                                                 device=device)
        self.branch_2['exp_3x1Conv'] = ConvBlock(in_channels=red_3x3,
                                                 out_channels=out_3x3,
                                                 kernel_size=(3, 1),
                                                 stride=1,
                                                 padding=(1, 0),
                                                 activation=activation,
                                                 device=device)

        # Branch n.3: Max Pooling (k=3, s=1, p=1) --> 1D_Conv (k=1, s=1, p=0)
        self.branch_3['MaxPooling_to_1D_Conv'] = nn.Sequential(nn.MaxPool2d(kernel_size=3,
                                                                            stride=1,
                                                                            padding=1,
                                                                            return_indices=False,
                                                                            ceil_mode=False).to(device),
                                                               ConvBlock(in_channels=in_channels,
                                                                         out_channels=out_1x1_pool,
                                                                         kernel_size=1,
                                                                         stride=1,
                                                                         padding=0,
                                                                         activation=activation,
                                                                         device=device))

        # Branch n.4: 1D Conv (k=1, s=1, p=0)
        self.branch_4['1D_Conv'] = ConvBlock(in_channels,
                                             out_channels=out_1x1,
                                             kernel_size=1,
                                             stride=1,
                                             padding=0,
                                             activation=activation,
                                             device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return out : Output Tensor (batch_size, out1_3x3 + out2_3x3 + 2*out_3x3 + out_1x1_pool + out_1x1, height, width)
        :rtype out  : torch.Tensor
        """
        out_1_int = self.branch_1['1D_to_3x3Conv'](x)
        out_1_1 = self.branch_1['exp_1x3Conv'](out_1_int)
        out_1_2 = self.branch_1['exp_3x1Conv'](out_1_int)
        out_1 = torch.cat([out_1_1, out_1_2], dim=1)

        out_2_int = self.branch_2['1D_Conv'](x)
        out_2_1 = self.branch_2['exp_1x3Conv'](out_2_int)
        out_2_2 = self.branch_2['exp_3x1Conv'](out_2_int)
        out_2 = torch.cat([out_2_1, out_2_2], dim=1)

        out_3 = self.branch_3['MaxPooling_to_1D_Conv'](x)
        out_4 = self.branch_4['1D_Conv'](x)

        # Concatenation on dim=1 (dim=0 represents batch_size)
        out = torch.cat([out_1, out_2, out_3, out_4], dim=1)

        return out


class V210Block(nn.Module):
    def __init__(self, in_channels, in_3x3, out1_3x3, out2_3x3, add_ch, activation, device=device):
        """Creates a Pytorch module consisting of optimized pooling and striding for V25Block.
        It is referred to as Inception Block V2.10 (Figure 10).
        (see C. Szegedy - "Rethinking the Inception Architecture for Computer Vision", https://arxiv.org/pdf/1512.00567v3.pdf)

        :param in_channels      : Input tensor channels
        :type in_channels       : int
        :param in_3x3           : 1st branch feature map input channels
        :type in_3x3            : int
        :param out1_3x3         : 1st branch feature map output channels
        :type out1_3x3          : int
        :param out2_3x3         : 2nd branch feature map output channels
        :type out2_3x3          : int
        :param add_ch           : additional feature map output channels
        :type add_ch            : int
        :param activation       : Common output activation function (w. attributes), defaults to nn.ReLU()
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(V210Block, self).__init__()
        self.branch_1 = nn.ModuleDict()
        self.branch_2 = nn.ModuleDict()
        self.branch_3 = nn.ModuleDict()

        # Branch n.1: 1D_Conv: (k=1, s=1, p=0) --> 3x3_Conv (k=3, s=1, p=1) --> 3x3_Conv (k=3, s=2, p=0)
        self.branch_1['1D_to_3x3_to_3x3Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                        out_channels=in_3x3,
                                                                        kernel_size=1,
                                                                        stride=1,
                                                                        padding=0,
                                                                        activation=activation,
                                                                        device=device),
                                                              ConvBlock(in_channels=in_3x3,
                                                                        out_channels=out1_3x3 + add_ch,
                                                                        kernel_size=3,
                                                                        stride=1,
                                                                        padding=1,
                                                                        activation=activation,
                                                                        device=device),
                                                              ConvBlock(in_channels=out1_3x3 + add_ch,
                                                                        out_channels=out1_3x3 + add_ch,
                                                                        kernel_size=3,
                                                                        stride=2,
                                                                        padding=0,
                                                                        activation=activation,
                                                                        device=device))

        # Branch n.2: 1D_Conv (k=1, s=1, p=0) --> 3x3_Conv (k=3, s=2, p=0)
        self.branch_2['1D_to_3x3Conv'] = nn.Sequential(ConvBlock(in_channels,
                                                                 out_channels=in_3x3,
                                                                 kernel_size=1,
                                                                 stride=1,
                                                                 padding=0,
                                                                 activation=activation,
                                                                 device=device),
                                                       ConvBlock(in_channels=in_3x3,
                                                                 out_channels=out2_3x3 + add_ch,
                                                                 kernel_size=3,
                                                                 stride=2,
                                                                 padding=0,
                                                                 activation=activation,
                                                                 device=device))

        # Branch n.3: Max Pooling (k=3, s=2, p=0)
        self.branch_3['MaxPooling'] = nn.MaxPool2d(kernel_size=3,
                                                   stride=2,
                                                   padding=0,
                                                   return_indices=False,
                                                   ceil_mode=False).to(device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return out : Output Tensor (batch_size, out1_3x3 + out2_3x3 + 2*add_ch + in_channels, ..., ...)
        :rtype out  : torch.Tensor
        """
        out_1 = self.branch_1['1D_to_3x3_to_3x3Conv'](x)
        out_2 = self.branch_2['1D_to_3x3Conv'](x)
        out_3 = self.branch_3['MaxPooling'](x)

        # Concatenation on dim=1 (dim=0 represents batch_size)
        out = torch.cat([out_1, out_2, out_3], dim=1)

        return out
