# PROYECTO TERMICAL (TÉRMYCAL) — Informe de traspaso / contexto completo
> **Propósito:** documento de handoff para continuar este proyecto en Claude Code. Contiene TODO el estado: decisiones, IDs, links, datos del cliente, sprint y pendientes. Fecha de corte: **7 jul 2026, ~18:00 CET**.
> **Sugerencia de uso:** colocar como `CLAUDE.md` (o incluir en él) en el repo/carpeta del proyecto.

---

## 0. REGLAS DE TRABAJO DEL PROYECTO (no negociables)
- **Idioma:** español neutro latinoamericano (nunca "vosotros" ni vocabulario peninsular en entregables internos; el bot del cliente SÍ habla castellano de España, tono andaluz-neutro).
- **Nomenclatura de marca:** "omnia" SIEMPRE en minúsculas · "ómibu" minúscula con acento.
- **NUNCA decir "GHL" o "Go High Level" de cara al cliente** → siempre "omnia CRM" o "el sistema/la plataforma".
- El sistema **nunca envía nada sin aprobación humana** ("la última palabra la tiene el humano" — Henry). Regla de arquitectura, no de estilo.

## 1. CLIENTE
| Dato | Valor |
|---|---|
| Nombre fiscal | Alejandro Rodríguez Medina |
| Negocio | TÉRMYCAL — termos, calentadores, calderas, aerotermos (unipersonal) |
| NIF | 75564623D |
| Dirección fiscal | Avda. Don Bosco, 38 · Granada 18007 |
| Teléfono / WhatsApp negocio | 644 962 421 (confirmado para conectar a WABA) |
| Email | termycalgranada@gmail.com |
| IBAN | ES30 2100 0944 6202 0021 8036 |
| Web actual | termosycalentadoresgranada.com — la web WordPress está VIVA (el "caído" del traspaso era falso; 106 reseñas Google integradas; alojada en Hostinger, IP 147.93.92.228 — cuenta del webmaster, sin acceso). ✅ DNS MIGRADO 10/7: se clonó la zona real en Piensa Solutions (A/www 147.93.92.228 · MX mx1/mx2.hostinger.es · SPF hostinger · google-site-verification) + los 6 registros del dominio de envío info.* (mailgun/LC), y se cambiaron los nameservers a ns5/ns6.piensasolutions.com. El DNS se gestiona ya en Piensa (Panel de Control → Entradas DNS, nombres FQDN completos). Rollback: ns1/ns2.dns-parking.com (zona Hostinger intacta). También posee termycal.com (con Y, no "termical.com"), termycal.es, termosycalentadoresgranada.es y calderasgranada.es (hosting WP en Piensa) |
| Zona | Granada capital + 20 km de radio |
| Canal | 100% B2C |
| Particularidad | Colaborador de Leroy Merlin (le agendan por software propio web NO integrable) |
| Problema raíz | Calidad de vida: madruga para facturas/presupuestos en Excel; pierde leads al no poder atender WhatsApp mientras instala |

**Contexto comercial:** cliente traído por Víctor/Samuel (ómibu). Equipo técnico omnia: Henry Buenaño, Germán Borrello, Oliver Guerrero.

## 2. PRESUPUESTO (APROBADO)
En EUR: **Núcleo €2.690** (CRM €500 + Agente IA €590 + Proforma €430 + Agendado €350 + Automatizaciones+formación €820) · **Adicionales €790** (voz €180, one-page €420, reseñas €190) · **Setup completo €3.480** · **Mensual €200** (mantenimiento €130 + IA €70).
Entregables del presupuesto: `presupuesto_termical.html` (HTML interactivo estilo omnia con calculadora modular y ROI) y `Termical_Presupuesto_Holder.md`.
⚠️ Se eliminó del presupuesto toda referencia a "llamada perdida→WhatsApp automático" (imposible: número ES sin Twilio/LC Phone) — sustituida por "notificación de lead caliente".

