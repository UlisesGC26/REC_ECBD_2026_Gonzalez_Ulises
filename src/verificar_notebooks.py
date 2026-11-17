"""Ejecuta todos los notebooks mediante un kernel Jupyter real y guarda evidencia."""
import json
from datetime import datetime, timezone
import nbformat
from nbclient import NotebookClient
from src.preparacion_datos import ROOT, guardar_json


def verificar():
    informe=[]
    for ruta in sorted((ROOT/'notebooks').glob('*.ipynb')):
        print('Ejecutando', ruta.name, flush=True)
        nb=nbformat.read(ruta, as_version=4)
        NotebookClient(nb, timeout=900, kernel_name='python3', resources={'metadata': {'path': str(ROOT)}}).execute()
        nbformat.write(nb, ruta)
        errores=[o for c in nb.cells for o in c.get('outputs',[]) if o.output_type=='error']
        assert not errores
        informe.append({'notebook': ruta.name,'celdas_codigo': sum(c.cell_type=='code' for c in nb.cells),'errores':len(errores)})
    guardar_json(ROOT/'docs/verificacion_notebooks.json',{'fecha_utc':datetime.now(timezone.utc).isoformat(),'kernel':'Jupyter python3','resultados':informe})
    print('Verificación completa:',len(informe),'notebooks',flush=True)


if __name__ == '__main__': verificar()
