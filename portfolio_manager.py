import json
import os

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    with open(PORTFOLIO_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_portfolio(portfolio_list):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio_list, f, indent=4)

def add_to_portfolio(ticker, shares, buy_price):
    portfolio = load_portfolio()
    # Check if already exists
    for item in portfolio:
        if item['ticker'] == ticker:
            # Update average price and shares
            total_cost = (item['shares'] * item['buy_price']) + (shares * buy_price)
            item['shares'] += shares
            item['buy_price'] = total_cost / item['shares']
            save_portfolio(portfolio)
            return True
            
    portfolio.append({
        "ticker": ticker,
        "shares": shares,
        "buy_price": buy_price
    })
    save_portfolio(portfolio)
    return True

def remove_from_portfolio(ticker):
    portfolio = load_portfolio()
    portfolio = [item for item in portfolio if item['ticker'] != ticker]
    save_portfolio(portfolio)
