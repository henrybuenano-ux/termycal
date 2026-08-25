"""SP05 v2 — "Secuencia de ficha" según reunión 19-ago (ACUERDOS-reunion-2026-08-19.md §1).

La ficha se dispara AL DETECTAR EL CURSO (ya no al confirmar sede). Árbol por CURSO con las
3 ramas de talleres; software/gestión caen en None (silencioso) hasta que llegue su contenido.

Cada rama de taller (9 nodos):
  1. apagar bot          (update_conversation_ai_status keep-same/inactive, clonado de SP06)
  2. SMS apertura        (texto oficial de Lucía, firmado Valeria)
  3-6. SMS imagen 1-4    (caption corto + línea "image - <url>" que el gateway vuelve imagen)
  7. SMS pregunta final  ("¿Surco, Los Olivos o Provincia Arequipa?")
  8. tag ficha-enviada   (marcador DESPUÉS del envío)
  9. activar BOT-01      (update_conversation_ai_status bot concreto/active, clonado de LS01)

Guarda de entrada (exit): tag ficha-enviada presente OR Curso de interés vacío.
Triggers que quedan: 'Curso de interés cambió' + 'Enviar Ficha' (tag). Los de Sede/Modalidad
se ELIMINAN (con la ficha temprana provocarían dobles envíos por carrera con el marcador).

El PUT reutiliza el workflow SP05 existente (mismo ID). Los nodos v1 quedan respaldados en
sp05_v1_backup.json. allowMultiple SIEMPRE en el body (gotcha 19-ago).

Excepción temporal documentada: URLs del CDN en el body (pilot SMS); los custom values
se remodelan cuando entren las plantillas WABA.

Uso: build_sp05_v2.py [--aplicar]   (sin flag = dry-run: imprime resumen y valida clones)
"""
import os, sys, json, uuid, pathlib
ROOT = pathlib.Path("/home/user/grupo-galk")
for l in (ROOT / ".env").read_text().splitlines():
    l = l.strip()
    if l and not l.startswith("#") and "=" in l:
        k, v = l.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts_ghl"))
from wf_lib import C, LOC

SP05 = "ae78625c-8f91-4af1-a7b0-3be0b2e4a667"
SP06 = "84811c16-30d8-4c08-a05d-0c12fa46567d"
BOT01 = "L9hj6kGF7Ie73EhRzgqD"          # BOT-01 Talleres
BOT02 = "6vDo80qswCZgzWEIxXRC"          # BOT-02 Software
CURSO_ID = "bjDW7b9QoRiFWL5d578w"        # ID del campo Curso de interés (el de los triggers)
BACKUP = ROOT / "scripts_ghl" / "sp05_v1_backup.json"
CDN = "https://assets.cdn.filesafe.space/YN2uRSDcNeBdTWm3UPCU/media/%s.jpeg"
WA_PHONE = "1138517799350419"            # número oficial conectado (termina en 645), del molde de la UI

# nombre y tamaño exacto de cada imagen del media store (para whatsapp_media)
MEDIA = {
 "6a4b0fed70834e617c689aa1": ("Melamina-1.jpeg", 214198),
 "6a4b0fed1bf938e5479bed61": ("Melamina-2.jpeg", 217826),
 "6a4b0fed8a69aa2441919a1a": ("Melamina-3.jpeg", 295127),
 "6a4b0fed8a69aa2441919a14": ("Melamina-4.jpeg", 233140),
 "6a4da7e82467f0ff08fed87d": ("Drywall-1.jpeg", 261582),
 "6a4da7f02467f0ff08ff12a5": ("Drywall-2.jpeg", 224894),
 "6a4da7f01e3d535c0821a6ae": ("Drywall-3.jpeg", 256058),
 "6a4da7f02d9cf805155950d4": ("Drywall-4.jpeg", 249634),
 "6a51b6b1eada8c1f450813db": ("Electricidad-3.jpeg", 233765),
 "6a51b6b19c9b37b5fd3f5d4a": ("Electricidad-2.jpeg", 260773),
 "6a51b6b10e67afc013822d3f": ("Electricidad-1.jpeg", 258571),
 "6a51b6b1eada8c1f450813d7": ("Electricidad-4.jpeg", 232372),
}

