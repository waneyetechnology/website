from .log import logger
import requests
import re
import html

def fetch_central_bank_policies():
    """
    Fetches the latest policy statements, rate decisions, and monetary policy outlooks for the 9 most important central banks for traders.
    Returns a list of dicts: {"bank": ..., "policy": ...}
    """
    banks = [
        {"name": "Federal Reserve", "country": "United States", "code": "fed", "url": "https://www.federalreserve.gov/monetarypolicy.htm"},
        {"name": "European Central Bank", "country": "Eurozone", "code": "ecb", "url": "https://www.ecb.europa.eu/press/pr/date/latest/html/index.en.html"},
        {"name": "Bank of England", "country": "United Kingdom", "code": "boe", "url": "https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes"},
        {"name": "Bank of Japan", "country": "Japan", "code": "boj", "url": "https://www.boj.or.jp/en/mopo/mpmdeci/index.htm/"},
        {"name": "Swiss National Bank", "country": "Switzerland", "code": "snb", "url": "https://www.snb.ch/en/iabout/stat/statpub/zirefi/id/statpub_zirefi_hist"},
        {"name": "Bank of Canada", "country": "Canada", "code": "boc", "url": "https://www.bankofcanada.ca/press/press-releases/"},
        {"name": "Reserve Bank of Australia", "country": "Australia", "code": "rba", "url": "https://www.rba.gov.au/media-releases/"},
        {"name": "People's Bank of China", "country": "China", "code": "pboc", "url": "http://www.pbc.gov.cn/english/130721/index.html"},
        {"name": "Reserve Bank of New Zealand", "country": "New Zealand", "code": "rbnz", "url": "https://www.rbnz.govt.nz/news"},
    ]
    policies = []
    keywords = [
        "monetary policy", "interest rate decision", "policy statement",
        "inflation outlook", "economic projections", "rate decision",
        "policy committee", "central bank statement"
    ]
    boilerplate_keywords = [
        "copyright", "contact us", "terms of use", "privacy policy", "terms of service",
        "skip to main content", "official website", "toggle navigation", "go to main content",
        "accessibility", "sitemap", "search", "menu", "home", "about us", "careers",
        "all rights reserved", "last updated", "share this page", "print this page",
        "media releases", "press releases", "publications", "news", "events", "videos",
        "related links", "follow us", "subscribe", "sign up", "log in", "register",
        "feedback", "help", "faq", "glossary", "archive", "archives", "download", "pdf",
        "disclaimer", "legal", "notices", "site map", "related topics", "more information",
        "key topics", "useful links", "language selection", "choose language", "español", "français"
    ]
    pboc_report_keywords = ["monetary policy report", "policy release", "pbc news"]

    for bank in banks:
        is_debug_bank = bank["name"] in ["Bank of Canada", "Bank of Japan", "Federal Reserve"] # Keep light log for Fed too
        try:
            resp = requests.get(bank["url"], timeout=20)
            resp.raise_for_status()

            # Use utf-8-sig to handle BOM transparently
            text_content = resp.content.decode('utf-8-sig', errors='replace')

            # Secondary BOM strip, just in case (though utf-8-sig should handle it)
            if text_content.startswith('\ufeff'):
                text_content = text_content[1:]

            text_content = re.sub(r'<script[^>]*>.*?</script>', '', text_content, flags=re.DOTALL | re.IGNORECASE)
            text_content = re.sub(r'<style[^>]*>.*?</style>', '', text_content, flags=re.DOTALL | re.IGNORECASE)
            text_content = html.unescape(text_content)
            text_content = re.sub(r'<[^>]+>', '', text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()

            if is_debug_bank:
                 logger.debug(f"{bank['name']} POST-HTML_CLEAN (first 300 chars): {text_content[:300]}")

            paragraphs = [p.strip() for p in re.split(r'\n\s*\n+', text_content) if p.strip()]
            if (bank["name"] in ["Bank of Canada", "Bank of Japan"]) and len(paragraphs) < 10: # Adjusted threshold
                if is_debug_bank: logger.debug(f"{bank['name']} HAD {len(paragraphs)} paragraphs with multi-newline split, trying single newline.")
                paragraphs_single_split = [p.strip() for p in text_content.splitlines() if p.strip()]
                if len(paragraphs_single_split) > len(paragraphs):
                    paragraphs = paragraphs_single_split
                    if is_debug_bank: logger.debug(f"{bank['name']} Using single-newline split, now {len(paragraphs)} paragraphs.")

            relevant_paragraphs_indices = []
            for i, p_text in enumerate(paragraphs):
                p_lower = p_text.lower()

                # Advanced Boilerplate Check:
                # Count how many different boilerplate keywords are in the paragraph
                bp_matches = sum(1 for bp_keyword in boilerplate_keywords if bp_keyword in p_lower)

                is_bp = False
                if bp_matches > 0 and len(p_text) < 250: # If any boilerplate keyword in a short-ish paragraph
                    is_bp = True
                elif bp_matches >= 2: # Or if multiple (2+) boilerplate keywords, likely a footer/nav block
                    is_bp = True

                if is_bp:
                    # if is_debug_bank: logger.debug(f"Boilerplate para: {p_text[:100]}...") # Reduce logging
                    continue

                if len(p_text) < 25: # Skip very short paragraphs (slightly reduced from 30)
                    # if is_debug_bank: logger.debug(f"Too short para: {p_text[:100]}...") # Reduce logging
                    continue

                has_policy_keywords = any(kw.lower() in p_lower for kw in keywords)
                is_pboc_report = (bank["name"] == "People's Bank of China" and \
                                  any(pboc_kw.lower() in p_lower for pboc_kw in pboc_report_keywords))

                if has_policy_keywords or is_pboc_report:
                    relevant_paragraphs_indices.append(i)

            # if is_debug_bank: logger.debug(f"{bank['name']} Relevant para indices: {relevant_paragraphs_indices}") # Reduce logging

            collected_paragraphs_text = []
            if relevant_paragraphs_indices:
                for rel_idx in relevant_paragraphs_indices:
                    collected_paragraphs_text.append(paragraphs[rel_idx])
                    if bank["name"] in ["Bank of Canada", "Bank of Japan", "People's Bank of China", "Reserve Bank of Australia"]: # Apply to RBA too
                        # Grab next 1-2 non-boilerplate, sufficiently long paragraphs
                        for lookahead in range(1, 3): # Look 1 or 2 paragraphs ahead
                            next_idx = rel_idx + lookahead
                            if next_idx < len(paragraphs) and next_idx not in relevant_paragraphs_indices:
                                next_p_text = paragraphs[next_idx]
                                next_p_lower = next_p_text.lower()
                                next_bp_matches = sum(1 for bp_keyword in boilerplate_keywords if bp_keyword in next_p_lower)

                                is_next_bp = False
                                if next_bp_matches > 0 and len(next_p_text) < 250: is_next_bp = True
                                elif next_bp_matches >=2: is_next_bp = True

                                if not is_next_bp and len(next_p_text) > 50: # Ensure it's reasonably long
                                    collected_paragraphs_text.append(next_p_text)
                                else: # If the immediate next is boilerplate/short, stop looking further for this block
                                    break
                            else: # Out of bounds or already included
                                break
                final_relevant_paragraphs_text = list(dict.fromkeys(collected_paragraphs_text)) # Remove duplicates
            else:
                final_relevant_paragraphs_text = []

            # if is_debug_bank: logger.debug(f"{bank['name']} Collected paras: {final_relevant_paragraphs_text[:2]}") # Reduce logging

            extracted_summary = ""
            if final_relevant_paragraphs_text:
                full_relevant_text = " ".join(final_relevant_paragraphs_text)
                # Sentence splitting logic remains the same
                sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', full_relevant_text)

                current_summary_sentences = []
                char_count = 0
                sentence_target = 3 # Aim for 3 good sentences

                for sentence_text in sentences:
                    sentence_text = sentence_text.strip()
                    if not sentence_text: continue

                    # Try to ensure sentences are somewhat substantial
                    if len(sentence_text) < 20 and len(current_summary_sentences) > 0 : continue # Avoid very short follow-up sentences

                    # Prioritize sentences with keywords, but take initial sentences anyway to start building context
                    if any(keyword.lower() in sentence_text.lower() for keyword in keywords) or len(current_summary_sentences) < sentence_target:
                        current_summary_sentences.append(sentence_text)
                        char_count += len(sentence_text) + 1
                        if len(current_summary_sentences) >= sentence_target and char_count > 200: # If we have enough sentences and reasonable length
                            break
                        if char_count > 450: # Absolute max char count
                            break

                extracted_summary = " ".join(current_summary_sentences)
                if len(extracted_summary) > 500:
                    extracted_summary = extracted_summary[:497] + "..."

            if not extracted_summary:
                policy_summary = "Relevant policy information not found after filtering."
            else:
                policy_summary = extracted_summary

            policies.append({"bank": bank["name"], "policy": policy_summary, "url": bank["url"]})

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching policy for {bank['name']} from {bank['url']}: {e}")
            policies.append({"bank": bank["name"], "policy": f"Could not fetch policy: Request error ({type(e).__name__}).", "url": bank["url"]})
        except Exception as e:
            logger.error(f"Generic error processing policy for {bank['name']} from {bank['url']}: {e}", exc_info=True)
            policies.append({"bank": bank["name"], "policy": "Error processing policy data.", "url": bank["url"]})

    return policies

def fetch_central_bank_rates():
    """
    Fetches the latest policy/interest rate for each of the 9 major central banks.
    Returns a list of dicts: {"bank": ..., "rate": ..., "url": ...}
    """
    banks = [
        {"name": "Federal Reserve", "code": "fed", "url": "https://www.federalreserve.gov/monetarypolicy/openmarket.htm"},
        {"name": "European Central Bank", "code": "ecb", "url": "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/key_ecb_interest_rates/html/index.en.html"},
        {"name": "Bank of England", "code": "boe", "url": "https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp"},
        {"name": "Bank of Japan", "code": "boj", "url": "https://www.boj.or.jp/en/statistics/boj/other/interest/index.htm/"},
        {"name": "Swiss National Bank", "code": "snb", "url": "https://www.snb.ch/en/iabout/stat/statpub/zirefi/id/statpub_zirefi_hist"},
        {"name": "Bank of Canada", "code": "boc", "url": "https://www.bankofcanada.ca/rates/interest-rates/canadian-interest-rates/"},
        {"name": "Reserve Bank of Australia", "code": "rba", "url": "https://www.rba.gov.au/statistics/cash-rate/"},
        {"name": "People's Bank of China", "code": "pboc", "url": "http://www.pbc.gov.cn/en/3688229/index.html"},
        {"name": "Reserve Bank of New Zealand", "code": "rbnz", "url": "https://www.rbnz.govt.nz/monetary-policy/official-cash-rate"},
    ]
    rates_data = []

    # Define bank-specific extraction rules
    # Rule: (keyword_to_find, regex_for_rate_after_keyword, search_window_chars)
    # The regex_for_rate_after_keyword should have one capturing group for the rate value itself.
    # Define a more robust general regex for rate values
    robust_rate_regex = r"(-?\d+(?:\.\d+)?)\s*(?:%|percent|per\s*cent)\b" # \b for word boundary

    bank_specific_rules = {
        "fed": [
            ("federal funds rate target range", r"(\d+\.\d+\s*(?:to|-)\s*\d+\.\d+\s*percent|\d+(?:\.\d+)?\s*percent|\d+(?:\.\d+)?%)", 250),
            ("federal funds rate", r"(\d+(?:\.\d+)?\s*(?:to|-)\s*\d+(?:\.\d+)?\s*percent|\d+(?:\.\d+)?\s*percent|\d+(?:\.\d+)?%)", 250)
        ],
        "ecb": [ # Keywords are already lowercase
            ("main refinancing operations", robust_rate_regex, 150),
            ("deposit facility", robust_rate_regex, 150),
            ("marginal lending facility", robust_rate_regex, 150)
        ],
        "boe": [
            ("bank rate", robust_rate_regex, 150)
        ],
        "boj": [
            ("uncollateralized overnight call rate", r"(around\s*-?\d+\.\d+|-?\d+\.\d+)\s*(?:%|percent|per\s*cent)\b", 250),
            ("short-term policy interest rate", r"(-?\d+\.\d+)\s*(?:%|percent|per\s*cent)\b", 200)
        ],
        "snb": [
            ("snb policy rate", robust_rate_regex, 150)
        ],
        "boc": [
            ("policy interest rate", robust_rate_regex, 150),
            ("target for the overnight rate", robust_rate_regex, 150)
        ],
        "rba": [
            ("cash rate target", robust_rate_regex, 150), # Will handle "per cent"
            ("cash rate", robust_rate_regex, 150)
        ],
        "pboc": [
            ("loan prime rate \(lpr\)", robust_rate_regex, 200),
            ("lpr", robust_rate_regex, 150)
        ],
        "rbnz": [
            ("official cash rate \(ocr\)", robust_rate_regex, 200),
            ("official cash rate", robust_rate_regex, 150)
        ]
    }

    generic_fallbacks = [
        (r"policy interest rate", robust_rate_regex, 150),
        (r"interest rate", robust_rate_regex, 150),
        (r"cash rate", robust_rate_regex, 150),
        (r"benchmark rate", robust_rate_regex, 150),
    ]

    # More restrictive: numbers < 50%, up to 2 decimal places. \b for word boundary.
    last_resort_percentage_regex = r"\b((?:[0-9]|[1-4][0-9])(?:\.\d{1,2})?|0\.\d{1,2})\s*%"

    # Banks to provide detailed search_area logging for this run
    debug_search_area_banks = ["Federal Reserve", "European Central Bank", "Bank of Canada", "Reserve Bank of Australia", "People's Bank of China"]

    for bank in banks:
        rate_str = "Rate not found"
        keyword_found_for_bank = False # Flag to control last resort regex application
        try:
            resp = requests.get(bank["url"], timeout=15)
            resp.raise_for_status()

            text = resp.text
            clean_text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
            clean_text = re.sub(r'<style[^>]*>.*?</style>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            clean_text_lower = clean_text.lower()

            if bank["name"] == "Federal Reserve":
                 logger.debug(f"Cleaned text for {bank['name']} (first 500 chars): {clean_text_lower[:500]}")

            bank_code = bank.get("code")
            if bank_code in bank_specific_rules:
                logger.info(f"Attempting specific rules for {bank['name']}...")
                for keyword, rate_regex_str, window in bank_specific_rules[bank_code]:
                    keyword_match = re.search(keyword, clean_text_lower)
                    if keyword_match:
                        keyword_found_for_bank = True
                        logger.info(f"Keyword '{keyword}' found for {bank['name']}.")
                        start_index = keyword_match.end()
                        search_area = clean_text[start_index : start_index + window]
                        if bank["name"] in debug_search_area_banks:
                            logger.debug(f"Search area for {bank['name']} (rule '{keyword}'): '{search_area}'")

                        rate_match = re.search(rate_regex_str, search_area, re.IGNORECASE)
                        if rate_match and rate_match.group(1):
                            rate_str = rate_match.group(1).strip()
                            rate_str = re.sub(r"\s*(?:percent|per\s*cent)\s*", "%", rate_str, flags=re.IGNORECASE) # Normalize
                            if "%" not in rate_str and ("rate" in keyword or "target" in keyword or "facility" in keyword):
                                rate_str += "%"
                            logger.info(f"Rate regex matched for {bank['name']} ('{keyword}'). Extracted: {rate_str}")
                            break
                    # else: logger.info(f"Keyword '{keyword}' NOT found for {bank['name']}.") # Too verbose
                if rate_str != "Rate not found":
                    rates_data.append({"bank": bank["name"], "rate": rate_str, "url": bank["url"]})
                    continue

            if rate_str == "Rate not found":
                logger.info(f"Specific rules failed for {bank['name']}. Trying generic fallbacks...")
                for keyword_regex_str_generic, rate_regex_str_generic, window_generic in generic_fallbacks:
                    keyword_match_generic = re.search(keyword_regex_str_generic, clean_text_lower) # Search in lower text
                    if keyword_match_generic:
                        keyword_found_for_bank = True
                        logger.info(f"Generic keyword regex '{keyword_regex_str_generic}' found for {bank['name']}.")
                        start_index_generic = keyword_match_generic.end()
                        search_area_generic = clean_text[start_index_generic : start_index_generic + window_generic]
                        if bank["name"] in debug_search_area_banks:
                             logger.debug(f"Search area for {bank['name']} (generic rule '{keyword_regex_str_generic}'): '{search_area_generic}'")

                        rate_match_generic = re.search(rate_regex_str_generic, search_area_generic, re.IGNORECASE)
                        if rate_match_generic and rate_match_generic.group(1):
                            rate_str = rate_match_generic.group(1).strip()
                            rate_str = re.sub(r"\s*(?:percent|per\s*cent)\s*", "%", rate_str, flags=re.IGNORECASE) # Normalize
                            logger.info(f"Generic rate regex matched for {bank['name']}. Extracted: {rate_str}")
                            break
                if rate_str != "Rate not found":
                    rates_data.append({"bank": bank["name"], "rate": rate_str, "url": bank["url"]})
                    continue

            if rate_str == "Rate not found" and not keyword_found_for_bank: # Only use last resort if NO keywords were found
                logger.info(f"Generic fallbacks failed for {bank['name']} AND no keywords previously found. Trying last resort percentage regex...")
                match = re.search(last_resort_percentage_regex, clean_text) # Search on original case text for this specific regex
                if match:
                    # This regex already includes % in its capture group or implies it by structure
                    rate_str = match.group(1).strip()
                    # No need to re-add %, already part of regex logic or implied by it for <50 values
                    logger.info(f"Last resort percentage regex matched for {bank['name']}. Extracted: {rate_str}")
            elif rate_str == "Rate not found" and keyword_found_for_bank:
                 logger.info(f"Keywords were found for {bank['name']}, but rate value regexes failed. NOT using last resort regex.")


            rates_data.append({"bank": bank["name"], "rate": rate_str, "url": bank["url"]})

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching rate for {bank['name']} from {bank['url']}: {e}")
            rates_data.append({"bank": bank["name"], "rate": "Could not fetch rate (Request Error)", "url": bank["url"]})
        except Exception as e:
            logger.error(f"Generic error processing rate for {bank['name']}: {e}", exc_info=True)
            rates_data.append({"bank": bank["name"], "rate": "Error processing rate data", "url": bank["url"]})

    return rates_data
