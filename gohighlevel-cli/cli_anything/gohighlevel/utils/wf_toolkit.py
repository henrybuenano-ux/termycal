# -*- coding: utf-8 -*-
"""wf_toolkit — formas de nodos y operaciones de workflow VALIDADAS EN PRODUCCIÓN.

Todo lo que hay aquí se probó de punta a punta en una subcuenta real (proyecto Grupo GALK,
ago-2026): cada forma de nodo ejecutó de verdad — no solo "se guardó bonito". Antes de
inventar un atributo nuevo, lee PLAYBOOK-GHL.md: la lección número uno de ese proyecto es
que GHL acepta y muestra nodos malformados que luego NO ejecutan (fallo silencioso).

REGLA DE ORO: si necesitas un tipo de nodo que no esté aquí, créalo una vez A MANO en la
UI, léelo por API, y clona su forma exacta. Nunca fabriques atributos.

Uso típico:
    from gohighlevel.utils.wf_toolkit import *
    pub = ClientePublico()            # lee .env (GHL_API_KEY, GHL_LOCATION_ID)
    interno = ClienteInterno()        # + GHL_FIREBASE_REFRESH_TOKEN
"""
import os, json, uuid, pathlib

# ---------------------------------------------------------------------------
# entorno
# ---------------------------------------------------------------------------

def cargar_env(raiz="."):
    p = pathlib.Path(raiz) / ".env"
    if p.exists():
        for l in p.read_text().splitlines():
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

def nid():
    return str(uuid.uuid4())

# ---------------------------------------------------------------------------
# FORMAS DE NODOS VALIDADAS (ejecutaron en producción)
# ---------------------------------------------------------------------------

def n_whatsapp_texto(mensaje, from_phone):
    """WhatsApp free-form (sin plantilla). Requiere sesión abierta de 24h (el lead
    escribió primero). Clave del cuerpo: `message`. Multipath apagado para que la
    cadena siga recta (la UI lo crea con Delivered/Undelivered encendido)."""
    return {"template_id": "0", "toggle_branch": False, "from_phone_number": from_phone,
            "snippet_id": "", "message": mensaje, "type": "whatsapp_v2",
            "__customInputs__": {}, "cat": "", "convertToMultipath": False,
            "transitions": [], "__name__": "WhatsApp"}

def n_whatsapp_media(url, nombre, size_bytes, from_phone, caption="", media_type="image"):
    """WhatsApp con imagen o PDF. `media_url` es LISTA de {name,url,size} y la URL puede
    ser del propio media store (assets.cdn.filesafe.space) — la UI no deja pegar URL,
    pero el JSON sí la acepta y ejecuta. media_type: "image" | "document" (PDF, validado)."""
    return {"__dynamicAttachments__": {}, "from_number_id": from_phone,
            "media_type": media_type,
            "media_url": [{"name": nombre, "url": url, "size": size_bytes}],
            "media_caption": caption, "type": "whatsapp_media", "__customInputs__": {}}

def n_sms(cuerpo, adjuntos=None):
    """SMS inline. ⚠️ El cuerpo va en `body`, NO en `message` (message lo rechaza el
    validador). ⚠️ `attachments` con URLs ejecuta [null] — las imágenes por SMS van como
    línea "image - <url>" dentro del body si el gateway la soporta (WaAutoReply sí)."""
    return {"template_id": "", "body": cuerpo, "attachments": adjuntos or []}

def n_wait_segundos(segundos=3):
    """Espera corta (acepta segundos). Clonado de un Wait hecho en la UI."""
    return {"type": "time", "startAfter": {"type": "seconds", "value": segundos, "when": "after"},
            "name": "Wait", "cat": "", "timePeriodInputMode": "standard",
            "unitInputMode": "standard", "isHybridAction": True, "hybridActionType": "wait",
            "convertToMultipath": False, "transitions": []}

def n_wait_minutos(minutos):
    return {"type": "time", "startAfter": {"type": "minutes", "value": minutos, "when": "after"},
            "name": "Wait", "cat": "", "timePeriodInputMode": "standard",
            "unitInputMode": "standard", "isHybridAction": True, "hybridActionType": "wait",
            "convertToMultipath": False, "transitions": []}

