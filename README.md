# Waneye Financial World Dashboard

This project fetches financial headlines from multiple sources, generates a modern HTML dashboard (index.html) with cards for each headline (including images), and displays additional financial data like central bank rates, economic indicators, and forex information.

## How to Use
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set required API keys as environment variables:
   ```sh
   export OPENAI_API_KEY=your_api_key_here  # Required for AI image generation
   export NEWSAPI_API_KEY=your_api_key_here  # Optional for additional news sources
   export FMP_API_KEY=your_api_key_here      # Optional for additional news sources
   export MARKETAUX_API_KEY=your_api_key_here  # Optional for additional news sources
   export GNEWS_API_KEY=your_api_key_here    # Optional for additional news sources
   ```
4. Run the site generator:
   ```sh
   python generate_site.py
   ```
5. Open `index.html` in your browser to view the dashboard.

## Project Files
- `generate_site.py`: Main script to fetch data and generate the dashboard.
- `src/news.py`: Logic for fetching headlines, images, and generating AI images when needed.
- `src/htmlgen.py`: HTML generation for the dashboard with responsive design.
- `src/central_banks.py`: Fetches central bank data.
- `src/economic_data.py`: Fetches economic indicators.
- `src/forex_data.py`: Fetches forex exchange rates.
- `static/`: Contains CSS, JS, and images used in the dashboard.
- `.github/copilot-instructions.md`: Copilot custom instructions.

## Notes
- OpenAI API key is required for generating images for headlines when no image can be fetched.
- Without an OpenAI API key, the system will fall back to using colorful default images.
- At least one news API key is recommended for fetching headlines, but the system will attempt to fetch from available free sources if no API keys are provided.
- The dashboard is generated statically and can be hosted on any web server.
- The script is designed for educational and demonstration purposes.
