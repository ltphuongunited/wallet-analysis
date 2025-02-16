import json
import click
from src.workflow import WalletAnalysisWorkflow
from src.config import get_report_path, REPORTS_DIR, DATA_DIR
from pathlib import Path

@click.group()
def cli():
    """Wallet Analysis CLI"""
    pass

@cli.command()
@click.argument('wallet_address')
def analyze_single(wallet_address: str):
    """Analyze a single wallet"""
    workflow = WalletAnalysisWorkflow()
    result = workflow.analyze_wallet(wallet_address)
    click.echo(f"Analysis completed for {wallet_address}")
    click.echo(f"Report saved to: {get_report_path(wallet_address)}")

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def analyze_batch(input_file: str):
    """Analyze multiple wallets from a JSON file"""
    with open(input_file) as f:
        wallets = json.load(f)
    
    workflow = WalletAnalysisWorkflow()
    results = workflow.run_batch(wallets)
    
    success = sum(1 for r in results.values() if isinstance(r, dict))
    click.echo(f"Analysis completed: {success}/{len(wallets)} successful")

@cli.command()
@click.option('--data/--no-data', default=False, help='Also clear data files')
def clear(data: bool):
    """Clear all reports and optionally data files"""
    # Clear reports
    for file in REPORTS_DIR.glob("*.txt"):
        file.unlink()
    click.echo("Reports cleared")
    
    # Clear data if requested
    if data:
        for file in DATA_DIR.glob("*.json"):
            file.unlink()
        click.echo("Data files cleared")

@cli.command()
def list_reports():
    """List all generated reports"""
    reports = list(REPORTS_DIR.glob("*.txt"))
    if not reports:
        click.echo("No reports found")
        return
    
    click.echo("\nAvailable reports:")
    for report in reports:
        click.echo(f"- {report.name}")

if __name__ == "__main__":
    cli() 