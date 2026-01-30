from tools.apps import manage_apps
import json

print("--- Testing Uninstall of Non-Existent App (Simulation) ---")
# 1. Try to uninstall a fake package
# This simulates the scenario where standard winget uninstall fails
result = manage_apps(action="uninstall", package_id="NonExistent.FakeApp.v999")

print(f"Success: {result['success']}")
if not result['success']:
    print(f"Error Message Received: {result.get('error')}")
    print("\n[VERIFICATION] This error message is what tells JARVIS to stop and suggest WMIC.")
else:
    print("[FAILURE] It claimed success on a fake app! This would cause hallucinations.")
