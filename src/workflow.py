import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from phi.workflow import Workflow
from phi.utils.log import logger
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

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
    console: Optional[Console] = None

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
            wallet_age_agent=WalletAgeAgent(),
            console=Console()  # Add console to config
        )
        
        # Pass config to parent class constructor
        super().__init__(name="wallet_analysis", config=config)

    def analyze_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """Analyze a single wallet"""
        try:
            self.config.console.rule("[bold blue]New Wallet Analysis", style="blue")
            self.config.console.print(Panel(f"[bold green]Analyzing wallet:[/] {wallet_address}", 
                                   border_style="green"))
            
            # Collect data with progress indicator
            with self.config.console.status("[bold yellow]Collecting wallet data...", spinner="dots"):
                self.config.data_collector.collect_data(wallet_address)

            analysis_results = {}
            analysis_steps = [
                ("behavior", self.config.behavior_agent, "Analyzing behavior patterns"),
                ("transactions", self.config.transaction_agent, "Analyzing transaction history"),
                ("trends", self.config.trend_agent, "Analyzing market trends"),
                ("age", self.config.wallet_age_agent, "Analyzing wallet age")
            ]

            for key, agent, message in analysis_steps:
                with self.config.console.status(f"[bold yellow]{message}...", spinner="dots"):
                    analysis_results[key] = agent.analyze(wallet_address)
                self.config.console.print(f"[green]✓[/] {message} completed")
            
            # Generate and save report
            with self.config.console.status("[bold yellow]Generating final report...", spinner="dots"):
                report = generate_final_report(
                    wallet_address,
                    analysis_results["age"],
                    analysis_results["transactions"],
                    analysis_results["trends"],
                    analysis_results["behavior"]
                )
                report_path = get_report_path(wallet_address)
                report_path.write_text(report)

            self.config.console.print(Panel("[bold green]Analysis completed successfully!", 
                                   border_style="green"))
            return analysis_results
            
        except Exception as e:
            error_message = f"Error analyzing wallet {wallet_address}: {str(e)}"
            self.config.console.print(Panel(f"[bold red]ERROR:[/] {error_message}", 
                                   border_style="red"))
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
    
    sections = [
        ("🕒 WALLET AGE ANALYSIS", wallet_age_report),
        ("📈 TREND ANALYSIS", trend_report),
        ("💰 TRANSACTION ANALYSIS", transaction_report),
        ("🤖 BEHAVIORAL ANALYSIS", behavior_report)
    ]
    
    formatted_sections = []
    for title, content in sections:
        section = f"║ {title}\n{format_dict_to_string(content, indent=1)}"
        formatted_sections.append(section)
    
    border_line = "═" * 70
    separator = f"\n╠{border_line}\n"
    
    report = (
        f"\n╔{border_line}\n"
        f"║ 📌 Wallet Analysis Report\n"
        f"║ Address: {wallet}\n"
        f"╠{border_line}\n"
        f"║ \n"
        f"{separator.join(formatted_sections)}\n"
        f"║ \n"
        f"╚{border_line}\n"
    )
    return report
