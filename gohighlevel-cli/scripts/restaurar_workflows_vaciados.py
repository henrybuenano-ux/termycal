#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restaura los workflows que quedaron VACÍOS el 25-ago-2026.

QUÉ PASÓ
    `reparar_reingreso_y_notificaciones.py` mandaba el PUT sin `workflowData`
    cuando el workflow solo necesitaba el arreglo de allowMultiple. El PUT de
    workflow resetea a default TODO campo raíz omitido (playbook §2.1) — y eso
    incluye `workflowData`. Resultado: 13 workflows se quedaron sin nodos.
    Sobrevivieron los dos donde sí se mandaron nodos (BOT-DH, SP03) y los RBD,
    que no necesitaban cambios.

CÓMO SE RECUPERA
    GHL guarda el historial completo en `/workflow/{loc}/{wid}/history`: cada
    entrada trae un `fileUrl` a un snapshot JSON en Firebase Storage con los
    `templates` de esa versión. Se busca la versión más reciente CON nodos y se
    reescribe, esta vez mandando el body completo.

LECCIÓN (ya en el playbook §9): en un PUT de workflow, o mandas TODOS los campos
raíz o pierdes los que omitas. Usa siempre `put_workflow()` del toolkit.

Uso:
    python3 scripts/restaurar_workflows_vaciados.py            # dry-run
    python3 scripts/restaurar_workflows_vaciados.py --aplicar  # restaura
"""
import os, sys, json, time, pathlib, urllib.request

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))


def cargar_env_pisando(raiz):
    p = pathlib.Path(raiz) / ".env"
    if not p.exists():
        sys.exit(f"Falta {p}")
    for l in p.read_text().splitlines():
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, v = l.split("=", 1)
            os.environ[k.strip()] = v.strip()


cargar_env_pisando(RAIZ)
from cli_anything.gohighlevel.utils.ghl_internal_client import InternalGHLClient, TokenManager

LOC = os.environ.get("GHL_LOCATION_ID", "oWWElLfvuaO9tDThqa6d")
APLICAR = "--aplicar" in sys.argv


def snapshot(url):
    """Descarga un snapshot del historial y devuelve sus templates (o [])."""
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
        j = json.loads(raw) if raw.strip() else {}
        return (j.get("workflowData") or {}).get("templates") or j.get("templates") or []
    except Exception:
        return []


def main():
    cli = InternalGHLClient(TokenManager(), LOC)
    lst = cli.request("GET", f"/workflow/{LOC}")
    wfs = [w for w in (lst if isinstance(lst, list) else lst.get("workflows", [])) if w.get("name")]

    print(f"{'RESTAURANDO' if APLICAR else 'DRY-RUN (nada se escribe)'} · revisando {len(wfs)} workflows\n")
    vacios = restaurados = irrecuperables = 0

    for w in sorted(wfs, key=lambda x: x["name"]):
        wid, nombre = w["id"], w["name"]
        d = cli.request("GET", f"/workflow/{LOC}/{wid}")
        if not d or d.get("_error"):
            continue
        if (d.get("workflowData") or {}).get("templates"):
            continue                      # tiene nodos: no se toca

        vacios += 1
        hist = cli.request("GET", f"/workflow/{LOC}/{wid}/history") or []
        hist = sorted([h for h in hist if isinstance(h, dict)],
                      key=lambda x: x.get("version", 0), reverse=True)

        tpl, ver = [], None
        for h in hist:
            if not h.get("fileUrl"):
                continue
            t = snapshot(h["fileUrl"])
            if t:
                tpl, ver = t, h.get("version")
                break

        if not tpl:
            irrecuperables += 1
            print(f"  ❌ {nombre[:56]}\n       VACÍO y sin snapshot con nodos en el historial")
            continue

        restaurados += 1
        print(f"  ♻️  {nombre[:56]}")
        print(f"       recuperando v{ver} · {len(tpl)} nodos: {' → '.join(s.get('type','?') for s in tpl)}")

        if not APLICAR:
            continue

        fresco = cli.request("GET", f"/workflow/{LOC}/{wid}")
        r = cli.request("PUT", f"/workflow/{LOC}/{wid}", {
            "name": fresco.get("name"),
            "version": fresco.get("version"),
            "parentId": fresco.get("parentId"),
            "status": fresco.get("status"),
            "allowMultiple": True,                       # el arreglo que sí queríamos
            "workflowData": {"templates": tpl},          # ← lo que faltó la primera vez
        })
        ok = r and not (isinstance(r, dict) and r.get("_error"))
        print(f"       {'✅ restaurado' if ok else '❌ FALLÓ: ' + str(r)[:120]}")
        time.sleep(1.5)

    print(f"\nvacíos: {vacios} · recuperables: {restaurados} · sin snapshot: {irrecuperables}")
    if not APLICAR and restaurados:
        print("Repite con --aplicar para restaurarlos.")


if __name__ == "__main__":
    main()
