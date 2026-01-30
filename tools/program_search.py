"""
Program search utilities
Finds installed programs on Windows
"""

import os
import subprocess
import winreg
from pathlib import Path
from typing import Optional
from functools import lru_cache


@lru_cache(maxsize=1)
def get_installed_programs() -> list[dict]:
    """Get list of installed programs from Windows registry and common paths."""
    programs = []
    
    # Registry paths for installed programs
    registry_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    
    for hkey, path in registry_paths:
        try:
            key = winreg.OpenKey(hkey, path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    try:
                        name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        try:
                            install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        except:
                            install_location = ""
                        programs.append({
                            "name": name,
                            "location": install_location
                        })
                    except:
                        pass
                    winreg.CloseKey(subkey)
                except:
                    continue
            winreg.CloseKey(key)
        except:
            continue
    
    return programs


def search_program(query: str) -> list[dict]:
    """Search for programs matching the query."""
    query_lower = query.lower()
    programs = get_installed_programs()
    
    matches = []
    for prog in programs:
        name = prog["name"].lower()
        if query_lower in name:
            # Calculate relevance score
            score = 100 if query_lower == name else (50 if name.startswith(query_lower) else 10)
            matches.append({
                "name": prog["name"],
                "location": prog["location"],
                "score": score
            })
    
    # Sort by score
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:10]


def find_executable(program_name: str) -> Optional[str]:
    """Find the executable path for a program."""
    # Search in installed programs
    matches = search_program(program_name)
    
    for match in matches:
        location = match.get("location", "")
        if location and os.path.isdir(location):
            # Look for common executable patterns
            exe_patterns = [
                f"{program_name}.exe",
                f"{program_name.replace(' ', '')}.exe",
                f"{match['name'].split()[0].lower()}.exe",
            ]
            
            for pattern in exe_patterns:
                for root, dirs, files in os.walk(location):
                    for file in files:
                        if file.lower() == pattern.lower():
                            return os.path.join(root, file)
                    # Only search top level and one level deep
                    if root.count(os.sep) - location.count(os.sep) >= 2:
                        break
    
    # Try 'where' command
    try:
        result = subprocess.run(
            ["where", program_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            paths = result.stdout.strip().split('\n')
            if paths:
                return paths[0]
    except:
        pass
    
    # Search in common program directories
    common_paths = [
        os.environ.get("ProgramFiles", "C:\\Program Files"),
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs"),
    ]
    
    for base_path in common_paths:
        if not base_path or not os.path.exists(base_path):
            continue
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.lower().endswith('.exe'):
                    file_name = file[:-4].lower()
                    if program_name.lower() in file_name or file_name in program_name.lower():
                        return os.path.join(root, file)
            # Limit depth
            if root.count(os.sep) - base_path.count(os.sep) >= 3:
                break
    
    return None


def get_start_menu_apps() -> list[dict]:
    """Get apps from Start Menu shortcuts."""
    apps = []
    
    start_menu_paths = [
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.environ.get("ProgramData", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
    ]
    
    for base_path in start_menu_paths:
        if not os.path.exists(base_path):
            continue
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.lnk'):
                    apps.append({
                        "name": file[:-4],  # Remove .lnk
                        "path": os.path.join(root, file)
                    })
    
    return apps
