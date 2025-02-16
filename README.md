# 🔍 Wallet Analysis Project

## 📝 Description
This project provides a tool for analyzing Ethereum wallets, allowing users to collect and analyze data from Ethereum wallets. The tool uses agents to analyze behavior, transactions, trends, and the age of the wallet, generating detailed reports.

## 🛠️ Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/wallet-analysis.git
   cd wallet-analysis
   ```

2. **Install the required dependencies**:
   Use `pip` to install the necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file**:
   Create a `.env` file in the root directory of the project and add the necessary API keys:
   ```plaintext
   ETHERSCAN_KEY=your_etherscan_api_key
   GEMINI_KEY=your_gemini_api_key
   BINANCE_API_URL="https://api.binance.com/api/v3/ticker/price"
   ```

## 💡 Usage Examples

### 🚀 Running the Main File

After setting up and configuring the `.env` file, you can run the application using the following command:

To analyze a single wallet:
```bash
python main.py analyze-single <wallet_address>
```

To analyze multiple wallets from a JSON file:
```bash
python main.py analyze-batch <path_to_wallets_file.json>
```

### 🧹 Clearing Data and Reports

To clear all generated reports and optionally data files:
```bash
python main.py clear --data
```

### 📄 Listing Reports

To list all generated reports:
```bash
python main.py list_reports
```

## 🏗️ Design Decisions

- **🧩 Modular Architecture**: The project is designed with a modular architecture using agents for different analysis tasks (e.g., behavior, transaction, trend, and age analysis). This allows for easy maintenance and scalability.
- **🤖 AI Integration**: The project uses Gemini AI for providing insights and analysis, enhancing the depth of the reports.
- **🔐 Environment Configuration**: Sensitive information like API keys is managed using environment variables for security.

## ⚠️ Limitations and Assumptions

- **📊 Data Accuracy**: The accuracy of the analysis depends on the data provided by the APIs. Rate limits and data availability can affect the results.
- **🔍 Assumptions**: The analysis assumes that the transaction data is complete and accurate. Any missing data can lead to incorrect analysis.
- **⏳ Rate Limits**: The tool considers rate limits of data sources and implements retry mechanisms to handle temporary failures.

## 📂 Data Format

The wallet data is stored in JSON format with the following structure:
```json
{
    "Wallet Address": "0x...",
    "ETH Balance": 0.0,
    "Token Holdings": {
        "TOKEN_SYMBOL": 0.0
    },
    "Transaction History": [
        {
            "blockNumber": "block_number",
            "timeStamp": "timestamp",
            "hash": "transaction_hash",
            "nonce": "nonce",
            "blockHash": "block_hash",
            "transactionIndex": "transaction_index",
            "from": "sender_address",
            "to": "recipient_address",
            "value": "transaction_value",
            "gas": "gas",
            "gasPrice": "gas_price",
            "isError": "is_error",
            "txreceipt_status": "txreceipt_status",
            "input": "input_data",
            "contractAddress": "contract_address",
            "cumulativeGasUsed": "cumulative_gas_used",
            "gasUsed": "gas_used",
            "confirmations": "confirmations",
            "methodId": "method_id",
            "functionName": "function_name"
        }
    ]
}
```

## 🔄 Steps and Output

1. **📥 Data Collection**: Collects data from Etherscan API and stores it in JSON format.
2. **🔍 Analysis**: Uses different agents to analyze the collected data.
3. **📝 Report Generation**: Generates a detailed report and saves it in the `reports` directory.

## 🧪 Testing

To run tests for the project, use the following command:
```bash
pytest tests/
```
The tests verify the accuracy of the agents and workflow, ensuring everything functions as expected.

## 📊 Output Format

The analysis results will be saved as a report file in the `reports` directory. The report file will be formatted as follows:

```
╔══════════════════════════════════════════════════════════════════════════════
║ 📌 Wallet Analysis Report
║ Address: <wallet_address>
╠══════════════════════════════════════════════════════════════════════════════
║ 
║ 🕒 WALLET AGE ANALYSIS
First Transaction: YYYY-MM-DD
Wallet Age: X years, Y months, Z days
Category: [Category]
Analysis: [Brief interpretation]

╠══════════════════════════════════════════════════════════════════════════════
║ 📈 TREND ANALYSIS
30-Day Trend:
- Overall change: [increase/decrease/stable]
- Notable changes: [List significant changes]

90-Day Trend:
- Overall change: [increase/decrease/stable]
- Notable changes: [List significant changes]

180-Day Trend:
- Overall change: [increase/decrease/stable]
- Notable changes: [List significant changes]

Conclusion: [Interpretation of holder's strategy]

╠══════════════════════════════════════════════════════════════════════════════
║ 💰 TRANSACTION ANALYSIS
Average Transaction Size: $X (Classification: [Size Category])
Total 30-Day Volume: $Y (X% of total wallet value)

Top Assets in Transactions:
1. Asset A: X% (Direction: [Pattern])
2. Asset B: Y% (Direction: [Pattern])
3. Asset C: Z% (Direction: [Pattern])

Average Daily Transactions: X
Analysis: [Interpretation of behavior]

╠══════════════════════════════════════════════════════════════════════════════
║ 🤖 BEHAVIORAL ANALYSIS
Classification: [Bot/Human/Uncertain]
Confidence Level: [High/Medium/Low]
Key Indicators:
- [List key factors supporting classification]
- [List any contradicting factors]
Analysis: [Brief explanation of conclusion]

║ 
╚══════════════════════════════════════════════════════════════════════════════
```

