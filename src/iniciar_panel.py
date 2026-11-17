"""Abre el panel local: python -m src.iniciar_panel desde la raíz."""
from importlib.util import find_spec
from pathlib import Path
import subprocess
import sys


def main():
    raiz = Path(__file__).resolve().parents[1]
    if find_spec("streamlit") is None or find_spec("plotly") is None:
        print("Instala las bibliotecas del panel con:")
        print(f'"{sys.executable}" -m pip install -r requirements.txt')
        return 1
    print("Abriendo el panel de eficiencia energética en tu navegador.", flush=True)
    print("Si no se abre automáticamente, entra en http://localhost:8501", flush=True)
    print("Mantén esta terminal abierta. Para detener el panel usa Ctrl+C.", flush=True)
    try:
        return subprocess.call([
            sys.executable, "-m", "streamlit", "run", str(raiz / "dashboard/app.py"),
            "--browser.gatherUsageStats=false",
        ], cwd=raiz)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
