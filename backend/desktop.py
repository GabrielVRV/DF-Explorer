import subprocess
import sys
import threading
import time
from pathlib import Path

import uvicorn
import webview

ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"
FRONTEND_DIST = FRONTEND_DIR / "dist"


def ensure_frontend_built() -> None:
    if getattr(sys, "frozen", False):
        # Empacotado: o frontend ja foi compilado e incluido no build. Nada a fazer.
        return
    if FRONTEND_DIST.exists():
        return
    print("Compilando o frontend pela primeira vez (pode levar um minuto)...")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    subprocess.run([npm, "install"], cwd=FRONTEND_DIR, check=True)
    subprocess.run([npm, "run", "build"], cwd=FRONTEND_DIR, check=True)


def start_server() -> None:
    from app.main import app as fastapi_app

    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000, log_level="warning")


def main() -> None:
    ensure_frontend_built()

    webview.settings["ALLOW_DOWNLOADS"] = True

    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(1.5)

    webview.create_window(
        "Datasul DF Explorer",
        "http://127.0.0.1:8000",
        width=1440,
        height=900,
        min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
