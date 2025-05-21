# Waneye Financial World Dashboard

This project fetches the CNN.com homepage HTML and uses an LLM API to extract the top 5 financial/economics-related headlines, then generates a modern HTML dashboard (index.html) with additional financial data.

## How to Use
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set your LLM API endpoint and key in the source code if you wish to use a real LLM (currently uses mock data).
4. Run the site generator:
   ```sh
   python generate_site.py
   ```
5. Open `index.html` in your browser to view the dashboard.

## Project Files
- `generate_site.py`: Main script to fetch, extract, and generate the dashboard.
- `src/`: Source folder containing all logic for news, central banks, economic data, forex, and HTML generation.
- `.github/copilot-instructions.md`: Copilot custom instructions.

## Notes
- You need access to an LLM API (such as OpenAI, Azure, etc.) for real headline extraction. The current version uses mock data for demonstration.
- The script is designed for educational and demonstration purposes.
