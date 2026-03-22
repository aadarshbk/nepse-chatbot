"""Utility helper functions."""
import re
import logging

logger = logging.getLogger(__name__)

NEPSE_SYMBOLS: dict[str, str] = {
    # Commercial Banks
    "NABIL":  "Commercial Bank", "HBL":    "Commercial Bank",
    "EBL":    "Commercial Bank", "KBL":    "Commercial Bank",
    "MBL":    "Commercial Bank", "BOKL":   "Commercial Bank",
    "NICA":   "Commercial Bank", "SCB":    "Commercial Bank",
    "SBI":    "Commercial Bank", "ADBL":   "Commercial Bank",
    "GBIME":  "Commercial Bank", "PRVU":   "Commercial Bank",
    "SANIMA": "Commercial Bank", "NIC":    "Commercial Bank",
    "NBB":    "Commercial Bank", "CBL":    "Commercial Bank",
    "PCBL":   "Commercial Bank", "SRBL":   "Commercial Bank",
    "LXBL":   "Commercial Bank", "NIMB":   "Commercial Bank",
    "MEGA":   "Commercial Bank", "CZBIL":  "Commercial Bank",
    "SBL":    "Commercial Bank", "CCBL":   "Commercial Bank",
    "NMB":    "Commercial Bank", "JBNL":   "Commercial Bank",
    "KUMARI": "Commercial Bank",
    # Development Banks
    "MLBL":   "Development Bank", "NCCB":   "Development Bank",
    "SHINE":  "Development Bank", "CORBL":  "Development Bank",
    "KSBBL":  "Development Bank", "SAPDBL": "Development Bank",
    "MNBBL":  "Development Bank", "NABBC":  "Development Bank",
    "SINDU":  "Development Bank",
    # Finance
    "GUFL": "Finance", "ICFC": "Finance",
    "MPFL": "Finance", "UFIL": "Finance", "SIFC": "Finance",
    # Insurance
    "NLIC":  "Insurance", "NLICL": "Insurance", "PICL": "Insurance",
    "LICN":  "Insurance", "PRIN":  "Insurance", "SGIC": "Insurance",
    "SIC":   "Insurance", "UIC":   "Insurance", "RBCL": "Insurance",
    "SRLI":  "Insurance",
    # Hydropower
    "HIDCL": "Hydropower", "CHCL":  "Hydropower", "UPPER": "Hydropower",
    "BPCL":  "Hydropower", "API":   "Hydropower", "NIFRA": "Hydropower",
    "RURU":  "Hydropower", "HPPL":  "Hydropower", "RADHI": "Hydropower",
    "RHPC":  "Hydropower", "GHL":   "Hydropower", "DHPL":  "Hydropower",
    "MKJC":  "Hydropower", "PMHPL": "Hydropower", "MANDU": "Hydropower",
    "BARUN": "Hydropower", "SHL":   "Hydropower", "KKHC":  "Hydropower",
    "UMHL":  "Hydropower", "HDHPC": "Hydropower",
    # Microfinance
    "NMBMF": "Microfinance", "CBBL":  "Microfinance", "SMFDB": "Microfinance",
    "SDBL":  "Microfinance", "GILB":  "Microfinance", "MLBSL": "Microfinance",
    "JSLBB": "Microfinance",
    # Manufacturing & Others
    "SHIVM": "Manufacturing", "HDL":  "Manufacturing", "JYOTI": "Manufacturing",
}


def get_symbol_sector(symbol: str) -> str:
    """Get sector for a given NEPSE symbol."""
    return NEPSE_SYMBOLS.get(symbol.upper(), "Unknown Sector")


def extract_stock_symbol(message: str, fallback: str = "NABIL") -> str:
    """
    Extract stock symbol from user message.
    Returns the symbol if found, otherwise returns fallback.
    """
    message = message.upper()
    for symbol in NEPSE_SYMBOLS.keys():
        if symbol in message:
            return symbol
    return fallback


def sanitize(text: str, max_length: int = 500) -> str:
    """
    Sanitize and truncate user input.
    """
    return text.strip()[:max_length]


def strip_markdown(text: str) -> str:
    """
    Remove all markdown formatting from text so it displays as clean plain text.
    
    Handles: **bold**, *italic*, # headers, ``` code blocks, `inline code`
    """
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # fenced code blocks
    text = re.sub(r'`(.+?)`',   r'\1', text)                # inline code
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)            # **bold**
    text = re.sub(r'\*(.+?)\*',     r'\1', text)            # *italic*
    text = re.sub(r'__(.+?)__',     r'\1', text)            # __bold__
    text = re.sub(r'_(.+?)_',       r'\1', text)            # _italic_
    text = re.sub(r'#{1,6}\s*',     '',    text)            # ## headings
    text = re.sub(r'\n{3,}', '\n\n', text)                  # collapse extra blank lines
    return text.strip()
