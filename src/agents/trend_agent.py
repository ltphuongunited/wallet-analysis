from phi.agent import Agent
from phi.utils.log import logger
from datetime import datetime, timedelta
import google.generativeai as genai
import json
import os

class TrendAgent(Agent):
    def __init__(self):
        super().__init__(name="trend_analyzer")
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

    def calculate_trend(self, wallet_address, days):
        try:
            wallet_data = self.load_wallet_data(wallet_address)
            if not wallet_data:
                return None

            transactions = wallet_data["Transaction History"]
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            filtered_transactions = [tx for tx in transactions 
                                   if datetime.utcfromtimestamp(int(tx["timeStamp"])) > cutoff_date]

            current_value = wallet_data.get("Total Portfolio Value", 0)
            past_value = current_value - sum([float(tx["value"]) / 1e18 
                                            for tx in filtered_transactions])

            trend = "Increase" if past_value < current_value else "Decrease" if past_value > current_value else "Stable"

            notable_changes = [tx["hash"] for tx in filtered_transactions[:5]]

            return {
                "Time Period": f"{days}-Day",
                "Overall Change": trend,
                "Notable Changes": notable_changes
            }

        except Exception as e:
            logger.error(f"Error calculating trend for wallet {wallet_address}: {str(e)}")
            raise

    def get_ai_analysis(self, trends):
        try:
            conclusion = "The wallet holder's strategy appears to be focused on " + \
                         ("accumulation." if trends["180"]["Overall Change"] == "Increase" else "consolidation." if trends["180"]["Overall Change"] == "Stable" else "liquidation.")
            
            prompt = f"""
            Analyze the following Ethereum wallet:
            30-Day Trend:
            - Overall change: {trends["30"]["Overall Change"]}
            - Notable changes: {', '.join(trends["30"]["Notable Changes"])}

            90-Day Trend:
            - Overall change: {trends["90"]["Overall Change"]}
            - Notable changes: {', '.join(trends["90"]["Notable Changes"])}

            180-Day Trend:
            - Overall change: {trends["180"]["Overall Change"]}
            - Notable changes: {', '.join(trends["180"]["Notable Changes"])}

            Provide interpretation of holder's strategy. Only return final conclusion.
            """

            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            logger.error(f"Error getting AI analysis: {str(e)}")
            return "AI analysis failed"

    def analyze(self, wallet_address):
        """Main analysis method"""
        trends = {
            "30": self.calculate_trend(wallet_address, 30),
            "90": self.calculate_trend(wallet_address, 90),
            "180": self.calculate_trend(wallet_address, 180)
        }

        ai_analysis = self.get_ai_analysis(trends)
        
        formatted_output = f"""30-Day Trend:
- Overall change: {trends["30"]["Overall Change"]}
- Notable changes:
    {chr(10).join(['    • ' + change for change in trends["30"]["Notable Changes"]])}

90-Day Trend:
- Overall change: {trends["90"]["Overall Change"]}
- Notable changes:
    {chr(10).join(['    • ' + change for change in trends["90"]["Notable Changes"]])}

180-Day Trend:
- Overall change: {trends["180"]["Overall Change"]}
- Notable changes:
    {chr(10).join(['    • ' + change for change in trends["180"]["Notable Changes"]])}

Conclusion: {ai_analysis}"""

        return formatted_output