# Brochures PDF: se suben desde contenido-fichas/assets/ con subir_pdfs.py y aquí se pega
# la tupla que imprime: ("<media_id>", "<nombre>", <bytes>, "<ext>").
# Mientras una tupla sea None, SU rama no se construye (las demás sí).
SKETCHUP_PDF = ("e9d01350-f587-4268-a61a-c9175672ca2e", "G1-SketchUp-Brochure.pdf", 710633, "pdf")
REVIT_PDF = ("567c5263-a487-4b33-ba03-3ad307948922", "G4.2-Revit-Brochure.pdf", 7759762, "pdf")

def wa_texto_attrs(mensaje):
    """whatsapp_v2 free-form: claves del MOLDE TEXTO de la UI, multipath apagado como en v1."""
    return {"template_id": "0", "toggle_branch": False, "from_phone_number": WA_PHONE,
            "snippet_id": "", "message": mensaje, "type": "whatsapp_v2",
            "__customInputs__": {}, "cat": "", "convertToMultipath": False,
            "transitions": [], "__name__": "WhatsApp"}

CAPTIONS = False   # 20-ago (Oliver): imágenes limpias, sin texto abajo. Los captions siguen
                   # en RAMAS por si tras las pruebas hiciera falta reactivarlos (poner True).

def wa_media_attrs(media_id, caption, media_type="image", nombre=None, size=None, ext="jpeg"):
    """whatsapp_media: claves del MOLDE IMAGEN de la UI, con la URL del propio storage.
    media_type "document" (PDF) usa la misma forma — pendiente de validar en ejecución."""
    if nombre is None:
        nombre, size = MEDIA[media_id]
    url = f"https://assets.cdn.filesafe.space/YN2uRSDcNeBdTWm3UPCU/media/{media_id}.{ext}"
    return {"__dynamicAttachments__": {}, "from_number_id": WA_PHONE, "media_type": media_type,
            "media_url": [{"name": nombre, "url": url, "size": size}],
            "media_caption": caption if CAPTIONS else "", "type": "whatsapp_media",
            "__customInputs__": {}}

def wait_attrs(segundos=3):
    """Wait corto entre mensajes (forma clonada del Wait de 5s de SP06, hecho en la UI)."""
    return {"type": "time", "startAfter": {"type": "seconds", "value": segundos, "when": "after"},
            "name": "Wait", "cat": "", "timePeriodInputMode": "standard",
            "unitInputMode": "standard", "isHybridAction": True, "hybridActionType": "wait",
            "convertToMultipath": False, "transitions": []}

def nid(): return str(uuid.uuid4())

# ---------- contenido oficial (contenido-fichas/*.md, verbatim, firmado Valeria) ----------
APERTURA_ELEC = """💬 ¡Hola! ¿Cuál es tu nombre? 😊
Soy Valeria de Grupo GALK y tengo una oportunidad especial para ti 🎉

Aprende una habilidad muy demandada con nuestro G25 Taller de Electricidad y Automatización Residencial ⚡💡
Un curso *100% práctico*, ideal para comenzar desde cero y desarrollar competencias reales en instalaciones eléctricas y automatización.

📌 Ofertas vigentes por tiempo limitado:
✅ S/600 – separa tu vacante con S/100

📍*Sedes:* Lima-Surco (Calle Aldabas 559) o Los Olivos (Av. Antunes de Mayolo 822). Provincia-Arequipa (Calle José Santos Chocano 249– Umacollo)
🧾 Incluye: certificación, materiales y asesorías personalizadas

📸 Te comparto las imágenes del taller con toda la información y beneficios. ¡Mira lo completo que está este programa! 👇"""

