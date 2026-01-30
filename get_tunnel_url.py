import subprocess
import re
import sys

# Run cloudflared and capture output
cloudflared_path = r"C:\Users\stealer0002\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"

process = subprocess.Popen(
    [cloudflared_path, "tunnel", "--url", "http://localhost:8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

url_found = False
try:
    for line in process.stdout:
        print(line, end='', flush=True)
        # Look for the tunnel URL
        if "trycloudflare.com" in line:
            match = re.search(r'https://[a-zA-Z0-9\-]+\.trycloudflare\.com', line)
            if match:
                url = match.group(0)
                print(f"\n{'='*60}")
                print(f"🌐 SUA URL DE ACESSO REMOTO:")
                print(f"   {url}")
                print(f"{'='*60}")
                print(f"\nCopie essa URL e acesse do celular!")
                print(f"Pressione Ctrl+C para parar o tunnel.\n")
                url_found = True
    
    process.wait()
except KeyboardInterrupt:
    process.terminate()
    print("\nTunnel encerrado.")
