# Proyecto TÉRMYCAL — contexto para Claude Code

> **Lee `PLAYBOOK-GHL.md` antes de tocar nada.** Ahí están los gotchas de GHL aprendidos a
> golpes en producción. Las formas de nodos validadas están en
> `gohighlevel-cli/cli_anything/gohighlevel/utils/wf_toolkit.py` — úsalas, no fabriques
> atributos. *(CLI v2.1 adoptado el 25-ago-2026.)*

---

## 1. Arranque de sesión

`.env` en `gohighlevel-cli/` (NO está en git):

```
GHL_API_KEY=pit-...                  # Private Integration Token
GHL_LOCATION_ID=oWWElLfvuaO9tDThqa6d
GHL_FIREBASE_REFRESH_TOKEN=AMf-...   # token interno; si da 401, pedir uno nuevo
```

```bash
cd gohighlevel-cli && python3 -m venv .venv && .venv/bin/pip install requests
.venv/bin/python scripts/<script>.py            # dry-run
.venv/bin/python scripts/<script>.py --aplicar  # escribe
```

⚠️ **Gotcha del entorno (25-ago):** el contenedor trae un `GHL_FIREBASE_REFRESH_TOKEN`
viejo en las variables de entorno, y `wf_toolkit.cargar_env()` usa `setdefault`, así que
el token caducado le gana al bueno del `.env`. Los scripts del proyecto usan
`cargar_env_pisando()`, que fuerza el `.env`. Si un script falla con "token refresh
failed" y el `.env` es correcto, es esto.

⚠️ El contenedor se recicla entre sesiones y se lleva `.venv` y `.env`. Ambos se
reconstruyen; el token hay que pedírselo al usuario.

---

## 2. Reglas al escribir en GHL

- **Subcuenta EN PRODUCCIÓN**: todo lo nuevo es aditivo; lo heredado no se edita.
- **Idempotencia obligatoria**: todo script verifica si ya existe y salta. Dry-run por
  defecto, `--aplicar` para escribir.
- **Workflows como DRAFT** hasta revisión humana. **Publicar es SOLO desde el toggle de la
  UI** — por API es ruleta y la lectura del estado por API miente (playbook §2.7).
- **Después de cada PUT**: `verificar_triggers()` y confirmar `allowMultiple`
  (el PUT resetea todo campo raíz omitido — `put_workflow()` lo maneja).
- **Re-GET antes de cada PUT**: cada PUT incrementa `version` y un PUT con version vieja
  se ignora en silencio.
- **Textos para la UI de bots: contar caracteres SIEMPRE** (límite 500 en campos de
  acciones; el prompt no tiene ese límite).
- **Nada de URLs hardcodeadas** en workflows definitivos: custom values.
- La verdad está en la API y en pruebas en vivo, **nunca en cómo se ve el panel**.

## 3. Reglas de comunicación del proyecto

- **Idioma:** español neutro latinoamericano en entregables internos (nunca "vosotros").
  El bot del cliente SÍ habla castellano de España, tono andaluz-neutro.
- **Marca:** "omnia" siempre en minúsculas · "ómibu" minúscula con acento.
- **NUNCA decir "GHL" o "Go High Level" al cliente** → "omnia CRM" o "el sistema".
- **El sistema nunca envía nada sin aprobación humana.** Regla de arquitectura, no de
  estilo ("la última palabra la tiene el humano" — Henry).

---

## 4. Cliente

| Dato | Valor |
|---|---|
| Nombre fiscal | Alejandro Rodríguez Medina |
| Negocio | TÉRMYCAL — termos, calentadores, calderas, aerotermos (unipersonal) |
| NIF | 75564623D |
| Dirección | Avda. Don Bosco, 38 · Granada 18007 |
| WhatsApp negocio | 644 962 421 (confirmado para WABA) |
| Email | termycalgranada@gmail.com |
| IBAN | ES30 2100 0944 6202 0021 8036 |
| Zona | Granada capital + 20 km · 100% B2C |
| Particularidad | Colabora con Leroy Merlin (agenda propia NO integrable) |
| Problema raíz | Madruga para facturas en Excel; pierde leads por no atender WhatsApp mientras instala |

**Dominios** (todos en Piensa Solutions): `termosycalentadoresgranada.com` (el principal,
WordPress vivo, DNS migrado 10/7 a ns5/ns6.piensasolutions.com · rollback:
ns1/ns2.dns-parking.com) · `termycal.com` · `termycal.es` ·
`termosycalentadoresgranada.es` · `calderasgranada.es` (único con hosting WP contratado).