def n_tag(tags):
    return {"tags": tags if isinstance(tags, list) else [tags]}
    # type del nodo: "add_contact_tag" o "remove_contact_tag"

def n_ai_status_apagar():
    """Pausa el bot de la conversación sin reasignarla ('keep-same')."""
    return {"assignedEmployeeId": "keep-same", "status": "inactive",
            "shouldReactivateAfterTimeOut": False, "type": "update_conversation_ai_status"}

def n_ai_status_activar(bot_id):
    """Activa (y ASIGNA — ojo, reasigna la conversación) un bot concreto."""
    return {"assignedEmployeeId": bot_id, "status": "active",
            "shouldReactivateAfterTimeOut": False, "type": "update_conversation_ai_status"}

def n_notificacion(titulo, cuerpo, usuario_id=None):
    """Notificación interna. ⚠️ userType solo acepta DOS valores válidos:
        al dueño del contacto -> "assign" + assignedOwners:["contact_owner"]
        a un usuario concreto -> "user"   + selectedUser:"<id>"
    Cualquier otro valor (assigned_user, specific_user...) se guarda pero NO AVISA A NADIE."""
    n = {"type": "send_notification", "body": cuerpo, "title": titulo,
         "redirectPage": "conversation"}
    if usuario_id:
        n.update({"userType": "user", "selectedUser": usuario_id})
    else:
        n.update({"userType": "assign", "assignedOwners": ["contact_owner"]})
    return n

def n_oportunidad(pipeline_id, stage_id, status="open", valor="{{contact.precio_cotizado}}"):
    """Create/Update opportunity. ⚠️ Sin monetary_value algunos tenants lo rechazan o lo
    ejecutan mal — inclúyelo siempre (puede ser un merge field)."""
    return {"fields": [], "type": "create_opportunity", "pipeline_id": pipeline_id,
            "pipeline_stage_id": stage_id, "opportunity_name": "{{contact.name}}",
            "opportunity_status": status, "monetary_value": valor}

def n_vaciar_campos(campos):
    """Vaciar custom fields. ⚠️ La forma que ejecuta de verdad exige por campo:
    field(id) + value:"" + date:"" + title + type correcto ("select" para SINGLE_OPTIONS,
    "date" para DATE, "string" para texto). Si faltan claves, GHL ejecuta
    customFields: [] — un no-op silencioso (verificado con el registro de auditoría).
    `campos` = lista de dicts {"id":..., "title":..., "dataType": "TEXT|SINGLE_OPTIONS|DATE"}"""
    tipo = {"DATE": "date", "SINGLE_OPTIONS": "select"}
    fs = [{"field": c["id"], "value": "", "title": c["title"],
           "type": tipo.get(c.get("dataType", "TEXT"), "string"), "date": ""} for c in campos]
    return {"actionType": "clear_field_data", "type": "update_contact_field", "fields": fs}

# ---------------------------------------------------------------------------
# TRIGGERS
# ---------------------------------------------------------------------------

def cond_trigger_campo(field_id, titulo, operador="has-changed", tipo="string"):
    """Condición de trigger contact_changed. ⚠️ El campo va DOBLE: como
    "contact.<ID>" en `field` Y pelado en `id`. Con el ID pelado el trigger se guarda,
    pero el desplegable de la UI queda en "Seleccionar" y NUNCA dispara."""
    return {"operator": operador, "field": f"contact.{field_id}", "title": titulo,
            "type": tipo, "id": field_id}

def cond_trigger_tag(tag):
    return {"operator": "index-of-true", "field": "tagsAdded", "value": tag,
            "title": "Tag Added", "type": "select", "id": "tag-added"}

# ---------------------------------------------------------------------------
# ESTRUCTURA IF/ELSE — convención que el canvas SÍ renderiza
# ---------------------------------------------------------------------------
# Reglas (rompe el canvas si no se cumplen):
#  · header if_else:  nodeType="condition-node", SIN parent, next = LISTA de ids de
#    todas sus ramas (branch-yes... + branch-no)
#  · rama:            nodeType="branch-yes"/"branch-no", parent=header,
#    sibling=[los otros ids de rama], next = primer nodo de su cadena (string)
#  · un if_else ANIDADO se cuelga solo por el `next` del branch que lo contiene
#    (SIN parent propio)
#  · los nodos de una cadena llevan parent = EL ID DE LA RAMA (no el nodo anterior),
#    encadenados por next

