import pandas as pd
import yfinance as yf
from datetime import datetime

class User:
    def __init__(self, username, initial_balance):
        self.username = username
        self.balance = initial_balance
        self.portfolio = {}

    def buy_stock(self, ticker, quantity):
        stock_data = yf.download(ticker, start="2020-01-01", end=datetime.today().strftime('%Y-%m-%d'))
        current_price = stock_data['Close'][-1]
        total_cost = current_price * quantity

        if total_cost > self.balance:
            return "Insufficient balance"

        self.balance -= total_cost
        if ticker in self.portfolio:
            self.portfolio[ticker]['quantity'] += quantity
        else:
            self.portfolio[ticker] = {'quantity': quantity, 'purchase_price': current_price}

        return f"Bought {quantity} shares of {ticker} at ${current_price} each."

    def sell_stock(self, ticker, quantity):
        if ticker not in self.portfolio:
            return "Stock not found in portfolio"

        if self.portfolio[ticker]['quantity'] < quantity:
            return "Insufficient shares"

        stock_data = yf.download(ticker, start="2020-01-01", end=datetime.today().strftime('%Y-%m-%d'))
        current_price = stock_data['Close'][-1]
        total_sale = current_price * quantity

        self.balance += total_sale
        self.portfolio[ticker]['quantity'] -= quantity

        if self.portfolio[ticker]['quantity'] == 0:
            del self.portfolio[ticker]

        return f"Sold {quantity} shares of {ticker} at ${current_price} each."

    def view_portfolio(self):
        portfolio_value = self.balance
        portfolio_details = []

        for ticker, details in self.portfolio.items():
            stock_data = yf.download(ticker, start="2020-01-01", end=datetime.today().strftime('%Y-%m-%d'))
            current_price = stock_data['Close'][-1]
            value = details['quantity'] * current_price
            portfolio_value += value
            portfolio_details.append({
                'ticker': ticker,
                'quantity': details['quantity'],
                'purchase_price': details['purchase_price'],
                'current_price': current_price,
                'value': value
            })

        return portfolio_details, portfolio_value

def main():
    users = {}

    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter username: ")
            initial_balance = float(input("Enter initial balance: "))
            users[username] = User(username, initial_balance)
            print(f"User {username} registered with an initial balance of ${initial_balance}")

        elif choice == "2":
            username = input("Enter username: ")
            if username in users:
                user = users[username]
                while True:
                    print("\n1. Buy Stock\n2. Sell Stock\n3. View Portfolio\n4. Logout")
                    action = input("Choose an action: ")

                    if action == "1":
                        ticker = input("Enter stock ticker: ")
                        quantity = int(input("Enter quantity: "))
                        print(user.buy_stock(ticker, quantity))

                    elif action == "2":
                        ticker = input("Enter stock ticker: ")
                        quantity = int(input("Enter quantity: "))
                        print(user.sell_stock(ticker, quantity))

                    elif action == "3":
                        portfolio_details, portfolio_value = user.view_portfolio()
                        print(f"Portfolio Value: ${portfolio_value}")
                        for stock in portfolio_details:
                            print(stock)

                    elif action == "4":
                        break

                    else:
                        print("Invalid action")

            elif username not in users:
                print("User not found")

        elif choice == "3":
            break

        else:
            print("Invalid option")

if __name__ == "__main__":
    main()