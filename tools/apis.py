"""
External API Tools - Free APIs for real-time data
No API keys required for these services.
"""

import httpx
from core.tools import tool


@tool(
    name="get_weather",
    description="Obtém a previsão do tempo para uma cidade. Use para perguntas como 'Como está o tempo em São Paulo?', 'Vai chover amanhã?'",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "Nome da cidade (ex: 'São Paulo', 'Rio de Janeiro', 'New York')"
            },
            "lang": {
                "type": "string",
                "description": "Idioma da resposta (pt = português, en = inglês). Padrão: pt"
            }
        },
        "required": ["city"]
    }
)
def get_weather(city: str, lang: str = "pt") -> dict:
    """Get weather forecast using wttr.in (free, no API key)."""
    try:
        # wttr.in provides free weather data
        # Format: ?format=j1 returns JSON
        url = f"https://wttr.in/{city}?format=j1&lang={lang}"
        
        headers = {
            "User-Agent": "JARVIS-Agent/1.0"
        }
        
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract current conditions
        current = data.get("current_condition", [{}])[0]
        location = data.get("nearest_area", [{}])[0]
        
        # Get weather description in requested language
        weather_desc = current.get(f"lang_{lang}", [{}])
        if weather_desc:
            desc = weather_desc[0].get("value", current.get("weatherDesc", [{}])[0].get("value", ""))
        else:
            desc = current.get("weatherDesc", [{}])[0].get("value", "")
        
        # Get forecast for next 3 days
        forecast = []
        for day in data.get("weather", [])[:3]:
            forecast.append({
                "date": day.get("date"),
                "max_temp": f"{day.get('maxtempC')}°C",
                "min_temp": f"{day.get('mintempC')}°C",
                "description": day.get("hourly", [{}])[4].get("weatherDesc", [{}])[0].get("value", "")
            })
        
        return {
            "success": True,
            "location": {
                "city": location.get("areaName", [{}])[0].get("value", city),
                "region": location.get("region", [{}])[0].get("value", ""),
                "country": location.get("country", [{}])[0].get("value", "")
            },
            "current": {
                "temperature": f"{current.get('temp_C')}°C",
                "feels_like": f"{current.get('FeelsLikeC')}°C",
                "humidity": f"{current.get('humidity')}%",
                "wind": f"{current.get('windspeedKmph')} km/h",
                "description": desc,
                "uv_index": current.get("uvIndex")
            },
            "forecast": forecast
        }
        
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"Cidade não encontrada ou serviço indisponível: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_crypto_price",
    description="Obtém o preço atual de criptomoedas (Bitcoin, Ethereum, etc). Use para perguntas como 'Qual o preço do Bitcoin?', 'Quanto vale 1 ETH?'",
    parameters={
        "type": "object",
        "properties": {
            "coin": {
                "type": "string",
                "description": "Nome ou símbolo da criptomoeda (ex: 'bitcoin', 'ethereum', 'btc', 'eth', 'solana')"
            },
            "currency": {
                "type": "string",
                "description": "Moeda para conversão (ex: 'brl', 'usd', 'eur'). Padrão: brl"
            }
        },
        "required": ["coin"]
    }
)
def get_crypto_price(coin: str, currency: str = "brl") -> dict:
    """Get cryptocurrency price using CoinGecko API (free, no API key)."""
    try:
        # Map common symbols to CoinGecko IDs
        coin_map = {
            "btc": "bitcoin",
            "eth": "ethereum",
            "sol": "solana",
            "ada": "cardano",
            "xrp": "ripple",
            "doge": "dogecoin",
            "dot": "polkadot",
            "bnb": "binancecoin",
            "matic": "matic-network",
            "link": "chainlink",
            "ltc": "litecoin",
            "avax": "avalanche-2",
            "shib": "shiba-inu",
            "uni": "uniswap",
            "atom": "cosmos",
        }
        
        coin_id = coin_map.get(coin.lower(), coin.lower())
        currency = currency.lower()
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "community_data": "false",
            "developer_data": "false"
        }
        
        headers = {
            "User-Agent": "JARVIS-Agent/1.0"
        }
        
        response = httpx.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        market_data = data.get("market_data", {})
        current_price = market_data.get("current_price", {})
        price_change_24h = market_data.get("price_change_percentage_24h", 0)
        price_change_7d = market_data.get("price_change_percentage_7d", 0)
        
        # Format currency symbol
        currency_symbols = {"brl": "R$", "usd": "$", "eur": "€"}
        symbol = currency_symbols.get(currency, currency.upper())
        
        price = current_price.get(currency, current_price.get("usd", 0))
        
        # Format price based on value
        if price >= 1:
            formatted_price = f"{symbol} {price:,.2f}"
        else:
            formatted_price = f"{symbol} {price:.6f}"
        
        return {
            "success": True,
            "coin": {
                "name": data.get("name"),
                "symbol": data.get("symbol", "").upper(),
                "rank": data.get("market_cap_rank")
            },
            "price": {
                "current": formatted_price,
                "raw": price,
                "currency": currency.upper()
            },
            "change": {
                "24h": f"{price_change_24h:+.2f}%",
                "7d": f"{price_change_7d:+.2f}%"
            },
            "market_cap": market_data.get("market_cap", {}).get(currency),
            "ath": market_data.get("ath", {}).get(currency),
            "ath_date": market_data.get("ath_date", {}).get(currency)
        }
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"success": False, "error": f"Criptomoeda '{coin}' não encontrada. Tente o nome completo (ex: 'bitcoin' ao invés de 'btc')."}
        return {"success": False, "error": f"Erro na API: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="get_exchange_rate",
    description="Obtém a cotação de moedas (Dólar, Euro, etc). Use para perguntas como 'Quanto está o dólar?', 'Qual a cotação do Euro?'",
    parameters={
        "type": "object",
        "properties": {
            "from_currency": {
                "type": "string",
                "description": "Moeda de origem (ex: 'USD', 'EUR', 'GBP'). Padrão: USD"
            },
            "to_currency": {
                "type": "string",
                "description": "Moeda de destino (ex: 'BRL', 'EUR'). Padrão: BRL"
            },
            "amount": {
                "type": "number",
                "description": "Quantidade a converter. Padrão: 1"
            }
        }
    }
)
def get_exchange_rate(from_currency: str = "USD", to_currency: str = "BRL", amount: float = 1) -> dict:
    """Get currency exchange rates using exchangerate.host (free, no API key)."""
    try:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Use exchangerate.host API (free)
        url = f"https://api.exchangerate.host/convert"
        params = {
            "from": from_currency,
            "to": to_currency,
            "amount": amount
        }
        
        headers = {
            "User-Agent": "JARVIS-Agent/1.0"
        }
        
        response = httpx.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get("success", True):
            # Fallback to a different free API
            return _fallback_exchange_rate(from_currency, to_currency, amount)
        
        rate = data.get("info", {}).get("rate", 0)
        result = data.get("result", amount * rate)
        
        # Format based on currency
        currency_symbols = {
            "BRL": "R$", "USD": "$", "EUR": "€", "GBP": "£", 
            "JPY": "¥", "ARS": "ARS$", "CLP": "CLP$"
        }
        
        from_symbol = currency_symbols.get(from_currency, from_currency)
        to_symbol = currency_symbols.get(to_currency, to_currency)
        
        return {
            "success": True,
            "conversion": {
                "from": f"{from_symbol} {amount:,.2f}",
                "to": f"{to_symbol} {result:,.2f}",
                "rate": rate
            },
            "currencies": {
                "from": from_currency,
                "to": to_currency
            },
            "message": f"{from_symbol} {amount:,.2f} = {to_symbol} {result:,.2f}"
        }
        
    except Exception as e:
        # Try fallback
        try:
            return _fallback_exchange_rate(from_currency, to_currency, amount)
        except:
            return {"success": False, "error": str(e)}