APERTURA_MELA = """💬 ¡Hola! ¿Cuál es tu nombre? 😊
Soy Valeria del equipo de Grupo GALK, ¡un gusto saludarte! 🙌
Me alegra mucho tu interés en nuestro Taller de Armado de Muebles en Melamina 🎉

Este taller es una gran oportunidad para aprender desde cero a trabajar con melamina y fabricar tus propios muebles paso a paso, incluso si nunca antes lo has hecho 🪚✨

📌 Ofertas vigentes hasta el 24 de agosto:
✅ S/525 un taller (G13 – Taller desde Cero o G16 – Taller Avanzado 16 hrs cada uno) – separa tu vacante con S/100
✅ S/890 el Pack Completo (G13 + G16 – Desde Cero + Avanzado 32 hrs) – separa con S/200

📍*Sedes:* Lima-Surco (Calle Aldabas 559) o Los Olivos (Av. Antunes de Mayolo 822). Provincia-Arequipa (Calle José Santos Chocano 249)
🧾 Incluye: certificación, materiales y asesorías personalizadas
⚠️ Importante – Requisitos para el taller: Por temas de *seguridad e higiene*, los alumnos deberán asistir obligatoriamente con:
🧤 Guantes con palma de nitrilo
👓 Lentes de seguridad transparentes

📸 Te comparto las imágenes del taller con toda la información y beneficios. ¡Mira lo completo que está este programa! 👇"""

APERTURA_DRY = """💬 ¡Hola! ¿Cuál es tu nombre? 😊
Soy Valeria del equipo de Grupo GALK y tengo una oferta especial para ti 🎉

Aprende a construir y diseñar con Drywall desde cero con nuestro Taller de Sistemas Constructivos en Drywall 🧱💪
Ideal si buscas capacitarte profesionalmente o emprender en el rubro de la construcción ligera.

📌 Ofertas vigentes hasta el 24 de agosto:
✅ S/450 – un taller (G24 – Desde Cero o G28 – Avanzado, 16 hrs cada uno) – reserva con S/100
✅ S/850 – Pack Completo (G24 + G28 – Desde Cero + Avanzado, 32 hrs) – reserva con S/200

📍*Sedes:* Lima-Surco (Calle Aldabas 559) o Los Olivos (Av. Antunes de Mayolo 822). Provincia-Arequipa (Calle José Santos Chocano 249)
🧾 Incluye: certificación y asesoría personalizada
⚠️ Importante – Requisitos para el taller: Por temas de *seguridad e higiene*, los alumnos deberán asistir obligatoriamente con:
🧤 Guantes con palma de nitrilo
👓 Lentes de seguridad transparentes
*CUTTERS DE MANGO GRUESO*

📸 Te comparto las imágenes del taller con toda la información y beneficios. ¡Mira lo completo que está este programa! 👇"""

FINAL_MSG = """✨ Una vez que me confirmes tu nombre, te envío los horarios y fechas disponibles en la sede que te quede más cerca.
¿Te interesa en Surco, Los Olivos o Provincia Arequipa? 😊"""

APERTURA_SKP = """📢 ¡Hola! ¿Cuál es tu nombre? 😊
Soy Valeria de Grupo GALK ✨ y quiero compartirte la información de nuestro Curso G1 | SketchUp 2025 + V-Ray 7 + PSD + twinmotion + IA 🎨💻. Aprenderás a crear renders profesionales y potenciar tus proyectos con herramientas de última tecnología. 🚀

🚀 Curso 100% práctico – Aprende desde cero con expertos.
📌 Modalidad: Virtual – En vivo por Zoom y Presencial Surco (Calle Aldabas 559)

🎁 *📌 Ofertas vigentes por tiempo limitado:
✅ S/370 modalidad online en vivo– Separa tu vacante con S/100
✅ S/550 modalidad presencial – Separa tu vacante con S/100
🛠️ Incluye certificación y asesoría personalizada

📸 Te comparto el brochure con toda la información sobre el contenido, duración y beneficios del curso. ¡Mira lo completo que está este programa! 👇"""

RESERVA_SKP = "Reserva tu vacante con S/100 y cancela el saldo hasta 2 días antes del inicio de clases."

FINAL_SKP = """✨ Para confirmarte el grupo ideal, cuéntame:
¿Deseas llevarlo en modalidad presencial en Surco o prefieres virtual en vivo? 😊"""

