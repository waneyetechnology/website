"""
DeepSeek Financial Expert Class

This module provides AI-powered financial analysis using the DeepSeek API.
It analyzes financial headlines and provides comprehensive market insights.
"""

import os
import time
import requests
from ..log import logger


class DeepSeekFinancialExpert:
    """
    A financial expert AI that analyzes headlines and provides comprehensive market insights
    using the DeepSeek API.
    """

    # Default analysis question - can be customized via constructor or setter
    DEFAULT_ANALYSIS_QUESTION = "What's the current financial situation today, any news that I should pay the most attention to?"

    def __init__(self, api_key=None, analysis_question=None):
        """
        Initialize the DeepSeek Financial Expert.

        Args:
            api_key (str, optional): DeepSeek API key. If not provided, will look for DEEPSEEK_API_KEY env var.
            analysis_question (str, optional): Custom analysis question. If not provided, uses default.
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.model = "deepseek-chat"
        self.analysis_question = analysis_question or self.DEFAULT_ANALYSIS_QUESTION

        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY is not set. Financial analysis will be unavailable.")

    def is_available(self):
        """
        Check if the DeepSeek API is available (API key is configured).

        Returns:
            bool: True if API key is available, False otherwise.
        """
        return bool(self.api_key)

    def set_analysis_question(self, question):
        """
        Set a custom analysis question.

        Args:
            question (str): The analysis question to use for financial analysis
        """
        self.analysis_question = question
        logger.info(f"Analysis question updated: {question[:50]}...")

    def get_analysis_question(self):
        """
        Get the current analysis question.

        Returns:
            str: Current analysis question
        """
        return self.analysis_question

    def _prepare_headlines_text(self, headlines, max_headlines=None):
        """
        Prepare headlines text for analysis.

        Args:
            headlines (list): List of headline dictionaries
            max_headlines (int, optional): Maximum number of headlines to include. If None, includes all headlines.

        Returns:
            str: Formatted headlines text
        """
        # If max_headlines is None, use all headlines
        headlines_to_process = headlines if max_headlines is None else headlines[:max_headlines]

        headlines_text = ""
        for i, headline in enumerate(headlines_to_process, 1):
            headlines_text += f"{i}. {headline['headline']}\n"
            if headline.get('url'):
                # Extract just the domain from the URL
                from urllib.parse import urlparse
                try:
                    parsed_url = urlparse(headline['url'])
                    domain = parsed_url.netloc
                    # Remove 'www.' prefix if present for cleaner display
                    if domain.startswith('www.'):
                        domain = domain[4:]
                    headlines_text += f"   Source: {domain}\n"
                except Exception:
                    # Fallback to original URL if parsing fails
                    headlines_text += f"   Source: {headline['url']}\n"
            headlines_text += "\n"

        return headlines_text.strip()

    def _create_analysis_prompt(self, headlines_text):
        """
        Create the analysis prompt for the AI.

        Args:
            headlines_text (str): Formatted headlines text

        Returns:
            str: Complete analysis prompt
        """
        current_date = time.strftime("%B %d, %Y")
        current_time = time.strftime("%H:%M")

        return f"""You are DeepSeek, an advanced AI financial analyst with real-time financial news data provided.
Your expertise includes:
- Market analysis and trend identification
- Risk assessment and portfolio optimization
- Economic indicator interpretation
- Company fundamental analysis
- Technical analysis and chart patterns
- Global macro-economic insights

Your analysis should be:
1. Data-driven and evidence-based
2. Balanced with both opportunities and risks
3. Actionable with clear recommendations
4. Contextual with historical perspective
5. Forward-looking with scenario analysis

Provide a comprehensive analysis of today's financial headlines ({current_date}).

Headlines to analyze:
{headlines_text}

Please provide a detailed financial analysis answering: "{self.analysis_question}"

Your answer should be in JSON format to be consumed easily by other applications.

Format your response as a JSON object with the following structure:
{{
  "analysis_date": "{current_date}",
  "analysis_time": "{current_time}",
  "executive_summary": {{
    "key_highlights": ["Add as many key highlights as relevant to cover the main points"],
    "market_sentiment_score": 85,
    "overall_sentiment": "positive/negative/neutral"
  }},
  "market_insights": {{
    "sectors": [
      {{
        "sector": "Technology",
        "trend": "description",
        "implications": "impact analysis"
      }}
    ],
    "key_themes": ["Include all relevant themes identified from the headlines"]
  }},
  "risk_assessment": [
    {{
      "risk_factor": "Factor name",
      "impact": "High/Medium/Low",
      "likelihood": "High/Medium/Low",
      "mitigation": "Strategy description"
    }}
  ],
  "strategic_recommendations": {{
    "opportunities": [
      {{
        "recommendation": "Action to take",
        "rationale": "Why this is recommended",
        "tickers": ["Include relevant ticker symbols as appropriate"],
        "timeframe": "short/medium/long-term"
      }}
    ],
    "defensive_moves": [
      {{
        "recommendation": "Defensive action",
        "rationale": "Risk mitigation reasoning",
        "tickers": ["Include relevant defensive tickers as appropriate"],
        "timeframe": "short/medium/long-term"
      }}
    ]
  }},
  "market_outlook": {{
    "short_term": "1-3 month outlook",
    "long_term": "6-12 month outlook",
    "key_catalysts": ["Include all significant upcoming events or factors that could impact markets"],
    "watch_list": ["Include all important indicators, events, or metrics to monitor"]
  }}
}}

