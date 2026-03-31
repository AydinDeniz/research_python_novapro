import ccxt
import pandas as pd
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.envs import DummyVecEnv
from stable_baselines3.common.vec_env import VecNormalize
from gym import Env, spaces
import datetime

# Initialize exchange
exchange = ccxt.binance({
    'enableRateLimit': True,
})

# Define the trading environment
class TradingEnv(Env):
    def __init__(self, data):
        super(TradingEnv, self).__init__()
        self.data = data
        self.current_step = 0
        self.balance = 10000  # Starting balance
        self.position = 0  # No position initially
        self.action_space = spaces.Discrete(3)  # 0: hold, 1: buy, 2: sell
        self.observation_space = spaces.Box(low=0, high=1, shape=(len(data.columns),), dtype=np.float32)

    def reset(self):
        self.current_step = 0
        self.balance = 10000
        self.position = 0
        return self._next_observation()

    def step(self, action):
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        reward = 0

        current_price = self.data.iloc[self.current_step]['Close']
        next_price = self.data.iloc[self.current_step + 1]['Close']

        if action == 1:  # Buy
            if self.balance >= current_price:
                self.position = self.balance / current_price
                self.balance = 0
        elif action == 2:  # Sell
            if self.position > 0:
                self.balance = self.position * next_price
                self.position = 0

        if self.position > 0:
            reward = next_price - current_price

        return self._next_observation(), reward, done, {}

    def _next_observation(self):
        obs = self.data.iloc[self.current_step].values
        return obs

# Fetch historical data
def fetch_data(symbol, timeframe='1d', since=None):
    if since is None:
        since = exchange.parse8601('2020-01-01T00:00:00Z')
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Backtest function
def backtest(model, env):
    obs = env.reset()
    total_reward = 0
    for _ in range(len(env.data) - 1):
        action, _states = model.predict(obs)
        obs, reward, done, _ = env.step(action)
        total_reward += reward
        if done:
            break
    return total_reward

# Main function
def main():
    symbol = 'BTC/USDT'
    data = fetch_data(symbol)
    env = DummyVecEnv([lambda: TradingEnv(data)])
    env = VecNormalize(env, norm_obs=True, norm_reward=True)

    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)

    total_reward = backtest(model, TradingEnv(data))
    print(f"Total reward: {total_reward}")

if __name__ == "__main__":
    main()