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
    rates = []
    for bank in banks:
        try:
            resp = requests.get(bank["url"], timeout=10)
            if resp.ok:
                text = resp.text
                # Try to extract a rate (look for numbers like 5.25%, 0.10%, etc.)
                match = re.search(r'(\d+\.\d+|\d+)[ ]?%?', text)
                rate = match.group(0) if match else "Rate not found"
                rates.append({"bank": bank["name"], "rate": rate, "url": bank["url"]})
            else:
                rates.append({"bank": bank["name"], "rate": "Could not fetch rate", "url": bank["url"]})
        except Exception:
            rates.append({"bank": bank["name"], "rate": "Error fetching rate", "url": bank["url"]})
    return rates
