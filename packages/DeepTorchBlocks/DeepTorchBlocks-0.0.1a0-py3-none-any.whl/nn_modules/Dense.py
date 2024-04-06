"""
Dense - PyTorch modules (inheriting nn.Module) for densely connected blocks layering
(Sphynx Docstrings)
"""

__version__ = "0.0.1"


import torch
import torch.nn as nn
from torch.nn import functional as F

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class DenseConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, padding, dropout=False, device=device, **kwargs):
        """Creates a Pytorch module comprising a BatchNorm Layer, followed by a ReLU activation and a Convolutional layer.
        It is the basic building module of a DenseNet Architecture. (see Gao Huang et al. -
        "Densely Connected Convolutional Networks", 10.1109/CVPR.2017.243)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param stride       : Convolutional kernel (filter) striding step(s)
        :type stride        : int or tuple
        :param padding      : Input tensor padding quantity and/or mode
        :type padding       : int or tuple or str
        :param dropout      : Output dropout condition (w. **kwargs probability), defaults to False (drop_rate=0.5)
        :type dropout       : bool
        :param device      : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(DenseConvBlock, self).__init__()
        self.layers = nn.ModuleDict()
        self.dropout = dropout
        self.drop_rate = kwargs.get('drop_rate', 0.5)

        # 2D Batch Normalization
        self.layers['batch_norm_2D'] = nn.BatchNorm2d(in_channels).to(device)

        # ReLU Activation
        self.act_fun = nn.ReLU().to(device)

        # 2D Convolutional Layer
        self.layers['conv_2D'] = nn.Conv2d(in_channels=in_channels,
                                           out_channels=out_channels,
                                           kernel_size=kernel_size,
                                           stride=stride,
                                           padding=padding,
                                           bias=True).to(device)

        # Weights & Bias initialization
        for layer in self.layers.keys():
            try:
                nn.init.kaiming_normal_(self.layers[layer].weight, mode='fan_in')                                       # Kaiming-He (Normal) init
            except:
                pass                                                                                                    # Batch layer could not be init!
            self.layers[layer].bias.data.fill_(0.)                                                                      # Biases initialization (0.)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        x = self.layers['batch_norm_2D'](x)
        x = self.act_fun(x)
        x = self.layers['conv_2D'](x)
        if self.dropout is True:
            x = F.dropout(x, p=self.drop_rate, training=self.training)

        return x


class DenseLayer(nn.Module):
    def __init__(self, in_channels, growth_rate, dropout=False, device=device, **kwargs):
        """Creates a Pytorch module consisting of a standard Dense Layer of a DenseNet Architecture.
        (see "Gao Huang et al. - "Densely Connected Convolutional Networks", 10.1109/CVPR.2017.243)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param growth_rate  : Output channels quantity
        :type growth_rate   : int or float
        :param dropout      : Output dropout condition (w. **kwargs probability), defaults to False (drop_rate=0.5)
        :type dropout       : bool
        :param device      : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(DenseLayer, self).__init__()
        self.layers = nn.ModuleDict()
        self.dropout = dropout
        self.drop_rate = kwargs.get('drop_rate', 0.5)

        # Dense Convolutional Block Stage (1x1, NO-DropOut)
        self.layers['Dense_ConvBlock_1x1'] = DenseConvBlock(in_channels=in_channels,
                                                            out_channels=4*growth_rate,
                                                            kernel_size=1,
                                                            stride=1,
                                                            padding=0,
                                                            dropout=False,
                                                            device=device)

        # Dense Convolutional Block Stage (3x3, DropOut)
        self.layers['Dense_ConvBlock_3x3'] = DenseConvBlock(in_channels=4*growth_rate,
                                                            out_channels=growth_rate,
                                                            kernel_size=3,
                                                            stride=1,
                                                            padding=1,
                                                            dropout=self.dropout,
                                                            device=device,
                                                            drop_rate=self.drop_rate)

    def forward(self, x):
        """Forward method

        :param x    : Input tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :returns    : Output tensor (batch_size, growth_rate, ..., ...)
        :rtype      : torch.Tensor
        """
        y = self.layers['Dense_ConvBlock_1x1'](x)
        y = self.layers['Dense_ConvBlock_3x3'](y)
        y = torch.cat([x, y], dim=1)

        return y


class TransitionLayer(nn.Module):
    def __init__(self, in_channels, comp_factor, pooling=nn.AvgPool2d(kernel_size=2, stride=2), device=device):
        """Creates a Pytorch module consisting of a Bottleneck Transition Layer of a DenseNet Architecture.
        (see "Gao Huang et al. - "Densely Connected Convolutional Networks", 10.1109/CVPR.2017.243)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param comp_factor  : Output channels quantity
        :type comp_factor   : int or float
        :param pooling      : Output pooling stage (w. attributes), defaults to nn.AvgPool2d(kernel_size=2, stride=2)
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(TransitionLayer, self).__init__()
        self.layers = nn.ModuleDict()

        # 2D Batch Normalization
        self.layers['batch_norm_2D'] = nn.BatchNorm2d(in_channels).to(device)

        # 1D Convolutional Layer
        self.layers['pw_conv'] = nn.Conv2d(in_channels=in_channels,
                                           out_channels=int(round(in_channels * comp_factor)),
                                           kernel_size=1,
                                           stride=1,
                                           padding=0,
                                           bias=True).to(device)

        # Features pooling stage
        self.pooling = pooling

        # Weights & Bias initialization
        for layer in self.layers.keys():
            try:
                nn.init.kaiming_normal_(self.layers[layer].weight, mode='fan_in')                                       # Kaiming-He (Normal) init
            except:
                pass                                                                                                    # Batch layer could not be init
            self.layers[layer].bias.data.fill_(0.)                                                                      # Biases initialization (0.)

    def forward(self, x):
        """Forward method

        :param x    : Input tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :returns    : Output tensor (batch_size, round(in_channels * comp_factor), ..., ...)
        :rtype      : torch.Tensor
        """
        x = self.layers['batch_norm_2D'](x)
        x = self.layers['pw_conv'](x)
        x = self.pooling(x)

        return x
