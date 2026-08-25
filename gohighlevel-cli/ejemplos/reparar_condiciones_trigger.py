"""Triggers `contact_changed` cuyo campo no queda seleccionado en la UI.

SÍNTOMA
-------
Abres el trigger en la UI y el desplegable del campo dice **"Seleccionar"**, vacío, aunque
el nombre del trigger sí diga "Curso de interés cambió". El trigger existe, está activo, y
no dispara nunca. Otra vez silencioso.

CAUSA
-----
La condición se guardaba con el ID pelado:

    {"operator": "has-changed", "field": "<ID>", "title": "...", "type": "text"}

y la UI la guarda con tres cosas distintas:

    {"operator": "has-changed", "field": "contact.<ID>", "title": "...",
     "type": "string" | "select", "id": "<ID>"}

Falta el prefijo `contact.` en `field` y falta la clave `id`. Sin eso el selector no
resuelve el campo. Verificado el 15-ago: los triggers de SP06 que Oliver rearmó a mano
quedaron con el formato de arriba, los creados por script no.

ALCANCE
-------
8 triggers nuestros nacieron mal. El más caro es **WF-MOD**, que por eso nunca corrió: la
`Modalidad` la venía llenando WF-NORM-2 desde el gemelo de texto, no WF-MOD. También
WF-NORM-4, SP12, AP02, AP04, PS01, PS01-B y PS02 — estos últimos en draft, así que todavía
no habían hecho daño.

QUÉ TOCA Y QUÉ NO
-----------------
Se corrigen `field` e `id`, que son los que demostradamente rompen el selector, y `type`
**solo** donde hay mapeo verificado contra la UI (TEXT → `string`, SINGLE_OPTIONS →
`select`). En DATE y NUMERICAL se deja el `type` como está: no hay ejemplo hecho a mano
para compararlos y no se adivina.

No se tocan los triggers de Francisco (política §3), ni los que ya están bien.
"""
import sys, json, pathlib

ROOT = pathlib.Path("/home/user/grupo-galk")
sys.path.insert(0, str(ROOT / "scripts_ghl"))
import wf_lib
from wf_lib import C, LOC

SOLO_MIRAR = "--aplicar" not in sys.argv
NUESTROS = ("SP0", "SP1", "AP0", "PS0", "LS0", "WF-NORM", "WF-MOD", "WF-SWITCH")
VERIFICADO = {"TEXT": "string", "SINGLE_OPTIONS": "select"}


def main():
    byid = {f["id"]: f for f in wf_lib._cf.values()}
    tocados = 0

    for w in C.request("GET", f"/workflow/{LOC}") or []:
        if not w.get("name", "").startswith(NUESTROS):
            continue
        for t in C.request("GET", f"/workflow/{LOC}/trigger?workflowId={w['id']}") or []:
            if t.get("type") != "contact_changed":
                continue
            conds = t.get("conditions") or []
            nuevas, cambios = [], []
            for c in conds:
                fid = str(c.get("field", "")).split(".")[-1]
                m = byid.get(fid)
                if not m:                       # campo estándar (assignedTo y demás)
                    nuevas.append(c); continue
                n = dict(c)
                if not str(c.get("field", "")).startswith("contact."):
                    n["field"] = f"contact.{fid}"; cambios.append("field")
                if c.get("id") != fid:
                    n["id"] = fid; cambios.append("id")
                esperado = VERIFICADO.get(m["dataType"])
                if esperado and c.get("type") != esperado:
                    n["type"] = esperado; cambios.append(f"type→{esperado}")
                n["title"] = m["name"]
                nuevas.append(n)

            if not cambios:
                continue
            tocados += 1
            print(f"  {w['name'][:44]:46} '{t.get('name')}'  [{', '.join(sorted(set(cambios)))}]")
            print(f"      antes:  {json.dumps(conds, ensure_ascii=False)[:110]}")
            print(f"      queda:  {json.dumps(nuevas, ensure_ascii=False)[:110]}")
            if SOLO_MIRAR:
                print("      (simulación; --aplicar para escribir)\n"); continue

            body = dict(t)
            body["conditions"] = nuevas
            body["triggersChanged"] = True
            r = C.request("PUT", f"/workflow/{LOC}/trigger/{t['id']}", body)
            ok = r and not (isinstance(r, dict) and r.get("_error"))
            v = next((x for x in (C.request("GET", f"/workflow/{LOC}/trigger?workflowId={w['id']}")
                                  or []) if x["id"] == t["id"]), {})
            est = (C.request("GET", f"/workflow/{LOC}/{w['id']}") or {}).get("status")
            print(f"      PUT: {'OK' if ok else r} · active={v.get('active')} · workflow={est}\n")

    print(f"\n{tocados} trigger(s) con el formato malo." if tocados
          else "\nTodos los triggers contact_changed nuestros tienen el formato bueno.")


if __name__ == "__main__":
    main()
