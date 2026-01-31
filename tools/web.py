"""
Web tools - Search, browse, and fetch web content
"""

import httpx
import re
from core.tools import tool


# ============ CONTENT POLICY FILTER ============
BLOCKED_KEYWORDS = [
    # Pornography (explicit)
    "porn", "xxx", "xvideos", "pornhub", "xnxx", "xhamster", "redtube",
    "onlyfans", "fansly", "hentai", "rule34", "nhentai", "hanime",
    # Child exploitation (ZERO TOLERANCE)
    "cp ", "pthc", "child porn", "loli", "shota", "underage",
]

def _is_query_blocked(query: str) -> tuple[bool, str]:
    """Check if query contains blocked content."""
    query_lower = query.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in query_lower:
            if any(term in query_lower for term in ["child", "cp ", "pthc", "loli", "shota", "underage"]):
                return True, "🚨 BLOQUEADO: Isso é crime. Não vou ajudar e sugiro que você repense suas escolhas."
            return True, "🚫 BLOQUEADO: Conteúdo adulto não é permitido. Posso ajudar com outra coisa?"
    return False, ""


@tool(
    name="web_search",
    description="Pesquisa na web usando DuckDuckGo. Use para buscar informações, notícias, tutoriais, etc.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Termo de busca"
            },
            "max_results": {
                "type": "integer",
                "description": "Número máximo de resultados (padrão: 5)"
            },
            "time_limit": {
                "type": "string",
                "description": "Filtro de tempo: 'd' (dia), 'w' (semana), 'm' (mês), 'y' (ano). Padrão: null",
                "enum": ["d", "w", "m", "y"]
            }
        },
        "required": ["query"]
    }
)
def web_search(query: str, max_results: int = 5, time_limit: str = None) -> dict:
    """Search the web using DuckDuckGo with retry, caching and time filter."""
    import time
    
    # Content policy check
    is_blocked, message = _is_query_blocked(query)
    if is_blocked:
        return {"success": False, "blocked": True, "message": message}
    
    # Global cache for the session (simple in-memory)
    
    # Global cache for the session (simple in-memory)
    if not hasattr(web_search, "cache"):
        web_search.cache = {}
    
    # Cache key includes time_limit
    cache_key = f"{query}_{time_limit}"
    
    # Check cache (TTL 5 minutes)
    current_time = time.time()
    if cache_key in web_search.cache:
        timestamp, data = web_search.cache[cache_key]
        if current_time - timestamp < 300:  # 300 seconds TTL
            data["cached"] = True
            return data
            
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Use DuckDuckGo HTML search (no API key needed)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            params = {"q": query}
            if time_limit and time_limit in ['d', 'w', 'm', 'y']:
                params['df'] = time_limit
            
            response = httpx.get(
                "https://html.duckduckgo.com/html/",
                params=params,
                headers=headers,
                timeout=30,
                follow_redirects=True
            )
            response.raise_for_status()
            
            # Parse results from HTML
            html = response.text
            results = []
            
            # Find result blocks
            result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a class="result__snippet"[^>]*>([^<]+(?:<[^>]+>[^<]*</[^>]+>)*[^<]*)</a>'
            
            links = re.findall(result_pattern, html)
            snippets = re.findall(snippet_pattern, html)
            
            for i, (url, title) in enumerate(links[:max_results]):
                # Extract real URL from DuckDuckGo redirect
                # Format: //duckduckgo.com/l/?uddg=REAL_URL&rut=...
                real_url = url
                if "uddg=" in url:
                    try:
                        from urllib.parse import parse_qs, urlparse, unquote
                        parsed = urlparse(url)
                        query_params = parse_qs(parsed.query)
                        if "uddg" in query_params:
                            real_url = query_params["uddg"][0]
                    except:
                        pass
                
                # Fix protocol relative URLs
                if real_url.startswith("//"):
                    real_url = "https:" + real_url
                    
                result = {
                    "title": title.strip(),
                    "url": real_url,
                }
                if i < len(snippets):
                    # Clean HTML tags from snippet
                    snippet = re.sub(r'<[^>]+>', '', snippets[i])
                    result["snippet"] = snippet.strip()
                results.append(result)
            
            if results:
                response_data = {
                    "success": True,
                    "query": query,
                    "time_limit": time_limit,
                    "count": len(results),
                    "results": results
                }
                # Store in cache
                web_search.cache[cache_key] = (time.time(), response_data)
                return response_data
            else:
                response_data = {
                    "success": True,
                    "query": query,
                    "time_limit": time_limit,
                    "count": 0,
                    "message": "Nenhum resultado encontrado"
                }
                web_search.cache[cache_key] = (time.time(), response_data)
                return response_data

        except Exception as e:
            last_error = e
            time.sleep(2)
            
    return {"success": False, "error": f"Falha após {max_retries} tentativas. Último erro: {str(last_error)}"}


