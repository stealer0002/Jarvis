"""
Test content policy filter
"""
import sys
sys.path.insert(0, '.')

from tools.web import _is_query_blocked

def test_content_policy():
    print("🛡️ TESTE DE POLÍTICA DE CONTEÚDO")
    print("-" * 50)
    
    # Should be BLOCKED
    blocked_queries = [
        "pornhub videos",
        "xvideos brasil",
        "onlyfans leaks",
    ]
    
    # Should be ALLOWED
    allowed_queries = [
        "fitgirl repacks download",
        "jogos crackeados",
        "torrent games",
        "gta 5 crack",
    ]
    
    print("\n❌ Queries que DEVEM ser bloqueadas:")
    for q in blocked_queries:
        is_blocked, msg = _is_query_blocked(q)
        status = "✅ BLOQUEADO" if is_blocked else "⚠️ PASSOU (ERRO!)"
        print(f"  {status}: '{q}'")
        assert is_blocked, f"Deveria ter bloqueado: {q}"
    
    print("\n✅ Queries que DEVEM ser permitidas:")
    for q in allowed_queries:
        is_blocked, msg = _is_query_blocked(q)
        status = "✅ PERMITIDO" if not is_blocked else "⚠️ BLOQUEADO (ERRO!)"
        print(f"  {status}: '{q}'")
        assert not is_blocked, f"Não deveria ter bloqueado: {q}"
    
    print("\n🎉 POLÍTICA DE CONTEÚDO OK!")

if __name__ == "__main__":
    test_content_policy()