# (nombre, condiciones "contains" sobre Curso de interés, apertura, [(caption, media_id) x4])
# La rama Supervisión va PRIMERA y sin nodos: "Gestión y Supervisión de Melamina" contiene
# "melamina" y sin esta atrapadora se llevaría la ficha del taller. Sale sin enviar nada
# (su ficha de gestión llega después).
RAMAS = [
    # (nombre, condiciones "contains" en Curso de interés, bot que se activa al final,
    #  mensajes: ("texto", str) | ("img", media_id, caption) | ("doc", SKETCHUP_PDF, caption))
    ("Supervision (gestion, sin ficha aun)", ["supervisi"], None, []),
    ("Melamina", ["melamina"], BOT01, [
        ("texto", APERTURA_MELA),
        ("img", "6a4b0fed70834e617c689aa1", "🪚 Así se vive el taller — 100% práctico y presencial"),
        ("img", "6a4b0fed1bf938e5479bed61", "📚 Temario completo: las 16 horas, paso a paso"),
        ("img", "6a4b0fed8a69aa2441919a1a", "💪 Dos niveles: G13 desde cero a intermedio · G16 avanzado"),
        ("img", "6a4b0fed8a69aa2441919a14", "📝 Reserva tu vacante con S/100 — medios de pago"),
        ("texto", FINAL_MSG),
    ]),
    ("Drywall", ["drywall"], BOT01, [
        ("texto", APERTURA_DRY),
        ("img", "6a4da7e82467f0ff08fed87d", "🧱 Así se vive el taller — 100% práctico y presencial"),
        ("img", "6a4da7f02467f0ff08ff12a5", "📚 Temario completo: las 16 horas, paso a paso"),
        ("img", "6a4da7f01e3d535c0821a6ae", "💪 Dos niveles: G24 desde cero a intermedio · G28 avanzado"),
        ("img", "6a4da7f02d9cf805155950d4", "📝 Reserva tu vacante con S/100 — medios de pago"),
        ("texto", FINAL_MSG),
    ]),
    ("Electricidad", ["electricidad"], BOT01, [
        ("texto", APERTURA_ELEC),
        ("img", "6a51b6b1eada8c1f450813db", "⚡ Así se vive el taller — 100% práctico y presencial"),
        ("img", "6a51b6b19c9b37b5fd3f5d4a", "📚 Temario completo: las 20 horas, paso a paso"),
        ("img", "6a51b6b10e67afc013822d3f", "💪 Empiezas desde cero, sales instalando y automatizando"),
        ("img", "6a51b6b1eada8c1f450813d7", "📝 Reserva tu vacante con S/100 — medios de pago"),
        ("texto", FINAL_MSG),
    ]),
]

# Las ramas de software entran al árbol solo cuando su PDF ya esté en el media store
if SKETCHUP_PDF:
    RAMAS.append(("SketchUp", ["sketch"], BOT02, [
        ("texto", APERTURA_SKP),
        ("doc", SKETCHUP_PDF, "Brochure G1 SketchUp"),
        ("texto", RESERVA_SKP),
        ("texto", FINAL_SKP),
    ]))

APERTURA_RVT = """💬 ¡Hola! ¿Cuál es tu nombre? 😊
Soy *Valeria del equipo de Grupo GALK*, ¡un gusto saludarte! 🙌
Te escribo porque tenemos una oferta especial en nuestro curso *"BIM desde Cero – Revit + Render IA + Lumion (G4.2)"*, ideal para arquitectos, diseñadores e ingenieros que desean profesionalizar sus proyectos en 3D y renderizado ✨

📌 Modalidad: Virtual – En vivo por Zoom y Presencial Lima, Surco (Calle Aldabas 559)

🎁 *📌 Ofertas vigentes por tiempo limitado:
✅ S/370 modalidad virtual (reserva con S/100)
✅ S/550 modalidad presencial (reserva con S/100)

🧾 Incluye: certificación, clases en vivo, asesorías personalizadas y acceso a biblioteca de familias Revit GALK 💻

📸 Te comparto el brochure con toda la información sobre el contenido, duración y beneficios del curso. ¡Mira lo completo que está este programa! 👇"""

