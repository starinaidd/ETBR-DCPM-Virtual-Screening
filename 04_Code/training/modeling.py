import torch.nn.functional as F
import torch.nn as nn


class SimpleDNN(nn.Module):
    def __init__(self, inputs, hideen_units, outputs, dp_ratio):
        """
        :param inputs: number of inputs
        :param hideen_units: [128, 256, 512]
        :param out_puts: number of outputs
        :param dp_ratio:
        """
        super().__init__()
        # layers
        self.hidden1 = nn.Linear(inputs, hideen_units[0])
        self.dropout1 = nn.Dropout(dp_ratio)

        self.hidden2 = nn.Linear(hideen_units[0], hideen_units[1])
        self.dropout2 = nn.Dropout(dp_ratio)

        self.hidden3 = nn.Linear(hideen_units[1], hideen_units[2])
        self.dropout3 = nn.Dropout(dp_ratio)

        self.output = nn.Linear(hideen_units[2], 1)

    def forward(self, x):
        x = self.hidden1(x)
        x = F.relu(self.dropout1(x))

        x = self.hidden2(x)
        x = F.relu(self.dropout2(x))

        x = self.hidden3(x)
        x = F.relu(self.dropout3(x))

        return self.output(x)
