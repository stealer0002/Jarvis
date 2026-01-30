from tools.processes import get_system_info
import json

r = get_system_info()
print(json.dumps(r, indent=2, ensure_ascii=False))
