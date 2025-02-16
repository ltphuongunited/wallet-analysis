from phi.agent import Agent
from phi.utils.log import logger
from datetime import datetime, timedelta
import google.generativeai as genai
from collections import Counter
import json
import os
from src.utils.rate_limiter import etherscan_rate_limit, with_retry

class BehaviorAgent(Agent):
    def __init__(self):
        super().__init__(name="behavior_analyzer")
        self.gemini_key = os.getenv("GEMINI_KEY")
        genai.configure(api_key=self.gemini_key)

    def load_wallet_data(self, wallet_address):
        file_name = f"data/wallet_data_{wallet_address}.json"
        try:
            with open(file_name, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Data file not found: {file_name}")
            return None

    def filter_transactions(self, transactions, days=30):
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return [tx for tx in transactions if datetime.utcfromtimestamp(int(tx["timeStamp"])) > cutoff_date]

    def analyze_behavior(self, wallet_address):
        try:
            wallet_data = self.load_wallet_data(wallet_address)
            if not wallet_data:
                return None

            transactions = wallet_data["Transaction History"]
            recent_transactions = self.filter_transactions(transactions, 30)

            if not recent_transactions:
                return "No transactions in the last 30 days."

            # Analyze transaction patterns
            tx_dates = [datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d') 
                       for tx in recent_transactions]
            date_counts = Counter(tx_dates)

            tx_hours = [datetime.utcfromtimestamp(int(tx["timeStamp"])).hour 
                       for tx in recent_transactions]
            hour_counts = Counter(tx_hours)

            # Calculate metrics
            avg_gas_used = sum(int(tx["gasUsed"]) for tx in recent_transactions) / len(recent_transactions)
            avg_gas_price = sum(int(tx["gasPrice"]) / 1e9 for tx in recent_transactions) / len(recent_transactions)
            
            repetitive_hours = sum(1 for count in hour_counts.values() if count > 5) / len(hour_counts)
            repetitive_days = sum(1 for count in date_counts.values() if count > 3) / len(date_counts)

            # Classify behavior
            if repetitive_days > 0.5 and repetitive_hours > 0.5 and avg_gas_used < 25000:
                classification = "Likely Bot"
                confidence = "High"
            elif repetitive_days > 0.3 or repetitive_hours > 0.3:
                classification = "Uncertain"
                confidence = "Medium"
            else:
                classification = "Likely Human"
                confidence = "High"

            return {
                "Classification": classification,
                "Confidence Level": confidence,
                "Key Indicators": {
                    "Average Gas Used": f"{avg_gas_used:.2f}",
                    "Average Gas Price (Gwei)": f"{avg_gas_price:.2f}",
                    "Repetitive Trading Hours": f"{repetitive_hours:.2%}",
                    "Repetitive Trading Days": f"{repetitive_days:.2%}"
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing behavior for wallet {wallet_address}: {str(e)}")
            raise

    def get_ai_analysis(self, behavior_data):
        try:
            prompt = f"""
            Analyze the following Ethereum wallet behavior data:
            - Classification: {behavior_data["Classification"]}
            - Confidence: {behavior_data["Confidence Level"]}
            - Key Indicators:
                - Avg Gas Used: {behavior_data["Key Indicators"]["Average Gas Used"]}
                - Avg Gas Price: {behavior_data["Key Indicators"]["Average Gas Price (Gwei)"]}
                - Repetitive Hours: {behavior_data["Key Indicators"]["Repetitive Trading Hours"]}
                - Repetitive Days: {behavior_data["Key Indicators"]["Repetitive Trading Days"]}

            Provide a detailed analysis of whether this wallet is operated by a bot or human.
            """

            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error getting AI analysis: {str(e)}")
            return "AI analysis failed"

    def analyze(self, wallet_address):
        """Main analysis method"""
        behavior_data = self.analyze_behavior(wallet_address)
        if isinstance(behavior_data, str):
            return behavior_data

        ai_analysis = self.get_ai_analysis(behavior_data)
        
        return {
            **behavior_data,
            "Analysis": ai_analysis
        } 