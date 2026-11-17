"""Validación estructural PBIR usando esquemas públicos de Microsoft."""
import json
import urllib.request
from pathlib import Path
import jsonschema
from src.preparacion_datos import ROOT


def validar():
    cache = ROOT / 'tmp/schemas'; cache.mkdir(parents=True, exist_ok=True)
    def obtener(uri):
        import hashlib
        path = cache / (hashlib.sha256(uri.encode()).hexdigest()+'.json')
        if not path.exists():
            with urllib.request.urlopen(uri, timeout=30) as r:
                path.write_bytes(r.read())
        return json.loads(path.read_text(encoding='utf-8'))
    n = 0
    for path in (ROOT/'dashboard/Energia.Report/definition').rglob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        if '$schema' not in data: continue
        uri = data['$schema']; schema = obtener(uri)
        resolver = jsonschema.RefResolver(uri, schema, handlers={'https': obtener})
        jsonschema.Draft7Validator(schema, resolver=resolver).validate(data)
        n += 1
    print(f'{n} archivos PBIR válidos contra esquemas de Microsoft')


if __name__ == '__main__': validar()
