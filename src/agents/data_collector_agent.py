from phi.agent import Agent
from phi.utils.log import logger
from ..utils.rate_limiter import etherscan_rate_limit, with_retry
from ..config import API_CONFIG, get_wallet_data_path
import requests
import json

class DataCollectorAgent(Agent):
    def __init__(self):
        super().__init__(name="data_collector")
        self.etherscan_url = API_CONFIG["etherscan"]["url"]
        self.api_key = API_CONFIG["etherscan"]["key"]

    @with_retry(max_retries=3)
    def get_wallet_balance(self, wallet_address):
        """Get ETH balance"""
        etherscan_rate_limit()
        url = f"{self.etherscan_url}?module=account&action=balance&address={wallet_address}&tag=latest&apikey={self.api_key}"
        response = requests.get(url).json()
        return int(response["result"]) / 1e18 if response["status"] == "1" else None

    @with_retry(max_retries=3)
    def get_transactions(self, wallet_address):
        """Get transaction history"""
        etherscan_rate_limit()
        url = f"{self.etherscan_url}?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.api_key}"
        response = requests.get(url).json()
        return response["result"] if response["status"] == "1" else []

    @with_retry(max_retries=3)
    def get_token_holdings(self, wallet_address):
        """Get ERC-20 token holdings"""
        etherscan_rate_limit()
        url = f"{self.etherscan_url}?module=account&action=tokentx&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={self.api_key}"
        response = requests.get(url).json()
        
        if response["status"] == "1":
            token_dict = {}
            for tx in response["result"]:
                token_symbol = tx["tokenSymbol"]
                token_value = int(tx["value"]) / (10 ** int(tx["tokenDecimal"]))
                if tx["to"].lower() == wallet_address.lower():
                    token_dict[token_symbol] = token_dict.get(token_symbol, 0) + token_value
                else:
                    token_dict[token_symbol] = token_dict.get(token_symbol, 0) - token_value
            return token_dict
        return {}

    def collect_data(self, wallet_address: str) -> str:
        """Collect all wallet data"""
        try:
            logger.info(f"Collecting data for wallet: {wallet_address}")
            
            data = {
                "Wallet Address": wallet_address,
                "ETH Balance": self.get_wallet_balance(wallet_address),
                "Token Holdings": self.get_token_holdings(wallet_address),
                "Transaction History": self.get_transactions(wallet_address)
            }
            
            # Save to file
            file_path = get_wallet_data_path(wallet_address)
            file_path.parent.mkdir(exist_ok=True)
            file_path.write_text(json.dumps(data, indent=4))
                
            logger.info(f"Data collected and saved for wallet: {wallet_address}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error collecting data for wallet {wallet_address}: {str(e)}")
            raise 