# CNN Financial Headlines Extractor

This project fetches the CNN.com homepage HTML and uses an LLM API to extract the top 5 financial/economics-related headlines, printing them to the console.

## How to Use
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```sh
   pip install requests
   ```
3. Set your LLM API endpoint and key in the script.
4. Run the script:
   ```sh
   python cnn_financial_headlines.py
   ```

## Project Files
- `cnn_financial_headlines.py`: Main script to fetch and extract headlines.
- `.github/copilot-instructions.md`: Copilot custom instructions.

## Notes
- You need access to an LLM API (such as OpenAI, Azure, etc.) for this script to work.
- The script is designed for educational and demonstration purposes.
