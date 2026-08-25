#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migra nodos SMS a WhatsApp free-form (sin plantilla Meta).

SOLO para mensajes que RESPONDEN dentro de la ventana de 24 h. Un WhatsApp
free-form fuera de esa ventana no da error: simplemente NO SE ENTREGA. Los
mensajes que ABREN conversación (recordatorios, seguimientos a días, link de
valoración) necesitan plantilla aprobada por Meta y NO se tocan aquí.

La forma del nodo está clonada EXACTAMENTE de un molde hecho a mano en la UI
(SP-V, 25-ago-2026) — playbook regla nº1: nunca fabricar atributos. Ojo: el
molde real NO lleva `snippet_id`, aunque wf_toolkit.n_whatsapp_texto() sí lo
incluya; manda la forma leída de la cuenta.

Uso:
    python3 scripts/migrar_sms_a_whatsapp.py            # dry-run
    python3 scripts/migrar_sms_a_whatsapp.py --aplicar  # escribe
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

# Sacado del molde hecho a mano en SP-V. Si cambia el número conectado, hay que
# rehacer el molde en la UI y releerlo: no inventarlo.
FROM_PHONE = "317681791426807"

# (fragmento del nombre del workflow, order del nodo SMS a convertir)
A_MIGRAR = [
    ("SP-V",   0),   # "¡Recibido! En breves te contactamos" — sale segundos después
                     #  de que el cliente escriba al bot: sesión abierta segura.
    ("RBD 04", 1),   # "te mando el link directo" — responde a que el cliente dice
                     #  que no puede abrir el link: sesión abierta.
]

# Nodos duplicados a eliminar (el molde que se creó a mano para leer su forma).
MOLDES_A_LIMPIAR = [("SP-V", "whatsapp_v2", "WhatsApp")]


def nodo_whatsapp(mensaje):
    """Forma EXACTA leída del molde de SP-V. No añadir ni quitar claves."""
    return {
        "template_id": "0",
        "toggle_branch": False,
        "from_phone_number": FROM_PHONE,
        "message": mensaje,
        "type": "whatsapp_v2",
        "__customInputs__": {},
        "cat": "",
        "convertToMultipath": False,
        "transitions": [],
        "__name__": "WhatsApp",
    }


def main():
    cli = InternalGHLClient(TokenManager(), LOC)
    lst = cli.request("GET", f"/workflow/{LOC}")
    wfs = [w for w in (lst if isinstance(lst, list) else lst.get("workflows", [])) if w.get("name")]

    print(f"{'APLICANDO' if APLICAR else 'DRY-RUN (nada se escribe)'}\n")

    objetivos = {}
    for frag, orden in A_MIGRAR:
        for w in wfs:
            if w["name"].startswith(frag):
                objetivos.setdefault(w["id"], {"name": w["name"], "ordenes": set()})["ordenes"].add(orden)

    for wid, info in objetivos.items():
        d = cli.request("GET", f"/workflow/{LOC}/{wid}")
        tpl = sorted((d.get("workflowData") or {}).get("templates") or [], key=lambda x: x.get("order", 0))
        antes = len(tpl)
        print(f"▸ {info['name'][:56]}  ({antes} nodos)")

        cambios = []
        nuevos = []
        for s in tpl:
            # limpiar el molde duplicado creado a mano
            es_molde = any(info["name"].startswith(f) and s.get("type") == t and s.get("name") == n
                           for f, t, n in MOLDES_A_LIMPIAR)
            if es_molde:
                cambios.append(f"  eliminar molde duplicado (nodo {s.get('order')})")
                continue

            if s.get("type") == "sms" and s.get("order") in info["ordenes"]:
                cuerpo = (s.get("attributes") or {}).get("body") or ""
                s = dict(s)
                s["type"] = "whatsapp_v2"
                s["name"] = "WhatsApp - " + (s.get("name", "").replace("CAMBIAR A WhatsApp - ", "")
                                             .replace("WA ", "")).strip()[:60]
                s["attributes"] = nodo_whatsapp(cuerpo)
                s["workflowsActionType"] = "INTERNAL"   # sin esto el PUT rechaza
                s.setdefault("cat", "")
                cambios.append(f"  SMS → WhatsApp (nodo {s.get('order')}): «{cuerpo[:60]}…»")
            nuevos.append(s)

        if not cambios:
            print("   nada que cambiar\n")
            continue
        for c in cambios:
            print(c)

        # ⛔ El reencadenado lineal SOLO vale en workflows sin ramas. En uno con
        # if_else los `order` se repiten entre ramas y reescribir order/parentKey/next
        # colapsa el canvas (playbook §3). Si hay ramas, se cambian type y attributes
        # EN SU SITIO y no se toca un solo campo estructural.
        ramificado = any(s.get("type") == "if_else" or s.get("nodeType") for s in nuevos)
        if len(nuevos) != antes:
            if ramificado:
                print("   ⛔ ABORTADO: hay que eliminar un nodo en un workflow CON RAMAS."
                      "\n      Hazlo a mano en la UI: reencadenar por script rompería el canvas.")
                print()
                continue
            for i, s in enumerate(nuevos):
                s["order"] = i
                if i > 0:
                    s["parentKey"] = nuevos[i - 1]["id"]
                else:
                    s.pop("parentKey", None)
                if i < len(nuevos) - 1:
                    s["next"] = nuevos[i + 1]["id"]
                else:
                    s.pop("next", None)
            print(f"   cadena lineal reencadenada · {antes} nodos → {len(nuevos)} nodos")
        else:
            print(f"   estructura intacta ({'con ramas' if ramificado else 'lineal'}) · "
                  f"solo cambian type y attributes · {antes} nodos")
        if not APLICAR:
            print()
            continue

        fresco = cli.request("GET", f"/workflow/{LOC}/{wid}")
        r = cli.request("PUT", f"/workflow/{LOC}/{wid}", {
            "name": fresco.get("name"),
            "version": fresco.get("version"),
            "parentId": fresco.get("parentId"),
            "status": fresco.get("status"),
            "allowMultiple": fresco.get("allowMultiple", True),
            "workflowData": {"templates": nuevos},     # SIEMPRE, aunque no cambien
        })
        ok = r and not (isinstance(r, dict) and r.get("_error"))
        print(f"   {'✅ escrito' if ok else '❌ FALLÓ: ' + str(r)[:160]}")
        time.sleep(1.5)

        if ok:   # verificación inmediata: el 200 no garantiza nada (playbook §9.1)
            v = cli.request("GET", f"/workflow/{LOC}/{wid}")
            vt = (v.get("workflowData") or {}).get("templates") or []
            tipos = [s.get("type") for s in sorted(vt, key=lambda x: x.get("order", 0))]
            print(f"   verificado: {len(vt)} nodos · {' → '.join(tipos)}")
        print()


if __name__ == "__main__":
    main()