def header_if(branches_def):
    """branches_def = [{"id","name","segments"}]. Devuelve el nodo header."""
    return {"id": nid(), "order": 0, "name": "yes", "type": "if_else", "cat": "conditions",
            "comments": [], "nodeType": "condition-node",
            "attributes": {"currentRecipeType": "", "branches": branches_def,
                           "operator": "and", "if": False, "conditionName": "Condition",
                           "version": 2, "noneBranchName": "None"}}

def rama(nombre, header_id, siblings, primer_nodo="", nodeType="branch-yes"):
    return {"id": nid(), "order": 0, "attributes": {"if": False, "conditionName": "Condition",
            "operator": "and", "branches": []}, "name": nombre, "type": "if_else",
            "nodeType": nodeType, "cat": "conditions", "sibling": siblings,
            "parent": header_id, "parentKey": header_id, "next": primer_nodo}

def cadena(rama_id, nodos_def):
    """nodos_def = [(attrs, name, type, workflowsActionType|None)]. Devuelve la lista de
    nodos encadenados con parent = la rama, y el id del primero."""
    ids = [nid() for _ in nodos_def]
    out = []
    for i, (attrs, name, tipo, wat) in enumerate(nodos_def):
        n = {"id": ids[i], "order": 0, "attributes": attrs, "name": name, "type": tipo,
             "parent": rama_id, "parentKey": rama_id,
             "next": ids[i + 1] if i < len(ids) - 1 else ""}
        if wat:
            n["workflowsActionType"] = wat   # "INTERNAL": whatsapp_v2/media, ai_status
        out.append(n)
    return out, (ids[0] if ids else "")

# ---------------------------------------------------------------------------
# OPERACIONES DE WORKFLOW SEGURAS
# ---------------------------------------------------------------------------

def put_workflow(cliente_interno, loc, wid, templates, allow_multiple=None):
    """PUT de workflowData que NO rompe la configuración.
    ⚠️ El PUT resetea a default cualquier campo raíz omitido — en particular
    allowMultiple (Reingreso): SIEMPRE va en el body. Este helper lo preserva
    leyendo el estado actual salvo que se fuerce."""
    d = cliente_interno.request("GET", f"/workflow/{loc}/{wid}")
    am = d.get("allowMultiple", False) if allow_multiple is None else allow_multiple
    return cliente_interno.request("PUT", f"/workflow/{loc}/{wid}",
        {"name": d.get("name"), "version": d.get("version"), "parentId": d.get("parentId"),
         "status": d.get("status"), "allowMultiple": am,
         "workflowData": {"templates": templates}})

def verificar_triggers(cliente_interno, loc, wid):
    """Chequeo post-PUT obligatorio: triggers activos, targetActionId apuntando a un nodo
    vivo, y condiciones de campo con el formato doble. Devuelve lista de problemas."""
    problemas = []
    d = cliente_interno.request("GET", f"/workflow/{loc}/{wid}")
    ids = {n["id"] for n in d["workflowData"]["templates"]}
    trs = cliente_interno.request("GET", f"/workflow/{loc}/trigger?workflowId={wid}") or []
    if isinstance(trs, dict):
        trs = trs.get("triggers", [])
    for t in trs:
        ta = t.get("targetActionId")
        if ta is not None and ta not in ids:
            problemas.append(f"trigger {t.get('name')!r}: targetActionId ROTO ({ta[:8]}...)")
        if not t.get("active"):
            problemas.append(f"trigger {t.get('name')!r}: INACTIVO (publicado != funcionando)")
        for c in t.get("conditions", []):
            f = c.get("field", "")
            if f.startswith("contact.") and c.get("id") != f.replace("contact.", ""):
                problemas.append(f"trigger {t.get('name')!r}: condición sin `id` doble — "
                                 "en la UI queda en 'Seleccionar' y no dispara")
    return problemas