DURACION_RVT = """🕓 Duración: 28 horas académicas (24 horas en vivo O presenciales + 4 grabadas)
_Reserva tu vacante con S/100 y cancela el saldo hasta 2 días antes del inicio de clases._"""

# ⚠️ Orden del cierre según lo recibido (pregunta ANTES de duración) — pendiente de
# confirmar con Oliver si la pregunta va al final; ver contenido-fichas/G4.2-revit.md
if REVIT_PDF:
    RAMAS.append(("Revit", ["revit", "bim"], BOT02, [
        ("texto", APERTURA_RVT),
        ("doc", REVIT_PDF, "Brochure G4.2 Revit"),
        ("texto", FINAL_SKP),
        ("texto", DURACION_RVT),
    ]))

# ---------- clonar formas vivas (regla de oro) ----------
def clonar_ai_status():
    """Devuelve (attrs_apagar, attrs_activar) clonados de nodos hechos/validados en la UI."""
    apagar = activar = None
    d6 = C.request("GET", f"/workflow/{LOC}/{SP06}")
    for n in d6["workflowData"]["templates"]:
        if n["type"] == "update_conversation_ai_status":
            a = json.loads(json.dumps(n["attributes"]))
            if str(a.get("status", a.get("botStatus", ""))).lower().startswith("inactive") or "inactive" in json.dumps(a).lower():
                apagar = a
    ws = C.request("GET", f"/workflow/{LOC}")
    ls01 = [w for w in ws if w.get("name", "").startswith("LS01")][0]
    dl = C.request("GET", f"/workflow/{LOC}/{ls01['id']}")
    for n in dl["workflowData"]["templates"]:
        if n["type"] == "update_conversation_ai_status" and "active" == str(n["attributes"].get("status", "")).lower():
            activar = json.loads(json.dumps(n["attributes"]))
    if not (apagar and activar):
        print("ABORT: no pude clonar los nodos de AI status (apagar=%s activar=%s)" % (bool(apagar), bool(activar)))
        print("  SP06 y LS01 deben tener sus nodos update_conversation_ai_status vivos.")
        sys.exit(1)
    # el bot destino se fija POR RAMA en el bucle de construcción
    return apagar, activar

def cond_curso(valor):
    return {"conditionType": "contact_detail", "conditionSubType": CURSO_ID,
            "conditionOperator": "contains", "conditionValue": valor,
            "__conditionId": nid(), "ifElseNodeId": "", "__customFieldType__": "standard", "isWait": False}

def n_sms(nodo_id, body, name, nxt="", parent=None):
    n = {"id": nodo_id, "order": 0,
         "attributes": {"template_id": "", "body": body, "attachments": []},
         "name": name, "type": "sms", "next": nxt}
    if parent: n.update({"parent": parent, "parentKey": parent})
    return n

