# utils.py
import re

def extract_stock_symbol(message):
    """
    Extracts potential stock symbols from user message.
    Looks for 3-5 uppercase letters commonly found in NEPSE.
    """
    symbols = re.findall(r'\b[A-Z]{3,5}\b', message.upper())
    # Common NEPSE symbols to validate against (Expand this list)
    valid_symbols = [
        'NABIL', 'NICA', 'SPUBL', 'GBIME', 'NCCB', 'HDL', 'NIFRA', 
        'UPPER', 'JYOTI', 'API', 'SCB', 'EBL', 'NIFRA', 'SRL', 'MLBL'
    ]
    
    for symbol in symbols:
        if symbol in valid_symbols:
            return symbol
    return None