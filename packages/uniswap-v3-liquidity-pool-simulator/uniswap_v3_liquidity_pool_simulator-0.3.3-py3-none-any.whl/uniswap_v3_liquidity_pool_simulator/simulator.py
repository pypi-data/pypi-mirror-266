import requests
import pandas as pd


class V3LiquidityPoolSimulator:
    def __init__(self, token1: str = "usdc", token2: str = "usdt", position_range: tuple = (1.0, 1.0)):
        self.token1 = token1
        self.token2 = token2
        self.position_range = position_range
        self.prices = self.fetch_current_prices()

    def fetch_current_prices(self):
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "usd-coin,tether",
            "vs_currencies": "usd"
        }
        response = requests.get(url, params=params).json()
        prices = {
            "usdc": response["usd-coin"]["usd"],
            "usdt": response["tether"]["usd"]
        }
        return prices

    def simulate_earnings(self):
        # For simplicity, let's say it just returns a static value for now
        return 100

# Example usage
# from v3_liquidity_pool_simulator.simulator import V3LiquidityPoolSimulator
simulator = V3LiquidityPoolSimulator(position_range=(0.99, 1.01))
print("Current Prices:", simulator.prices)
print("Simulated Earnings:", simulator.simulate_earnings())
