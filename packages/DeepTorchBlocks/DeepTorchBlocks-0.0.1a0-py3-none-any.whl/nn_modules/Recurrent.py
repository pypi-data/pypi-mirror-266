"""
Recurrent - PyTorch modules (inheriting nn.Module) for recurrent blocks layering
(Sphynx Docstrings)
"""

__version__ = "0.0.1"


import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable

device = 'cuda' if torch.cuda.is_available() else 'cpu'


# ---------------------------------------------- Recurrent Blocks (RNN) ------------------------------------------------
class RNNCell(nn.Module):
    def __init__(self, input_size, hidden_size, activation, device=device):
        """Creates a Pytorch module consisting of a standard RecurrentNN (also RNN) cell and
        an arbitrary activation function. (for more insights see
        W.S.McCulloch & W.Pitts - "A logical calculus of the ideas immanent in nervous activity", 10.1007/BF02478259)


        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layer size
        :type hidden_size   : int
        :param activation   : Output activation function (w. attributes), default should be nn.Tanh()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(RNNCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.device = device
        self.layers = nn.ModuleDict()

        # Input & Hidden Layers initialization
        self.layers['input_2_hidden'] = nn.Linear(input_size, hidden_size, bias=True).to(device)
        self.layers['hidden_2_hidden'] = nn.Linear(hidden_size, hidden_size, bias=True).to(device)
        self.act_fun = activation

        self.reset_parameters()

    def reset_parameters(self):
        # Compute Standard deviation (based on layer length)
        std = 1.0 / np.sqrt(self.hidden_size)
        for layer in self.layers.keys():
            for weights in self.layers[layer].weight:
                weights.data.uniform_(-std, std)                                                                        # Uniform init. in STD interval

            self.layers[layer].bias.data.fill_(0.)                                                                      # Bias initialization (0.)

    def forward(self, x, hx=None):
        """Forward method

        :param x    : Input Tensor (batch_size, input_size)
        :type x     : torch.Tensor
        :param hx   : Hidden Tensor from previous recurrent cells (batch_size, hidden_size)
        :type hx    : torch.Tensor
        :return hy  : Hidden Tensor (batch_size, hidden_size)
        :rtype hy   : torch.Tensor
        """
        if hx is None:
            hx = Variable(x.new_zeros(x.size(0), self.hidden_size).to(self.device))                                     # Feedback vector initialization

        hy = self.layers['input_2_hidden'](x) + self.layers['hidden_2_hidden'](hx)
        hy = self.act_fun(hy)

        return hy


class LSTMCell(nn.Module):
    def __init__(self, input_size, hidden_size, device=device):
        """Creates a Pytorch module consisting of a Long Short-Term Memory (LSTM) cell w. specific activation functions.
        (see S. Hochreiter & J. Schmidhuber - "Long Short-Term Memory", 10.1162/neco.1997.9.8.1735)


        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layer size
        :type hidden_size   : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(LSTMCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size                                                                                  # ... (* 4) for separate gates inputs dimensioning
        self.device = device
        self.layers = nn.ModuleDict()

        # Input & Hidden Layers initialization
        self.layers['input_2_hidden'] = nn.Linear(input_size, 4 * hidden_size, bias=True).to(device)
        self.layers['hidden_2_hidden'] = nn.Linear(hidden_size, 4 * hidden_size, bias=True).to(device)

        # Activation functions initialization
        self.act_input = nn.Sigmoid().to(device)
        self.act_forget = nn.Sigmoid().to(device)
        self.act_gate = nn.Tanh().to(device)
        self.act_out = nn.Sigmoid().to(device)
        self.act_fun = nn.Tanh().to(device)

        self.reset_parameters()

    def reset_parameters(self):
        # Compute Standard deviation (based on layer length)
        std = 1.0 / np.sqrt(self.hidden_size)
        for layer in self.layers.keys():
            for weights in self.layers[layer].weight:
                weights.data.uniform_(-std, std)                                                                        # Uniform init. in STD interval

            self.layers[layer].bias.data.fill_(0.)                                                                      # Bias initialization (0.)

    def forward(self, x, hx=None):
        """Forward method

        :param x    : Input Tensor (batch_size, input_size)
        :type x     : torch.Tensor
        :param hx   : Hidden Tensor from previous recurrent cells (batch_size, hidden_size)
        :type hx    : torch.Tensor
        :return hy  : Hidden Tensor (batch_size, hidden_size)
        :rtype hy   : torch.Tensor
        :return cy  : Cell output (batch_size, hidden_size)
        :rtype cy   : torch.Tensor
        """
        # Feedback vector initialization
        if hx is None:
            hx = Variable(x.new_zeros(x.size(0), self.hidden_size).to(self.device))
            hx = (hx, hx)

        hx, cx = hx                                                                                                     # Cell & Hidden memory init.
        gates = self.layers['input_2_hidden'](x) + self.layers['hidden_2_hidden'](hx)

        # Gates chunks: input_tensor, forget_tensor, gate_tensor, output_tensor
        input_gate, forget_gate, cell_gate, output_gate = gates.chunk(4, 1)

        # Activation step
        i_t = self.act_input(input_gate)
        f_t = self.act_forget(forget_gate)
        g_t = self.act_gate(cell_gate)
        o_t = self.act_out(output_gate)

        cy = cx * f_t + i_t * g_t                                                                                       # Cell output
        hy = o_t * self.act_fun(cy)                                                                                     # Hidden state output

        return hy, cy


class GRUCell(nn.Module):
    def __init__(self, input_size, hidden_size, device=device):
        """Creates a Pytorch module consisting of a Gated Recurrent Unit (GRU) cell w. specific activation functions.
        (see Kyunghyun Cho et al. - "Learning Phrase Representations using RNN Encoder–Decoder
        for Statistical Machine Translation", https://arxiv.org/pdf/1406.1078.pdf)

        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layer size
        :type hidden_size   : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(GRUCell, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size                                                                                  # ... (* 3) for separate gates inputs dimensioning
        self.device = device
        self.layers = nn.ModuleDict()

        # Input & Hidden Layers initialization
        self.layers['input_2_hidden'] = nn.Linear(input_size, 3 * hidden_size, bias=True).to(device)
        self.layers['hidden_2_hidden'] = nn.Linear(hidden_size, 3 * hidden_size, bias=True).to(device)

        # Activation functions initialization
        self.act_reset = nn.Sigmoid().to(device)
        self.act_update = nn.Sigmoid().to(device)
        self.act_new = nn.Tanh().to(device)

        self.reset_parameters()

    def reset_parameters(self):
        # Compute Standard deviation (based on layer length)
        std = 1.0 / np.sqrt(self.hidden_size)
        for layer in self.layers.keys():
            for weights in self.layers[layer].weight:
                weights.data.uniform_(-std, std)                                                                        # Uniform init. in STD interval

            self.layers[layer].bias.data.fill_(0.)                                                                      # Bias initialization (0.)

    def forward(self, x, hx=None):
        """Forward method

        :param x    : Input Tensor (batch_size, input_size)
        :type x     : torch.Tensor
        :param hx   : Hidden Tensor from previous recurrent cells (batch_size, hidden_size)
        :type hx    : torch.Tensor
        :return hy  : Hidden Tensor (batch_size, hidden_size)
        :rtype hy   : torch.Tensor
        """
        # Feedback vector initialization
        if hx is None:
            hx = Variable(x.new_zeros(x.size(0), self.hidden_size).to(self.device))

        x_t = self.layers['input_2_hidden'](x)
        h_t = self.layers['hidden_2_hidden'](hx)

        # Reset gate, Update gate & input_gate tensor cropping
        x_reset, x_upd, x_new = x_t.chunk(3, 1)
        h_reset, h_upd, h_new = h_t.chunk(3, 1)

        reset_gate = self.act_reset(x_reset + h_reset)
        update_gate = self.act_update(x_upd + h_upd)
        new_gate = self.act_new(x_new + (reset_gate * h_new))

        hy = update_gate * hx + (1 - update_gate) * new_gate

        return hy


# ---------------------------------------- Deep Recurrent Networks (DeepRNN) -------------------------------------------
class DeepRNN(nn.Module):
    def __init__(self, input_size, hidden_size, num_cells, output_size, activation, device=device):
        """Creates a Pytorch module consisting of a deep stack of RNN cells.

        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layers size
        :type hidden_size   : int
        :param num_cells    : Number of RNN cells stacked
        :type num_cells     : int
        :param output_size  : Output tensor length
        :type output_size   : int
        :param activation   : Output activation function (w. attributes), default should be nn.Tanh()
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(DeepRNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_cells = num_cells
        self.output_size = output_size
        self.device = device
        self.layers = nn.ModuleDict()

        # Deep Stacking & Output layer initialization
        self.layers['Cell_1'] = RNNCell(input_size=self.input_size,
                                        hidden_size=self.hidden_size,
                                        activation=activation,
                                        device=self.device)

        for cell in range(1, self.num_cells):
            self.layers[f'Cell_{cell + 1}'] = RNNCell(input_size=self.hidden_size,
                                                      hidden_size=self.hidden_size,
                                                      activation=activation,
                                                      device=self.device)

        self.layers['out_fc'] = nn.Linear(self.hidden_size, self.output_size).to(self.device)
        nn.init.kaiming_normal_(self.layers['out_fc'].weight, mode='fan_in')                                            # Kaiming-He (Normal) init
        self.layers['out_fc'].bias.data.fill_(0.)                                                                       # Bias initialization (0.)

    def forward(self, x, hx=None):
        """Forward method

        :param x    : Input Tensor (batch_size, sequence_length, input_size)
        :type x     : torch.Tensor
        :param hx   : Hidden Tensor from previous recurrent cells (batch_size, hidden_size)
        :type hx    : torch.Tensor
        :return out : Hidden Tensor (batch_size, output_size)
        :rtype out  : torch.Tensor
        """
        if hx is None:
            h0 = Variable(torch.zeros(self.num_cells, x.size(0), self.hidden_size).to(self.device))
        else:
            h0 = hx

        outs = []

        hidden = list()
        for cell in range(self.num_cells):
            hidden.append(h0[cell, :, :])

        for t in range(x.size(1)):
            for cell in range(self.num_cells):
                if cell == 0:
                    hidden_l = self.layers['Cell_1'](x[:, t, :], hidden[cell])
                else:
                    hidden_l = self.layers[f'Cell_{cell + 1}'](hidden[cell - 1], hidden[cell])

                hidden[cell] = hidden_l

            outs.append(hidden_l)

        # Output pass
        out = outs[-1].squeeze()
        out = self.layers['out_fc'](out)

        return out


class DeepLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_cells, output_size, device=device):
        """Creates a Pytorch module consisting of a deep stack of LSTM cells.

        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layers size
        :type hidden_size   : int
        :param num_cells    : Number of LSTM cells stacked
        :type num_cells     : int
        :param output_size  : Output tensor length
        :type output_size   : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(DeepLSTM, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_cells = num_cells
        self.output_size = output_size
        self.device = device
        self.layers = nn.ModuleDict()

        # Deep Stacking & Output layer initialization
        self.layers['Cell_1'] = LSTMCell(input_size=self.input_size,
                                         hidden_size=self.hidden_size,
                                         device=self.device)

        for cell in range(1, self.num_cells):
            self.layers[f'Cell_{cell + 1}'] = LSTMCell(input_size=self.hidden_size,
                                                       hidden_size=self.hidden_size,
                                                       device=self.device)

        self.layers['out_fc'] = nn.Linear(self.hidden_size, self.output_size).to(self.device)
        nn.init.kaiming_normal_(self.layers['out_fc'].weight, mode='fan_in')                                            # Kaiming-He (Normal) init
        self.layers['out_fc'].bias.data.fill_(0.)                                                                       # Bias initialization (0.)

    def forward(self, x, hx=None):
        """Forward method

        :param x    : Input Tensor (batch_size, sequence_length, input_size)
        :type x     : torch.Tensor
        :param hx   : Hidden Tensor from previous recurrent cells (batch_size, hidden_size)
        :type hx    : torch.Tensor
        :return out : Hidden Tensor (batch_size, output_size)
        :rtype out  : torch.Tensor
        """
        if hx is None:
            h0 = Variable(torch.zeros(self.num_cells, x.size(0), self.hidden_size).to(self.device))
        else:
            h0 = hx

        outs = []

        hidden = list()
        for cell in range(self.num_cells):
            hidden.append((h0[cell, :, :], h0[cell, :, :]))

        for t in range(x.size(1)):
            for cell in range(self.num_cells):
                if cell == 0:
                    hidden_l = self.layers['Cell_1'](x[:, t, :], (hidden[cell][0], hidden[cell][1]))
                else:
                    hidden_l = self.layers[f'Cell_{cell + 1}'](hidden[cell - 1][0], (hidden[cell][0], hidden[cell][1]))

                hidden[cell] = hidden_l

            outs.append(hidden_l[0])

        out = outs[-1].squeeze()
        out = self.layers['out_fc'](out)

        return out


class DeepGRU(nn.Module):
    def __init__(self, input_size, hidden_size, num_cells, output_size, device=device):
        """Creates a Pytorch module consisting of a deep stack of GRU cells.

        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layers size
        :type hidden_size   : int
        :param num_cells    : Number of GRU cells stacked
        :type num_cells     : int
        :param output_size  : Output tensor length
        :type output_size   : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        """
        super(DeepGRU, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_cells = num_cells
        self.output_size = output_size
        self.device = device
        self.layers = nn.ModuleDict()

        # Deep Stacking & Output layer initialization
        self.layers['Cell_1'] = GRUCell(input_size=self.input_size,
                                        hidden_size=self.hidden_size,
                                        device=self.device)

        for cell in range(1, self.num_cells):
            self.layers[f'Cell_{cell + 1}'] = GRUCell(input_size=self.hidden_size,
                                                      hidden_size=self.hidden_size,
                                                      device=self.device)

        self.layers['out_fc'] = nn.Linear(self.hidden_size, self.output_size).to(self.device)
        nn.init.kaiming_normal_(self.layers['out_fc'].weight, mode='fan_in')  # Kaiming-He (Normal) init
        self.layers['out_fc'].bias.data.fill_(0.)

    def forward(self, x, hx=None):
        """Forward method

        :param x    : Input Tensor (batch_size, sequence_length, input_size)
        :type x     : torch.Tensor
        :param hx   : Hidden Tensor from previous recurrent cells (batch_size, hidden_size)
        :type hx    : torch.Tensor
        :return out : Hidden Tensor (batch_size, output_size)
        :rtype out  : torch.Tensor
        """
        if hx is None:
            h0 = Variable(torch.zeros(self.num_cells, x.size(0), self.hidden_size).to(self.device))
        else:
            h0 = hx

        outs = []

        hidden = list()
        for cell in range(self.num_cells):
            hidden.append(h0[cell, :, :])

        for t in range(x.size(1)):
            for cell in range(self.num_cells):
                if cell == 0:
                    hidden_l = self.layers['Cell_1'](x[:, t, :], hidden[cell])
                else:
                    hidden_l = self.layers[f'Cell_{cell + 1}'](hidden[cell - 1], hidden[cell])

                hidden[cell] = hidden_l

            outs.append(hidden_l)

        out = outs[-1].squeeze()
        out = self.layers['out_fc'](out)

        return out


class BRNN(nn.Module):
    def __init__(self, input_size, hidden_size, cells: list, output_size, device=device, **kwargs):
        """Creates a Pytorch module consisting of a Bi-directional deep stack of arbitrary Recurrent cells (also BRNN).
        (see M. Schuster & K.K. Paliwal - "Bidirectional Recurrent Neural Networks", 10.1109/78.650093)

        :param input_size   : Input tensor length
        :type input_size    : int
        :param hidden_size  : Hidden layers size
        :type hidden_size   : int
        :param cells        : The architecture cells sequence, e.g.: [LSTM, RNN, ..., GRU]
        :type cells         : list
        :param output_size  : Output tensor length
        :type output_size   : int
        :param device       : Host device ('cpu' or 'cuda:X')
        :type device        : str
        :param kwargs       : "activation", output activation function (for RNNs only)
        """
        super(BRNN, self).__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_cells = len(cells)
        self.cells = cells
        self.output_size = output_size
        self.device = device
        self.activation = kwargs.get('activation', nn.Tanh().to(device))
        self.layers = nn.ModuleDict()

        # Input Cell initialization
        if cells[0] == 'GRU':
            self.layers['Cell_1'] = GRUCell(input_size=self.input_size,
                                            hidden_size=self.hidden_size,
                                            device=self.device)
        elif cells[0] == 'LSTM':
            self.layers['Cell_1'] = LSTMCell(input_size=self.input_size,
                                             hidden_size=self.hidden_size,
                                             device=self.device)
        else:
            self.layers['Cell_1'] = RNNCell(input_size=self.input_size,
                                            hidden_size=self.hidden_size,
                                            activation=self.activation,
                                            device=self.device)

        # Hidden Cells initialization
        for count, cell in enumerate(cells[1:]):
            if cell == 'GRU':
                self.layers[f'Cell_{count + 2}'] = GRUCell(input_size=self.hidden_size,
                                                           hidden_size=self.hidden_size,
                                                           device=self.device)
            elif cell == 'LSTM':
                self.layers[f'Cell_{count + 2}'] = LSTMCell(input_size=self.hidden_size,
                                                            hidden_size=self.hidden_size,
                                                            device=self.device)
            else:
                self.layers[f'Cell_{count + 2}'] = RNNCell(input_size=self.hidden_size,
                                                           hidden_size=self.hidden_size,
                                                           activation=self.activation,
                                                           device=self.device)

        # Output Layer initialization
        self.layers['out_fc'] = nn.Linear(self.hidden_size * 2, self.output_size).to(self.device)
        nn.init.kaiming_normal_(self.layers['out_fc'].weight, mode='fan_in')                                            # Kaiming-He (Normal) init
        self.layers['out_fc'].bias.data.fill_(0.)

    def forward(self, x):
        """Forward method

        :param x    : Input Tensor (batch_size, sequence_length, input_size)
        :type x     : torch.Tensor
        :return out : Hidden Tensor (batch_size, output_size)
        :rtype out  : torch.Tensor
        """
        h0 = Variable(torch.zeros(self.num_cells, x.size(0), self.hidden_size).to(self.device))
        hT = Variable(torch.zeros(self.num_cells, x.size(0), self.hidden_size).to(self.device))

        outs = []
        outs_rev = []

        hidden_forward = list()
        for layer in range(self.num_cells):
            if isinstance(self.layers[f'Cell_{layer + 1}'], LSTMCell):
                hidden_forward.append((h0[layer, :, :], h0[layer, :, :]))
            else:
                hidden_forward.append(h0[layer, :, :])

        hidden_backward = list()
        for layer in range(self.num_cells):
            if isinstance(self.layers[f'Cell_{layer + 1}'], LSTMCell):
                hidden_backward.append((hT[layer, :, :], hT[layer, :, :]))
            else:
                hidden_backward.append(hT[layer, :, :])

        for t in range(x.shape[1]):
            for layer in range(self.num_cells):
                if isinstance(self.layers[f'Cell_{layer + 1}'], LSTMCell):      # If LSTMCell instance
                    if layer == 0:
                        # Forward net
                        h_forward_l = self.layers[f'Cell_{layer + 1}'](x[:, t, :], (hidden_forward[layer][0], hidden_forward[layer][1]))
                        # Backward net
                        h_back_l = self.layers[f'Cell_{layer + 1}'](x[:, -(t + 1), :], (hidden_backward[layer][0], hidden_backward[layer][1]))
                    else:
                        # Forward net
                        h_forward_l = self.layers[f'Cell_{layer + 1}'](hidden_forward[layer - 1][0], (hidden_forward[layer][0], hidden_forward[layer][1]))
                        # Backward net
                        h_back_l = self.layers[f'Cell_{layer + 1}'](hidden_backward[layer - 1][0], (hidden_backward[layer][0], hidden_backward[layer][1]))
                else:                                                                                                   # ...if RNN_TANH, RNN_RELU or GRU instance
                    if layer == 0:
                        # Forward net
                        h_forward_l = self.layers[f'Cell_{layer + 1}'](x[:, t, :], hidden_forward[layer])
                        # Backward net
                        h_back_l = self.layers[f'Cell_{layer + 1}'](x[:, -(t + 1), :], hidden_backward[layer])
                    else:
                        # Forward net
                        if isinstance(self.layers[f'Cell_{layer}'], LSTMCell):
                            h_forward_l = self.layers[f'Cell_{layer + 1}'](hidden_forward[layer - 1][0], torch.unsqueeze(hidden_forward[layer][0], 0))
                        else:
                            h_forward_l = self.layers[f'Cell_{layer + 1}'](hidden_forward[layer - 1], hidden_forward[layer])
                        # Backward net
                        if isinstance(self.layers[f'Cell_{layer}'], LSTMCell):
                            h_back_l = self.layers[f'Cell_{layer + 1}'](hidden_backward[layer - 1][0], torch.unsqueeze(hidden_backward[layer][0], 0))
                        else:
                            h_back_l = self.layers[f'Cell_{layer + 1}'](hidden_backward[layer - 1], hidden_backward[layer])

                hidden_forward[layer] = h_forward_l
                hidden_backward[layer] = h_back_l

                # a step Forward NOW, if it doesn't work --> indent 1 step Backward
                if isinstance(self.layers[f'Cell_{layer + 1}'], LSTMCell):
                    outs.append(h_forward_l[0])
                    outs_rev.append(h_back_l[0])
                else:
                    outs.append(h_forward_l)
                    outs_rev.append(h_back_l)

        # Take only last time step and modify it for seq2seq
        out = outs[-1].squeeze()
        out_rev = outs_rev[0].squeeze()
        out = torch.cat((out, out_rev))

        out = self.layers['out_fc'](out)

        return out


# ------------------------------------- Convolutional Recurrent Networks (CRNN) ----------------------------------------
class ConvLSTMCell(nn.Module):
    def __init__(self, in_shape, in_channels, hidden_channels, kernel_size, padding, peephole=False, device=device):
        """Creates a Pytorch module consisting of a Convolutional LSTM cell.
        (see Xingjian Shi et al. - "Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting",
        https://arxiv.org/pdf/1506.04214.pdf)

        :param in_shape         : Input features map tensor shape
        :type in_shape          : tuple
        :param in_channels      : Input features map tensor channels
        :type in_channels       : int
        :param hidden_channels  : LSTM Hidden channels
        :type hidden_channels   : int
        :param kernel_size      : Convolutional kernel (filter) dimensions
        :type kernel_size       : int or tuple
        :param padding          : Input tensor padding quantity and/or mode
        :type padding           : str or int or tuple
        :param peephole         : Peephole connections condition
        :type peephole          : bool
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(ConvLSTMCell, self).__init__()
        self.height, self.width = in_shape
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.kernel_size = kernel_size
        if isinstance(padding, str):
            self.padding = padding
        elif isinstance(padding, int):
            self.padding = kernel_size // 2, kernel_size // 2
        else:
            self.padding = kernel_size[0] // 2, kernel_size[1] // 2
        self.peephole = peephole
        self.device = device
        self.act_fun_i = nn.Sigmoid().to(device)
        self.act_fun_f = nn.Sigmoid().to(device)
        self.act_fun_o = nn.Sigmoid().to(device)
        self.act_fun_g = nn.Tanh().to(device)
        self.layers = nn.ModuleDict()

        # Peephole weights layer initialization
        if peephole:
            self.Wci = nn.Parameter(torch.FloatTensor(self.hidden_channels, self.height, self.width)).to(device)
            self.Wcf = nn.Parameter(torch.FloatTensor(self.hidden_channels, self.height, self.width)).to(device)
            self.Wco = nn.Parameter(torch.FloatTensor(self.hidden_channels, self.height, self.width)).to(device)

        # Features mapping layer initialization
        self.layers['Feature_Extraction'] = nn.Conv2d(in_channels=self.in_channels + self.hidden_channels,
                                                      out_channels=4 * self.hidden_channels,
                                                      kernel_size=self.kernel_size,
                                                      padding=self.padding,
                                                      stride=1,
                                                      bias=True).to(device)

        # Parameters initialization
        self.reset_parameters()

    def reset_parameters(self):
        """Parameters initialization method

        Convolutional layer --> Xavier uniform
        Peephole weights --> U[-std, std]
        """
        # Convolutional layer init (Weights & Bias)
        nn.init.xavier_uniform_(self.layers['Feature_Extraction'].weight, gain=nn.init.calculate_gain('tanh'))
        self.layers['Feature_Extraction'].bias.data.zero_()

        # LSTM Peephole parameters init
        if self.peephole:
            std = 1. / np.sqrt(self.hidden_dim)

            self.Wci.data.uniform_(-std, std)
            self.Wcf.data.uniform_(-std, std)
            self.Wco.data.uniform_(-std, std)

    def forward(self, x, prev_state=None):
        """Forward method

        :param x            : Input Tensor (batch_size, in_channels, in_size[0], in_size[1])
        :type x             : torch.Tensor
        :param prev_state   : Previous Hidden state Tensor (batch_size, hidden_channels, in_size[0], in_size[1])
        :type prev_state    : torch.Tensor
        :return h_cur       : Hidden state Tensor (batch_size, hidden_channels, ..., ...)
        :rtype h_cur        : torch.Tensor
        :return c_cur       : Cell state Tensor (batch_size, hidden_channels, ..., ...)
        :rtype c_cur        : torch.Tensor
        """
        if prev_state is None:
            prev_state = (torch.zeros(x.shape[0], self.hidden_channels, self.height, self.width, device=self.device),
                          torch.zeros(x.shape[0], self.hidden_channels, self.height, self.width, device=self.device))

        h_prev, c_prev = prev_state

        combined = torch.cat((x, h_prev), dim=1)
        combined_conv = self.layers['Feature_Extraction'](combined)

        cc_i, cc_f, cc_o, cc_g = torch.split(combined_conv, self.hidden_channels, dim=1)

        if self.peephole:
            input_gate = self.act_fun_i(cc_i + self.Wci * c_prev)
            forget_gate = self.act_fun_f(cc_f + self.Wcf * c_prev)
        else:
            input_gate = self.act_fun_i(cc_i)
            forget_gate = self.act_fun_f(cc_f)

        g = self.act_fun_g(cc_g)
        c_cur = forget_gate * c_prev + input_gate * g

        if self.peephole:
            out = self.act_fun_o(cc_o + self.Wco * c_cur)
        else:
            out = self.act_fun_o(cc_o)

        h_cur = out * self.act_fun_g(c_cur)

        return h_cur, c_cur


class ConvGRUCell(nn.Module):
    def __init__(self, in_shape, in_channels, hidden_channels, kernel_size, padding, device=device):
        """Creates a Pytorch module consisting of a Convolutional GRU cell. (see N. Ballas et al. -
        "Delving Deeper into Convolutional Networks for Learning Video Representations", https://arxiv.org/pdf/1511.06432v4.pdf)

        :param in_shape         : Input features map tensor shape
        :type in_shape          : tuple
        :param in_channels      : Input features map tensor channels
        :type in_channels       : int
        :param hidden_channels  : LSTM Hidden channels
        :type hidden_channels   : int
        :param kernel_size      : Convolutional kernel (filter) dimensions
        :type kernel_size       : int or tuple
        :param padding          : Input tensor padding quantity and/or mode
        :type padding           : str or int or tuple
        :param device           : Host device ('cpu' or 'cuda:X')
        :type device            : str
        """
        super(ConvGRUCell, self).__init__()
        self.height, self.width = in_shape
        self.in_channels = in_channels
        self.hidden_channels = hidden_channels
        self.kernel_size = kernel_size
        if isinstance(padding, str):
            self.padding = padding
        elif isinstance(padding, int):
            self.padding = kernel_size // 2, kernel_size // 2
        else:
            self.padding = kernel_size[0] // 2, kernel_size[1] // 2
        self.device = device
        self.layers = nn.ModuleDict()

        # Layers initialization
        self.layers['Conv_ZR'] = nn.Conv2d(in_channels=self.in_channels + self.hidden_channels,
                                           out_channels=2 * self.hidden_channels,
                                           kernel_size=self.kernel_size,
                                           padding=self.padding,
                                           bias=True).to(device)

        self.layers['Conv_H1'] = nn.Conv2d(in_channels=self.in_channels,
                                           out_channels=self.hidden_channels,
                                           kernel_size=self.kernel_size,
                                           padding=self.padding,
                                           bias=True).to(device)

        self.layers['Conv_H2'] = nn.Conv2d(in_channels=self.hidden_channels,
                                           out_channels=self.hidden_channels,
                                           kernel_size=self.kernel_size,
                                           padding=self.padding,
                                           bias=True).to(device)

        # Activation functions
        self.act_fun = nn.Sigmoid()
        self.out_act = nn.Tanh()

        self.reset_parameters()

    def reset_parameters(self):
        """Parameters initialization method

        Convolutional layers --> Xavier uniform
        """
        for layer in self.layers.keys():
            nn.init.xavier_uniform_(self.layers[layer].weight, gain=nn.init.calculate_gain('tanh'))
            self.layers[layer].bias.data.zero_()

    def forward(self, x, prev_state=None):
        """Forward method

        :param x            : Input Tensor (batch_size, in_channels, in_size[0], in_size[1])
        :type x             : torch.Tensor
        :param prev_state   : Previous Hidden state Tensor (batch_size, hidden_channels, in_size[0], in_size[1])
        :type prev_state    : torch.Tensor
        :return out         : Hidden Tensor (batch_size, hidden_channels, ..., ...)
        :rtype out          : torch.Tensor
        """
        if prev_state is None:
            prev_state = torch.zeros(x.shape[0], self.hidden_dim, self.height, self.width, device=self.device)

        combined = torch.cat((x, prev_state), dim=1)
        combined_conv = self.act_fun(self.layers['Conv_ZR'](combined))

        z, r = torch.split(combined_conv, self.hidden_dim, dim=1)
        h_ = self.out_act(self.layers['Conv_H1'](x) + r * self.layers['Conv_H2'](prev_state))

        out = (1 - z) * h_ + z * prev_state

        return out
