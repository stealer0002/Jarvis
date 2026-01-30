from tools.apps import manage_apps
import time

# Target: 7-Zip
PKG_ID = "7zip.7zip"

print(f"--- TESTE REAL: Ciclo de Vida do {PKG_ID} ---")

# 1. SETUP: Install to ensure it exists
print("\n[1/2] Garantindo que 7-Zip está instalado...")
install_res = manage_apps(action="install", package_id=PKG_ID)
if install_res['success']:
    print("      >> INSTALADO COM SUCESSO (ou já estava).")
else:
    # Winget might return error if already installed, depending on flags.
    # But usually with --no-upgrade it just exits.
    print(f"      >> Nota de Instalação: {install_res.get('error')}")

# Wait a bit to let OS settle
time.sleep(3)

# 2. TEST: Uninstall
print("\n[2/2] TENTANDO DESINSTALAR (O Que Você Pediu)...")
uninstall_res = manage_apps(action="uninstall", package_id=PKG_ID)

if uninstall_res['success']:
    print("      >> SUCESSO! 7-Zip foi removido.")
    print(f"      >> Mensagem: {uninstall_res.get('message')}")
else:
    print("      >> FALHA na Desinstalação.")
    print(f"      >> Erro: {uninstall_res.get('error')}")
