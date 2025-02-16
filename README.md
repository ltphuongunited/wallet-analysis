# 🔍 Wallet Analysis Project

## 📝 Description
This project provides a tool for analyzing Ethereum wallets, allowing users to collect and analyze data from Ethereum wallets. The tool uses agents to analyze behavior, transactions, trends, and the age of the wallet, generating detailed reports.

## 🛠️ Setup Instructions

1. **Install the required dependencies**:
   Use `pip` to install the necessary libraries:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file**:
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
            "timeStamp": "timestamp",
            "value": "transaction_value",
            "to": "recipient_address",
            "tokenSymbol": "TOKEN_SYMBOL"
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
- First Transaction: <date>
- Wallet Age: <age>
- Category: <category>
║ 
║ 📈 TREND ANALYSIS
- 30-Day Trend: <trend>
- Notable Changes: <changes>
║ 
║ 💰 TRANSACTION ANALYSIS
- Average Transaction Size: <size>
- Total Volume: <volume>
║ 
║ 🤖 BEHAVIORAL ANALYSIS
- Classification: <classification>
- Confidence Level: <confidence>
║ 
╚══════════════════════════════════════════════════════════════════════════════
```

