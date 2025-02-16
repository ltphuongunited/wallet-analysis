from phi.agent import Agent
from phi.utils.log import logger
from datetime import datetime
import google.generativeai as genai
import json
import os
from ..config import API_CONFIG

class WalletAgeAgent(Agent):
    def __init__(self):
        super().__init__(name="age_analyzer")
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

    def calculate_age(self, transaction_history):
        try:
            if not transaction_history:
                return None

            first_tx = min(transaction_history, key=lambda x: int(x["timeStamp"]))
            first_tx_time = int(first_tx["timeStamp"])
            first_tx_date = datetime.utcfromtimestamp(first_tx_time).strftime('%Y-%m-%d')

            age_days = (datetime.utcnow() - datetime.utcfromtimestamp(first_tx_time)).days
            age_years, remaining_days = divmod(age_days, 365)
            age_months = remaining_days // 30
            age_days = remaining_days % 30  # Calculate remaining days

            if age_years >= 5:
                category = "Veteran"
            elif age_years >= 2:
                category = "Established"
            elif age_years >= 1:
                category = "Intermediate"
            else:
                category = "Newcomer"

            return {
                "First Transaction": first_tx_date,
                "Wallet Age": f"{age_years} years, {age_months} months, {age_days} days",
                "Category": category
            }

        except Exception as e:
            logger.error(f"Error calculating wallet age: {str(e)}")
            raise

    def get_ai_analysis(self, age_data):
        try:
            prompt = f"""
            Analyze the following Ethereum wallet age data:
            - First Transaction: {age_data["First Transaction"]}
            - Wallet Age: {age_data["Wallet Age"]}
            - Category: {age_data["Category"]}

            Provide a brief interpretation of what the wallet's age suggests about the holder's experience.
            """

            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error getting AI analysis: {str(e)}")
            return "AI analysis failed"

    def analyze(self, wallet_address):
        """Main analysis method"""
        wallet_data = self.load_wallet_data(wallet_address)
        if not wallet_data:
            return None

        age_data = self.calculate_age(wallet_data["Transaction History"])
        if not age_data:
            return "No transaction history available"

        ai_analysis = self.get_ai_analysis(age_data)
        
        return {
            **age_data,
            "Analysis": ai_analysis
        } 