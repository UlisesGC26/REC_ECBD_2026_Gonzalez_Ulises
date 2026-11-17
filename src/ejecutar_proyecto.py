"""Ejecutar desde la carpeta del proyecto: python -m src.ejecutar_proyecto"""
from src.preparacion_datos import preparar
from src.modelos_supervisados import ajustar_modelos
from src.modelos_no_supervisados import analizar

if __name__ == "__main__":
    preparar()
    ajustar_modelos()
    analizar()
    print("Análisis completo. Para cargar SQL Server: python -m src.etl_sqlserver --cargar")
    print("Para abrir las gráficas y predicciones en el navegador ejecuta:")
    print("  python -m src.iniciar_panel")