def _fallback_exchange_rate(from_currency: str, to_currency: str, amount: float) -> dict:
    """Fallback using frankfurter.app API."""
    try:
        url = f"https://api.frankfurter.app/latest"
        params = {
            "from": from_currency,
            "to": to_currency,
            "amount": amount
        }
        
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        rate = data.get("rates", {}).get(to_currency, 0)
        
        currency_symbols = {
            "BRL": "R$", "USD": "$", "EUR": "€", "GBP": "£", 
            "JPY": "¥", "ARS": "ARS$", "CLP": "CLP$"
        }
        
        from_symbol = currency_symbols.get(from_currency, from_currency)
        to_symbol = currency_symbols.get(to_currency, to_currency)
        
        result = amount * rate if rate else 0
        
        return {
            "success": True,
            "conversion": {
                "from": f"{from_symbol} {amount:,.2f}",
                "to": f"{to_symbol} {result:,.2f}",
                "rate": rate
            },
            "currencies": {
                "from": from_currency,
                "to": to_currency
            },
            "message": f"{from_symbol} {amount:,.2f} = {to_symbol} {result:,.2f}"
        }
        
    except Exception as e:
        return {"success": False, "error": f"Não foi possível obter cotação: {str(e)}"}


@tool(
    name="get_news_headlines",
    description="Obtém as principais manchetes de notícias. Use para 'Quais as notícias de hoje?', 'O que está acontecendo no mundo?'",
    parameters={
        "type": "object",
        "properties": {
            "country": {
                "type": "string",
                "description": "Código do país (br = Brasil, us = EUA). Padrão: br"
            },
            "category": {
                "type": "string",
                "description": "Categoria: general, business, technology, sports, entertainment, health, science",
                "enum": ["general", "business", "technology", "sports", "entertainment", "health", "science"]
            }
        }
    }
)
def get_news_headlines(country: str = "br", category: str = "general") -> dict:
    """Get news headlines using free RSS feeds from Google News with robust XML parsing."""
    try:
        import xml.etree.ElementTree as ET
        
        country_config = {
            "br": {"hl": "pt-BR", "gl": "BR", "ceid": "BR:pt"},
            "us": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
            "pt": {"hl": "pt-PT", "gl": "PT", "ceid": "PT:pt"},
            "uk": {"hl": "en-GB", "gl": "UK", "ceid": "UK:en"},
        }
        
        config = country_config.get(country.lower(), country_config["br"])
        category_topics = {
            "general": "",
            "business": "/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FuQjBHZ0pDVWlnQVAB",
            "technology": "/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FuQjBHZ0pDVWlnQVAB",
            "sports": "/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FuQjBHZ0pDVWlnQVAB",
            "entertainment": "/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FuQjBHZ0pDVWlnQVAB",
            "health": "/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FuQjBLQUFQAQ",
            "science": "/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FuQjBHZ0pDVWlnQVAB",
        }
        
        topic_path = category_topics.get(category, "")
        url = f"https://news.google.com/rss{topic_path}?hl={config['hl']}&gl={config['gl']}&ceid={config['ceid']}"
        
        headers = {"User-Agent": "JARVIS-Agent/1.0"}
        response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        response.raise_for_status()
        
        # Parse XML using ElementTree (more robust than regex)
        root = ET.fromstring(response.text)
        headlines = []
        
        for item in root.findall(".//item")[:10]:
            title_elem = item.find("title")
            link_elem = item.find("link")
            pub_elem = item.find("pubDate")
            source_elem = item.find("source")
            
            headlines.append({
                "title": title_elem.text if title_elem is not None else "Sem titulo",
                "source": source_elem.text if source_elem is not None else "Google News",
                "published": pub_elem.text if pub_elem is not None else "",
                "url": link_elem.text if link_elem is not None else ""
            })
            
        return {
            "success": True,
            "country": country.upper(),
            "category": category,
            "count": len(headlines),
            "headlines": headlines
        }
    except Exception as e:
        return {"success": False, "error": f"Erro XML: {str(e)}"}
