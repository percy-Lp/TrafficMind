import torch.nn as nn
import torch

class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        """
        初始化DQN神经网络
        :param state_size: 状态空间大小（输入维度）
        :param action_size: 动作空间大小（输出维度）
        """
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 24)  # 输入层，第一层全连接层
        self.fc2 = nn.Linear(24, 24)  # 第二层全连接层
        self.fc3 = nn.Linear(24, action_size)  # 输出层

    def forward(self, x):
        """
        前向传播
        :param x: 输入状态(tensor)
        :return: 每个动作的Q值(tensor)
        """
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)
