import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from phi.workflow import Workflow
from phi.utils.log import logger

from src.agents.behavior_agent import BehaviorAgent
from src.agents.transaction_agent import TransactionAgent
from src.agents.trend_agent import TrendAgent
from src.agents.wallet_age_agent import WalletAgeAgent
from src.agents.data_collector_agent import DataCollectorAgent
from src.config import get_wallet_data_path, get_report_path

class WalletAnalysisConfig(BaseModel):
    data_collector: Optional[DataCollectorAgent] = None
    behavior_agent: Optional[BehaviorAgent] = None
    transaction_agent: Optional[TransactionAgent] = None
    trend_agent: Optional[TrendAgent] = None
    wallet_age_agent: Optional[WalletAgeAgent] = None

    model_config = {
        "arbitrary_types_allowed": True
    }

class WalletAnalysisWorkflow(Workflow):
    config: WalletAnalysisConfig

    def __init__(self):
        # Initialize config first
        config = WalletAnalysisConfig(
            data_collector=DataCollectorAgent(),
            behavior_agent=BehaviorAgent(),
            transaction_agent=TransactionAgent(),
            trend_agent=TrendAgent(),
            wallet_age_agent=WalletAgeAgent()
        )
        
        # Pass config to parent class constructor
        super().__init__(name="wallet_analysis", config=config)

    def analyze_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Analyze a single wallet"""
        try:
            print('==================================')
            logger.info(f"Starting analysis for wallet: {wallet_address}")
            
            logger.info("Collecting data for wallet analysis")
            self.config.data_collector.collect_data(wallet_address)
            logger.info("Analyzing behavior")
            behavior_analysis = self.config.behavior_agent.analyze(wallet_address)
            logger.info("Analyzing transactions")
            transactions_analysis = self.config.transaction_agent.analyze(wallet_address)
            logger.info("Analyzing trends")
            trends_analysis = self.config.trend_agent.analyze(wallet_address)
            logger.info("Analyzing wallet age")
            age_analysis = self.config.wallet_age_agent.analyze(wallet_address)
            analysis_results = {
                "behavior": behavior_analysis,
                "transactions": transactions_analysis,
                "trends": trends_analysis,
                "age": age_analysis
            }
            
            # Generate and save report
            report = generate_final_report(
                wallet_address,
                analysis_results["age"],
                analysis_results["transactions"],
                analysis_results["trends"],
                analysis_results["behavior"]
            )
            report_path = get_report_path(wallet_address)
            report_path.write_text(report)
            
            logger.info(f"Analysis completed for wallet: {wallet_address}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing wallet {wallet_address}: {str(e)}")
            raise

    def run_batch(self, wallets: List[str]) -> Dict[str, Any]:
        """Run analysis for multiple wallets"""
        results = {}
        for wallet in wallets:
            try:
                results[wallet] = self.analyze_wallet(wallet)
            except Exception as e:
                results[wallet] = f"Analysis failed: {str(e)}"
        return results

def format_dict_to_string(d, indent=0):
    """Helper function to format dictionary data"""
    if not isinstance(d, dict):
        return str(d)
    
    result = []
    indent_str = "    " * indent
    for key, value in d.items():
        if isinstance(value, dict):
            result.append(f"{indent_str}{key}:")
            result.append(format_dict_to_string(value, indent + 1))
        elif isinstance(value, list):
            result.append(f"{indent_str}{key}:")
            for item in value:
                result.append(f"{indent_str} {item}")
        else:
            result.append(f"{indent_str}{key}: {value}")
    return "\n".join(result)

def generate_final_report(wallet, wallet_age_report, transaction_report, trend_report, behavior_report):
    """Generate a well-formatted report"""
    
    # Format each section
    age_section = format_dict_to_string(wallet_age_report, indent=1)
    trend_section = format_dict_to_string(trend_report, indent=1)
    transaction_section = format_dict_to_string(transaction_report, indent=1)
    behavior_section = format_dict_to_string(behavior_report, indent=1)
    
    report = f"""
╔══════════════════════════════════════════════════════════════════════════════
║ 📌 Wallet Analysis Report
║ Address: {wallet}
╠══════════════════════════════════════════════════════════════════════════════
║ 
║ 🕒 WALLET AGE ANALYSIS
{age_section}
╠══════════════════════════════════════════════════════════════════════════════
║ 📈 TREND ANALYSIS
{trend_section}
╠══════════════════════════════════════════════════════════════════════════════
║ 💰 TRANSACTION ANALYSIS
{transaction_section}
╠══════════════════════════════════════════════════════════════════════════════
║ 🤖 BEHAVIORAL ANALYSIS
{behavior_section}
║ 
╚══════════════════════════════════════════════════════════════════════════════
"""
    return report
