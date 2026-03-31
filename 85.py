# Prompt 85

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the DQN model
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, output_dim)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Initialize the DQN
input_dim = 6  # Example input dimension
output_dim = 4  # Example output dimension (actions)
dqn = DQN(input_dim, output_dim)

# Define the environment
class DroneEnvironment:
    def __init__(self):
        self.state = np.random.rand(3)  # Random initial position
        self.goal = np.array([1, 1, 1])  # Goal position
        self.obstacles = [np.array([0.5, 0.5, 0.5])]  # Example obstacle
    
    def step(self, action):
        # Update state based on action
        self.state += action
        reward = -np.linalg.norm(self.state - self.goal)  # Negative distance to goal
        done = np.linalg.norm(self.state - self.goal) < 0.1  # Goal reached
        for obstacle in self.obstacles:
            if np.linalg.norm(self.state - obstacle) < 0.1:  # Collision
                reward -= 10
                done = True
        return self.state, reward, done
    
    def reset(self):
        self.state = np.random.rand(3)
        return self.state

# Training loop
env = DroneEnvironment()
optimizer = optim.Adam(dqn.parameters(), lr=0.001)
criterion = nn.MSELoss()

for episode in range(1000):
    state = env.reset()
    total_reward = 0
    done = False
    
    while not done:
        state_tensor = torch.FloatTensor(state)
        q_values = dqn(state_tensor)
        action = torch.argmax(q_values).item()
        
        next_state, reward, done = env.step(np.array([action]))
        next_state_tensor = torch.FloatTensor(next_state)
        target_q_values = dqn(next_state_tensor).detach()
        
        target = reward + 0.99 * torch.max(target_q_values)
        loss = criterion(q_values, target.unsqueeze(0))
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        state = next_state
        total_reward += reward
    
    print(f"Episode {episode}, Total Reward: {total_reward}")

# Real-time visualization
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot initial state and goal
ax.scatter(*env.state, color='blue')
ax.scatter(*env.goal, color='green')

# Plot obstacles
for obstacle in env.obstacles:
    ax.scatter(*obstacle, color='red')

plt.show()