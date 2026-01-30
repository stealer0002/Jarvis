from tools.apps import manage_apps
import json

def test_search(app_name):
    print(f"\n--- Testing Search for: {app_name} ---")
    result = manage_apps(action="search", query=app_name)
    # Print only a snippet to avoid flooding
    output = result.get("output", "")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Found (first 200 chars): {output[:200]}...")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_search("Discord")
    test_search("Notepad++")
    test_search("Python")
