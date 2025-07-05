from .log import logger

from .news import fetch_financial_headlines
from .central_banks import fetch_central_bank_policies, fetch_central_bank_rates
from .economic_data import fetch_economic_data
from .forex_data import fetch_forex_cfd_data
from .htmlgen import generate_html
