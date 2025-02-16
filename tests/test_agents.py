import pytest
from src.agents.behavior_agent import BehaviorAgent
from src.agents.transaction_agent import TransactionAgent
from src.agents.trend_agent import TrendAgent
from src.agents.wallet_age_agent import WalletAgeAgent
from src.agents.data_collector_agent import DataCollectorAgent
from src.workflow import WalletAnalysisWorkflow

@pytest.fixture
def test_wallet():
    return "0x60761c78308a866b5cc0dbc443c5a04e4f705115"

@pytest.fixture
def workflow():
    return WalletAnalysisWorkflow()

def test_data_collector_agent(test_wallet):
    agent = DataCollectorAgent()
    result = agent.collect_data(test_wallet)
    assert result is not None
    
def test_behavior_agent(test_wallet):
    agent = BehaviorAgent()
    result = agent.analyze(test_wallet)
    assert result is not None
    assert "Classification" in result

def test_transaction_agent(test_wallet):
    agent = TransactionAgent()
    result = agent.analyze(test_wallet)
    assert result is not None
    assert "Average Transaction Size" in result

def test_trend_agent(test_wallet):
    agent = TrendAgent()
    result = agent.analyze(test_wallet)
    assert result is not None
    assert "30-Day Trend" in result

def test_wallet_age_agent(test_wallet):
    agent = WalletAgeAgent()
    result = agent.analyze(test_wallet)
    assert result is not None
    assert "Wallet Age" in result

def test_workflow_integration(workflow, test_wallet):
    result = workflow.analyze_wallet(test_wallet)
    assert result is not None
    assert isinstance(result, str)
