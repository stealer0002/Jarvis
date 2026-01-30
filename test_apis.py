"""Test all new API tools."""
from tools.apis import get_weather, get_crypto_price, get_exchange_rate, get_news_headlines

print("=" * 60)
print("TESTE DE APIs GRATUITAS")
print("=" * 60)

# Test 1: Weather
print("\n[1/4] Testando get_weather('São Paulo')...")
result = get_weather("São Paulo")
if result["success"]:
    current = result["current"]
    print(f"      ✅ Temperatura: {current['temperature']}")
    print(f"      ✅ Sensação: {current['feels_like']}")
    print(f"      ✅ Condição: {current['description']}")
else:
    print(f"      ❌ Erro: {result['error']}")

# Test 2: Crypto
print("\n[2/4] Testando get_crypto_price('bitcoin')...")
result = get_crypto_price("bitcoin")
if result["success"]:
    print(f"      ✅ {result['coin']['name']}: {result['price']['current']}")
    print(f"      ✅ Variação 24h: {result['change']['24h']}")
else:
    print(f"      ❌ Erro: {result['error']}")

# Test 3: Exchange Rate
print("\n[3/4] Testando get_exchange_rate('USD', 'BRL')...")
result = get_exchange_rate("USD", "BRL")
if result["success"]:
    print(f"      ✅ {result['message']}")
    print(f"      ✅ Taxa: {result['conversion']['rate']}")
else:
    print(f"      ❌ Erro: {result['error']}")

# Test 4: News
print("\n[4/4] Testando get_news_headlines('br')...")
result = get_news_headlines("br")
if result["success"]:
    print(f"      ✅ {result['count']} manchetes encontradas")
    for i, headline in enumerate(result["headlines"][:3], 1):
        print(f"      {i}. {headline['title'][:60]}...")
else:
    print(f"      ❌ Erro: {result['error']}")

print("\n" + "=" * 60)
print("TESTE FINALIZADO")
print("=" * 60)
