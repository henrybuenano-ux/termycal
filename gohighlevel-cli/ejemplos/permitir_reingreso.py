"""Reingreso (`allowMultiple`): sin esto, un contacto pasa por el workflow UNA vez en su vida.

CÓMO SE ENCONTRÓ
----------------
15-ago, contacto 5NpaZkeAeQTgWKJY1EJv. SP06 calificó perfecto y SP05 no envió la ficha, con
la misma estructura y los mismos triggers. La única diferencia entre los dos workflows, al
compararlos entero por API, era una clave:

    SP06 → allowMultiple = true      (Oliver lo activó en Configuración)
    SP05 → allowMultiple = false

SP05 entró temprano —cuando `Sede` todavía estaba vacía—, la guarda cortó, y cuando la sede
por fin llegó **el trigger no pudo volver a enrolarlo**. Gastó su único turno.

POR QUÉ IMPORTA MÁS ALLÁ DE SP05
--------------------------------
Los normalizadores viven de dispararse cada vez que cambia su campo. Con el reingreso
apagado, un lead que empieza en "Melamina Desde Cero" y se pasa a "Melamina Avanzado" se
queda con la `Modalidad` y la `Sede` de la primera pasada: WF-NORM y WF-MOD ya no vuelven a
correr. Y sus escrituras son idempotentes, así que entrar de más no cuesta nada.

QUÉ SE ACTIVA Y QUÉ NO
----------------------
Se activa solo donde volver a entrar es inofensivo o necesario: normalizadores y limpieza.

NO se toca lo que **hace algo hacia afuera** al entrar —mandar recordatorios, cerrar la
oportunidad, matricular—, porque ahí reingresar significa repetir el efecto:
AP02, AP04, SP10-B, SP11, SP12, PS01, PS01-B, PS02. Esos se revisan uno por uno cuando les
toque, con su propio marcador de "ya hecho" si hace falta, como el `ficha-enviada` de SP05.
"""
import sys, pathlib

ROOT = pathlib.Path("/home/user/grupo-galk")
sys.path.insert(0, str(ROOT / "scripts_ghl"))
from wf_lib import C, LOC

SOLO_MIRAR = "--aplicar" not in sys.argv

# Escrituras idempotentes: volver a entrar solo recalcula lo mismo.
# SP05 y SP06 también van: sus guardas de entrada (`ficha-enviada` / `Calificado`)
# hacen el reingreso seguro, y SIN reingreso se rompen — entran una vez con datos
# incompletos, la guarda los saca, y ya nunca pueden volver (visto el 19-ago con
# el PUT que reseteó allowMultiple de SP05: el lead calificaba y la ficha no salía).
# Prefijos con " |" para no arrastrar variantes (SP06.1 | CAPI reenvía un evento
# de conversión hacia afuera: reingreso ahí = evento duplicado, NO va).
CON_REINGRESO = ("WF-NORM-1", "WF-NORM-2", "WF-NORM-3", "WF-NORM-4",
                 "WF-MOD", "WF-SWITCH", "SP05 |", "SP06 |")


def main():
    ws = C.request("GET", f"/workflow/{LOC}") or []
    pendientes = []
    for w in ws:
        if not w["name"].startswith(CON_REINGRESO):
            continue
        d = C.request("GET", f"/workflow/{LOC}/{w['id']}") or {}
        if d.get("allowMultiple"):
            print(f"  ya estaba  · {w['name']}")
            continue
        pendientes.append((w, d))

    if not pendientes:
        print("\nTodos con reingreso activo. Nada que hacer (idempotencia §3).")
        return

    for w, d in pendientes:
        print(f"  activar    · {w['name']}  ({d.get('status')})")
        if SOLO_MIRAR:
            continue
        tpl = (d.get("workflowData") or {}).get("templates") or []
        if not tpl:
            print("      ABORTA: no pude leer los nodos, no mando un PUT vacío"); continue
        r = C.request("PUT", f"/workflow/{LOC}/{w['id']}",
                      {"name": d.get("name"), "version": d.get("version"),
                       "parentId": d.get("parentId"), "status": d.get("status"),
                       "allowMultiple": True, "workflowData": {"templates": tpl}})
        v = C.request("GET", f"/workflow/{LOC}/{w['id']}") or {}
        print(f"      PUT: {'OK' if r and not r.get('_error') else r} · "
              f"reingreso={v.get('allowMultiple')} · {v.get('status')} · "
              f"{len((v.get('workflowData') or {}).get('templates') or [])} nodos")

    if SOLO_MIRAR:
        print("\n(simulación; --aplicar para escribir)")


if __name__ == "__main__":
    main()
