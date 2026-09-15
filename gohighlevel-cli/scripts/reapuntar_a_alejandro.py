#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reapunta las asignaciones y las notificaciones internas a Alejandro.

POR QUÉ
    Oliver (8QrIxCm1EIlYSPKDyEJy) ya no existe en la subcuenta — se comprobó el
    15-sep listando usuarios: hoy solo están Alejandro y Horacio Siciliano. Pero
    LS01, LS02 y RBD 05 seguían asignándole los contactos, así que los contactos
    se quedaban SIN DUEÑO y las 9 notificaciones internas, que apuntan a
    `contact_owner`, no llegaban a nadie. Fallo silencioso clásico: ningún error.

QUÉ HACE
    1. En los nodos `assign_user`, sustituye el id de Oliver por el de Alejandro
       (en user_list, traffic_weightage y traffic_index).
    2. En los nodos `internal_notification` con userType "assign", pasa a
       userType "user" + selectedUser con el id de Alejandro. Así el aviso ya no
       depende de que alguien haya asignado dueño al contacto.

NO publica nada: publicar es solo desde el toggle de la UI (playbook §2.7).
Manda SIEMPRE workflowData en el PUT — omitirlo vacía el workflow (playbook §9.1).

Uso:
    python3 scripts/reapuntar_a_alejandro.py            # dry-run
    python3 scripts/reapuntar_a_alejandro.py --aplicar  # escribe
"""
import os, sys, json, time, pathlib

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

OLIVER    = "8QrIxCm1EIlYSPKDyEJy"          # ya no existe en la subcuenta
ALEJANDRO = "oHzoJLAxYzRzgAqudYwc"          # Alejandro Rodríguez Medina, admin


def main():
    cli = InternalGHLClient(TokenManager(), LOC)
    lst = cli.request("GET", f"/workflow/{LOC}")
    wfs = [w for w in (lst if isinstance(lst, list) else lst.get("workflows", [])) if w.get("name")]

    print(f"{'APLICANDO' if APLICAR else 'DRY-RUN (nada se escribe)'} · {len(wfs)} workflows\n")
    tocados = 0

    for w in sorted(wfs, key=lambda x: x["name"]):
        wid, nombre = w["id"], w["name"]
        d = cli.request("GET", f"/workflow/{LOC}/{wid}")
        if not d or d.get("_error"):
            continue
        tpl = sorted((d.get("workflowData") or {}).get("templates") or [], key=lambda x: x.get("order", 0))
        if not tpl:
            continue

        cambios = []
        for s in tpl:
            a = s.get("attributes") or {}

            # 1 · asignación de dueño
            if s.get("type") == "assign_user":
                crudo = json.dumps(a, ensure_ascii=False)
                if OLIVER in crudo:
                    s["attributes"] = json.loads(crudo.replace(OLIVER, ALEJANDRO))
                    cambios.append(f"assign_user: Oliver → Alejandro (nodo {s.get('order')})")

            # 2 · notificación interna: de 'dueño del contacto' a Alejandro directo
            if s.get("type") == "internal_notification":
                n = a.get("notification")
                if isinstance(n, dict) and n.get("userType") == "assign":
                    n.pop("assignedOwners", None)
                    n["userType"] = "user"
                    n["selectedUser"] = ALEJANDRO
                    cambios.append(f"notificación: contact_owner → Alejandro (nodo {s.get('order')})")

        if not cambios:
            continue

        tocados += 1
        print(f"▸ {nombre[:58]}")
        for c in cambios:
            print(f"    · {c}")

        if not APLICAR:
            continue

        fresco = cli.request("GET", f"/workflow/{LOC}/{wid}")
        nodos = (fresco.get("workflowData") or {}).get("templates") or []
        if not nodos:
            print("    ⛔ ABORTADO: el re-GET vino sin nodos")
            continue
        r = cli.request("PUT", f"/workflow/{LOC}/{wid}", {
            "name": fresco.get("name"),
            "version": fresco.get("version"),
            "parentId": fresco.get("parentId"),
            "status": fresco.get("status"),          # se preserva: no publicamos por API
            "allowMultiple": fresco.get("allowMultiple", True),
            "workflowData": {"templates": tpl},      # SIEMPRE, u omitirlo lo vacía
        })
        ok = r and not (isinstance(r, dict) and r.get("_error"))
        print(f"    {'✅ escrito' if ok else '❌ FALLÓ: ' + str(r)[:130]}")
        time.sleep(1.5)

    print(f"\n{tocados} workflows con cambios.")
    if not APLICAR and tocados:
        print("Repite con --aplicar para escribirlos.")


if __name__ == "__main__":
    main()
