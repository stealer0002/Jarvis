from tools.web import deep_news_search
import json

print("Testing Deep News Search with Time Filter (m)...")
result = deep_news_search("Notícias Brasil")
# We expect to see 'Filtro: Mês' in the message
print(json.dumps(result, indent=2, ensure_ascii=False))
