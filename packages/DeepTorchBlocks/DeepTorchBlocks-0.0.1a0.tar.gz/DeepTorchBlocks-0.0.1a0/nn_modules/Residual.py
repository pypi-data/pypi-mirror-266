"""
Residual - PyTorch modules (inheriting nn.Module) for residual blocks layering
(Sphynx Docstrings)
"""

__version__ = "0.0.1"


import torch
import torch.nn as nn
from Standard import ConvBlock, DWConv, PWConv, HardSigmoid, HardSwish, SquExBlock

device = 'cuda' if torch.cuda.is_available() else 'cpu'


class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=2, device=device):
        """Creates a Pytorch module consisting of a Residual Block of a ResNet Architecture.
        (see Kaiming He et al. - "Deep Residual Learning for Image Recognition", 10.1109/CVPR.2016.90)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param stride       : Convolutional kernel (filter) striding step(s), defaults to 1
        :type stride        : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(ResidualBlock, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.layers = nn.ModuleDict()
        self.skip = 'INPUT Re-Shaping (...to Conv_1x1)'

        # Standard Convolution Block
        self.layers['Conv_Block_ReLU'] = ConvBlock(in_channels=in_channels,
                                                   out_channels=out_channels,
                                                   kernel_size=3,
                                                   stride=stride,
                                                   padding=1,
                                                   activation=nn.ReLU(),
                                                   device=device)
        # 2nd Standard ConvBlock (no activation)
        self.layers['Conv_Block_ID'] = ConvBlock(in_channels=out_channels,
                                                 out_channels=out_channels,
                                                 kernel_size=3,
                                                 stride=1,
                                                 padding=1,
                                                 activation=nn.Identity(),
                                                 device=device)

        # Output ReLU Activation
        self.act_fun = nn.ReLU().to(device)

        # Shortcut evaluation
        if in_channels != out_channels:                                                                                 # Shortcut w. Reshaping
            self.layers['conv_1D'] = nn.Conv2d(in_channels=in_channels,
                                               out_channels=out_channels,
                                               kernel_size=1,
                                               stride=stride,
                                               padding=0,
                                               bias=True).to(device)

            nn.init.kaiming_normal_(self.layers['conv_1D'].weight, mode='fan_in')                                       # Kaiming He init.
            self.layers['conv_1D'].bias.data.fill_(0.)                                                                  # Biases initialization (0.)

        else:
            self.skip = 'Direct ADD'

    def forward(self, x):
        """Forward method

        :param x    : Input tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :returns    : Output tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        y = self.layers['Conv_Block_ReLU'](x)
        y = self.layers['Conv_Block_ID'](y)
        if self.in_channels != self.out_channels:
            x = self.layers['conv_1D'](x)
        y += x
        y = self.act_fun(y)

        return y


class BottleneckBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, reduction, activation, device=device):
        """Creates a Pytorch module consisting of a Bottleneck module from a ResNet architecture.
        (see Kaiming He et al. - "Deep Residual Learning for Image Recognition", https://arxiv.org/pdf/1512.03385.pdf)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param stride       : Convolutional kernel (filter) striding step(s)
        :type stride        : int or tuple
        :param reduction    : Hidden stage channels reduction factor
        :type reduction     : int or float
        :param activation   : Output activation function (w. attributes), default should be nn.ReLU()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(BottleneckBlock, self).__init__()
        reduced_features = out_channels // reduction
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.layers = nn.ModuleDict()
        self.skip = 'INPUT Re-Shaping (...to Conv_1x1)'

        # Features learning Layers initialization
        self.layers['COMP_PW_Conv_Block'] = PWConv(in_channels=in_channels,
                                                   out_channels=reduced_features,
                                                   stride=stride,
                                                   padding=0,
                                                   activation=activation,
                                                   device=device)

        self.layers['Conv_Block'] = ConvBlock(in_channels=reduced_features,
                                              out_channels=reduced_features,
                                              kernel_size=kernel_size,
                                              stride=1,
                                              padding='same',
                                              activation=activation,
                                              device=device)

        self.layers['EXP_PW_Conv_Block'] = PWConv(in_channels=reduced_features,
                                                  out_channels=out_channels,
                                                  stride=1,
                                                  padding=0,
                                                  activation=nn.Identity(),
                                                  device=device)

        if in_channels != out_channels:
            self.layers['shortcut'] = PWConv(in_channels=in_channels,
                                             out_channels=out_channels,
                                             stride=stride,
                                             padding=0,
                                             activation=nn.Identity(),
                                             device=device)
        else:
            self.skip = 'Direct ADD'

        self.act_fun = activation.to(device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output Tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        y = self.layers['COMP_PW_Conv_Block'](x)
        y = self.layers['Conv_Block'](y)
        y = self.layers['EXP_PW_Conv_Block'](y)

        if self.in_channels != self.out_channels:
            x = self.layers['shortcut'](x)

        out = self.act_fun(x + y)

        return out


class ResNextBlock(nn.Module):
    def __init__(self, in_channels, out_channels, groups, bot_exp, stride, device=device):
        """Creates a Pytorch module consisting of a custom Residual Block of a ResNext Architecture.
        (see "Saining Xie et al. - "Aggregated Residual Transformations for Deep Neural Networks", 10.1109/CVPR.2017.634)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param groups       : Kernel quantity (subgroups subdivision)
        :type groups        : int
        :param bot_exp      : Bottleneck expansion factor (multiplier)
        :type bot_exp       : int or float
        :param stride       : Convolutional kernel (filter) striding step(s), defaults to 1
        :type stride        : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(ResNextBlock).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        bottleneck_channels = int(round(self.out_channels * bot_exp))
        self.skip = 'INPUT Re-Shaping (...to Conv_1x1)'
        self.layers = nn.ModuleDict()

        # Point-wise Convolution Block (1)
        self.layers['PW_Conv_Block_1'] = PWConv(in_channels=in_channels,
                                                out_channels=bottleneck_channels,
                                                stride=1,
                                                padding=0,
                                                activation=nn.ReLU(),
                                                device=device)

        # 3x3 "Grouped-Convolution" Block (Conv + Batch-Norm2D)
        self.layers['grouped_conv3x3'] = nn.Conv2d(in_channels=bottleneck_channels,
                                                   out_channels=bottleneck_channels,
                                                   kernel_size=3,
                                                   stride=stride,
                                                   padding=1,
                                                   groups=bottleneck_channels//groups,
                                                   bias=True).to(device)

        nn.init.kaiming_normal_(self.layers['grouped-3x3conv'].weight, mode='fan_in')                                   # Kaiming He init.
        self.layers['grouped_conv3x3'].bias.data.fill_(0.)                                                              # Biases initialization (0.)

        self.layers['batch_norm_2D'] = nn.BatchNorm2d(bottleneck_channels).to(device)
        self.layers['batch_norm_2D'].bias.data.fill_(0.)                                                                # Biases initialization (0.)

        # Activation function for both Grouped-Conv and Output layer
        self.act_fun = nn.ReLU().to(device)

        # Point-wise Convolution Block (2)
        self.layers['PW_Conv_Block_2'] = PWConv(in_channels=bottleneck_channels,
                                                out_channels=out_channels,
                                                stride=1,
                                                padding=0,
                                                activation=nn.Identity(),
                                                device=device)
        # Shortcut evaluation
        if self.in_channels != self.out_channels:                                                                       # Shortcut w. Reshaping
            # Re-shaping w. 1D convolution
            self.layers['conv_1D'] = nn.Conv2d(in_channels=in_channels,
                                               out_channels=out_channels,
                                               kernel_size=1,
                                               stride=stride,
                                               padding=0,
                                               bias=True).to(device)
            nn.init.kaiming_normal_(self.layers['conv_1D'].weight, mode='fan_in')                                       # Kaiming He init.
            self.layers['conv_1D'].bias.data.fill_(0.)                                                                  # Biases initialization (0.)
        else:
            self.skip = 'Direct ADD'

    def forward(self, x):
        """Forward method

        :param x    : Input tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :returns    : Output tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        y = self.layers['PW_Conv_Block_1'](x)
        y = self.layers['grouped_conv3x3'](y)
        y = self.layers['batch_norm_2D'](y)
        y = self.act_fun(y)
        y = self.layers['PW_Conv_Block_2'](y)
        if self.in_channels != self.out_channels:
            x = self.layers['conv_1D'](x)
        y += x
        y = self.act_fun(y)

        return y


class BottleNextBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, reduction, activation, device=device):
        """Creates a Pytorch module consisting of a Bottleneck module variation from a ResNext architecture.
        (see Zhuang Liu et al. - "A ConvNet for the 2020s", https://arxiv.org/pdf/2201.03545.pdf)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param stride       : Convolutional kernel (filter) striding step(s)
        :type stride        : int or tuple
        :param reduction    : Hidden stage channels reduction factor
        :type reduction     : int or float
        :param activation   : Output activation function (w. attributes), default should be nn.ReLU()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(BottleNextBlock, self).__init__()
        reduced_features = out_channels // reduction
        self.layers = nn.ModuleDict()

        # Features learning Layers initialization
        self.layers['COMP_PW_Conv_Block'] = PWConv(in_channels=in_channels,
                                                   out_channels=reduced_features,
                                                   stride=stride,
                                                   padding=0,
                                                   activation=activation,
                                                   device=device)

        self.layers['Conv_Block'] = DWConv(in_channels=reduced_features,
                                           kernel_size=kernel_size,
                                           stride=1,
                                           padding='same',
                                           activation=activation,
                                           device=device)

        self.layers['EXP_PW_Conv_Block'] = PWConv(in_channels=reduced_features,
                                                  out_channels=out_channels,
                                                  stride=1,
                                                  padding=0,
                                                  activation=nn.Identity(),
                                                  device=device)

        self.layers['shortcut'] = PWConv(in_channels=in_channels,
                                         out_channels=out_channels,
                                         stride=stride,
                                         padding=0,
                                         activation=nn.Identity(),
                                         device=device)

        self.act_fun = activation

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output Tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        y = self.layers['COMP_PW_Conv_Block'](x)
        y = self.layers['Conv_Block'](y)
        y = self.layers['EXP_PW_Conv_Block'](y)

        x = self.layers['shortcut'](x)

        out = self.act_fun(x + y)

        return out


class InvResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, expansion, stride, activation=nn.ReLU6(), device=device):
        """Creates a Pytorch module consisting of an expansion Point-wise Convolution block, followed by an adaptive
        Depth-wise Convolution and a Bottleneck Point-wise Convolution blocks. It is called Inverted Residual Block,
        and it is the basic building module of a MobileNet_V2 Architecture.
        (see M. Sandler et al. - "MobileNetV2: Inverted Residuals and Linear Bottlenecks", https://arxiv.org/pdf/1801.04381.pdf)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param expansion    : expansion factor (for hidden_stage channels computation)
        :type expansion     : int or float
        :param stride       : Convolutional kernel (filter) striding step(s), defaults to 1
        :type stride        : int
        :param activation   : activation function (w. attributes), defaults to nn.ReLU6()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(InvResBlock, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.skip = False
        self.stride = stride

        if self.stride == 1:
            if self.in_channels == self.out_channels:
                self.skip = True

        self.expansion = expansion
        self.hidden_dim = int(round(self.expansion * in_channels))
        self.layers = nn.ModuleDict()

        # Layers Initialization
        if self.expansion != 1:
            self.layers['Exp_PW_Conv_Block'] = PWConv(in_channels=in_channels,
                                                      out_channels=self.hidden_dim,
                                                      stride=1,
                                                      padding=0,
                                                      activation=activation,
                                                      device=device)

        if self.stride == 1:
            self.layers['DW_Conv_Block'] = DWConv(in_channels=self.hidden_dim,
                                                  kernel_size=(3, 3),
                                                  stride=1,
                                                  padding='same',
                                                  activation=activation,
                                                  device=device)
        else:
            self.layers['DW_Conv_Block'] = DWConv(in_channels=self.hidden_dim,
                                                  kernel_size=(3, 3),
                                                  stride=2,
                                                  padding=(1, 1),
                                                  activation=activation,
                                                  device=device)

        self.layers['Bottleneck_PW_Conv_Block'] = PWConv(in_channels=self.hidden_dim,
                                                         out_channels=out_channels,
                                                         stride=1,
                                                         padding=0,
                                                         activation=nn.Identity(),                                      # Linear activation
                                                         device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :returns    : Output tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        if self.expansion == 1:
            y = self.layers['DW_Conv_Block'](x)
            y = self.layers['Bottleneck_PW_Conv_Block'](y)
        else:
            y = self.layers['Exp_PW_Conv_Block'](x)
            y = self.layers['DW_Conv_Block'](y)
            y = self.layers['Bottleneck_PW_Conv_Block'](y)

        if self.stride == 1:
            if self.in_channels == self.out_channels:                                                                   # Residual skip connection
                y = y + x

        return y


class InvBottleNextBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, expansion, activation, device=device):
        """Creates a Pytorch module consisting of an Inverted Bottleneck module variation from a ResNext architecture.
        (see Zhuang Liu et al. - "A ConvNet for the 2020s", https://arxiv.org/pdf/2201.03545.pdf)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param stride       : Convolutional kernel (filter) striding step(s)
        :type stride        : int or tuple
        :param expansion    : Hidden stage channels expansion factor
        :type expansion     : int or float
        :param activation   : Output activation function (w. attributes), default should be nn.ReLU()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(InvBottleNextBlock, self).__init__()
        expanded_features = round(out_channels * expansion)
        self.layers = nn.ModuleDict()

        # Features learning Layers initialization
        self.layers['EXP_PW_Conv_Block'] = PWConv(in_channels=in_channels,
                                                  out_channels=expanded_features,
                                                  stride=stride,
                                                  padding=0,
                                                  activation=activation,
                                                  device=device)

        self.layers['Conv_Block'] = DWConv(in_channels=expanded_features,
                                           kernel_size=kernel_size,
                                           stride=1,
                                           padding='same',
                                           activation=activation,
                                           device=device)

        self.layers['COMP_PW_Conv_Block'] = PWConv(in_channels=expanded_features,
                                                   out_channels=out_channels,
                                                   stride=1,
                                                   padding=0,
                                                   activation=nn.Identity(),
                                                   device=device)

        self.layers['shortcut'] = PWConv(in_channels=in_channels,
                                         out_channels=out_channels,
                                         stride=stride,
                                         padding=0,
                                         activation=nn.Identity(),
                                         device=device)

        self.act_fun = activation.to(device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output Tensor (batch_size, out_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        y = self.layers['EXP_PW_Conv_Block'](x)
        y = self.layers['Conv_Block'](y)
        y = self.layers['COMP_PW_Conv_Block'](y)

        x = self.layers['shortcut'](x)

        out = self.act_fun(x + y)

        return out


class ConvNextStage(nn.Module):
    def __init__(self, in_channels, kernel_size, stride, factor, depth, activation, inv=False, device=device):
        """Creates a Pytorch module consisting of a ConvNext Stage.
        (see Zhuang Liu et al. - "A ConvNet for the 2020s", https://arxiv.org/pdf/2201.03545.pdf)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param kernel_size  : Convolutional kernels (filter) dimensions
        :type kernel_size   : int or tuple
        :param stride       : Convolutional kernels (filter) striding step(s)
        :type stride        : int or tuple
        :param factor       : Hidden stage channels compression/expansion factor
        :type factor        : int or float
        :param depth        : Bottlenecks stages
        :type depth         : int
        :param activation   : Output activation function (w. attributes), default should be nn.GELU()
        :param inv          : Inverted BottleNextBlock usage condition
        :type inv           : bool
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(ConvNextStage, self).__init__()
        self.depth = depth
        self.layers = nn.ModuleDict()

        if inv is False:
            for stage in range(depth):
                self.layers[f'Bottleneck_Stage_{stage + 1}'] = BottleNextBlock(in_channels=in_channels,
                                                                               out_channels=in_channels,
                                                                               kernel_size=kernel_size,
                                                                               stride=stride,
                                                                               reduction=factor,
                                                                               activation=activation,
                                                                               device=device)

        else:
            for stage in range(depth):
                self.layers[f'Bottleneck_Stage_{stage + 1}'] = InvBottleNextBlock(in_channels=in_channels,
                                                                                  out_channels=in_channels,
                                                                                  kernel_size=kernel_size,
                                                                                  stride=stride,
                                                                                  expansion=factor,
                                                                                  activation=activation,
                                                                                  device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output Tensor (batch_size, in_channels, ..., ...)
        :rtype      : torch.Tensor
        """
        for stage in range(self.depth):
            x = self.layers[f'Bottleneck_Stage_{stage + 1}'](x)

        return x


class InvResSEBlock(nn.Module):
    def __init__(self, in_channels, hidden_chs, out_channels, kernel_size, dw_stride, use_se, use_hs, device=device):
        """Creates a Pytorch module consisting of an Inverted Residual Squeeze-and-Excitation convolutional block.
        (see A.G.Howard - "Searching for MobileNetV3", https://arxiv.org/pdf/1905.02244.pdf)

        :param in_channels  : Input tensor channels
        :type in_channels   : int
        :param hidden_chs   : Squeeze-and-Excite tensor channels
        :type hidden_chs    : int
        :param out_channels : Output tensor channels
        :type out_channels  : int
        :param kernel_size  : Convolutional kernel (filter) dimensions
        :type kernel_size   : int or tuple
        :param dw_stride    : Depth-wise block striding
        :type dw_stride     : int or tuple
        :param use_se       : Use Squeeze-and-Exciting block processing condition
        :type use_se        : bool
        :param use_hs       : Use Hard Sigmoid activation function (for SquExBlock)
        :type use_hs        : bool
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(InvResSEBlock, self).__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.stride = dw_stride
        self.identity = dw_stride == 1 and in_channels == out_channels
        self.layers = nn.ModuleDict()

        if in_channels == hidden_chs:
            self.layers['DW_Conv_Block'] = DWConv(in_channels=hidden_chs,
                                                  kernel_size=kernel_size,
                                                  stride=self.stride,
                                                  padding=(kernel_size - 1) // 2,
                                                  activation=HardSwish() if use_hs else nn.ReLU(),
                                                  device=device)

            if use_se:
                self.layers['SE_Block'] = SquExBlock(in_channels=hidden_chs,
                                                     reduction=4,
                                                     activation=HardSigmoid(),
                                                     device=device)

            self.layers['PW_Conv_Block'] = PWConv(in_channels=hidden_chs,
                                                  out_channels=out_channels,
                                                  stride=1,
                                                  padding=0,
                                                  activation=nn.Identity(),
                                                  device=device)
        else:
            self.layers['PW_Conv_1'] = PWConv(in_channels=in_channels,
                                              out_channels=hidden_chs,
                                              stride=1,
                                              padding=0,
                                              activation=HardSwish() if use_hs else nn.ReLU(),
                                              device=device)

            self.layers['DW_Conv_Block'] = DWConv(in_channels=hidden_chs,
                                                  kernel_size=kernel_size,
                                                  stride=self.stride,
                                                  padding=(kernel_size - 1) // 2,
                                                  activation=nn.Identity(),
                                                  device=device)

            if use_se:
                self.layers['SE_Block'] = SquExBlock(in_channels=hidden_chs,
                                                     reduction=4,
                                                     activation=HardSwish() if use_hs else nn.ReLU(),
                                                     device=device)

            self.layers['PW_Conv_2'] = PWConv(in_channels=hidden_chs,
                                              out_channels=out_channels,
                                              stride=1,
                                              padding=0,
                                              activation=nn.Identity(),
                                              device=device)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, in_channels, height, width)
        :type x     : torch.Tensor
        :return     : Output Tensor (batch_size, out_channels, height, width)
        :rtype      : torch.Tensor
        """
        y = x

        if self.identity:
            for layer in self.layers.keys():
                y = self.layers[f'{layer}'](y)

            return x + y                                                                                                # Shortcut

        else:
            for layer in self.layers.keys():
                x = self.layers[f'{layer}'](x)

            return x
