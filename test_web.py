from tools.web import web_search
import json

print("Testing Web Search...")
result = web_search("Notícias Brasil Janeiro 2026")
print(json.dumps(result, indent=2, ensure_ascii=False))
