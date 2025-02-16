from phi.agent import Agent
from phi.utils.log import logger
from datetime import datetime, timedelta
import google.generativeai as genai
from collections import Counter
import json
import os
from ..config import API_CONFIG

class TransactionAgent(Agent):
    def __init__(self):
        super().__init__(name="transaction_analyzer")
        self.gemini_key = API_CONFIG["gemini"]["key"]
        genai.configure(api_key=self.gemini_key)

    def load_wallet_data(self, wallet_address):
        file_name = f"data/wallet_data_{wallet_address}.json"
        try:
            with open(file_name, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found: {file_name}")
            return None

    def analyze_transactions(self, wallet_address):
        try:
            wallet_data = self.load_wallet_data(wallet_address)
            if not wallet_data:
                return None

            transactions = wallet_data.get("Transaction History", [])
            total_wallet_value = wallet_data.get("Total Portfolio Value", 0)
            
            recent_transactions = [tx for tx in transactions 
                                 if datetime.utcfromtimestamp(int(tx["timeStamp"])) > 
                                 datetime.utcnow() - timedelta(days=30)]

            if not recent_transactions:
                return "No transactions in the last 30 days."

            # Calculate metrics
            total_volume = sum(float(tx["value"]) / 1e18 for tx in recent_transactions)
            avg_size = total_volume / len(recent_transactions)
            volume_percentage = (total_volume / total_wallet_value * 100) if total_wallet_value > 0 else 0
            
            # Determine transaction size category
            if avg_size > 100000:
                size_category = "Large"
            elif avg_size > 10000:
                size_category = "Medium"
            else:
                size_category = "Small"

            # Analyze token transactions and patterns
            token_data = {}
            for tx in recent_transactions:
                token = tx.get("tokenSymbol", "ETH")
                if token not in token_data:
                    token_data[token] = {"count": 0, "in": 0, "out": 0}
                token_data[token]["count"] += 1
                if tx["to"].lower() == wallet_address.lower():
                    token_data[token]["in"] += 1
                else:
                    token_data[token]["out"] += 1

            # Calculate percentages and patterns
            total_txs = len(recent_transactions)
            top_assets = []
            for token, data in sorted(token_data.items(), key=lambda x: x[1]["count"], reverse=True)[:3]:
                percentage = (data["count"] / total_txs) * 100
                pattern = "Accumulating" if data["in"] > data["out"] else "Distributing" if data["out"] > data["in"] else "Mixed"
                top_assets.append((token, percentage, pattern))

            avg_daily_txs = len(recent_transactions) / 30

            return {
                "avg_size": f"${avg_size:.2f}",
                "size_category": size_category,
                "total_volume": f"${total_volume:.2f}",
                "volume_percentage": f"{volume_percentage:.1f}",
                "top_assets": top_assets,
                "avg_daily_txs": f"{avg_daily_txs:.1f}"
            }

        except Exception as e:
            logger.error(f"Error analyzing transactions for wallet {wallet_address}: {str(e)}")
            raise

    def get_ai_analysis(self, transaction_data):
        try:
            prompt = f"""
            Analyze this wallet's transaction behavior and provide a concise interpretation:
            - Average transaction size: {transaction_data['avg_size']} ({transaction_data['size_category']})
            - Daily transaction frequency: {transaction_data['avg_daily_txs']}
            - Volume relative to total value: {transaction_data['volume_percentage']}%
            - Top assets and their patterns: {transaction_data['top_assets']}
            """

            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error getting AI analysis: {str(e)}")
            return "AI analysis failed"

    def analyze(self, wallet_address):
        """Main analysis method"""
        transaction_data = self.analyze_transactions(wallet_address)
        if isinstance(transaction_data, str):
            return transaction_data

        ai_analysis = self.get_ai_analysis(transaction_data)
        
        # Format the output according to specified template
        formatted_output = f"""Average Transaction Size: {transaction_data['avg_size']} (Classification: {transaction_data['size_category']})
Total 30-Day Volume: {transaction_data['total_volume']} ({transaction_data['volume_percentage']}% of total wallet value)

Top Assets in Transactions:"""

        for i, (token, pct, pattern) in enumerate(transaction_data['top_assets'], 1):
            formatted_output += f"\n{i}. {token}: {pct:.1f}% (Direction: {pattern})"

        formatted_output += f"\n\nAverage Daily Transactions: {transaction_data['avg_daily_txs']}\nAnalysis: {ai_analysis}"

        return formatted_output