**Presupuesto aprobado:** setup €3.480 · mensual €200.
Equipo omnia: Henry Buenaño, Germán Borrello, Oliver Guerrero.

---

## 5. IDs del proyecto

| Qué | ID |
|---|---|
| Location | `oWWElLfvuaO9tDThqa6d` |
| Bot Conversation AI ("Termycal BOT") | `ZZB1BGZbmJDcYVuPe5sg` |
| ClickUp workspace / folder Termical | `90132832373` / `1000460000001977` |
| Drive (carpeta oficial, unidad Omnia › Clientes) | `1dyCmIhyVXa0YqaqijSjy31xLh5GJnof3` |

**Workflows** (carpeta Termical):

| Workflow | ID |
|---|---|
| PUENTE BOT → tag pide-presupuesto | `df39e466-9081-462f-95ab-417141b2f780` |
| PUENTE BOT → tag pide-visita | `b711063f-a139-4273-8f50-485d98a28a45` |
| PUENTE BOT → tag derivado-humano | `c731f3ee-9d27-46a1-b481-95d3eaa13acc` |
| BOT-DH · Aviso por derivación a humano | `51e5c379-8bae-43b1-a9a0-3c64766b160f` |
| BOT-FU · Inactividad 3 días | `7d3e7e58-5db8-4913-aac7-e674359a3595` |
| BOT-FU · Inactividad 5 días | `9fd39c86-de9e-43d4-bb7a-df2c62bb0d64` |
| LS01 · WhatsApp entrante | *(ver lista por API)* |
| LS02 · Formulario web · SP-N · SP-V · SP03 · SP04 · SP06 · AP01 · AP02-RBD · RBD 01-05 | *(ídem)* |

**Custom fields (contacto).** General: `fuente_contacto` (dropdown), `fecha_primer_contacto`.
Proforma: `tipo_servicio`, `tipo_aparato`, `litros_capacidad`, `paquete_interes`,
`valor_estimado` (Monetary), `direccion_servicio`, `detalle_trabajo`.
Oportunidad: `requiere_visita`, `estado_proforma`.

**Tags (exactos, minúsculas):** `lead-whatsapp` · `lead-web` · `pide-presupuesto` ·
`pide-visita` · `derivado-humano` · `aprobar-proforma` · `resena-solicitada` · `frio`

**Pipeline "Comercial Termical" (9 etapas):** Nuevo lead → Conversando → Visita agendada →
Proforma enviada → Presupuesto formal enviado → Aprobado → Trabajo agendado → Completado →
Cerrado

---

## 6. Decisiones de arquitectura (cerradas — no re-litigar)

1. **Bot:** Conversation AI (prompt + KB), NO Agent Studio. Arranque Suggestive →
   Auto-Pilot tras 1-2 semanas.
2. **El bot NO puede aplicar tags.** Se hace con 3 **workflows puente** de un nodo
   (`PUENTE BOT → tag …`) que el bot invoca desde sus Actions.
3. **Follow-ups por inactividad: el BOT pone el CUÁNDO, el WORKFLOW el QUÉ.**
   El Auto Follow-up del bot ("Contact Stopped Replying") cuenta 6 h / 3 días / 5 días y se
   detiene solo si el cliente responde — no se reconstruye ese contador en un workflow.
   El de 6 h va nativo ("Let AI Send The Message", dentro de la ventana de 24 h); los de 3 y
   5 días solo disparan su workflow, que manda la plantilla Meta. El Custom Message que
   exige la UI no molesta: fuera de las 24 h no se entrega. Sin guards: quien se cae en los
   primeros mensajes no llegó a tener tags que filtrar *(decisión Henry, 2/8)*.
4. **Proforma dual.** Flujo B (~80%): bot captura + tag `pide-presupuesto` → SP-N notifica →
   Alejandro añade `aprobar-proforma` → SP04 genera y envía. Flujo A: manual desde plantilla.
   **Trigger de envío SIEMPRE por TAG, nunca por etapa** + guard `estado_proforma`=enviada.
5. **AGENDADO 100% MANUAL.** El bot NUNCA agenda ni ve el calendario. Protege su ruta y su
   segunda agenda de Leroy Merlin. Visitas en rangos de 2 h; instalaciones bloquean
   mañana/día. Recordatorios 1 día + 2 h antes.