Provide comprehensive, data-driven analysis in this JSON structure without any markdown formatting."""

    def _make_api_request(self, prompt):
        """
        Make API request to DeepSeek.

        Args:
            prompt (str): Analysis prompt

        Returns:
            str or None: Analysis text or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": ("You are DeepSeek, a senior financial analyst with expertise in global markets, "
                               "providing comprehensive and actionable financial analysis. Your analysis "
                               "should be professional, data-driven, and include specific recommendations. "
                               "Always respond in JSON format when requested for easy consumption by applications.")
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,  # Lower temperature for more consistent, factual analysis
            "max_tokens": 4000,  # Sufficient for comprehensive analysis
            "stream": False
        }

        max_retries = 3
        retry_delay = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retrying DeepSeek API request (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff

                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=(30, 600)  # (connect timeout, read timeout)
                )

                if response.status_code == 200:
                    result = response.json()
                    analysis = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                    if analysis:
                        logger.info("Successfully generated financial analysis with DeepSeek")
                        return analysis
                    else:
                        logger.error("Empty analysis returned from DeepSeek")
                        return None
                else:
                    logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                    return None

            except requests.exceptions.Timeout as e:
                last_error = e
                logger.warning(f"DeepSeek API timeout (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"DeepSeek API failed after {max_retries} attempts: {last_error}")
                    return None
            except requests.exceptions.ConnectionError as e:
                last_error = e
                logger.warning(f"DeepSeek API connection error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"DeepSeek API failed after {max_retries} attempts: {last_error}")
                    return None
            except requests.exceptions.RequestException as e:
                last_error = e
                logger.error(f"Network error calling DeepSeek API (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"DeepSeek API failed after {max_retries} attempts: {last_error}")
                    return None
            except Exception as e:
                logger.error(f"Unexpected error calling DeepSeek API: {e}")
                return None

    def analyze_headlines(self, headlines, max_headlines=None):
        """
        Analyze financial headlines and provide comprehensive market insights.

        Args:
            headlines (list): List of headline dictionaries with 'headline' and 'url' keys
            max_headlines (int, optional): Maximum number of headlines to analyze. If None, analyzes all headlines.

        Returns:
            str or None: Comprehensive financial analysis or None if analysis failed
        """
        if not self.is_available():
            logger.warning("DeepSeek API key not available. Skipping financial analysis.")
            return None

        if not headlines:
            logger.warning("No headlines available for analysis")
            return None

        # Prepare headlines text
        headlines_text = self._prepare_headlines_text(headlines, max_headlines)
        if not headlines_text:
            logger.warning("No valid headlines text prepared for analysis")
            return None

        # Create analysis prompt
        prompt = self._create_analysis_prompt(headlines_text)

        # Make API request
        logger.info("Sending headlines to DeepSeek for financial analysis...")
        analysis = self._make_api_request(prompt)

        # Try to parse JSON response if available
        if analysis:
            try:
                import json
                import re

                # First try direct JSON parsing
                try:
                    json_data = json.loads(analysis)
                    logger.info("Successfully parsed JSON response from DeepSeek")
                    return json_data
                except json.JSONDecodeError:
                    pass

                # If direct parsing fails, try to clean and extract JSON
                # Remove any markdown formatting or extra text
                cleaned_analysis = analysis.strip()

                # Debug: Log the start of the response to see the format
                logger.debug(f"DeepSeek response starts with: {cleaned_analysis[:100]}...")

                # Check for the specific pattern mentioned by user: ```json { ... } ```
                if cleaned_analysis.startswith('```json') and cleaned_analysis.endswith('```'):
                    try:
                        # Extract JSON content between ```json and ```
                        json_content = cleaned_analysis[7:-3].strip()  # Remove ```json and ```
                        json_data = json.loads(json_content)
                        logger.info("Successfully extracted JSON from ```json code block")
                        return json_data
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse extracted JSON from code block: {e}")

                # Look for JSON block patterns - more comprehensive patterns
                json_patterns = [
                    r'```json\s*(\{.*?\})\s*```',        # ```json { ... } ```
                    r'```JSON\s*(\{.*?\})\s*```',        # ```JSON { ... } ``` (uppercase)
                    r'```\s*(\{.*?\})\s*```',            # ``` { ... } ``` (generic code blocks)
                    r'`json\s*(\{.*?\})\s*`',            # `json { ... } ` (single backticks)
                    r'json\s*(\{.*?\})',                 # json { ... } (no backticks)
                    r'(\{[^`]*?\})',                     # { ... } (any JSON-like content, avoiding backticks)
                ]

                for pattern in json_patterns:
                    matches = re.findall(pattern, cleaned_analysis, re.DOTALL)
                    for match in matches:
                        try:
                            json_data = json.loads(match.strip())
                            if isinstance(json_data, dict) and len(json_data) > 1:
                                logger.info("Successfully extracted and parsed JSON from DeepSeek response")
                                return json_data
                        except json.JSONDecodeError:
                            continue

                # If still no valid JSON found, check if it looks like JSON
                if cleaned_analysis.startswith('{') and cleaned_analysis.endswith('}'):
                    try:
                        # Try to fix common JSON issues
                        fixed_json = cleaned_analysis
                        # Fix any trailing commas
                        fixed_json = re.sub(r',\s*}', '}', fixed_json)
                        fixed_json = re.sub(r',\s*]', ']', fixed_json)

                        json_data = json.loads(fixed_json)
                        logger.info("Successfully parsed fixed JSON response from DeepSeek")
                        return json_data
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON response: {e}")
                        logger.debug(f"Raw response: {analysis[:500]}...")

                # Return raw text if all JSON parsing attempts fail
                logger.info("Could not parse response as JSON, returning raw text")
                return analysis

            except Exception as e:
                logger.error(f"Error processing DeepSeek response: {e}")
                return analysis

        return analysis

    def analyze_headlines_structured(self, headlines, max_headlines=None):
        """
        Analyze financial headlines and return structured data if JSON response is received.

        Args:
            headlines (list): List of headline dictionaries with 'headline' and 'url' keys
            max_headlines (int, optional): Maximum number of headlines to analyze. If None, analyzes all headlines.

        Returns:
            dict or str or None: Structured analysis data (if JSON), raw text, or None if failed
        """
        analysis = self.analyze_headlines(headlines, max_headlines)

        # If analysis is already a dict (JSON parsed), return it
        if isinstance(analysis, dict):
            return analysis

        # If it's a string, try to extract structured information
        if isinstance(analysis, str):
            # Try to find JSON-like patterns in the text
            try:
                import json
                import re

                # Look for JSON blocks in the text
                json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
                json_matches = re.findall(json_pattern, analysis, re.DOTALL)

                for match in json_matches:
                    try:
                        parsed = json.loads(match)
                        if isinstance(parsed, dict) and len(parsed) > 1:
                            logger.info("Extracted structured data from text response")
                            return parsed
                    except json.JSONDecodeError:
                        continue

                # If no JSON found, return original text
                return analysis

            except Exception as e:
                logger.debug(f"Error extracting structured data: {e}")
                return analysis

        return analysis

    def quick_sentiment_analysis(self, headlines, max_headlines=10):
        """
        Perform a quick sentiment analysis of headlines for faster processing.

        Args:
            headlines (list): List of headline dictionaries
            max_headlines (int): Maximum number of headlines to analyze

        Returns:
            dict or None: Sentiment analysis result with 'sentiment', 'score', and 'summary'
        """
        if not self.is_available():
            return None

        if not headlines:
            return None

        headlines_text = self._prepare_headlines_text(headlines, max_headlines)
        if not headlines_text:
            return None

        prompt = f"""Analyze the sentiment of these financial headlines and provide a brief assessment:

{headlines_text}

Respond in JSON format with:
- "sentiment": "positive", "negative", or "neutral"
- "score": integer from 1-100 (market optimism score)
- "summary": brief 2-3 sentence summary of key themes

Keep the response concise and data-focused."""

        # Use shorter timeout and lower token limit for quick analysis
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial sentiment analyst. Provide concise, accurate sentiment analysis in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 300,
            "stream": False
        }

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"Retrying quick sentiment analysis (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(retry_delay * (2 ** attempt))

                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=(15, 60)  # (connect timeout, read timeout)
                )

                if response.status_code == 200:
                    result = response.json()
                    analysis = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                    if analysis:
                        # Try to parse JSON response
                        import json
                        try:
                            sentiment_data = json.loads(analysis)
                            logger.info("Successfully generated quick sentiment analysis")
                            return sentiment_data
                        except json.JSONDecodeError:
                            logger.warning("Could not parse sentiment analysis JSON, returning raw text")
                            return {"summary": analysis, "sentiment": "neutral", "score": 50}

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"Sentiment analysis network error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Sentiment analysis failed after {max_retries} attempts")
                    return None
            except Exception as e:
                logger.error(f"Error in quick sentiment analysis: {e}")
                return None


# Factory function for easy import
def create_financial_expert(api_key=None, analysis_question=None):
    """
    Factory function to create a DeepSeek Financial Expert instance.

    Args:
        api_key (str, optional): DeepSeek API key
        analysis_question (str, optional): Custom analysis question

    Returns:
        DeepSeekFinancialExpert: Configured financial expert instance
    """
    return DeepSeekFinancialExpert(api_key, analysis_question)
