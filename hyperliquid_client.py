"""
Stub for hyperliquid_client to allow running backtests without the live trading module.
"""

class HyperliquidTradingClient:
    def __init__(self, live_mode=False, wallet_address=None, secret_key=None):
        self.is_live = False
        self._requested_live = False