6. **IVA: precios "+ IVA".** La proforma muestra Base + IVA 21% + Total.
7. **Firma digital: SÍ.** El bot pide **fotos** del aparato y su ubicación.
8. **Aerotermia: NUNCA se estima** (2.000-3.000 €+). Solo termos eléctricos, calentadores
   de gas y calderas.
9. **Reseñas: sistema RBD** (snapshot importado 14/7). Encuesta 1-5 → 1-3 form privado +
   aviso interno · 4-5 → Google.
10. **Diagnóstico 45 €+IVA**, descontable si repara/sustituye en 1 mes.
11. **Telefonía FUERA** (número ES sin Twilio/LC Phone). Mitigación: buzón de voz → WhatsApp.
12. **FASE 2:** facturación + Verifactu · suma automática de extras por IA · agenda Leroy Merlin.
13. **Urgencia con riesgo** (olor a gas, fuga): derivación inmediata + pautas de seguridad.

---

## 7. Catálogo de precios

Fuente de verdad: **`kb-operador/kb_catalogo_precios.csv`** (124 filas).

| Familia | Estado |
|---|---|
| Calentadores de gas | ✅ 22 refs · aparato + instalación + extras, todo SIN IVA |
| Termos eléctricos | ✅ 79 refs (26 modelos, 6 marcas, 15-200 L) · SIN IVA · ⛔ **falta el precio de instalación** |
| Calderas de condensación | 🟡 10 refs **BLOQUEADAS** · el .ods dice "IVA incluido" y el PDF de extras "sin IVA" — sin confirmar |
| Aerotermia | Nunca se cataloga: siempre bajo presupuesto |

**El modelo de precio cambia por familia:** calentadores y termos = aparato + instalación +
extras por separado. **Calderas = el precio YA incluye instalación básica**, solo se suman
extras. Hay que decírselo al bot en la KB o inflará los estimados.

**Dato sospechoso pendiente:** PROVAI Andros Duo 100 L (135,85 €) sale más barato que su
propio 50 L y 80 L. Probable errata.

**Regla de mantenimiento:** cambio de precio = actualizar KB del bot **y** Products (2 sitios).

---

## 8. Protocolo de pruebas

- 1 prueba = 1 contacto nuevo, creado CON sus etiquetas ANTES de escribir.
- Verificar por API, nunca por el panel del contacto (cachea).
- El Registro de ejecución solo pinta el trigger de entrada: auditar desde el Creador.

---

## 9. Gestión

- Tareas y estado: ClickUp (folder Termical). Cada workflow tiene su tarea con la anatomía
  nodo a nodo y sus pendientes en comentarios fechados.
- Los hallazgos y decisiones se registran en la tarea correspondiente **con fecha**, y no se
  re-litigan.
- Documentos del cliente en Drive (carpeta oficial arriba). ⚠️ Existe una carpeta
  **duplicada** en la raíz del Drive personal (`17Q6zAuykhvZ1EiVynIkA6HuFyS5msxjG`) —
  pendiente de borrar.
- El `.env` NUNCA se commitea.

---

## 10. Estado y pendientes (25-ago-2026)

**Bloqueos externos:** WABA (S02) · templates Meta (S03, ya son 9-10) · usuario de Alejandro
en el CRM (destinatario de TODOS los avisos internos) · ficha de Google (GBP).

**Del cliente:** precio de instalación de termos · confirmar IVA de calderas · confirmar el
Andros Duo 100 L · fotos de trabajos para la web.

**Deuda técnica detectada en la auditoría del 25-ago** (script:
`gohighlevel-cli/scripts/reparar_reingreso_y_notificaciones.py`):
1. **Reingreso apagado en los 15 workflows construidos por API.** Con `allowMultiple` en
   OFF el contacto entra UNA VEZ EN SU VIDA: el cliente que vuelve a pedir presupuesto meses
   después es saltado en silencio. Los RBD (importados por UI) sí lo tienen ON — confirma que
   la causa es el PUT que resetea campos omitidos.
2. **BOT-DH y SP03 tienen la notificación con forma inventada** (`userType: "all"`, clave
   `subject`, sin anidar). Se guardan, se ven bien y **no avisan a nadie**. El molde válido
   está en SP-N y en los RBD.
3. Los **BOT-FU están publicados con los SMS placeholder dentro** — hoy fallan en silencio
   (no hay número); el día que se conecte WhatsApp mandarían lo que no toca.
