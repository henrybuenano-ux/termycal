#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repara dos fallos silenciosos detectados en la auditoría del 25-ago-2026.

FALLO 1 · Reingreso (allowMultiple) apagado en TODOS los workflows.
    Playbook §2.2: allowMultiple apagado = el contacto entra UNA VEZ EN SU VIDA.
    En un negocio de reparaciones el cliente vuelve: se le rompe otra cosa, pide
    otro presupuesto, pide otra visita. Con el reingreso apagado, la segunda vez
    el sistema lo SALTA sin avisar y el lead se pierde en silencio.
    Causa probable: el PUT de workflow resetea a default todo campo raíz omitido
    (playbook §2.1) y los PUTs anteriores no lo incluían.

FALLO 2 · Nodos de notificación con forma inventada (BOT-DH y SP03).
    Playbook §0 y §4: userType solo acepta "assign" (+assignedOwners) o "user"
    (+selectedUser). Estos dos nodos se construyeron planos, con userType "all"
    y clave `subject` — se guardan, se ven bien en el canvas, y NO AVISAN A NADIE.
    El molde correcto se clona de SP-N, que sí tiene la forma anidada válida.

NO publica nada: publicar es solo desde la UI (playbook §2.7).

Uso:
    python3 scripts/reparar_reingreso_y_notificaciones.py           # dry-run
    python3 scripts/reparar_reingreso_y_notificaciones.py --aplicar # escribe
"""
import os, sys, json, time, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
def cargar_env_pisando(raiz):
    """Como wf_toolkit.cargar_env pero el .env GANA sobre lo que ya haya en el
    entorno. Necesario: el contenedor trae un GHL_FIREBASE_REFRESH_TOKEN viejo
    y `setdefault` haría que el token caducado le gane al bueno del .env."""
    p = pathlib.Path(raiz) / ".env"
    if not p.exists():
        sys.exit(f"Falta {p} — pide las credenciales al usuario.")
    for l in p.read_text().splitlines():
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, v = l.split("=", 1)
            os.environ[k.strip()] = v.strip()

cargar_env_pisando(RAIZ)
from cli_anything.gohighlevel.utils.ghl_internal_client import InternalGHLClient, TokenManager

LOC = os.environ.get("GHL_LOCATION_ID", "oWWElLfvuaO9tDThqa6d")
APLICAR = "--aplicar" in sys.argv

# Workflows que NO deben permitir reingreso (ninguno, por ahora: en este negocio
# el cliente siempre puede volver). Se deja la lista para documentar la decisión.
SIN_REINGRESO = set()

# Nodos de notificación con forma inventada → molde válido clonado de SP-N.
NOTIFS_A_REPARAR = {
    "BOT-DH": {
        "title": "El bot te pasó una conversación",
        "body": ("🙋 {{contact.name}} necesita que le atiendas tú. Tel: {{contact.phone}} · "
                 "Abre la conversación en WhatsApp — puede ser una urgencia (olor a gas o fuga)."),
    },
    "SP03": None,   # se conserva el texto que ya tenga; solo se corrige la forma
}


def molde_notificacion(titulo, cuerpo):
    """Forma anidada válida (playbook §4). userType 'assign' avisa al DUEÑO del
    contacto; cuando exista el usuario de Alejandro conviene pasar a
    userType 'user' + selectedUser con su id, que no depende de la asignación."""
    return {
        "type": "notification",
        "notification": {
            "type": "send_notification",
            "body": cuerpo,
            "title": titulo,
            "redirectPage": "conversation",
            "userType": "assign",
            "assignedOwners": ["contact_owner"],
        },
    }


def main():
    cli = InternalGHLClient(TokenManager(), LOC)
    lst = cli.request("GET", f"/workflow/{LOC}")
    wfs = lst if isinstance(lst, list) else (lst.get("workflows") or lst.get("data") or [])
    wfs = [w for w in wfs if w.get("name")]

    print(f"{'APLICANDO CAMBIOS' if APLICAR else 'DRY-RUN (nada se escribe)'} · {len(wfs)} workflows\n")
    cambios = 0

    for w in sorted(wfs, key=lambda x: x["name"]):
        wid, nombre = w["id"], w["name"]
        d = cli.request("GET", f"/workflow/{LOC}/{wid}")
        if not d or d.get("_error"):
            print(f"  ⚠️  {nombre[:48]}: no se pudo leer")
            continue

        pendientes = []
        steps = sorted(d.get("workflowData", {}).get("templates", []),
                       key=lambda x: x.get("order", 0))

        # ── Fallo 1: reingreso ──────────────────────────────────────────
        quiere_reingreso = nombre not in SIN_REINGRESO
        arreglar_am = quiere_reingreso and not d.get("allowMultiple")
        if arreglar_am:
            pendientes.append("reingreso OFF → ON")

        # ── Fallo 2: forma de las notificaciones ────────────────────────
        toco_nodos = False
        for s in steps:
            if s.get("type") != "internal_notification":
                continue
            a = s.get("attributes", {})
            if "notification" in a:      # ya tiene la forma anidada válida
                continue
            clave = next((k for k in NOTIFS_A_REPARAR if nombre.startswith(k)), None)
            if not clave:
                continue
            cfg = NOTIFS_A_REPARAR[clave]
            titulo = (cfg or {}).get("title") or a.get("subject") or a.get("title") or "Aviso"
            cuerpo = (cfg or {}).get("body") or a.get("body") or ""
            s["attributes"] = molde_notificacion(titulo, cuerpo)
            toco_nodos = True
            pendientes.append(f"notificación con forma inventada (userType={a.get('userType')!r}) → molde válido")

        if not pendientes:
            print(f"  ✓ {nombre[:60]}")
            continue

        cambios += 1
        print(f"  ⚠️  {nombre[:60]}")
        for p in pendientes:
            print(f"       · {p}")

        if not APLICAR:
            continue

        # Re-GET inmediato: cada PUT incrementa version y un PUT con version
        # vieja se ignora en silencio (playbook §2.7).
        fresco = cli.request("GET", f"/workflow/{LOC}/{wid}")
        body = {
            "name": fresco.get("name"),
            "version": fresco.get("version"),
            "parentId": fresco.get("parentId"),
            "status": fresco.get("status"),        # se preserva: no publicamos por API
            "allowMultiple": True if quiere_reingreso else fresco.get("allowMultiple", False),
        }
        if toco_nodos:
            body["workflowData"] = {"templates": steps}
        r = cli.request("PUT", f"/workflow/{LOC}/{wid}", body)
        ok = r and not (isinstance(r, dict) and r.get("_error"))
        print(f"       {'✅ escrito' if ok else '❌ FALLÓ: ' + str(r)[:90]}")
        time.sleep(1.5)   # el compilador de GHL es asíncrono: nada de ráfagas

    print(f"\n{cambios} workflows con cambios pendientes.")
    if not APLICAR and cambios:
        print("Repite con --aplicar para escribirlos.")
    if APLICAR:
        print("\nRecuerda: la publicación se hace SOLO desde el toggle de la UI (playbook §2.7).")
        print("Y verifica el reingreso en la UI, no por API — la lectura de estado no es fiable.")


if __name__ == "__main__":
    main()
