# Prompt 91

import ccxt
import pandas as pd
import time

class TradingBot:
    def __init__(self, exchange_id, api_key, secret_key):
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': api_key,
           'secret': secret_key,
        })
        self.transactions = []

    def get_ohlcv(self, symbol, timeframe='1h', limit=100):
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def calculate_moving_averages(self, df, short_window=5, long_window=20):
        df['short_ma'] = df['close'].rolling(window=short_window).mean()
        df['long_ma'] = df['close'].rolling(window=long_window).mean()
        return df

    def check_signals(self, df):
        if df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1] and df['short_ma'].iloc[-2] <= df['long_ma'].iloc[-2]:
            return 'buy'
        elif df['short_ma'].iloc[-1] < df['long_ma'].iloc[-1] and df['short_ma'].iloc[-2] >= df['long_ma'].iloc[-2]:
            return 'sell'
        else:
            return 'hold'

    def execute_trade(self, symbol, side, amount):
        order = self.exchange.create_market_order(symbol, side, amount)
        self.transactions.append({
            'timestamp': pd.Timestamp.now(),
           'symbol': symbol,
            'side': side,
            'amount': amount,
            'price': order['price'],
            'cost': order['cost'],
        })
        print(f"Executed {side} order for {amount} {symbol} at {order['price']}. Total cost: {order['cost']}")

    def run(self, symbol, short_window=5, long_window=20, amount=0.01):
        while True:
            df = self.get_ohlcv(symbol)
            df = self.calculate_moving_averages(df, short_window, long_window)
            signal = self.check_signals(df)

            if signal == 'buy':
                self.execute_trade(symbol, 'buy', amount)
            elif signal =='sell':
                self.execute_trade(symbol,'sell', amount)

            time.sleep(3600)  # Wait for 1 hour before checking again

    def log_transactions(self, filename='transactions.csv'):
        pd.DataFrame(self.transactions).to_csv(filename, index=False)

if __name__ == "__main__":
    bot = TradingBot('binance', 'your_api_key', 'your_secret_key')
    bot.run('BTC/USDT')
    bot.log_transactions()