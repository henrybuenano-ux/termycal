"""Sube TODOS los PDFs de contenido-fichas/assets/ al media store (carpeta FICHAS
WHATSAPP) e imprime las tuplas listas para pegar en build_sp05_v2.py.

Idempotente: si ya existe un archivo con ese nombre en la carpeta, no re-sube.
Uso: python3 scripts_ghl/subir_pdfs.py
"""
import os, sys, json, pathlib, requests

ROOT = pathlib.Path("/home/user/grupo-galk")
for l in (ROOT / ".env").read_text().splitlines():
    l = l.strip()
    if l and not l.startswith("#") and "=" in l:
        k, v = l.split("=", 1); os.environ.setdefault(k.strip(), v.strip())

H = {"Authorization": f"Bearer {os.environ['GHL_API_KEY']}", "Version": "2021-07-28",
     "Accept": "application/json"}
LOC = os.environ["GHL_LOCATION_ID"]
B = "https://services.leadconnectorhq.com"
CARPETA = "6a4b0f6a1209780f804ad8b5"   # FICHAS WHATSAPP
ASSETS = ROOT / "contenido-fichas" / "assets"

def listar():
    r = requests.get(f"{B}/medias/files", headers=H,
                     params={"altId": LOC, "altType": "location", "sortBy": "createdAt",
                             "sortOrder": "desc", "type": "file", "parentId": CARPETA, "limit": 100})
    r.raise_for_status()
    return r.json().get("files", [])

CONSTANTES = {"G1-SketchUp-Brochure.pdf": "SKETCHUP_PDF", "G4.2-Revit-Brochure.pdf": "REVIT_PDF"}
print("Pega esto en build_sp05_v2.py:\n")
for pdf in sorted(ASSETS.glob("*.pdf")):
    nombre = pdf.name
    ya = [f for f in listar() if f.get("name") == nombre]
    if not ya:
        with open(pdf, "rb") as fh:
            r = requests.post(f"{B}/medias/upload-file", headers=H,
                              files={"file": (nombre, fh, "application/pdf")},
                              data={"hosted": "false", "name": nombre, "parentId": CARPETA,
                                    "altId": LOC, "altType": "location"})
        if r.status_code not in (200, 201):
            print(f"# ERROR subiendo {nombre}: {r.status_code} {str(r.text)[:150]}"); continue
        ya = [f for f in listar() if f.get("name") == nombre]
        if not ya:
            print(f"# {nombre}: subido pero no aparece en la carpeta — revisar a mano"); continue
    f = ya[0]
    url = f.get("url", "")
    mid = url.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    ext = url.rsplit(".", 1)[-1]
    const = CONSTANTES.get(nombre, f"# (sin constante definida para {nombre})")
    print(f'{const} = ("{mid}", "{nombre}", {f.get("size")}, "{ext}")')
