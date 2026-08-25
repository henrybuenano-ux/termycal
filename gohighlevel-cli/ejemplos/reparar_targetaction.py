"""Triggers que apuntan a un nodo que ya no existe: el workflow nunca se ejecuta.

SÍNTOMA
-------
WF-NORM-1 está publicado, su trigger está activo, su rama `contain 'taller'` es correcta
y el campo `Familia de interés (bot)` sí se llena con "Talleres". Y aun así *Historial de
inscripciones* dice **"No se han encontrado inscripciones"**: ningún contacto entró nunca.

CAUSA
-----
Cada trigger guarda un `targetActionId`, que es **el nodo por el que el contacto entra al
workflow**. Los triggers viven en un endpoint aparte (`/workflow/{loc}/trigger`) y no se
tocan cuando se hace PUT del workflow. Así que cada vez que un script reconstruyó los
nodos —y todos generan IDs nuevos con `nid()`— el trigger se quedó apuntando al nodo
viejo. El trigger dispara, busca por dónde entrar, no encuentra el nodo y no pasa nada.
Silencioso: ni error, ni inscripción.

Son 5 workflows, no solo WF-NORM-1:

  · AP01 | Confirmación de matrícula
  · PS01-B | Reseña Google o alerta por nota baja
  · SP06 | Calificación y asignación      ← corría igual porque el bot lo llama con
                                            add_to_workflow, saltándose el trigger
  · WF-NORM-1 | Normalizar Familia de interés
  · WF-SWITCH | Limpiar interés al cambiar de familia

ARREGLO
-------
Se recalcula el nodo de entrada de cada workflow y se reapunta el trigger. El nodo de
entrada es el único que no tiene `parent` y al que nadie apunta con `next`. Si sale más de
un candidato, se aborta ese workflow en vez de adivinar.

El trigger se reenvía tal cual, cambiando solo `targetActionId`. En particular se respeta
`active`: mandar `active: True` en un trigger **publica el workflow**, así que los que
están en borrador tienen que seguir en borrador.
"""
import sys, pathlib

ROOT = pathlib.Path("/home/user/grupo-galk")
sys.path.insert(0, str(ROOT / "scripts_ghl"))
from wf_lib import C, LOC

SOLO_MIRAR = "--aplicar" not in sys.argv


def entrada(templates):
    """El nodo raíz: sin parent y sin nadie que lo apunte con next."""
    apuntados = set()
    for n in templates:
        nx = n.get("next")
        if isinstance(nx, list):
            apuntados.update(nx)
        elif nx:
            apuntados.add(nx)
    cand = [n["id"] for n in templates if not n.get("parent") and n["id"] not in apuntados]
    return cand


def main():
    rotos = []
    for w in C.request("GET", f"/workflow/{LOC}") or []:
        trs = C.request("GET", f"/workflow/{LOC}/trigger?workflowId={w['id']}") or []
        if not trs:
            continue
        d = C.request("GET", f"/workflow/{LOC}/{w['id']}") or {}
        tpl = (d.get("workflowData") or {}).get("templates") or []
        ids = {n["id"] for n in tpl}
        for t in trs:
            tgt = t.get("targetActionId")
            # OJO: targetActionId=None es VÁLIDO — significa "entrada por defecto". Decenas
            # de triggers de Francisco funcionan así en producción. Solo es un bug cuando
            # apunta a un ID que YA NO EXISTE (nodos regenerados por un PUT).
            if tgt and tgt not in ids:
                rotos.append((w, d, tpl, t))

    if not rotos:
        print("Todos los triggers apuntan a un nodo válido. Nada que hacer.")
        return

    print(f"{len(rotos)} trigger(s) apuntando a un nodo inexistente:\n")
    for w, d, tpl, t in rotos:
        cand = entrada(tpl)
        estado = d.get("status")
        print(f"  {w['name']}")
        print(f"    trigger '{t.get('name')}' [{t.get('type')}] active={t.get('active')} "
              f"· workflow {estado}")
        print(f"    apunta a {str(t.get('targetActionId'))[:8]} · candidatos de entrada: "
              f"{[c[:8] for c in cand]}")
        if len(cand) != 1:
            print("    ABORTA: no hay un único nodo de entrada, se revisa a mano\n")
            continue
        nuevo = cand[0]
        primero = next(n for n in tpl if n["id"] == nuevo)
        print(f"    -> {nuevo[:8]}  ({primero.get('type')} · {primero.get('name')})")
        if SOLO_MIRAR:
            print("    (simulación; corre con --aplicar para escribir)\n")
            continue
        body = dict(t)
        body["targetActionId"] = nuevo
        body["triggersChanged"] = True
        r = C.request("PUT", f"/workflow/{LOC}/trigger/{t['id']}", body)
        ok = r and not (isinstance(r, dict) and r.get("_error"))
        print(f"    PUT: {'OK' if ok else r}")
        v = C.request("GET", f"/workflow/{LOC}/{w['id']}") or {}
        vt = next((x for x in (C.request("GET", f"/workflow/{LOC}/trigger?workflowId={w['id']}")
                               or []) if x["id"] == t["id"]), {})
        print(f"    VERIFY: targetActionId={str(vt.get('targetActionId'))[:8]} "
              f"· active={vt.get('active')} · workflow={v.get('status')}\n")


if __name__ == "__main__":
    main()