## 3. ESTADO GLOBAL
✅ **SISTEMA APROBADO POR EL CLIENTE** (reunión 7/7, Fathom: https://fathom.video/share/D-JMK_fKMbUhiUcqGGJ88m9h7zKHRy4-)
✅ Diseño técnico v2.0 cerrado · KB redactada · Catálogo calentadores recibido · ClickUp completo (7 listas, 24 tareas padre, 44 subtareas, 20 dependencias, asignaciones y sprint) · Docs en Drive · Diagramas Figma.
🏃 **SPRINT EN CURSO: 8 → 15 jul 2026** (arranque mañana desde el corte). Subcuenta en creación (se le pasaron los datos a Henry hoy).

## 4. DISEÑO TÉCNICO v2.0 — DECISIONES DE ARQUITECTURA (todas cerradas)
1. **Bot:** Conversation AI (prompt + KB), NO Agent Studio. Arranque **Suggestive** → Auto-Pilot tras 1-2 semanas. Voice notes ON, imágenes ON, wait 10-15s, máx 15 msgs.
2. **KB del bot = única fuente de precios para ESTIMADOS conversacionales**. ⚠️ REVISIÓN 13/7 (Henry): se crearon los 22 productos de calentadores en GHL Products para el elemento "lista de productos" de la plantilla D&C — así el flujo A (proforma manual) suma tipo Excel con IVA 21% automático (resuelve el hallazgo de auditoría sobre el cálculo de IVA). Flujo B sigue por merge fields. REGLA DE MANTENIMIENTO: cambio de precio = actualizar KB del bot + Products (2 sitios).
3. **Proforma dual:**
   - **Flujo B (~80%):** bot captura campos+email+**fotos** → tag `pide-presupuesto` → WF SP-N notifica resumen aprobable → Termical añade tag `aprobar-proforma` (2 taps app) → WF SP04 genera doc D&C y **envía por email automático**.
   - **Flujo A (bajo presupuesto/aerotermia/extras):** genera desde plantilla, edita, envía manual.
   - **Trigger de envío SIEMPRE por TAG, nunca por etapa** (anti-duplicados) + Guard IF `estado_proforma`=enviada.
4. **AGENDADO 100% MANUAL** (decisión del cliente 7/7): el bot NUNCA agenda ni accede al calendario. Tag `pide-visita` → WF SP-V: WA "en breves momentos te contactamos" + notificación. Calendarios solo registro manual: **Visitas rangos 2h** (10-12, 12-14, 16-18, 18-20), **Instalaciones** bloquea mañana/día. Motivo: protege su ruta y su 2ª agenda de Leroy Merlin. Recordatorios: **1 día + 2h antes**.
5. **IVA: precios "+ IVA"** (el cliente pasa precios sin IVA). La proforma muestra Base + IVA 21% + Total.
6. **Firma digital: SÍ** (cualquier teléfono; le vale como respaldo para arrancar trabajos).
7. **Bot pide FOTOS** del aparato/ubicación (quedan en la conversación, sin campo).
8. **Aerotermia: NUNCA se estima** (2.000-3.000€+); el bot solo estima termos eléctricos, calentadores de gas y calderas (posibles extras 100-200€, comunicar como orientativo).
9. **Reseñas: sistema RBD (snapshot importado 14/7, sustituye al AP02+PS01 diseñado)**: al completar el trabajo, el workflow "AP02-RBD · Envío del link de valoración" manda el trigger link → RBD 01-05 (publicados) gestionan: survey 1-5 con pipeline propio "Reseñas de Google", 1-3 → form privado de comentarios + aviso interno, 4-5 → Google, "no puedo entrar" → link directo, reseña recibida → won + aviso. Mantiene el principio encuesta-filtro. Adaptaciones pendientes anotadas en ClickUp (nodo FT1 huérfano en RBD 01, SMS→WhatsApp en RBD 04, link GBP). PS02: IA responde reseñas (la notificación de reseña nueva ya la cubre RBD 05).
10. **Diagnóstico: 45€+IVA** descontable de la factura si repara/sustituye en 1 mes. Retirada del viejo + desplazamiento INCLUIDOS en paquetes.
11. **Telefonía FUERA** (número ES sin Twilio/LC Phone). Mitigación coste cero: buzón de voz con locución → WhatsApp (el cliente la graba).
12. **FASE 2 fuera de alcance:** facturación automática + Verifactu (normativa ES, enero) · suma automática de extras por IA (por ahora mapeados en plantilla, los agrega Termical) · integración agenda Leroy Merlin.
13. **Urgencia con riesgo** (olor a gas, fuga): derivación inmediata a humano + pautas de seguridad.

### Custom Fields (Contacto)
- Folder **General**: `fuente_contacto` (dropdown: WhatsApp/Web/Llamada o visita/Reseña), `fecha_primer_contacto` (date).
- Folder **Proforma**: `tipo_servicio`, `tipo_aparato`, `litros_capacidad` (50/80/100/150), `paquete_interes` (single line), `valor_estimado` (**Monetary** — va en CONTACTO porque el merge de D&C lee contacto), `direccion_servicio`, `detalle_trabajo` (multi line opcional).
- Oportunidad: `requiere_visita`, `estado_proforma` (borrador/revisada/enviada).
- Excluidos a propósito: estimado_realizado_por, notas_internas (negocio unipersonal).

### Tags (exactos, minúsculas)
`lead-whatsapp` · `lead-web` · `pide-presupuesto` · `pide-visita` · `derivado-humano` · `aprobar-proforma` · `resena-solicitada` (+ `frio` de follow-ups)

### Pipeline "Comercial Termical" (9 etapas)
Nuevo lead → Conversando → Visita agendada → Proforma enviada → Presupuesto formal enviado → Aprobado → Trabajo agendado → Completado → Cerrado

### Plantilla D&C "Proforma Termical" (replica formato REAL de sus presupuestos)
Cabecera "Presupuesto Nº + fecha" · Emisor fiscal (custom values) · Cliente (merge) · Concepto (`paquete_interes` + `detalle_trabajo`) · Bloque "Sí se incluye / No se incluye" por paquete (texto fijo, viene del catálogo) · Base + IVA 21% + Total · Pagos: Tarjeta·Bizum·Efectivo·Financiación·Transferencia IBAN · Validez 15 días · Pie RGPD · **Firma digital**.

### Workflows (anatomía completa en las tareas ClickUp)
LS01 WhatsApp entrante (5 nodos) · LS02 Form web (3) · SP-N Notificación lead caliente (3) · **SP04 Envío automático proforma flujo B (8 nodos, CRÍTICO)** · SP-V Solicitud visita manual (4) · SP03 Citas confirmación+recordatorios (5) · SP06 Seguimiento post-proforma día 2+5 con guards de salida (8) · AP01 Trabajo agendado (4) · AP02+PS01 Cierre→encuesta-filtro→reseña (6) · PS02 Reputación IA (3).

### Validaciones críticas pre-go-live (S11)
1. ⚠️ **CRÍTICA:** acción "D&C: Send Document" respeta merge fields + email sale del dominio sin spam + guard anti-duplicados. **Si falla → todo opera en flujo A** (degradación elegante).
2. Captura de campos por el bot estable.
3. SP02 notas de voz: GHL manda audio como adjunto, no nota de voz nativa — validar en móvil real.
4. Firma digital desde móvil del cliente final.
5. Encuesta 1-5: captura de respuesta numérica para el IF.

## 5. CLICKUP — ESTRUCTURA COMPLETA (workspace 90132832373)
**Espacio:** GHL Team Latam · **Folder Termical:** `1000460000001977`
URL: https://app.clickup.com/90132832373/v/o/f/1000460000001977?pr=1000460000000699

### Miembros (user IDs para asignaciones)
- Henry Buenano: `111980811` (henry89dy@gmail.com)
- Germán Borrello: `180203721` (info@germanborrello.com)
- Oliver Guerrero: `89242515` (oliver.guerrero84@gmail.com)
- (Jaime Forero `111980812` — no participa en este proyecto)

### Listas (list_id)
| Lista | ID |
|---|---|
| 🏗️ 00 · Setup | 1000460000002931 |
| 🤖 01 · Bot Conversation AI | 1000460000002932 |
| 🔵 02 · Lead Sources | 1000460000002933 |
| 🟢 03 · Sales Pipeline | 1000460000002934 |
| 🔴 04 · Active Projects | 1000460000002935 |
| 🌟 05 · Reviews | 1000460000002936 |
| 🌐 06 · One-page Web | 1000460000002937 |

### Tareas padre (task_id) + SPRINT 8-15 jul (asignado · start→due)
| Tarea | ID | Asignado | Fechas |
|---|---|---|---|
| [S01] Subcuenta+dominio+correo | wdx6zenj47 | Henry | 8→9 jul |
| [S02] WhatsApp Business API | wdx6zenj4e | Germán | 9→9 |
| [S03] Templates Meta (URGENT) | wdx6zenj4k | Oliver | 9→10 |
| [S04] Custom Fields | wdx6zenj4v | Germán | 8→8 |
| [S05] Tags+Pipeline | wdx6zenj52 | Henry | 8→8 |
| [S06] Calendarios manuales | wdx6zenj54 | Oliver | 8→8 |
| [S07] Custom Values | wdx6zenj5a | Oliver | 8→8 |
| [S08] Formulario interno | wdx6zenj5j | Germán | 9→9 |
| [S09] Plantilla D&C+firma | wdx6zenj5p | Henry | 9→10 |
| [S10] KB (FAQs ✅ + catálogo ⛔) | wdx6zenj5t | Germán | 8→9 |
| [S11] Validaciones pre-go-live | wdx6zenj5u | Oliver | 14→15 |
| [BOT] Conversation AI (8 subtareas) | wdx6zenj5w | Henry | 10→11 |
| [LS01] WhatsApp entrante (5 subt.) | wdx6zenj71 | Oliver | 9→9 |
| [LS02] Formulario web (3 subt.) | wdx6zenj7x | Germán | 13→14 |
| [SP-V] Solicitud visita manual (4 subt.) | wdx6zenj8d | Oliver | 9→9 |
| [SP-N] Notificación lead caliente (3 subt.) | wdx6zenj8u | Germán | 9→9 |
| [SP04] Envío automático proforma (8 subt., URGENT) | wdx6zenj96 | Germán | 10→13 |
| [SP03] Citas (5 subt.) | wdx6zenjb0 | Henry | 10→13 |
| [SP06] Seguimiento post-proforma (8 subt.) | wdx6zenjba | Germán | 13→13 |
| [Flujo A] Proforma manual (procedimiento) | wdx6zenjby | Henry | 13→13 |
| [AP01] Trabajo agendado (4 subt.) | wdx6zenjc2 | Henry | 10→10 |
| [AP02+PS01] Cierre→encuesta→reseña (6 subt.) | wdx6zenjck | Oliver | 13→13 |
| [PS02] Respuesta IA a reseñas (3 subt.) | wdx6zenjd3 | Oliver | 14→14 |
| [WEB] One-page + baja WordPress (4 subt.) | wdx6zenjde | Oliver | 8→13 |

Subtareas (44 en total, formato skill "1 nodo = 1 subtarea" con `## Acción en GHL` + `## Contexto`). Rangos de IDs: BOT wdx6zenj5x→6v · LS01 wdx6zenj7a→7u · LS02 wdx6zenj82→8b · SP-V wdx6zenj8f→8r · SP-N wdx6zenj8y→93 · SP04 wdx6zenjak→ay · SP03 wdx6zenjb2→b9 · SP06 wdx6zenjbc→bw · AP01 wdx6zenjc4→ch · AP02 wdx6zenjcm→d2 · PS02 wdx6zenjd4→d8 · WEB wdx6zenjdh→dx.

### Dependencias creadas (20, tipo waiting_on: tarea ← bloqueante)
S02←S01 · S03←S02 · S09←S04 · S09←S07 · S08←S04 · BOT←S02 · BOT←S10 · SP04←S09 · SP04←S01 · SP03←S03 · SP03←S06 · SP06←S03 · AP02←S03 · WEB←S01 · LS02←WEB · PS02←AP02 · FlujoA←S09 · FlujoA←S08 · S11←SP04 · S11←BOT

### Comentario relevante
Tarea S10 (wdx6zenj5t) tiene comentario `1000460000029951` con el resumen del catálogo de calentadores recibido.

## 6. GOOGLE DRIVE (cuenta conectada: german.borrello@omibu.com)
**Carpeta OFICIAL:** Termycal en unidad compartida **Omnia › Clientes**
📁 https://drive.google.com/drive/folders/1dyCmIhyVXa0YqaqijSjy31xLh5GJnof3 (folder_id `1dyCmIhyVXa0YqaqijSjy31xLh5GJnof3`, parent Clientes `111n6it5_CwvT2v8JGQj9YGdb5XJjlgAx`, unidad `0AMII9XPqxaqgUk9PVA`)

| Doc | ID |
|---|---|
| Termical — Resumen Ejecutivo | 1U3eNluFcVlShc1vdEDgQgOJ9x1scnu-Ty3lzUfs5M3k |
| Termical — Diseño Técnico GHL v2.0 | 1bAEBJcclNrUJkOxctsG_IxvhFqq5mKWGA8U_Oma6EBY |
| Termical — Knowledge Base del Bot | 1Zo4u1FUmoHLjSTwGhqleNyCRNmjk0TmN6ENW0Fr0-LA |
| Termical — Catálogo de Precios | 1QJXcBTUcPyDFCGgJH0civgAUPXlKG0yKDJVqhHGpzxY |

⚠️ **PENDIENTE menor:** existe carpeta **Termycal DUPLICADA** en la raíz del Drive personal (`17Q6zAuykhvZ1EiVynIkA6HuFyS5msxjG`) con copias de los 4 docs — **borrar manualmente** (la buena es la de Clientes).

## 7. FIGMA (FigJam, generados con generate_diagram)
1. **"Termical - Flujo APROBADO por el cliente - v4 final"** — versión cliente: entradas, atención 24/7 con rama de urgencia, proforma B/A con firma, agenda manual, encuesta-filtro. Colores: azul=sistema, naranja=Termical, gris=cliente final, rojo=urgencia.
2. **"Termical - Arquitectura tecnica v3 - APROBADA"** — versión equipo: setup, bot, todos los WFs con triggers/nodos. Colores: morado=trigger, azul=acción, amarillo=condición, naranja=humano, gris=setup, verde=recibido/listo, rojo=bloqueado/validar.
(Los enlaces viven en la cuenta Figma del usuario; buscar por esos nombres. Versiones anteriores v1-v3 del flujo cliente y v1-v2 del técnico quedaron obsoletas.)

## 8. CATÁLOGO DE PRECIOS — FAMILIA CALENTADORES DE GAS (recibida 7/7 por email+PDF)
**Regla: TODOS los precios SIN IVA** → comunicar "+ IVA". Modelo: `Aparato + Instalación básica + Extras` → todo +IVA.

**Aparatos:** Ariston Next Evo X SFT estanco 11L 318,18€ / 16L 418,18€ · HTW LowNox estanco 12L 274,91€ · Bosch Therm 3600 S estanco 11L 389,11€ · Ariston Akros R X atmosférico 11L 245,98€ · Bosch T 4204 atmosférico 10L 335,02€.
**Instalación:** estanco 160€ · atmosférico 110€ · gas normativa RITE 130€ · enchufe con canaleta 55€.
**Extras (12):** 1m evacuación concéntrico 60/100 21,60€ · ½m 15,60€ · codos 90°/45° 15,60€ · abrazadera 5€ · latiguillos 8€ · grifos escuadra 14€ · grifo recto 6€ · goma butano 10€ · regulador gas 15€ · embellecedor 2€ · toma análisis combustión 15€.
**Paquetes orientativos para el bot:** estanco 11L instalado ≈ **478€+IVA** · estanco 16L ≈ **578€+IVA** · atmosférico 11L ≈ **356€+IVA**.
**Pendiente:** confirmar los 2-3 "estrella" de la familia · faltan familias: termos eléctricos, calderas (aerotermia = siempre bajo presupuesto).

## 9. KB DEL BOT (v2, redactada, lista para cargar)
9 FAQs: diagnóstico 45€+IVA descontable 1 mes · horario dinámico vía ficha Google (nunca promete horario fijo) · pagos (efectivo, Bizum, tarjeta, transferencia) · **financiación La Caixa 0% TIN/TAE, comisión apertura: 3m-2% / 6m-3,5% / 12m-4,5% / 18m-6,5% / 24m-8,5% / 36m-11%** + lista de documentación · garantías (3 meses reparación / fabricante aparatos) · reparaciones (intenta in situ, a veces recambios; sin proforma previa, solo visita) · zona 20 km · fotos · regla nunca-agenda. Reglas: urgencia olor a gas → derivación inmediata; nunca envía proforma; nunca cierra precio con extras.

## 10. ARCHIVOS GENERADOS (en el entorno claude.ai — /mnt/user-data/outputs/; NO accesibles desde Claude Code: copiarlos al repo)
- `Termical_Diseno_Tecnico_GHL_v1.md` — **v2.0 FINAL** (fuente de verdad técnica; también en Drive)
- `Termical_KB_Bot_v1.md` — v2 (también en Drive)
- `Termical_Catalogo_Precios.md` — calentadores de gas (también en Drive)
- `presupuesto_termical.html` — presupuesto interactivo aprobado (HTML omnia con calculadora)
- `Termical_Presupuesto_Holder.md` — presupuesto formato texto por partidas
- `Termical_Roadmap_Omnia.md` — roadmap inicial (parcialmente superado por v2.0)
- `Termical_Checklist_Discovery.md` — checklist de discovery (ya ejecutado, histórico)
- `formulario_reunion_termical.html` — formulario interactivo usado en la reunión del 7/7 (histórico)
**Material del cliente recibido (adjuntos email 5/7 y 7/7):** 3 presupuestos reales PDF (formato replicado en plantilla) · Logo.rar (pack completo: SVG/PNG/AI/EPS/PSD, RGB+CMYK, versiones +/-) · Tabla de Financiación PDF · Calentadores_de_gas.pdf.

## 11. HISTORIAL DE REUNIONES
- **15/6** Samuel+Víctor definen el caso ("el producto es siempre igual: termo 80/100/120L + instalación"; "grábate un buzón de voz").
- **16/6** equipo omnia (Henry, Germán, Oliver) — Henry: "estimado por una rama, formal por otra, última palabra humano".
- **5/7** email cliente: logo, 3 presupuestos reales, financiación, respuestas FAQs.
- **7/7** reunión de aprobación (Fathom link arriba): TODO aprobado salvo agendado→manual. Decisiones IVA, firma, fotos, encuesta-filtro, Verifactu→fase 2.
- **7/7** email cliente: PDF catálogo calentadores de gas.

## 12. PENDIENTES / PRÓXIMAS ACCIONES
**Del cliente (reclamar):**
1. ⛔ Accesos DNS del dominio (bloquea correo del dominio, publicación web).
2. ⛔ Familias restantes del catálogo: termos eléctricos (la más vendida), calderas.
3. Confirmar 2-3 calentadores "estrella" · fotos de trabajos para la web.

**Del equipo (sprint 8-15 jul):**
- Día 1 (mié 8): S04, S05, S06, S07 (sin bloqueos) + reclamar DNS.
- S03 Templates Meta cuanto antes (aprobación Meta 24-48h; vence vie 10).
- Validación S11-1 (Send Document + merge) ANTES de activar flujo B.
- Subcuenta: datos ya entregados a Henry (Business Name TÉRMYCAL, timezone Europe/Madrid, "client's account", SIN sample data).
- Onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla (él no pasa claves) + grabación buzón de voz + formación calendarios (bloqueos, estacionalidad).

**Housekeeping:**
- Borrar carpeta Drive duplicada de la raíz (`17Q6zAuykhvZ1EiVynIkA6HuFyS5msxjG`).

## 13. CAPACIDADES/CONEXIONES USADAS EN ESTE CHAT (para replicar en Claude Code vía MCP)
- **ClickUp MCP** (crear listas/tareas/subtareas/comentarios/dependencias/updates, miembros) — workspace 90132832373.
- **Google Drive MCP** (cuenta german.borrello@omibu.com; crear carpetas/docs, search).
- **Figma MCP** (generate_diagram con Mermaid → FigJam).
- Skills de usuario relevantes: `ghl-clickup-task-builder` (formato 1 nodo=1 subtarea), `ghl-onboarding-mapper`, `ghl-cotizador`, `generador-presupuestos` (HTML estilo omnia).

---
*Fin del informe. Con este documento + los 4 docs de Drive + el folder de ClickUp, cualquier sesión nueva tiene el 100% del contexto.*
