"""
Currency exchange rate service
Fetches real-time exchange rates from Frankfurter API
"""

import urllib.request
import json
from datetime import date, timedelta


# Cache to avoid repeated API calls
_rate_cache = {}
_cache_date = None


def get_exchange_rate(from_currency, to_currency):
    """
    Get exchange rate from one currency to another
    
    Args:
        from_currency: 3-letter currency code (e.g., 'USD')
        to_currency: 3-letter currency code (e.g., 'EUR')
    
    Returns:
        Exchange rate as integer in cents (e.g., 9200 for 0.92)
        Returns None if API call fails
    
    Example:
        rate = get_exchange_rate('USD', 'EUR')
        # Returns 9200 (meaning 1 USD = 0.92 EUR)
    """
    global _rate_cache, _cache_date
    
    # If same currency, rate is 1.0
    if from_currency == to_currency:
        return 10000  # 1.0 in our cent format
    
    # Check cache (valid for 1 day)
    today = date.today()
    cache_key = f"{from_currency}_{to_currency}"
    
    if _cache_date == today and cache_key in _rate_cache:
        print(f"  (Using cached rate for {from_currency} → {to_currency})")
        return _rate_cache[cache_key]
    
    # Fetch from API
    try:
        url = f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        
        print(f"  Fetching exchange rate: {from_currency} → {to_currency}...")
        
        # Create request with headers
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'RelocationOS/1.0 (Educational Project)'
            }
        )
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
            # Extract the rate
            rate_float = data['rates'][to_currency]
            
            # Convert to our cent format (multiply by 10000)
            rate_cents = int(rate_float * 10000)
            
            # Cache it
            _rate_cache[cache_key] = rate_cents
            _cache_date = today
            
            print(f"  ✓ Rate: 1 {from_currency} = {rate_float:.4f} {to_currency}")
            
            return rate_cents
            
    except Exception as e:
        print(f"  ⚠️  Could not fetch exchange rate: {e}")
        print(f"  You can enter the rate manually or use default (1.0)")
        return None


def convert_amount(amount_cents, from_currency, to_currency):
    """
    Convert an amount from one currency to another
    
    Args:
        amount_cents: Amount in cents (integer)
        from_currency: Source currency code
        to_currency: Target currency code
    
    Returns:
        Converted amount in cents, or original amount if conversion fails
    """
    rate = get_exchange_rate(from_currency, to_currency)
    
    if rate is None:
        return amount_cents
    
    # Convert: (amount * rate) / 10000
    converted = (amount_cents * rate) // 10000
    
    return converted


def format_currency(amount_cents, currency_code):
    """
    Format amount for display
    
    Args:
        amount_cents: Amount in cents
        currency_code: Currency code
    
    Returns:
        Formatted string like "$123.45" or "€123.45"
    """
    amount = amount_cents / 100
    
    # Currency symbols
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
    }
    
    symbol = symbols.get(currency_code, currency_code + ' ')
    
    return f"{symbol}{amount:,.2f}"


def get_manual_exchange_rate():
    """
    Prompt user to enter exchange rate manually
    
    Returns:
        Exchange rate in cents, or None if skipped
    """
    print("\nEnter exchange rate manually:")
    print("Example: If 1 USD = 0.92 EUR, enter: 0.92")
    
    try:
        rate_input = input("Exchange rate (or Enter to skip): ").strip()
        
        if not rate_input:
            return None
        
        rate_float = float(rate_input)
        rate_cents = int(rate_float * 10000)
        
        return rate_cents
        
    except ValueError:
        print("Invalid rate format")
        return None


def clear_cache():
    """Clear the exchange rate cache"""
    global _rate_cache, _cache_date
    _rate_cache = {}
    _cache_date = None
    print("✓ Exchange rate cache cleared")
