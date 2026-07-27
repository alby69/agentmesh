import random
from typing import Any, Dict, List, Optional, Tuple

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


if HAS_TORCH:
    class DQN(nn.Module):
        def __init__(self, state_dim: int = 4, action_dim: int = 3):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(state_dim, 64),
                nn.ReLU(),
                nn.Linear(64, 64),
                nn.ReLU(),
                nn.Linear(64, action_dim)
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            return self.net(x)


    class ReplayBuffer:
        def __init__(self, capacity: int = 10000):
            self.capacity = capacity
            self.buffer: List[Tuple] = []
            self.position = 0

        def push(self, state, action, reward, next_state, done):
            if len(self.buffer) < self.capacity:
                self.buffer.append(None)
            self.buffer[self.position] = (state, action, reward, next_state, done)
            self.position = (self.position + 1) % self.capacity

        def sample(self, batch_size: int) -> List[Tuple]:
            return random.sample(self.buffer, batch_size)

        def __len__(self) -> int:
            return len(self.buffer)


class DQNAgent:
    def __init__(self, state_dim: int = 4, action_dim: int = 3, lr: float = 0.001, gamma: float = 0.95, epsilon: float = 0.1):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon
        self.has_torch = HAS_TORCH

        if self.has_torch:
            self.policy_net = DQN(state_dim, action_dim)
            self.target_net = DQN(state_dim, action_dim)
            self.target_net.load_state_dict(self.policy_net.state_dict())
            self.target_net.eval()

            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
            self.memory = ReplayBuffer(10000)
            self.batch_size = 32
            self.steps_done = 0
            self.target_update_frequency = 10
        else:
            self.policy_net = None

    def choose_action(self, state: List[float], actions_available: List[int]) -> int:
        if not self.has_torch:
            return random.choice(actions_available)

        if random.random() < self.epsilon:
            return random.choice(actions_available)

        self.policy_net.eval()
        with torch.no_grad():
            state_t = torch.tensor([state], dtype=torch.float32)
            q_values = self.policy_net(state_t)
            action = int(torch.argmax(q_values).item())
            if action in actions_available:
                return action
            return random.choice(actions_available)

    def store_transition(self, state, action, reward, next_state, done=False):
        if self.has_torch:
            self.memory.push(state, action, reward, next_state, done)

    def update(self) -> Optional[float]:
        if not self.has_torch or len(self.memory) < self.batch_size:
            return None

        self.policy_net.train()
        transitions = self.memory.sample(self.batch_size)

        states = torch.tensor([t[0] for t in transitions], dtype=torch.float32)
        actions = torch.tensor([t[1] for t in transitions], dtype=torch.long).unsqueeze(1)
        rewards = torch.tensor([t[2] for t in transitions], dtype=torch.float32).unsqueeze(1)
        next_states = torch.tensor([t[3] for t in transitions], dtype=torch.float32)
        dones = torch.tensor([t[4] for t in transitions], dtype=torch.float32).unsqueeze(1)

        # Get current Q values
        state_action_values = self.policy_net(states).gather(1, actions)

        # Compute next Q values from target network
        with torch.no_grad():
            next_state_values = self.target_net(next_states).max(1)[0].unsqueeze(1)
            expected_state_action_values = rewards + (self.gamma * next_state_values * (1.0 - dones))

        # Compute loss
        loss_fn = nn.MSELoss()
        loss = loss_fn(state_action_values, expected_state_action_values)

        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.steps_done += 1
        if self.steps_done % self.target_update_frequency == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        return float(loss.item())