@tool(
    name="fetch_webpage",
    description="Busca o conteúdo de texto de uma página web. Use para ler artigos, documentação, etc.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "URL da página a buscar"
            },
            "max_length": {
                "type": "integer",
                "description": "Tamanho máximo do texto retornado (padrão: 5000 caracteres)"
            }
        },
        "required": ["url"]
    }
)
def fetch_webpage(url: str, max_length: int = 5000) -> dict:
    """Fetch and clean text content from a webpage using BeautifulSoup."""
    try:
        from bs4 import BeautifulSoup
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = httpx.get(url, headers=headers, timeout=15, follow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove non-visual elements
        for element in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript", "svg", "aside"]):
            element.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        text = " ".join(text.split())  # Normalize whitespace
        
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return {
            "success": True,
            "url": url,
            "length": len(text),
            "content": text
        }
    except ImportError:
        # Fallback to regex if BeautifulSoup not available
        return {"success": False, "error": "BeautifulSoup não instalado. Use: pip install beautifulsoup4"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@tool(
    name="deep_news_search",
    description="Pesquisa notícias profundas e lê o conteúdo dos sites. Use EXCLUSIVAMENTE quando o usuário pedir 'notícias de hoje', 'fatos recentes' ou 'verificação de noticias'.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Termo de busca (ex: 'notícias Brasil hoje', 'guerra ucrânia')"
            }
        },
        "required": ["query"]
    }
)
def deep_news_search(query: str) -> dict:
    """Search and READ the top 5 results to answer with perfection."""
    # 1. Perform Search (FORCING time_limit='m' for past month)
    # Increased to 5 results for better cross-checking
    search_result = web_search(query, max_results=5, time_limit="m")
    
    if not search_result["success"] or search_result["count"] == 0:
        # Fallback to no time limit if month yields nothing
        search_result = web_search(query, max_results=5)
        if not search_result["success"] or search_result["count"] == 0:
            return search_result
        
    results = search_result.get("results", [])
    
    # 2. Fetch Content for Top 5
    detailed_reports = []
    
    for item in results:
        url = item.get("url")
        title = item.get("title")
        
        # Artificial delay to be polite
        import time
        time.sleep(1)
        
        # Fetch content (limit to 2000 chars to save context, since we have more sources)
        page_data = fetch_webpage(url, max_length=2000)
        
        if page_data["success"]:
            detailed_reports.append(f"--- FONTE: {title} ---\nURL: {url}\nCONTEÚDO (Excerto):\n{page_data['content']}\n")
        else:
            detailed_reports.append(f"--- FONTE: {title} ---\nURL: {url}\nERRO AO LER: {page_data.get('error')}\n")
            
    # 3. Compile Final Report
    full_report = "\n".join(detailed_reports)
    
    return {
        "success": True,
        "query": query,
        "message": f"Pesquisa profunda realizada em {len(results)} fontes (Filtro: Mês). Use esses dados para cruzar informações e validar fatos.",
        "content_read": full_report
    }