def main():
    aplicar = "--aplicar" in sys.argv
    d5 = C.request("GET", f"/workflow/{LOC}/{SP05}")
    v1 = d5["workflowData"]["templates"]
    if not BACKUP.exists():
        BACKUP.write_text(json.dumps(v1, ensure_ascii=False, indent=1))
        print(f"backup v1: {len(v1)} nodos -> {BACKUP.name}")
    ramas_vivas = {n.get("name") for n in v1 if n.get("nodeType") == "branch-yes"}
    ramas_esperadas = {r[0] for r in RAMAS}
    ya_v2 = (any(n["id"] == "84d3ebf4-7b4f-48d2-949f-697513061b01" for n in v1)
             and not any(n["type"] == "sms" for n in v1)
             and ramas_esperadas <= ramas_vivas)
    if not ya_v2 and ramas_vivas:
        print("ramas nuevas a construir:", sorted(ramas_esperadas - ramas_vivas))
    if ya_v2:
        print("SP05 ya es v2 (idempotencia §3). Nada que hacer."); return

    apagar_attrs, activar_attrs = clonar_ai_status()
    print("clones OK · apagar:", json.dumps(apagar_attrs, ensure_ascii=False)[:120])
    print("           activar:", json.dumps(activar_attrs, ensure_ascii=False)[:120])

    # ---- esqueleto: se reutilizan los nodos estructurales del v1 (convención que SÍ renderiza) ----
    v1_full = json.loads(BACKUP.read_text())
    by_id = {n["id"]: n for n in v1_full}
    guard_hdr = json.loads(json.dumps(by_id["84d3ebf4-7b4f-48d2-949f-697513061b01"]))
    g_yes    = json.loads(json.dumps(by_id["759bd187-862b-48b6-b5e4-4af8d9dc8097"]))
    g_no     = json.loads(json.dumps(by_id["ce095b41-b3f0-4dc9-8831-daa00f2aa357"]))
    tree_hdr = json.loads(json.dumps(by_id["a9eef63b-1e23-4716-801d-ed2ee6162aed"]))
    v1_none  = [n for n in v1_full if n.get("nodeType") == "branch-no" and n.get("parent") == tree_hdr["id"]][0]
    none_nd  = json.loads(json.dumps(v1_none))

    # guarda: dejar solo las condiciones ficha-enviada + curso vacío
    seg = guard_hdr["attributes"]["branches"][0]["segments"][0]
    seg["conditions"] = [c for c in seg["conditions"]
                         if c.get("conditionSubType") == "tags"
                         or (c.get("conditionSubType") == CURSO_ID and c.get("conditionOperator") == "has_no_value")]
    guard_hdr["attributes"]["branches"][0]["name"] = "No enviar (ya enviada o sin curso)"
    g_yes["name"] = "No enviar (ya enviada o sin curso)"
    assert len(seg["conditions"]) == 2, seg["conditions"]

    # árbol: ramas nuevas por curso
    branch_ids = {nombre: nid() for nombre, *_ in RAMAS}
    tree_branches = []
    for nombre, conds, _, _ in RAMAS:
        tree_branches.append({"id": branch_ids[nombre], "name": nombre,
            "segments": [{"__segmentId": nid(), "operator": "or",
                          "conditions": [cond_curso(v) for v in conds]}]})
    tree_hdr["attributes"]["branches"] = tree_branches
    tree_hdr["next"] = list(branch_ids.values()) + [none_nd["id"]]
    none_nd["sibling"] = list(branch_ids.values())
    none_nd["next"] = ""          # software/gestión: salida silenciosa

    nodes = []
    grupo = list(branch_ids.values()) + [none_nd["id"]]
    for nombre, conds, bot_destino, mensajes in RAMAS:
        bid = branch_ids[nombre]
        sib = [x for x in grupo if x != bid]
        rama = {"id": bid, "order": 0, "attributes": {"if": False, "conditionName": "Condition",
            "operator": "and", "branches": []}, "name": nombre, "type": "if_else",
            "nodeType": "branch-yes", "cat": "conditions", "sibling": sib,
            "parent": tree_hdr["id"], "parentKey": tree_hdr["id"], "next": ""}
        if not mensajes:          # rama atrapadora (Supervisión): sale sin enviar nada
            nodes.append(rama); continue
        # pausa-bot + [msg, wait, msg, wait, ...] + tag + activar
        N = 1 + (2 * len(mensajes) - 1) + 2
        ids = [nid() for _ in range(N)]
        rama["next"] = ids[0]
        nodes.append(rama)
        def chain(idx, nodo):     # convención v1: parent = LA RAMA, encadenado por next
            nodo.update({"id": ids[idx], "order": 0, "parent": bid, "parentKey": bid,
                         "next": ids[idx + 1] if idx < N - 1 else ""})
            nodes.append(nodo)
        chain(0, {"attributes": json.loads(json.dumps(apagar_attrs)),
                  "name": "Bot en pausa (secuencia)", "type": "update_conversation_ai_status",
                  "workflowsActionType": "INTERNAL"})
        idx = 1
        for j, m in enumerate(mensajes):
            if j > 0:
                chain(idx, {"attributes": wait_attrs(3), "name": "Pausa 3s", "type": "wait"})
                idx += 1
            tipo = m[0]
            if tipo == "texto":
                chain(idx, {"attributes": wa_texto_attrs(m[1]),
                            "name": f"Mensaje {j+1}: {nombre}", "type": "whatsapp_v2",
                            "workflowsActionType": "INTERNAL"})
            elif tipo == "img":
                chain(idx, {"attributes": wa_media_attrs(m[1], m[2]),
                            "name": f"Imagen: {nombre} ({j+1})", "type": "whatsapp_media",
                            "workflowsActionType": "INTERNAL"})
            elif tipo == "doc":
                mid, fname, size, ext = m[1]
                chain(idx, {"attributes": wa_media_attrs(mid, m[2], media_type="document",
                                                         nombre=fname, size=size, ext=ext),
                            "name": f"PDF: {nombre}", "type": "whatsapp_media",
                            "workflowsActionType": "INTERNAL"})
            idx += 1
        chain(idx, {"attributes": {"tags": ["ficha-enviada"]}, "name": "Marcar ficha-enviada",
                    "type": "add_contact_tag"})
        act = json.loads(json.dumps(activar_attrs))
        act["assignedEmployeeId"] = bot_destino
        chain(idx + 1, {"attributes": act, "name": f"Activar bot destino",
                        "type": "update_conversation_ai_status", "workflowsActionType": "INTERNAL"})

    hdr_id = guard_hdr["id"]      # los triggers ya apuntan aquí
    tpl = [guard_hdr, g_yes, g_no, tree_hdr, none_nd] + nodes
    print(f"v2: {len(tpl)} nodos (esqueleto v1 + 3 ramas x 9 + atrapadora)")
    if not aplicar:
        print("(dry-run — usa --aplicar)"); return

    r = C.request("PUT", f"/workflow/{LOC}/{SP05}",
                  {"name": d5.get("name"), "version": d5.get("version"),
                   "parentId": d5.get("parentId"), "status": d5.get("status"),
                   "allowMultiple": True, "workflowData": {"templates": tpl}})
    print("PUT:", "OK" if r and not (isinstance(r, dict) and r.get("_error")) else r)
    if isinstance(r, dict) and r.get("_error"):
        sys.exit(1)

    # ---- triggers: reapuntar los 2 buenos al header nuevo, borrar Sede/Modalidad ----
    trs = C.request("GET", f"/workflow/{LOC}/trigger?workflowId={SP05}") or []
    if isinstance(trs, dict): trs = trs.get("triggers", [])
    for t in trs:
        nombre = t.get("name", "")
        if nombre in ("Sede cambió", "Modalidad cambió"):
            rr = C.request("DELETE", f"/workflow/{LOC}/trigger/{t['id']}")
            print(f"trigger {nombre!r}: DELETE", "OK" if not (isinstance(rr, dict) and rr.get("_error")) else rr)
        else:
            body = {k: t[k] for k in t if not k.startswith("_")}
            body["targetActionId"] = hdr_id
            rr = C.request("PUT", f"/workflow/{LOC}/trigger/{t['id']}", body)
            print(f"trigger {nombre!r}: retarget ->", "OK" if not (isinstance(rr, dict) and rr.get("_error")) else rr)

    # ---- verificación ----
    d2 = C.request("GET", f"/workflow/{LOC}/{SP05}")
    tipos = {}
    for n in d2["workflowData"]["templates"]:
        tipos[n["type"]] = tipos.get(n["type"], 0) + 1
    print("tras PUT:", tipos, "· allowMultiple:", d2.get("allowMultiple"), "· status:", d2.get("status"))
    trs2 = C.request("GET", f"/workflow/{LOC}/trigger?workflowId={SP05}") or []
    if isinstance(trs2, dict): trs2 = trs2.get("triggers", [])
    ids2 = {n["id"] for n in d2["workflowData"]["templates"]}
    for t in trs2:
        ta = t.get("targetActionId")
        print(f"trigger {t.get('name')!r}: active={t.get('active')} target={'OK' if (ta is None or ta in ids2) else 'ROTO'}")

if __name__ == "__main__":
    main()
