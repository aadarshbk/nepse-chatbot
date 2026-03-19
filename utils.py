# utils.py
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
    "UNL":   "Manufacturing", "BNL":  "Manufacturing", "SPUBL": "Others",
    "SRL":   "Others",        "CIT":  "Investment",    "NIBL":  "Investment",
}

_SYMBOL_SET: set[str] = set(NEPSE_SYMBOLS.keys())


def extract_stock_symbol(message: str, fallback: str = "NABIL") -> str:
    if not message or not message.strip():
        return fallback
    for word in re.findall(r'\b[A-Za-z]{2,6}\b', message):
        symbol = word.upper()
        if symbol in _SYMBOL_SET:
            logger.debug(f"Symbol '{symbol}' extracted.")
            return symbol
    return fallback


def is_valid_symbol(symbol: str) -> bool:
    return symbol.upper().strip() in _SYMBOL_SET


def get_symbol_sector(symbol: str) -> str:
    return NEPSE_SYMBOLS.get(symbol.upper().strip(), "Unknown")


def get_all_symbols() -> list[str]:
    return sorted(_SYMBOL_SET)


def format_nepse_number(value: float) -> str:
    if value >= 10_000_000:
        return f"{value / 10_000_000:.2f} Crore"
    elif value >= 100_000:
        return f"{value / 100_000:.2f} Lakh"
    return f"{value:,.0f}"