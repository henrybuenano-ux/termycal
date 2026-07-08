# Auditoría del proyecto Termical en ClickUp — 8 jul 2026

Auditoría automatizada de las 85 tareas del folder Termical (ClickUp) contra el diseño técnico v2.0 (`CLAUDE.md`) y la mecánica real de GoHighLevel.
Método: 10 auditores independientes (7 por lista + dependencias/calendario + viabilidad GHL + cobertura); cada hallazgo verificado por un agente adversarial contra las fuentes primarias.

**Resultado: 96 hallazgos → 95 confirmados, 1 refutado** (4 críticos · 44 mayores · 39 menores · 8 sugerencias).


## 🔴 Críticos

### 1. Falta el nodo de espera de respuesta del cliente entre la encuesta y el IF: el router no tiene de dónde leer la nota
**Área:** 🔴 04 · Active Projects — AP02+PS01 · **Tareas:** wdx6zenjck [AP02 + PS01] Cierre → encuesta-filtro → reseña, wdx6zenjcx Send WhatsApp: encuesta de satisfacción 1-5 (Template), wdx6zenjcz IF nota: 1-3 → interno / 4-5 → reseña

La estructura de AP02+PS01 encadena el nodo 3 (Send WhatsApp encuesta) directamente con el nodo 4 (IF nota). En GHL la acción Send Message no captura la respuesta del contacto en ningún campo ni variable: sin un paso 'Wait → Contact Reply' (con timeout y rama de salida) el IF se evalúa milisegundos después del envío, con la condición vacía, y TODOS los contactos caen por una sola rama. Si caen por la rama 4-5, cada cliente —incluidos los insatisfechos— recibe el link público de reseña de Google, anulando exactamente la regla no negociable de encuesta-filtro. La subtarea del envío incluso admite el hueco al escribir 'Captura: Respuesta numérica 1-5 a un campo/variable para el IF' sin decir QUÉ mecanismo de GHL hace esa captura, porque no existe como parte de la acción de envío.

> Evidencia: Tarea wdx6zenjck, tabla de nodos: '3 | Send WhatsApp | Send WhatsApp: encuesta de satisfacción 1-5 (Template) | 4 | Router IF | IF nota: 1-3 → interno · 4-5 → reseña' (sin nodo de espera de respuesta entre ambos). Tarea wdx6zenjcx: 'Captura | Respuesta numérica 1-5 a un campo/variable para el IF'. CLAUDE.md §4 decisión 9: 'Reseñas: encuesta-filtro 1-5 antes del link' y validación S11-5: 'Encuesta 1-5: captura de respuesta numérica para el IF'.

**Recomendación:** Añadir una subtarea/nodo 'Wait: Contact Reply' (con timeout, p. ej. 3 días, y rama de no-respuesta → End) entre el envío y el IF, y definir el mecanismo concreto de captura: template Meta con botones quick-reply 1-5 y evaluación sobre el texto exacto de la respuesta (o workflow auxiliar con trigger Customer Replied que escriba la nota en un campo). Validarlo en S11-5 ANTES de activar el workflow.

**Matiz del verificador:** Dos matices que refuerzan y acotan el hallazgo. (a) El fallo es más grave que la formulación condicional del auditor ('Si caen por la rama 4-5...'): por el diseño del IF de wdx6zenjcz (Rama SÍ=1-3, Rama NONE=4-5), la condición vacía manda a TODOS los contactos por la rama else 4-5 de forma determinística — el envío del link de reseña a insatisfechos no es un riesgo, es el comportamiento garantizado del diseño actual. (b) Existe un colchón parcial que el hallazgo no menciona: la propia subtarea wdx6zenjcx remite a la validación S11-5 (programada 14-15 jul, antes del go-live), así que el equipo es consciente de que algo hay que validar; sin embargo, el fallback documentado en S11 ('Botones/opciones en lugar de número libre') NO corrige el hueco estructural — los botones quick-reply tampoco alimentan el IF sin un nodo Wait for Reply o un workflow auxiliar con trigger Customer Replied — por lo que apunta al problema equivocado (parsing de texto libre vs. ausencia total de captura) y el retrabajo es seguro. La severidad crítica se sostiene bajo el criterio 'si se implementa tal cual rompe el sistema'; como mucho podría argumentarse que no bloquea el go-live global (el módulo reseñas es un adicional de €190 y podría lanzarse desactivado), pero anula una regla de diseño cerrada (decisión 9) con daño reputacional directo al cliente.

### 2. El bot no puede 'aplicar tags' desde el prompt: ninguna tarea configura la acción real que dispara toda la arquitectura de workflows
**Área:** 01 Bot Conversation AI + 03 Sales Pipeline — mecánica de tags · **Tareas:** wdx6zenj69, wdx6zenj6m, wdx6zenj8f, wdx6zenj8y

Toda la arquitectura (SP-N, SP-V y por cadena SP04) se dispara EXCLUSIVAMENTE por los tags pide-presupuesto / pide-visita / derivado-humano que 'aplica el bot'. Pero en GHL, Conversation AI no ejecuta instrucciones escritas en el texto del prompt: solo ejecuta Actions configuradas explícitamente, y las disponibles son 'Add Contact Info' (actualizar campos de contacto), 'Trigger a Workflow' y 'Appointment Booking'. NO existe una acción nativa 'Add Tag' en el bot; la documentación oficial de HighLevel indica que añadir tags se hace vía la acción 'Trigger Workflow' que lanza un workflow que aplica el tag. Ni las subtareas del BOT ni las de SP-N/SP-V configuran esas Actions ni crean los workflows puente. Implementado tal cual (instrucción en el prompt), los tags nunca se aplican y ningún workflow del pipeline se activa: el sistema completo queda inerte aunque el bot converse perfectamente.

> Evidencia: wdx6zenj69 (Prompt — Objetivo): 'Flujo 2 · Pide proforma | Capturar: … → aplicar tag pide-presupuesto' y 'Los tags son los disparadores de los workflows SP-N y SP-V'. wdx6zenj6m: 'Al completar captura | Aplicar tag pide-presupuesto'. wdx6zenj8f: 'El bot aplica este tag en 3 casos…'. Ninguna subtarea menciona las Conversation AI Actions.

**Recomendación:** Añadir a [BOT] una subtarea explícita: configurar en Conversation AI las Actions 'Trigger Workflow' por intención (proforma / visita / derivado-humano) apuntando a 3 mini-workflows que apliquen el tag exacto correspondiente, y 'Add Contact Info' para la captura de campos. Incluir en S11-2 la validación de que el bot dispara esas acciones de forma estable antes de pasar a Auto-Pilot.

**Matiz del verificador:** Dos matices que no invalidan el hallazgo: (a) la parte de captura de campos SÍ está planificada — wdx6zenj6m configura "Bot Goals / captura de datos" (equivalente funcional de la Action "Update Contact Fields"/"Add Contact Info"), así que lo verdaderamente ausente es el mecanismo de tags (Actions "Trigger a Workflow" + los 3 mini-workflows puente que apliquen pide-presupuesto / pide-visita / derivado-humano), no toda la capa de Actions; (b) el fallo probablemente NO llegaría silencioso al go-live: la subtarea de pruebas wdx6zenj6v lista explícitamente "tag pide-visita" y "tag pide-presupuesto" como resultados esperados de los escenarios en Suggestive, por lo que el equipo lo detectaría en el rodaje — pero detectarlo no lo resuelve: el mecanismo no existe en ninguna tarea del folder y su construcción sería trabajo no planificado en medio del sprint (BOT vence 11 jul, S11 14-15 jul), con lo que la severidad crítica sigue siendo defendible (como mínimo mayor si se asume que las pruebas lo cazan a tiempo). Nota adicional coherente con el hallazgo: el tag derivado-humano ni siquiera tiene workflow consumidor en el folder, lo que refuerza que la mecánica bot→tag quedó sin diseñar.

### 3. El campo estado_proforma, del que depende el guard anti-duplicados de SP04, no lo crea ninguna tarea de setup
**Área:** Sales Pipeline · SP04 (completitud / dependencias) · **Tareas:** wdx6zenj96 [SP04], wdx6zenjam Guard IF: estado_proforma = enviada → STOP, wdx6zenjar Update Field: estado_proforma = enviada, wdx6zenj4v [S04] (referencia cruzada)

SP04 (workflow CRÍTICO) usa estado_proforma en sus nodos 2 (Guard IF) y 4 (Update Field), y su descripción lo lista como dependencia de S04. Pero la tarea S04 'Custom Fields — folders General + Proforma' NO incluye estado_proforma en ninguna de sus dos tablas (General: fuente_contacto, fecha_primer_contacto; Proforma: tipo_servicio, tipo_aparato, litros_capacidad, paquete_interes, valor_estimado, direccion_servicio, detalle_trabajo), y S05 (Tags+Pipeline) tampoco lo crea. Si el sprint se ejecuta tal cual está escrito, el 10-jul Germán no podrá configurar el guard ni el update porque el campo no existirá, bloqueando el pilar anti-duplicados del flujo B (regla no negociable: trigger por tag + guard estado_proforma) y la validación S11-1 que condiciona el go-live.

> Evidencia: SP04 (wdx6zenj96): 'Dependencias: S09 Plantilla D&C creada y validada (S11-1 CRÍTICA) · S04 campo estado_proforma · Correo del dominio operativo'. S04 (wdx6zenj4v) enumera los 9 campos de sus folders General y Proforma y estado_proforma no aparece en ninguno. CLAUDE.md: 'Trigger de envío SIEMPRE por TAG... + Guard IF estado_proforma=enviada'.

**Recomendación:** Añadir a la descripción de S04 (o crear subtarea) la creación explícita de estado_proforma (valores: borrador/revisada/enviada) y de requiere_visita, indicando el objeto donde viven, y formalizar la dependencia ClickUp SP04←S04 (hoy solo existen SP04←S01 y SP04←S09).

**Matiz del verificador:** Dos matices. (a) Origen del hueco: CLAUDE.md §4 ubica estado_proforma y requiere_visita a nivel de OPORTUNIDAD ("Oportunidad: requiere_visita, estado_proforma (borrador/revisada/enviada)"), mientras S04 se autolimita a campos de CONTACTO; por eso ninguna tarea es dueña de los campos de oportunidad. Pero las propias subtareas de SP04 los tratan como campo de CONTACTO (wdx6zenjam: "Condition object: Contact"; wdx6zenjar: "Update Contact Field"), contradiciendo a CLAUDE.md. Al corregir S04 hay que decidir y documentar el objeto: contacto es lo coherente con las subtareas y lo más práctico en GHL (el trigger es Contact Tag Added y las acciones ya escritas son de contacto). (b) Precisión menor: "Germán no podrá configurar el guard" exagera un poco — en GHL un custom field se crea ad hoc en minutos; el riesgo real es que se cree improvisado con valores u objeto distintos a los diseñados (borrador/revisada/enviada) o que el guard se omita, rompiendo el anti-duplicados y la validación S11-1. El fondo del hallazgo (ningún setup crea el campo, dependencia SP04←S04 inexistente) es correcto.

### 4. S04 omite los custom fields de Oportunidad (requiere_visita y estado_proforma), incluido el campo del guard obligatorio de SP04
**Área:** COMPLETITUD — 00 · Setup · **Tareas:** wdx6zenj4v [S04] Custom Fields

S04 solo crea campos de CONTACTO en los folders General y Proforma. El diseño define además dos campos a nivel de Oportunidad: requiere_visita y estado_proforma (borrador/revisada/enviada). estado_proforma es el guard anti-duplicados del envío de proforma — regla no negociable del proyecto — y ninguna otra tarea de Setup lo crea. Si el setup se ejecuta tal cual, cuando se construya SP04 (10-13 jul, tarea URGENT y crítica) el campo del guard no existirá: o el workflow no se puede montar según especificación o se monta sin guard, con riesgo de proformas duplicadas al cliente final.

> Evidencia: CLAUDE.md §4: "Oportunidad: `requiere_visita`, `estado_proforma` (borrador/revisada/enviada)" y "Trigger de envío SIEMPRE por TAG, nunca por etapa (anti-duplicados) + Guard IF `estado_proforma`=enviada". La tarea S04 solo lista "Folder \"General\"" y "Folder \"Proforma\" (los que mergea el documento)" — ningún campo de oportunidad aparece.

**Recomendación:** Añadir a S04 (vence 8 jul) la creación de estado_proforma (dropdown: borrador/revisada/enviada) y requiere_visita. Validar además que el guard sea evaluable desde un workflow disparado por tag (contexto de contacto en GHL): si el IF no expone campos de oportunidad en ese contexto, crear estado_proforma a nivel de contacto y documentarlo en SP04 y S11-1.

**Matiz del verificador:** Dos matices. (a) El hallazgo es incluso más sólido de lo reportado: SP04 declara textualmente la dependencia "S04 campo estado_proforma", prueba interna de que S04 era la tarea responsable de crearlo. (b) Sobre el impacto: existe red de seguridad parcial — S11-1 valida el ciclo completo del guard (tag → envío → estado → etapa) antes de activar el flujo B, con degradación elegante a flujo A — por lo que el escenario más probable no es "proformas duplicadas al cliente final" sino bloqueo/retrabajo del flujo B en plena construcción de SP04 (10-13 jul); la severidad crítica se sostiene porque tal cual está escrito SP04 no puede montarse según especificación. Nota menor: requiere_visita no lo consume ningún workflow del sprint (SP-V dispara por tag pide-visita), así que su omisión es secundaria frente a estado_proforma.


## 🟠 Mayores

### 5. El guard '¿existe appointment en calendario X?' no es configurable como condición IF/Else en GHL desde un trigger de pipeline stage
**Área:** 🔴 04 · Active Projects — AP01 · **Tareas:** wdx6zenjc7 Guard IF: ¿cita creada en calendario Trabajos?

En GHL, un workflow disparado por Pipeline Stage Changed no tiene ningún appointment en contexto, y las condiciones del IF/Else (campos de contacto, tags, campos de oportunidad) no incluyen 'el contacto tiene cita en el calendario X'. Los filtros de appointment solo están disponibles en workflows disparados por eventos de cita. Tal como está descrito, el técnico no puede montar el nodo 2 de AP01: hace falta un mecanismo indirecto.

> Evidencia: Tarea wdx6zenjc7: 'Action type | IF / Else · Condition | ¿Existe appointment asociado en calendario Trabajos?' con trigger declarado en wdx6zenjc4: 'Trigger | Opportunity Stage Changed'.

**Recomendación:** Rediseñar el guard con un mecanismo real: un workflow auxiliar con trigger 'Customer Booked Appointment' (calendario Instalaciones) que marque un campo o tag (p. ej. `cita_instalacion` = sí), y que el IF/Else de AP01 evalúe ese campo/tag; alternativamente invertir el diseño y disparar la confirmación desde el propio Appointment Booked. Documentarlo en la subtarea antes del 10 jul.

**Matiz del verificador:** Dos matices: (1) la recomendación menciona 'calendario Instalaciones', pero según S06 (wdx6zenj54) el calendario se llama 'Trabajos / instalaciones', así que la referencia de la subtarea a 'calendario Trabajos' es coherente con el proyecto — solo hay que usar el nombre exacto al implementar; (2) si se adopta el workaround del tag/campo (p. ej. `cita_instalacion` = sí), hay que prever el reseteo del flag al cerrar cada trabajo, porque un cliente repetidor conservaría el tag de una instalación anterior y el guard daría un falso 'SÍ' en el siguiente trabajo. Además, la variante de 'invertir el diseño' (confirmar desde Appointment Booked) ya está parcialmente cubierta por SP03 (confirmación + recordatorios al crear la cita), por lo que la solución más limpia es mantener AP01 solo como detector de olvido evaluando el flag.

### 6. La confirmación WhatsApp de AP01 es texto libre sin plantilla Meta: fuera de la ventana de 24h no se entregará
**Área:** 🔴 04 · Active Projects — AP01 · **Tareas:** wdx6zenjch Send WhatsApp: confirmación al cliente (rama SÍ)

El paso a 'Trabajo agendado' ocurre normalmente días después del último mensaje del cliente (firma la proforma, Termical lo llama por teléfono para cerrar fecha y mueve la tarjeta). Con WABA, un mensaje de formato libre fuera de la ventana de 24h desde el último mensaje entrante del cliente es rechazado por Meta: la confirmación fallaría silenciosamente. Las subtareas equivalentes de AP02 sí especifican 'Template Meta', pero esta no, y S03 solo contempla plantillas de 'encuesta + link reseña', así que no hay template previsto para esta confirmación.

> Evidencia: Tarea wdx6zenjch: 'Action type | Send Message → WhatsApp | Texto | "¡Genial, {{First Name}}! Queda confirmado tu trabajo..."' (sin mención a template), frente a wdx6zenjcx: 'Send Message → WhatsApp · Template Meta "encuesta satisfacción"'. Tarea wdx6zenjck, dependencias: 'S03 Templates Meta (encuesta + link reseña)'.

**Recomendación:** Añadir una plantilla Meta de 'confirmación de trabajo agendado' al alcance de S03 (urgente: la aprobación de Meta tarda 24-48h y S03 vence el 10 jul), especificarla en wdx6zenjch y crear la dependencia AP01←S03.

**Matiz del verificador:** La evidencia del auditor sobre S03 es imprecisa: S03 no contempla solo "encuesta + link reseña" (eso es solo la nota parentética en la sección Dependencias de AP02, wdx6zenjck); S03 lista 7 templates: confirmación de cita día+rango (SP03), recordatorios 1 día y 2h (SP03), seguimientos día 2 y 5 (SP06), encuesta 1-5 y agradecimiento+link reseña (AP02+PS01). El problema real es que ninguno de los 7 está asignado a AP01. Matiz adicional a la recomendación: el template #1 "Confirmación de cita (día + rango horario)" es casi idéntico en contenido al mensaje de AP01 ({{fecha}} + franja {{rango}}), por lo que puede bastar con reutilizarlo/adaptarlo para AP01 en lugar de crear un template nuevo — pero sigue siendo necesario especificarlo en wdx6zenjch, ampliar la columna "Uso" en S03 y crear la dependencia AP01←S03.

### 7. Merge fields {{fecha}} y {{rango}} inexistentes: sin appointment en contexto GHL no puede rellenar la fecha/franja de la cita
**Área:** 🔴 04 · Active Projects — AP01 · **Tareas:** wdx6zenjch Send WhatsApp: confirmación al cliente (rama SÍ)

El texto de confirmación usa los placeholders {{fecha}} y {{rango}}, que no son merge fields de GHL. Los merge fields de cita ({{appointment.start_time}}, etc.) solo se resuelven en workflows disparados por eventos de appointment; en este workflow (trigger Pipeline Stage Changed) no hay cita en contexto, así que el cliente recibiría el texto con los placeholders literales o vacíos. El propósito del mensaje —confirmar día y franja— no es alcanzable con la mecánica descrita.

> Evidencia: Tarea wdx6zenjch: 'Texto | "¡Genial, {{First Name}}! Queda confirmado tu trabajo. Te esperamos el {{fecha}} en la franja {{rango}}. Nos vemos 🔧"' con trigger de wdx6zenjc4 'Opportunity Stage Changed'.

**Recomendación:** Si se adopta el rediseño del guard (workflow auxiliar sobre Appointment Booked en Instalaciones), enviar la confirmación desde ese workflow donde sí existen los merge fields de cita ({{appointment.start_time}}); si no, reescribir el mensaje sin fecha/franja o copiarlas a campos custom al crear la cita.

**Matiz del verificador:** Matiz que refuerza el hallazgo: el mismo texto usa {{First Name}}, que tampoco es un merge field válido de GHL (la sintaxis correcta es {{contact.first_name}}), así que el mensaje tiene tres placeholders problemáticos, no dos. Nota sobre la recomendación: si se opta por copiar fecha/franja a campos custom del contacto al crear la cita, eso añade trabajo manual en un flujo pensado como red de seguridad automática; la opción más limpia es la primera (enviar la confirmación desde un workflow con trigger Appointment Booked en el calendario Instalaciones/Trabajos, donde {{appointment.start_time}}/{{appointment.end_time}} sí resuelven).

### 8. La condición del IF ('Valor de la encuesta') no referencia ningún campo existente y el diseño no define dónde se guarda la nota
**Área:** 🔴 04 · Active Projects — AP02+PS01 · **Tareas:** wdx6zenjcz IF nota: 1-3 → interno / 4-5 → reseña

La subtarea del router dice solo 'Condition: Valor de la encuesta', pero los custom fields del diseño (fuente_contacto, fecha_primer_contacto, tipo_servicio, tipo_aparato, litros_capacidad, paquete_interes, valor_estimado, direccion_servicio, detalle_trabajo, requiere_visita, estado_proforma) no incluyen ningún campo para la nota de la encuesta, y S04 no lo crea. Aunque se resuelva la captura de la respuesta, el técnico no tiene ningún campo que seleccionar en el IF/Else: la instrucción es inejecutable tal cual.

> Evidencia: Tarea wdx6zenjcz: 'Condition | Valor de la encuesta' (sin nombre de campo). CLAUDE.md §4 'Custom Fields (Contacto)' — la lista completa no contiene ningún campo de nota/encuesta.

**Recomendación:** Definir un custom field explícito (p. ej. `nota_encuesta`, numérico o dropdown 1-5), añadirlo al alcance de S04 y nombrarlo en las subtareas wdx6zenjcx (captura), wdx6zenjcz (condición del IF) y wdx6zenjd1 (merge field {{nota}} de la notificación interna); o si se opta por botones quick-reply, documentar la evaluación por texto de respuesta.

**Matiz del verificador:** Matiz: el diseño no ignora del todo el problema — la propia wdx6zenjcx y la validación S11-5 ya prevén el fallback a botones/opciones si la captura numérica falla. Pero ese fallback cubre la CAPTURA de la respuesta, no la DEFINICIÓN del almacenamiento: aunque la captura funcione, sigue sin existir campo que escribir ni que seleccionar en el IF, y el merge {{nota}} de wdx6zenjd1 queda sin fuente. La recomendación del auditor (crear p. ej. nota_encuesta, añadirlo al alcance de S04 y nombrarlo en wdx6zenjcx, wdx6zenjcz y wdx6zenjd1, o documentar la evaluación por texto/botones) es correcta y accionable.

### 9. No hay mecanismo configurado para aplicar los tags pide-visita y derivado-humano: solo pide-presupuesto tiene acción en Bot Goals
**Área:** Bot IA — Bot Goals / Prompt Objetivo · **Tareas:** wdx6zenj6m — Bot Goals: captura de campos a custom fields, wdx6zenj69 — Prompt — Objetivo (flujos y reglas de derivación)

En GHL Conversation AI el texto del Objective/prompt NO ejecuta acciones: los tags se aplican mediante Bot Goals (acciones al cumplir goal) o mediante un workflow disparado por el goal. La subtarea de Bot Goals solo configura una acción de tag para pide-presupuesto ('Al completar captura → Aplicar tag pide-presupuesto'), mientras que el prompt Objetivo declara que los flujos 3 (visita/avería), 4 (aerotermia) y 5 (pide humano) terminan aplicando pide-visita o derivado-humano, sin que exista ningún nodo/subtarea que configure esas acciones. Si se implementa tal cual está escrito, el bot 'dirá' que deriva pero los tags nunca se aplicarán y los workflows SP-V (visita) y la derivación a humano jamás se dispararán.

> Evidencia: wdx6zenj6m: 'Al completar captura | Aplicar tag `pide-presupuesto`' (única acción de tag configurada). wdx6zenj69: 'Flujo 3 · Visita/avería | NUNCA agendar… → tag `pide-visita`' y 'Flujo 5 · Pide humano / caso complejo | Tag `derivado-humano` + no insistir'. CLAUDE.md: 'Los tags son los disparadores de los workflows SP-N y SP-V' y decisión 4: 'Tag `pide-visita` → WF SP-V'.

**Recomendación:** Ampliar la subtarea de Bot Goals (o crear subtareas nuevas) con goals/acciones explícitos: goal 'solicita visita/avería/aerotermia' → acción Add Tag pide-visita; goal 'pide humano / caso complejo / urgencia' → acción Add Tag derivado-humano (o Trigger Workflow equivalente). Añadir su verificación al gate de pruebas.

**Matiz del verificador:** Matiz sobre el impacto del flujo 5: el detalle afirma que "la derivación a humano jamás se disparará", pero en el diseño actual NO existe ningún workflow disparado por `derivado-humano` (ninguna de las 85 tareas del folder lo consume como trigger); el efecto real de no aplicar ese tag es perder el marcador en el contacto y la trazabilidad del "no insistir", no dejar de disparar un workflow. El impacto fuerte y verificable es el de `pide-visita` (flujos 3 y 4), que deja SP-V sin disparador. De hecho, la ausencia de un consumidor para `derivado-humano` (ni SP-N ni ningún WF notifican al humano cuando el bot deriva) podría ser un hueco de diseño adicional que la recomendación del auditor (goal → Add Tag derivado-humano + notificación/workflow) resolvería de paso.

### 10. El follow-up de día 3 y día 5 no es viable como 'follow-up nativo del bot': cae fuera de la ventana de 24h de WhatsApp y requiere workflow con plantillas Meta
**Área:** Bot IA — Follow-up de inactividad · **Tareas:** wdx6zenj6t — Follow-up por inactividad: 6h / día 3 / día 5 → tag frio

La tarea instruye configurarlo en 'Conversation AI → Follow-up settings (nativo del bot)' y afirma que es 'mejor que un workflow separado'. Dos problemas de viabilidad GHL: (1) por política de Meta, pasadas 24h desde el último mensaje del cliente solo pueden enviarse plantillas Meta aprobadas — los toques de día 3 y día 5 vía WhatsApp fallarían como mensajes libres del bot, exactamente la razón por la que SP06 (día 2+5 post-proforma) sí se diseñó como workflow con templates Meta; (2) Conversation AI no ofrece un programador nativo de follow-ups multi-día que además aplique un tag ('Día 5 → añadir tag frio y detener') — la aplicación del tag frio necesita una acción de workflow. Solo el toque de 6h cabe dentro de la ventana de 24h. Tal como está escrito, los toques 2 y 3 no se enviarían y el tag frio nunca se aplicaría.

> Evidencia: wdx6zenj6t: 'Sección | Conversation AI → Follow-up settings (nativo del bot)' … '3º follow-up | Día 5 → añadir tag `frio` y detener' … 'El follow-up nativo del bot es mejor que un workflow separado… NO confundir con SP06, que es el seguimiento POST-proforma enviada (workflow aparte con templates Meta)'. La propia tarea reconoce que los envíos fuera de ventana requieren templates Meta.

**Recomendación:** Rediseñar la subtarea: nudge de ≤6h puede quedar en el bot (dentro de ventana); día 3 y día 5 como workflow aparte con plantillas Meta aprobadas (dependencia de S03 Templates Meta, wdx6zenj4k) y acción final Add Tag frio + stop. Añadir guards de salida si el cliente responde o si ya tiene pide-presupuesto/pide-visita.

**Matiz del verificador:** Dos matices a la recomendación: (a) el toque de 6h solo es viable dentro de la ventana si la inactividad se mide desde el último mensaje ENTRANTE del cliente (no desde el último mensaje del bot); (b) el rediseño como workflow implica redactar y enviar a aprobación 2 plantillas Meta adicionales (nudge día 3 y día 5 de inactividad) que hoy no están contempladas en el alcance de S03 (wdx6zenj4k) — hay que ampliar S03 explícitamente y crear la dependencia, o los templates no existirán cuando se monte el workflow. La severidad "mayor" es correcta, no está inflada: el fallo sería silencioso (los toques 2 y 3 simplemente no se envían y el tag frio de inactividad nunca se aplica) pero no bloquea el go-live del núcleo.

### 11. El Flujo 6 (urgencia con riesgo, olor a gas) no define la mecánica de la 'derivación INMEDIATA': ni tag ni canal de notificación a Termical
**Área:** Bot IA — Prompt Objetivo (Flujo 6 urgencia) · **Tareas:** wdx6zenj69 — Prompt — Objetivo (flujos y reglas de derivación)

El flujo de urgencia solo dice 'Derivación INMEDIATA + pautas de seguridad al cliente', sin especificar qué tag se aplica (¿derivado-humano?, ¿uno propio?) ni cómo se entera Alejandro de inmediato. Ningún workflow del diseño cubre este caso: SP-N notifica solo lead caliente (pide-presupuesto) y SP-V solo pide-visita. Un técnico no puede implementar este flujo sin ambigüedad, y es justamente el caso con riesgo de seguridad donde un fallo silencioso es más grave (un aviso de olor a gas quedaría esperando en la bandeja sin alerta).

> Evidencia: wdx6zenj69: 'Flujo 6 · URGENCIA con riesgo (olor a gas, fuga) | Derivación INMEDIATA + pautas de seguridad al cliente' — sin tag ni notificación. CLAUDE.md decisión 13: 'Urgencia con riesgo (olor a gas, fuga): derivación inmediata a humano + pautas de seguridad'; anatomía de workflows (§4): ninguno de los 10 notifica urgencias.

**Recomendación:** Especificar en la tarea: tag a aplicar en urgencia (p. ej. derivado-humano vía Bot Goal) + nodo/workflow de notificación inmediata a Termical (push de la app / notificación interna), y redactar las pautas de seguridad exactas que el bot debe dar (cerrar llave de gas, ventilar, no accionar interruptores, llamar a urgencias).

**Matiz del verificador:** Dos matices que refuerzan y acotan el hallazgo: (a) el hueco es más profundo de lo que sugiere la recomendación — reutilizar el tag derivado-humano NO bastaría, porque ningún workflow del diseño escucha ese tag (el Flujo 5 tampoco genera notificación); haría falta crear un workflow de notificación nuevo en cualquier caso. (b) Mitigación temporal: el bot arranca en modo Suggestive (decisión 1 de CLAUDE.md), donde un humano revisa cada respuesta, así que el fallo silencioso solo se materializa al pasar a Auto-Pilot en 1-2 semanas; esto justifica severidad "mayor" y no "crítica".

### 12. Falta el nodo que DETIENE al bot cuando se aplica derivado-humano: en Auto-Pilot el bot seguiría respondiendo al cliente ya derivado
**Área:** Bot IA — Derivación a humano (handoff) · **Tareas:** wdx6zenj69 — Prompt — Objetivo (flujos y reglas de derivación), wdx6zenj5w — [BOT] Conversation AI — configuración completa

Aplicar el tag derivado-humano no desactiva Conversation AI para ese contacto: en GHL hace falta una acción explícita (acción de workflow que apaga el bot para el contacto/conversación, o toggle manual en Conversations). La instrucción de prompt 'no insistir' no garantiza el silencio del bot ante nuevos mensajes del cliente. En Suggestive no se nota (nada se envía sin aprobación), pero el diseño pasa a Auto-Pilot tras 1-2 semanas y entonces el bot pisaría la conversación humana, contradiciendo el espíritu de 'la última palabra la tiene el humano'. Ninguna de las 8 subtareas ni los 10 workflows contempla este apagado.

> Evidencia: wdx6zenj69: 'Flujo 5 · Pide humano / caso complejo | Tag `derivado-humano` + no insistir'. wdx6zenj5w: 'Arranca en Suggestive (modo supervisado) → pasa a Auto-Pilot tras validación'. CLAUDE.md regla §0: 'El sistema nunca envía nada sin aprobación humana'.

**Recomendación:** Añadir un nodo/mini-workflow: trigger Tag Added derivado-humano → acción desactivar Conversation AI para el contacto + notificación interna a Termical, y documentar cuándo/cómo se reactiva el bot. Verificarlo en las pruebas pre-Auto-Pilot.

**Matiz del verificador:** Dos matices que refuerzan y acotan el hallazgo: (a) el problema es más amplio de lo reportado — `derivado-humano` es el único tag operativo SIN workflow consumidor: además del apagado del bot, tampoco existe notificación interna a Termical cuando un cliente pide humano (el hallazgo lo incluye en la recomendación pero no en el título), y lo mismo aplica al Flujo 6 (urgencia con riesgo), que también deriva sin workflow que alerte; (b) mitigante parcial: el ajuste "máx 15 msgs" por conversación (wdx6zenj60) acota la exposición en Auto-Pilot pero no la elimina ni sustituye el apagado explícito. La severidad "mayor" es correcta, no debe elevarse a crítica porque el arranque en Suggestive protege el go-live inicial.

### 13. El escenario de prueba nº1 ('termo de 80 litros') depende de la familia de termos eléctricos del catálogo, que el cliente aún NO ha enviado (⛔)
**Área:** Bot IA — Pruebas conversacionales / dependencia de catálogo · **Tareas:** wdx6zenj6v — Pruebas conversacionales en Suggestive (pre-Auto-Pilot), wdx6zenj5w — [BOT] Conversation AI — configuración completa

El primer escenario del gate exige que el bot dé un 'orientativo del catálogo +IVA' para un termo eléctrico de 80L, pero la KB solo tiene la familia de calentadores de gas: los termos eléctricos —'la más vendida' según el propio CLAUDE.md— están pendientes del cliente y bloqueados. Con el [BOT] con due 11 jul, esa prueba no puede pasar y el bot saldría al rodaje sin precios de su producto principal. Ni la tarea de pruebas ni el padre reflejan esta dependencia/bloqueo.

> Evidencia: wdx6zenj6v: '"¿Cuánto cuesta un termo de 80 litros?" | Orientativo del catálogo +IVA + oferta de proforma'. CLAUDE.md §8: 'faltan familias: termos eléctricos (la más vendida), calderas' y §12: '⛔ Familias restantes del catálogo: termos eléctricos (la más vendida), calderas'. Sprint: '[BOT] … Henry | 10→11 jul'.

**Recomendación:** Reclamar ya al cliente la familia de termos eléctricos (pendiente §12); mientras tanto marcar el escenario 1 como bloqueado o sustituirlo por calentador de gas (sí catalogado), y anotar en la tarea que el bot no debe inventar precios de termos hasta cargar esa familia en la KB.

**Matiz del verificador:** Dos precisiones: (a) la frase 'Ni la tarea de pruebas ni el padre reflejan esta dependencia/bloqueo' es parcialmente incorrecta — el padre [BOT] SÍ tiene dependencia formal waiting_on S10 (verificada en ClickUp, chain 0c66d3bd) y S10 lleva el ⛔ del catálogo en su nombre y descripción; lo que ocurre es que el padre la relaja explícitamente a 'S10 KB cargada (FAQs mínimo)', con lo que la dependencia se da por satisfecha sin el catálogo, y la subtarea de pruebas wdx6zenj6v no tiene dependencias propias ni nota de bloqueo del escenario 1 — el riesgo de fondo se mantiene. (b) La cita '(la más vendida)' pertenece a §12, no a §8; §8 solo dice 'faltan familias: termos eléctricos, calderas'.

### 14. S04 no crea los campos de oportunidad estado_proforma y requiere_visita que exige el diseño y que SP04 necesita para su guard anti-duplicados
**Área:** Setup (00) / Sales Pipeline (03) · **Tareas:** wdx6zenj4v [S04] Custom Fields, wdx6zenj96 [SP04] Envío automático de proforma, wdx6zenj5u [S11] Validaciones pre-go-live

El CLAUDE.md define campos a nivel Oportunidad: requiere_visita y estado_proforma (borrador/revisada/enviada). La descripción de S04 solo estructura los folders de CONTACTO 'General' y 'Proforma' y ningún otro sitio los crea. Sin embargo, SP04 declara explícitamente depender de 'S04 campo estado_proforma', su Guard IF y su Update Field usan ese campo, y la validación S11-1 prueba el ciclo 'tag → envío → estado → etapa'. Si S04 se ejecuta tal cual está escrito (Germán, due 8 jul), el campo del guard anti-duplicados del workflow CRÍTICO no existirá y habrá retrabajo o un guard mal montado (riesgo de proformas duplicadas). requiere_visita tampoco lo crea nadie.

> Evidencia: CLAUDE.md §4: 'Oportunidad: `requiere_visita`, `estado_proforma` (borrador/revisada/enviada)'. S04 solo lista '## Folder "General"' y '## Folder "Proforma"' sin esos campos. SP04: 'Dependencias: S09 Plantilla D&C creada y validada (S11-1 CRÍTICA) · S04 campo estado_proforma' y 'Guard IF: estado_proforma = enviada → STOP'.

**Recomendación:** Añadir a la descripción de S04 (o como subtarea) la creación de estado_proforma y requiere_visita, especificando el nivel (oportunidad según diseño, o decidir conscientemente moverlos a contacto como se hizo con valor_estimado) antes del 8 jul.

**Matiz del verificador:** Dos matices. (1) La verificación revela una inconsistencia adicional que refuerza la recomendación: las subtareas de SP04 ya implementan estado_proforma a nivel CONTACTO ("Condition object: Contact" en el Guard IF y "Update Contact Field" en el nodo 4), contradiciendo el nivel Oportunidad del CLAUDE.md §4; al añadir el campo a S04 hay que unificar el nivel (contacto es lo coherente con la mecánica del workflow tal como está escrita, igual que se hizo con valor_estimado). (2) requiere_visita no tiene ningún consumidor en ninguna tarea del proyecto (SP-V se dispara por el tag pide-visita, no por ese campo): su omisión aislada sería severidad "menor"; el peso de la severidad "mayor" recae en estado_proforma. Mitigante parcial: Germán es asignado tanto de S04 como de SP04, lo que reduce (pero no elimina) el riesgo de que el hueco pase desapercibido.

### 15. El formulario interno S08 no captura ningún dato que identifique al cliente (nombre/teléfono/email) y no existe workflow que procese su submit
**Área:** Setup (00) / Flujo A — vía formulario interno · **Tareas:** wdx6zenj5j [S08] Formulario interno Proforma, wdx6zenjby [Flujo A] Proforma MANUAL

S08 lista exactamente 7 campos, todos del folder Proforma. Ninguno identifica al contacto: sin email/teléfono el submit no puede matchear ni crear el contacto correcto en GHL, y el email es imprescindible para enviar la proforma (la plantilla D&C mergea 'Cliente: nombre, teléfono, email, dirección'). El caso de uso es justamente 'cuando el lead NO vino por el bot (visita, llamada, conocido)', es decir, un contacto que probablemente no existe aún. Además no hay ningún workflow tipo LS que procese ese Form Submitted: nadie setea fuente_contacto = 'Llamada o visita (manual)' (valor previsto en el dropdown de S04 exactamente para esta vía) ni crea la oportunidad, a diferencia de LS01/LS02.

> Evidencia: S08: '## Campos (mapear a custom fields del folder Proforma) tipo_servicio · tipo_aparato · litros_capacidad · paquete_interes · valor_estimado · direccion_servicio · detalle_trabajo (opcional)' — no hay nombre, teléfono ni email. S04 prevé el valor 'Llamada o visita (manual)' en fuente_contacto, que ningún workflow aplica. Flujo A: 'Lead captado por el formulario interno tras una visita'.

**Recomendación:** Ampliar S08 con los campos de identificación del contacto (nombre, teléfono, email) y añadir el mini-workflow (o los pasos) que al hacer submit matchee/cree el contacto, setee fuente_contacto = 'Llamada o visita (manual)' y cree la oportunidad, en paralelo a LS01/LS02.

**Matiz del verificador:** Matiz: la parte "no existe workflow que procese su submit" debe precisarse. El diseño sí contempla el eslabón POSTERIOR al formulario: el subtask trigger de SP-N (wdx6zenj8y) dice "Vía formulario interno, Termical ya tiene los datos y puede saltar directo al tag aprobar-proforma", es decir, el envío se resolvería por SP04 (tag → Send Document → Move Opportunity), no por un workflow de Form Submitted. Lo que realmente falta es: (a) los campos de identificación del contacto en S08 (el defecto duro, porque sin ellos el submit no escribe en el contacto correcto y SP04/Flujo A no tienen email al que enviar); (b) quién setea fuente_contacto = "Llamada o visita (manual)"; y (c) la creación de la oportunidad en esta vía — SP04 nodo 5 es "Move Opportunity → Proforma enviada", que presupone una oportunidad que nadie crea, y el procedimiento Flujo A (wdx6zenjby, paso 4 "Mover la oportunidad") tampoco documenta crearla ni crear el contacto. La recomendación del mini-workflow es válida pero también bastaría documentar en Flujo A/S08 la creación manual de contacto+oportunidad, ya que el propio proyecto define Flujo A como "procedimiento humano documentado", no workflow.

### 16. S03 no incluye templates Meta para los follow-ups por inactividad del bot (día 3 y día 5), que caen fuera de la ventana de 24 h
**Área:** Setup (00) / Bot Conversation AI (01) · **Tareas:** wdx6zenj4k [S03] Templates Meta WhatsApp, wdx6zenj6t Follow-up por inactividad (subtarea BOT)

La subtarea del BOT 'Follow-up por inactividad: 6h / día 3 / día 5 → tag frio' implica mensajes salientes a los 3 y 5 días de inactividad del lead, es decir, fuera de la ventana de 24 h de WhatsApp: requieren template aprobado por Meta. S03 —cuya propia descripción dice que existe para 'mensajes fuera de la ventana de 24 h'— solo lista 7 templates (3 de SP03, 2 de SP06, 2 de AP02+PS01). Si no se envían a aprobación el día 1 junto con el resto (Meta tarda 24-48 h), los follow-ups de inactividad del bot no se entregarán y habrá una segunda ronda de aprobación con retraso.

> Evidencia: S03: 'templates necesarios para mensajes fuera de la ventana de 24 h' con tabla de 7 templates donde ninguno corresponde a follow-up por inactividad. Subtarea BOT wdx6zenj6t: 'Follow-up por inactividad: 6h / día 3 / día 5 → tag frio'.

**Recomendación:** Añadir a S03 dos templates de follow-up por inactividad (día 3 y día 5) y enviarlos a aprobación en la misma tanda del 9-10 jul.

**Matiz del verificador:** La recomendación de añadir 2 templates a S03 es necesaria pero puede ser insuficiente: el follow-up nativo de Conversation AI en GHL envía mensajes libres generados por IA y no está garantizado que pueda usar templates aprobados de Meta. Es probable que los toques de día 3 y día 5 deban implementarse vía workflow (acción Send WhatsApp con template, análogo a SP06) en lugar del follow-up nativo, o al menos validarse esa capacidad como punto adicional en S11. El toque de 6 h sí puede quedarse en el follow-up nativo (dentro de la ventana de 24 h). Nota menor: el propio contexto de wdx6zenj6t ("NO confundir con SP06... workflow aparte con templates Meta") muestra que el equipo conocía la restricción para SP06 pero no la trasladó al follow-up del bot, lo que refuerza que es una omisión y no una decisión deliberada documentada.

### 17. La conexión de Google Business Profile no tiene tarea ni fecha, pero PS02 (due 14 jul) y AP02+PS01 (due 13 jul) dependen de ella dentro del sprint
**Área:** Reviews (05) / Active Projects (04) — dependencia GBP · **Tareas:** wdx6zenjd3 [PS02] Respuesta IA a reseñas, wdx6zenjck [AP02 + PS01] Cierre → encuesta → reseña

PS02 declara como dependencia la ficha GBP conectada y AP02+PS01 necesita el 'link de reseña de Google (requiere ficha GBP conectada)'. La KB del bot también se apoya en la ficha ('horario dinámico vía ficha Google'). Pero la conexión solo existe como parte del 'onboarding posterior con el cliente' del §12, que no tiene tarea, dueño ni fecha en ninguna de las 7 listas. Resultado: dos workflows con due date dentro del sprint (13 y 14 jul) dependen de un evento post-sprint no planificado — o se incumplen las fechas o se configuran sin poder probarse.

> Evidencia: PS02: 'Dependencias: Ficha Google Business Profile conectada al sistema (la conecta el CLIENTE guiado en la llamada de onboarding — no pasa claves)'. AP02: 'Link de reseña de Google (requiere ficha GBP conectada — onboarding con el cliente)'. CLAUDE.md §12: 'Onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla…' — sin tarea en ClickUp.

**Recomendación:** Crear una tarea 'Conectar Google Business Profile (llamada guiada con el cliente)' con dueño y fecha antes del 13 jul, y enlazarla como bloqueante (waiting_on) de PS02 y AP02+PS01; si no es viable en el sprint, mover los due dates de PS02/AP02 y documentar la degradación (encuesta sin link de reseña).

**Matiz del verificador:** Matiz sobre AP02+PS01: el impacto duro recae en PS02, no por igual en ambas. El link público de reseña de Google se puede obtener de la ficha en Maps sin conectar GBP a GHL (o construirse con el Place ID), de modo que AP02+PS01 (due 13 jul) sí puede configurarse con el link real aunque el onboarding no haya ocurrido — la propia tarea lo declara como dependencia, pero técnicamente no es bloqueante en GHL. En cambio PS02 (due 14 jul) sí es imposible de configurar y probar sin la integración GBP conectada por el cliente. La recomendación sigue siendo válida; además, nada impide agendar la llamada guiada de conexión GBP dentro del sprint (antes del 14 jul), lo que resolvería el problema sin mover fechas.

### 18. El onboarding con el cliente (grabación del buzón de voz §4.11, formación de calendarios, conexión de redes) no existe como tarea en ClickUp
**Área:** Cobertura — onboarding con el cliente · **Tareas:** wdx6zenj4e [S02] WhatsApp Business API, wdx6zenj54 [S06] Calendarios

El §12 del CLAUDE.md compromete un onboarding posterior con tres entregables, y dos decisiones de arquitectura dependen de él: (1) la mitigación de telefonía fuera —decisión §4.11: buzón de voz con locución que redirige a WhatsApp, sin la cual las llamadas perdidas (el problema raíz del cliente) no derivan al sistema— solo aparece como contexto informativo en S02; (2) la formación de calendarios que S06 dice explícitamente 'Incluir en la formación' (bloqueos, estacionalidad, agenda Leroy Merlin), imprescindible porque todo el agendado es manual. Ninguna de las 85 tareas cubre este onboarding: sin tarea, dueño ni fecha, el compromiso puede perderse tras el go-live. (La conexión GBP, que forma parte de la misma llamada, se reporta como hallazgo aparte por bloquear PS02/AP02.)

> Evidencia: CLAUDE.md §12: 'Onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla (él no pasa claves) + grabación buzón de voz + formación calendarios (bloqueos, estacionalidad)'. §4.11: 'Mitigación coste cero: buzón de voz con locución → WhatsApp (el cliente la graba)'. S06 contexto: 'Incluir en la formación: crear cita, bloquear días/franjas…'.

**Recomendación:** Crear una tarea padre 'Onboarding con el cliente' (con subtareas: guion + grabación del buzón de voz, formación de calendarios, conexión de redes) con dueño y fecha ligada al go-live, y referenciarla desde S02 y S06.

**Matiz del verificador:** Matiz que refuerza (no corrige) el hallazgo: la "formación" no es solo un compromiso del §12 sino partida pagada del presupuesto aprobado (§2: "Automatizaciones+formación €820"), lo que hace más grave que carezca de tarea, dueño y fecha. Precisión adicional: el conteo de "85 tareas" del hallazgo coincide exactamente con lo que devuelve ClickUp para el folder. Único matiz de alcance: el compromiso sí está registrado por escrito en el §12 del CLAUDE.md (no está totalmente indocumentado), pero al ser ClickUp la herramienta donde vive el sprint y las asignaciones, el riesgo de pérdida post-go-live descrito es real.

### 19. Los reclamos al cliente de los dos bloqueos ⛔ (accesos DNS y familias del catálogo) no tienen tarea con dueño ni fecha
**Área:** Cobertura — pendientes del cliente (⛔) · **Tareas:** wdx6zenj47 [S01] Subcuenta+dominio+correo, wdx6zenj5t [S10] Knowledge Base, wdx6zenjde [WEB] One-page

El §12 marca ambos como '⛔ Del cliente (reclamar)' y el plan de sprint asigna 'reclamar DNS' al día 1 (mié 8). En ClickUp solo existen como notas de bloqueo dentro de S01, S10, S09 y WEB — nadie es dueño de perseguirlos. El DNS bloquea el correo del dominio (por el que 'salen las proformas', S01 due 9 jul) y la publicación de la web (WEB due 13 → LS02 due 14); el catálogo bloquea S10 (due 9 jul) y por dependencia BOT←S10 (due 11 jul): sin familias de termos eléctricos ('la más vendida') el bot no puede estimar. Si nadie reclama el día 1, la ruta crítica se desliza.

> Evidencia: CLAUDE.md §12: 'Del cliente (reclamar): 1. ⛔ Accesos DNS del dominio (bloquea correo del dominio, publicación web). 2. ⛔ Familias restantes del catálogo: termos eléctricos (la más vendida), calderas.' y 'Día 1 (mié 8): S04, S05, S06, S07 (sin bloqueos) + reclamar DNS'. S01: '⛔ BLOQUEADO parcialmente: accesos DNS del dominio (el cliente los envía)'.

**Recomendación:** Crear en la lista Setup una tarea 'Reclamar al cliente: accesos DNS + familias del catálogo (termos eléctricos, calderas) + 2-3 estrella' con dueño y due 8 jul, enlazada como bloqueante de S01 y S10.

**Matiz del verificador:** Matiz leve a "nadie es dueño de perseguirlos": las tareas bloqueadas sí tienen dueño y fechas que arrancan el 8/7 (S01 Henry 8→9, S10 Germán 8→9, WEB Oliver 8→13), por lo que existe un responsable implícito del bloqueo. Sin embargo, el reclamo como acción no está representado en ninguna tarea, subtarea ni checklist, y las tres descripciones lo formulan en pasiva ("el cliente los envía", "esperando el correo del cliente", "cuando lleguen DNS"), así que el fondo del hallazgo se sostiene. Severidad "mayor" correcta: es riesgo de deslizamiento de la ruta crítica, no rotura del sistema. La recomendación podría dividirse en dos reclamos con dueños distintos (DNS → Henry, dueño de S01; catálogo + 2-3 estrella → Germán, dueño de S10) para alinear reclamo y tarea bloqueada, y enlazar también WEB (wdx6zenjde) y S09 (wdx6zenj5p), que sufren los mismos bloqueos.

### 20. S03 'Templates Meta DÍA 1' es imposible con su propia cadena de dependencias, y la aprobación de Meta (24-48h) come el margen de prueba de SP03/SP06/AP02
**Área:** calendario/fechas + dependencias · **Tareas:** [S03] wdx6zenj4k, [S02] wdx6zenj4e, [SP03] wdx6zenjb0, [SP06] wdx6zenjba, [AP02+PS01] wdx6zenjck

El título de S03 exige enviar a aprobación el día 1 (8 jul), pero S03 depende de S02 (WABA, due 9 jul) que a su vez depende de S01 (8→9): está programada 9→10 jul. Si se envía a Meta el viernes 10, la aprobación de 24-48h llega el 11-12 jul (sábado-domingo, sin tareas agendadas). SP03 (10→13), SP06 (13→13) y AP02 (13→13) necesitan templates APROBADOS para probar recordatorios, seguimientos y encuesta fuera de la ventana de 24h: les quedan 0-1 días de margen y todas sus pruebas reales se comprimen al lunes 13, un día antes de la ventana de S11 (14-15).

> Evidencia: Título de wdx6zenj4k: '[S03] Templates Meta WhatsApp — enviar a aprobación DÍA 1'; su descripción: 'Aprobación tarda 24-48 h: bloquean recordatorios y seguimientos — hacerlo el primer día'; dependencia ClickUp S03←S02 con S02 due 9 jul (1783580400000) y S03 start 9 jul; CLAUDE.md §12: 'S03 Templates Meta cuanto antes (aprobación Meta 24-48h; vence vie 10)'.

**Recomendación:** Adelantar S02 al 8 jul o desacoplar S03: redactar los 7 textos el 8 jul y enviarlos a Meta en cuanto la WABA esté activa el 9 por la mañana. Añadir buffer explícito entre la aprobación de Meta y las pruebas de SP03/SP06/AP02, o mover esas pruebas como precondición marcada dentro de S11.

**Matiz del verificador:** Dos matices de precisión: (a) el detalle afirma que el 11-12 jul está "sin tareas agendadas", pero [BOT] (wdx6zenj5w, 10→11 jul) vence el sábado 11; lo correcto es que ninguna tarea DEPENDIENTE DE TEMPLATES está agendada el 11-12, de modo que una aprobación que llegue en fin de semana no se aprovecha hasta el lunes 13. (b) La programación 9→10 de S03 no contradice el CLAUDE.md §12 (que ya asume "vence vie 10"); la contradicción real es interna a la tarea: su título/descripción ("DÍA 1"/"primer día") vs. su propia programación y su cadena de dependencias S03←S02←S01. Nota adicional: en la práctica Meta suele aprobar templates en minutos-horas, lo que puede suavizar el impacto, pero el plan debe dimensionarse con la asunción de 24-48h que el propio proyecto declara.

### 21. S01 mezcla la subcuenta (sin bloqueo) con DNS/correo (⛔ cliente) en una sola tarea: el grafo bloquea formalmente S02→S03 y WEB con un bloqueo que no les aplica
**Área:** dependencias · **Tareas:** [S01] wdx6zenj47, [S02] wdx6zenj4e, [S03] wdx6zenj4k, [SP04] wdx6zenj96, [WEB] wdx6zenjde

S01 (8→9 jul) contiene tres ítems: crear subcuenta (desbloqueada, datos ya entregados), configurar DNS y correo del dominio (⛔ esperando accesos del cliente, no recibidos a 7 jul). S02, SP04 y WEB dependen de S01 COMPLETA en ClickUp, pero S02 (y su cadena S03→SP03/SP06/AP02) solo necesita la subcuenta, y el diseño de WEB tampoco necesita DNS (solo la publicación, subtarea 4). Si el cliente no envía los DNS el 8-9 jul, S01 no puede cerrarse y el grafo deja formalmente parado medio sprint cuando en realidad casi todo podría avanzar. El único dependiente real del correo del dominio es SP04 (envío de proformas por email).

> Evidencia: Descripción de wdx6zenj47: '⛔ BLOQUEADO parcialmente: accesos DNS del dominio (el cliente los envía — tarea suya acordada el 7/7)' e ítem 2 'Configurar dominio + DNS (cuando lleguen accesos)'; dependencias ClickUp S02←S01, SP04←S01, WEB←S01; CLAUDE.md §12: '⛔ Accesos DNS del dominio (bloquea correo del dominio, publicación web)'.

**Recomendación:** Dividir S01 en 'S01a Subcuenta' (8 jul; bloquea S02 y el diseño de WEB) y 'S01b DNS + correo del dominio' (bloquea SP04 y la subtarea de publicación de WEB), recolgando las dependencias. Como mínimo, acordar por escrito que S02 arranca con la subcuenta creada aunque los DNS no hayan llegado.

**Matiz del verificador:** Dos precisiones que refuerzan el hallazgo: (a) la cadena formalmente bloqueada es aún mayor que la descrita — también BOT←S02 (wdx6zenj5w depende de wdx6zenj4e) y por tanto S11←BOT, es decir, la validación pre-go-live queda en la misma cadena; (b) hay una incoherencia interna adicional: WEB (wdx6zenjde) tiene start_date el 8 jul pese a depender de S01, cuyo due es el 9 jul, señal de que el propio plan asume que el diseño web arranca antes de que S01 cierre. Matiz menor a la frase 'el único dependiente real del correo del dominio es SP04': es cierta a nivel de tareas de primer orden, aunque la validación S11-1 (entregabilidad del email del dominio) también depende de ese correo — transitivamente cubierta porque S11 ya depende de SP04.

### 22. BOT programado 10→11 jul (el 11 es sábado) colgando de S10, cuyo catálogo sigue ⛔ esperando al cliente — y falta justo la familia más vendida (termos eléctricos)
**Área:** calendario/fechas · **Tareas:** [BOT] wdx6zenj5w, [S10] wdx6zenj5t, [S11] wdx6zenj5u

S10 vence el 9 jul pero su ítem 2 (catálogo de paquetes para la KB) está bloqueado por el cliente: solo se recibió calentadores de gas; faltan termos eléctricos ('la más vendida') y calderas, exactamente lo que el bot debe estimar. BOT tiene 2 días (viernes 10 y sábado 11) para 8 subtareas, incluidas 'Bot Goals: captura de campos a custom fields' (valor_estimado sale de la KB) y 'Pruebas conversacionales', imposibles de completar sin precios cargados. El sprint no agenda nada el domingo 12, así que cualquier resbalón cae al lunes 13 y estrecha la dependencia S11←BOT (validación 14-15). Además conviene confirmar si el due en sábado 11 es intencional.

> Evidencia: wdx6zenj5t: 'el catálogo de paquetes está ⛔ bloqueado esperando el correo del cliente'; CLAUDE.md §12: '⛔ Familias restantes del catálogo: termos eléctricos (la más vendida), calderas'; CLAUDE.md §4 decisión 8: 'el bot solo estima termos eléctricos, calentadores de gas y calderas'; fechas de wdx6zenj5w: start 1783666800000 (vie 10 jul) → due 1783753200000 (sáb 11 jul).

**Recomendación:** Reclamar el catálogo con fecha límite interna 8-9 jul. Si no llega: cargar la KB con FAQs + calentadores de gas (ya recibidos), construir el bot igualmente y añadir una validación específica de estimación de termos antes de pasar a Auto-Pilot. Revisar si el due del sábado 11 es realista o mover BOT a 10→13.

**Matiz del verificador:** Dos precisiones que suavizan el detalle sin invalidar el hallazgo: (1) La afirmación "imposibles de completar sin precios cargados" es exagerada — el catálogo de calentadores de gas SÍ está recibido con paquetes orientativos listos (≈478/578/356€ +IVA, CLAUDE.md §8), por lo que las subtareas "Bot Goals" y "Pruebas conversacionales" pueden ejecutarse y validarse con esa familia; lo que queda sin validar es la estimación de termos eléctricos (la familia más vendida) y calderas — es un hueco de cobertura, no una imposibilidad total. (2) La descripción de la propia tarea BOT ya declara la dependencia como "S10 KB cargada (FAQs mínimo)", es decir, el plan ya contempla construir el bot solo con FAQs; la recomendación del auditor de "cargar FAQs + gas y construir igualmente" coincide en parte con el diseño existente. Lo que sí falta y aporta valor de la recomendación es la validación específica de estimación de termos eléctricos antes de Auto-Pilot y la revisión del due en sábado 11 (aparentemente no intencional: es la única tarea que vence en fin de semana y el domingo 12 está vacío).

### 23. Los campos de OPORTUNIDAD (estado_proforma, requiere_visita) no los crea ninguna tarea: S04 solo crea campos de contacto y el guard anti-duplicados de SP04 depende de estado_proforma
**Área:** alcance/grafo + dependencias · **Tareas:** [S04] wdx6zenj4v, [SP04] wdx6zenj96, [Flujo A] wdx6zenjby

SP04 declara depender de 'S04 campo estado_proforma' y su nodo 2 es el guard anti-duplicados del flujo B ('Guard IF: estado_proforma = enviada → STOP'), que además es parte de la validación crítica S11-1. Pero las tablas de S04 solo incluyen los 9 campos de CONTACTO (folders General y Proforma): estado_proforma y requiere_visita — campos de oportunidad según CLAUDE.md — no aparecen en el alcance de ninguna de las 24 tareas. Si S04 se implementa tal cual está escrita, cuando Germán construya SP04 (10-13 jul) el campo del guard no existirá: retrabajo asegurado y riesgo de montar el flujo B sin su mecanismo anti-duplicados.

> Evidencia: wdx6zenj96: 'Dependencias: S09 Plantilla D&C creada y validada (S11-1 CRÍTICA) · S04 campo estado_proforma · Correo del dominio operativo' y nodo 2 'Guard IF: estado_proforma = enviada → STOP'; wdx6zenj4v lista solo fuente_contacto, fecha_primer_contacto, tipo_servicio, tipo_aparato, litros_capacidad, paquete_interes, valor_estimado, direccion_servicio, detalle_trabajo; CLAUDE.md: 'Oportunidad: requiere_visita, estado_proforma (borrador/revisada/enviada)'.

**Recomendación:** Añadir a S04 (o como subtarea nueva del 8 jul) la creación de los 2 campos de oportunidad estado_proforma y requiere_visita, y verificar en la construcción de SP04 que un workflow disparado por tag de CONTACTO puede leer/escribir el campo de OPORTUNIDAD; si no puede, mover estado_proforma a contacto y actualizar S09/SP04.

**Matiz del verificador:** Dos matices que no invalidan el hallazgo: (a) El riesgo de 'montar el flujo B sin su mecanismo anti-duplicados' en silencio es menor de lo que sugiere el detalle: GHL no permite configurar un IF sobre un campo inexistente, así que Germán detectaría el hueco al construir el nodo 2; el riesgo real es el retrabajo más la creación ad hoc del campo (p. ej. como campo de CONTACTO en vez de OPORTUNIDAD), divergiendo del diseño v2.0 y de S09. (b) requiere_visita efectivamente no lo crea ninguna tarea, pero tampoco lo consume ninguna (0 resultados en la búsqueda; SP-V opera por tag pide-visita), por lo que su omisión es de impacto funcional menor que la de estado_proforma — el campo bloqueante del hallazgo es estado_proforma. Dato adicional que refuerza el hallazgo: la dependencia 'S04 campo estado_proforma' solo existe como texto en la descripción de SP04; en el grafo formal de ClickUp no hay arista SP04←S04, de modo que ni siquiera el grafo forzaría a revisar S04 antes de construir SP04. La recomendación del auditor (añadir los 2 campos de oportunidad a S04 el 8 jul y validar en SP04 la lectura/escritura de campos de oportunidad desde un workflow con trigger de contacto) es correcta y accionable.

### 24. PS02 (due 14 jul) requiere la ficha de Google Business Profile conectada, pero esa conexión está planificada para el onboarding POSTERIOR al sprint y no existe ninguna tarea que la cubra
**Área:** alcance/grafo + dependencias · **Tareas:** [PS02] wdx6zenjd3, [AP02+PS01] wdx6zenjck

El único bloqueante de PS02 en ClickUp es AP02, pero su bloqueo real —declarado en su propia descripción— es la conexión de GBP, que la hace el cliente guiado en una llamada de onboarding que el CLAUDE.md sitúa después del sprint. Con las fechas actuales, PS02 no podrá activarse ni probarse el 14 jul. El problema alcanza también a AP02: su nodo 6 envía el 'link reseña Google', que igualmente requiere la ficha GBP conectada, y AP02 vence el 13 jul.

> Evidencia: wdx6zenjd3: 'Dependencias: Ficha Google Business Profile conectada al sistema (la conecta el CLIENTE guiado en la llamada de onboarding — no pasa claves)'; wdx6zenjck: 'Link de reseña de Google (requiere ficha GBP conectada — onboarding con el cliente)'; CLAUDE.md §12: 'Onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla (él no pasa claves)'.

**Recomendación:** Crear una tarea 'Conectar GBP con el cliente (llamada guiada)' agendada dentro del sprint (antes del 13-14 jul) y colgar PS02 y el nodo 6 de AP02 de ella; o reclasificar explícitamente PS02 y la rama de reseña de AP02 como post-go-live y excluirlas del alcance validable por S11.

**Matiz del verificador:** Matiz sobre el alcance en AP02: la dependencia del nodo 6 es más blanda que la de PS02. El link de reseña de Google es una URL estática que puede obtenerse sin conectar la integración GBP en GHL (el cliente puede facilitarla o extraerse de la ficha pública y guardarse como custom value), por lo que esa rama podría completarse el 13 jul con una mitigación simple; en cambio PS02 (auto-respuesta IA y notificación de nueva reseña) sí tiene dependencia dura e ineludible de la integración conectada. Además, S11 no incluye ninguna validación de GBP/reseñas entre sus 5 puntos, así que el gap no bloquea las validaciones pre-go-live: el impacto se limita al módulo de reseñas (adicional de 190€) y a la fecha comprometida del 14 jul. Nota menor: el CLAUDE.md lista el "Onboarding posterior" dentro del bloque "Del equipo (sprint 8-15 jul)" sin fecha, por lo que "posterior al sprint" es una inferencia razonable pero no está datado explícitamente; lo indiscutible es que no existe tarea ni fecha que garantice la conexión antes del 13-14 jul.

### 25. Cadena WEB (⛔ DNS) → LS02: LS02 vence el 14 jul DENTRO de la ventana de S11 (14-15) y S11 ni siquiera depende de LS02 — no queda margen para validarla
**Área:** calendario/fechas + dependencias · **Tareas:** [WEB] wdx6zenjde, [LS02] wdx6zenj7x, [S11] wdx6zenj5u

WEB (8→13) no puede publicarse sin los DNS del cliente (⛔ no recibidos a 7 jul). LS02 (13→14) arranca el MISMO día en que vence WEB y necesita el formulario publicado para probar el trigger 'Form Submitted' real. Si LS02 termina el 14, su validación cae dentro de la propia ventana de S11 (start 14 jul) sin margen alguno. Y como S11 solo depende de SP04 y BOT, un retraso de WEB/LS02 no bloquearía formalmente el arranque de la validación: se validaría con la captación web sin probar.

> Evidencia: wdx6zenjde: '⛔ DNS del dominio (accesos del cliente) para publicar bajo termosycalentadoresgranada.com o termical.com'; dependencia ClickUp LS02←WEB; fechas: WEB due 1783926000000 (13 jul) = LS02 start; LS02 due 1784012400000 (14 jul) = S11 start; dependencias de wdx6zenj5u: solo SP04 y BOT.

**Recomendación:** Fijar fecha límite interna para los DNS (9 jul) con plan B para probar LS02 sin dominio propio (publicar en subdominio/dominio temporal de GHL); añadir S11←LS02 y adelantar LS02 si la one-page está lista antes del 13.

**Matiz del verificador:** Matiz técnico sobre GHL: el trigger "Form Submitted" de LS02 SÍ puede probarse sin los DNS del cliente, porque los funnels/sites de GHL publican de inmediato en una URL alojada por GHL (subdominio por defecto); los DNS solo bloquean la publicación bajo el dominio propio (subtarea 4 de WEB) y la baja de WordPress. O sea, el bloqueo de LS02 es formal (dependencia ClickUp LS02←WEB con WEB definida como "publicada en el dominio"), no una imposibilidad técnica — el "plan B" que recomienda el auditor ya existe de forma nativa en GHL. El riesgo real y vigente es la cadena de fechas sin holgura (WEB due 13 = LS02 start; LS02 due 14 = S11 start) condicionada a un entregable del cliente pendiente, más el hecho verificado de que S11 no cubre ni depende de la captación web.

### 26. LS01, SP-V y SP-N tienen CERO dependencias en ClickUp y vencen el 9 jul, el mismo día en que S02 conecta la WABA de la que dependen
**Área:** dependencias + calendario/fechas · **Tareas:** [LS01] wdx6zenj71, [SP-V] wdx6zenj8d, [SP-N] wdx6zenj8u, [S02] wdx6zenj4e

Las tres tareas declaran sus bloqueantes en el propio cuerpo, pero en ClickUp dependencies está vacío. LS01 dispara con 'Contact Created (canal WhatsApp)' y SP-V tiene un nodo Send WhatsApp: sin S02 terminada no pueden probarse. Las tres vencen el 9 jul, el mismo due de S02, cuya migración se coordinará con el cliente 'en horario de baja actividad': solape de mismo día sin margen, y si S02 se mueve el grafo no avisa a nadie. Ojo: la dependencia del BOT que citan SP-V/SP-N es de ACTIVACIÓN (el bot vence el 11, después de ellas) — crearla como waiting_on invertiría las fechas; debe documentarse como orden de activación, no como bloqueo de construcción.

> Evidencia: wdx6zenj71 descripción: 'Dependencias: S04 Custom fields (fuente_contacto, fecha_primer_contacto) · S05 Pipeline + tags · S02 WhatsApp API activa' con dependencies:[] en ClickUp; wdx6zenj8d: 'Dependencias: S05 Tags · Bot con reglas de agendado configuradas · S06 Calendarios creados' con dependencies:[]; wdx6zenj8u: 'Dependencias: Bot con captura de campos activa · S05 Tags' con dependencies:[]; due de las tres = 1783580400000 (9 jul) = due de S02.

**Recomendación:** Crear en ClickUp: LS01←S02, LS01←S04, LS01←S05; SP-V←S02, SP-V←S05, SP-V←S06; SP-N←S05. Valorar mover el due de LS01/SP-V al 10 jul (de todas formas no se prueban sin la WABA estable) y anotar la relación con BOT como orden de activación.

**Matiz del verificador:** Matiz de alcance: la ausencia de S02 impide probar/activar LS01 y SP-V, no construirlas (los workflows pueden montarse en GHL sin la WABA viva), cosa que el hallazgo ya reconoce parcialmente. El riesgo central que justifica la severidad "mayor" es que, si S02 se desplaza, el grafo de ClickUp no avisa a los responsables de las tres tareas del 9 jul, y el solape de mismo día deja ventana cero para la validación. La recomendación de aristas es consistente con las fechas (S04/S05/S06 vencen el 8 jul, S02 el 9), sin inversiones.

### 27. Germán tiene 4 entregas que vencen el mismo jueves 9 jul, incluida la migración WABA coordinada con el cliente, que además bloquea la tarea URGENT de Oliver
**Área:** carga por persona · **Tareas:** [S02] wdx6zenj4e, [S08] wdx6zenj5j, [S10] wdx6zenj5t, [SP-N] wdx6zenj8u

El 9 jul Germán debe cerrar: S02 (migrar el 644 962 421 a WABA, coordinado con el cliente 'en horario de baja actividad'), S08 (formulario interno), S10 (carga de KB, con su ítem 2 bloqueado por el cliente) y SP-N (workflow 9→9). S02 bloquea S03 (URGENT, Oliver) ese mismo día: cualquier retraso de Germán arrastra la cadena de templates Meta (hallazgo 1). Mientras, el 8 jul solo tiene S04 y el arranque de S10.

> Evidencia: Cuatro tareas asignadas a 180203721 con due 1783580400000 (9 jul): wdx6zenj4e, wdx6zenj5j, wdx6zenj5t, wdx6zenj8u; wdx6zenj4e: 'Coordinar la migración en horario de baja actividad'; dependencia ClickUp S03←S02.

**Recomendación:** Adelantar S08 al 8 jul (solo requiere S04, que vence ese mismo día 8) o reasignar SP-N; ejecutar S02 a primera hora del 9 para liberar S03 de Oliver.

**Matiz del verificador:** Dos precisiones que no cambian el veredicto: (a) S03 no vence el 9 jul sino el 10 (1783666800000); lo que ocurre el 9 es su start, de modo que S02 debe cerrarse ese día para que Oliver pueda arrancar — la frase "ese mismo día" es correcta respecto al arranque, no al vencimiento de S03. (b) Parte de la carga del 9 es liviana: SP-N es un workflow de solo 3 nodos y el ítem 1 de S10 (FAQs) está "✅ Listo para cargar" con start el 8 jul, mientras que el ítem 2 (catálogo) está ⛔ bloqueado por el cliente y no se puede completar el 9 de todos modos. El riesgo central se mantiene: S02 exige coordinación con el cliente en horario de baja actividad y es cuello de botella del día para la tarea URGENT S03, cuya latencia externa de Meta (24-48h) es la verdadera ruta crítica.

### 28. Henry tiene 4 frentes el viernes 10 jul: cerrar S09 (que bloquea SP04 arrancando ese mismo día), AP01 completa, y arrancar BOT y SP03 en paralelo
**Área:** carga por persona · **Tareas:** [S09] wdx6zenj5p, [AP01] wdx6zenjc2, [BOT] wdx6zenj5w, [SP03] wdx6zenjb0, [SP04] wdx6zenj96

El 10 jul Henry debe: terminar S09 (plantilla D&C, pieza crítica del flujo B y bloqueante de SP04, que Germán arranca ese MISMO día — solape bloqueante/bloqueada sin margen), ejecutar AP01 entera (10→10) y arrancar BOT (10→11, 8 subtareas, con due en sábado) y SP03 (10→13). Si S09 se desliza unas horas, SP04 (URGENT) pierde su día de arranque; si BOT no avanza el viernes, su cierre cae en fin de semana.

> Evidencia: Cuatro tareas de 111980811 activas el 10 jul: S09 due 1783666800000, AP01 start=due 1783666800000, BOT start 1783666800000, SP03 start 1783666800000; dependencia ClickUp SP04←S09 con SP04 start (10 jul) = S09 due (10 jul).

**Recomendación:** Mover AP01 al 13 jul (no tiene dependientes en el grafo y es una red de seguridad de 4 nodos) o reasignarla; priorizar el cierre de S09 en la mañana del 10 para no frenar a Germán en SP04.

**Matiz del verificador:** Dos matices que refuerzan el hallazgo: (1) el 11-12 jul es fin de semana, así que Germán solo dispone de 2 días hábiles (vie 10 y lun 13) para las 8 subtareas de SP04 antes de que S11 arranque el 14 — cada hora que S09 se deslice el viernes recorta ese margen a la mitad de un día; (2) Flujo A (wdx6zenjby, también de Henry, 13 jul) también depende de S09 en ClickUp, un segundo dependiente que el hallazgo no menciona y que añade otra razón para cerrar S09 en la mañana del 10.

### 29. La encuesta 1-5 no tiene mecanismo de captura: falta el 'Wait for Customer Reply' y la condición IF 'Valor de la encuesta' no existe en GHL
**Área:** 04 Active Projects — AP02+PS01 (encuesta-filtro) · **Tareas:** wdx6zenjcx, wdx6zenjcz, wdx6zenjck

AP02 encadena Send WhatsApp (encuesta) → IF/Else directamente, sin ningún nodo que espere ni lea la respuesta del cliente. En GHL el IF/Else solo evalúa campos, tags y datos de oportunidad ya existentes: no hay condición 'valor de la encuesta', no existe ninguna variable con el cuerpo del último mensaje utilizable en el IF, y la respuesta numérica no se guarda sola en ningún campo. Implementado tal cual, el IF se evaluaría segundos después del envío con dato vacío y todos los contactos caerían por la rama 'NONE (4-5)': el link público de reseña de Google llegaría también a los clientes insatisfechos, justo lo que el filtro debía evitar. La mecánica real de GHL: (a) paso Wait de tipo 'Customer Replied' tras el envío, y (b) evaluar el contenido con un SEGUNDO workflow disparado por el trigger 'Customer Replied' con filtros 'contains phrase' (1/2/3 vs 4/5), Reply Channel = WhatsApp y un tag de control, o volcar la respuesta a un campo con una acción de IA y recién ahí el IF.

> Evidencia: wdx6zenjcx: 'Captura | Respuesta numérica 1-5 a un campo/variable para el IF'. wdx6zenjcz: 'Condition | Valor de la encuesta'. Entre ambos nodos no existe ninguna subtarea de espera/captura (secuencia: Trigger → Wait 4 horas → Send → IF).

**Recomendación:** Rediseñar AP02 en dos workflows y documentarlo en las subtareas antes del 13 jul: AP02a (trigger etapa Completado → Wait 4h → template encuesta → Add Tag encuesta-enviada) y AP02b (trigger Customer Replied filtrado por tag encuesta-enviada + frases 1-5 → rama 1-3 notificación interna / rama 4-5 agradecimiento+link → Remove Tag). Mantener la validación S11-5 sobre este nuevo diseño.

**Matiz del verificador:** Dos matices que no cambian el veredicto: (1) el gap no fue totalmente inadvertido — el propio diseño lo flageó como riesgo en la validación S11-5 (CLAUDE.md: 'Encuesta 1-5: captura de respuesta numérica para el IF') y en el contexto de wdx6zenjcx ('Si no, usar botones/opciones'); el problema es que se dejó como validación tardía (14-15 jul) en vez de resolverse en el diseño, y el fallback de botones tampoco funciona porque GHL no mapea el payload del botón a un campo evaluable por el IF. (2) La severidad 'mayor' es correcta y no está inflada: implementado tal cual invierte el propósito del filtro (link de reseña a insatisfechos) y obliga a rediseñar AP02 antes del 13 jul, pero no bloquea el go-live del núcleo del sistema (reseñas es un adicional de €190).

### 30. S03 prepara 7 plantillas Meta pero el sistema necesita al menos 9-10: faltan follow-up día 3, follow-up día 5 y la confirmación de trabajo de AP01
**Área:** 00 Setup — S03 Templates Meta (ventana 24h WhatsApp) · **Tareas:** wdx6zenj4k, wdx6zenj6t, wdx6zenjch, wdx6zenjaw

Los 7 templates de S03 cubren SP03 (confirmación + 2 recordatorios), SP06 (2 seguimientos) y AP02+PS01 (encuesta + agradecimiento). Quedan fuera envíos que también saldrán fuera de la ventana de 24h: (1)-(2) los follow-ups por inactividad del bot en día 3 y día 5 (tarea wdx6zenj6t) — a 3 y 5 días del último mensaje del cliente Meta exige plantilla aprobada; (3) AP01 'confirmación al cliente (rama SÍ)' (wdx6zenjch): se dispara cuando Termical mueve la etapa a 'Trabajo agendado', que puede ocurrir días después del último WhatsApp del cliente (cierre por teléfono tras la visita) → un mensaje libre sería rechazado y la tarea ni menciona template; (4) riesgo en SP04 (wdx6zenjaw): si Termical aprueba la proforma a la mañana siguiente (>24h desde el último mensaje), el aviso 'te lo he enviado al correo' fallará en silencio — la propia tarea reconoce 'habitualmente' en ventana. Como Meta tarda 24-48h en aprobar y S03 vence el 10 jul, descubrir estas plantillas después obliga a una segunda ronda de aprobación fuera del sprint.

> Evidencia: wdx6zenj4k lista exactamente 7 templates (tabla #1-#7). wdx6zenjch: 'Action type | Send Message → WhatsApp' sin mención de template, con trigger 'Opportunity Stage Changed → Trabajo agendado'. wdx6zenjaw: 'Tipo | Mensaje libre (aún en ventana 24 h habitualmente)'. wdx6zenj6t: '2º follow-up | Día 3 · 3º follow-up | Día 5'.

**Recomendación:** Ampliar S03 a 10 templates antes de enviarlos a Meta el 9 jul: añadir 'follow-up inactividad día 3', 'follow-up inactividad día 5' y 'confirmación de trabajo agendado' (opcional: 'presupuesto enviado al correo'). En aw y ch, anteponer la acción nativa 'WhatsApp Customer Service Window Check' para elegir mensaje libre vs template según la ventana.

**Matiz del verificador:** Dos matices a la recomendación: (a) para los follow-ups día 3/5 del bot, añadir los templates a S03 es necesario pero NO suficiente — el follow-up nativo de Conversation AI (wdx6zenj6t) envía mensajes libres generados por IA y no permite seleccionar plantilla Meta, así que esos dos toques requieren rediseño (p.ej. moverlos a un workflow con Send WhatsApp Template) o quedarán inoperantes fuera de ventana; el 1º follow-up (6h) sí funciona por estar dentro de ventana. (b) Verificar el nombre/existencia exacta de la acción nativa "WhatsApp Customer Service Window Check" en la versión actual de GHL antes de darla como solución; si no está disponible, usar If/Else sobre la fecha del último mensaje entrante o enviar siempre template en los nodos wdx6zenjaw y wdx6zenjch.

### 31. El guard crítico anti-duplicados de SP04 usa estado_proforma como campo de contacto, pero ninguna tarea lo crea y el diseño lo ubica en Oportunidad
**Área:** 00 Setup S04 + 03 Sales Pipeline SP04 — campo estado_proforma · **Tareas:** wdx6zenjam, wdx6zenjar, wdx6zenj4v

Los nodos de SP04 leen y escriben estado_proforma como campo de CONTACTO ('Condition object: Contact' y 'Update Contact Field'), pero S04 —la única tarea que crea custom fields— no lo incluye en ninguno de sus dos folders, y el CLAUDE.md lo define como campo de OPORTUNIDAD. En GHL, 'Update Contact Field' no puede escribir campos de oportunidad, y un IF/Else sobre campos de oportunidad dentro de un workflow disparado por 'Contact Tag Added' no tiene una oportunidad concreta en contexto (un contacto puede tener varias). Implementado tal cual: al construir SP04 (URGENT, 10-13 jul) el campo no existirá, y el guard anti-duplicados —que el propio diseño marca como validación crítica S11-1 y única protección contra doble envío de proforma al cliente final— quedará sin configurar o ligado a un objeto equivocado.

> Evidencia: wdx6zenjam: 'Condition object | Contact · Field | estado_proforma'. wdx6zenjar: 'Actualizar datos de campo (Update Contact Field) · Field | estado_proforma'. CLAUDE.md §4: 'Oportunidad: requiere_visita, estado_proforma (borrador/revisada/enviada)'. La descripción de S04 (wdx6zenj4v) enumera 9 campos y estado_proforma no aparece.

**Recomendación:** Decidir YA (antes del 8 jul, día de S04): crear estado_proforma como campo de CONTACTO en S04 —coherente con los nodos de SP04 y viable en un negocio unipersonal con una oportunidad activa por cliente— y corregir el CLAUDE.md/diseño v2.0. Añadir a S11-1 la prueba específica de que el guard corta un segundo tag aprobar-proforma.

**Matiz del verificador:** Dos matices. (1) El detalle dice que el guard es la "única protección contra doble envío": en rigor SP04 tiene tres mitigaciones (trigger por tag y no por etapa, Remove Tag en nodo 6, y el guard); pero contra el escenario que el propio nodo documenta —Termical re-añade el tag o el flujo A ya envió manualmente— el guard sí es la única barrera, así que la afirmación es esencialmente correcta. (2) El hallazgo se refuerza con evidencia que el auditor no citó: la tarea padre SP04 (wdx6zenj96) lista como dependencia "S04 campo estado_proforma", lo que confirma que la intención era crearlo en S04 y que la omisión es un olvido, no un diseño alternativo; la corrección natural es añadirlo a S04 como campo de contacto (coherente con los nodos de SP04) y actualizar CLAUDE.md/diseño v2.0. Nota colateral fuera del alcance de este hallazgo: requiere_visita, el otro campo de "Oportunidad" del CLAUDE.md, tampoco lo crea ninguna tarea (0 resultados en el folder).

### 32. 'Contact Created (canal WhatsApp)': el filtro de canal no existe en ese trigger y nunca dispara para contactos existentes que vuelven a escribir
**Área:** 02 Lead Sources — LS01 trigger de entrada · **Tareas:** wdx6zenj7a, wdx6zenj7f

Dos problemas de viabilidad: (1) los filtros documentados del trigger Contact Created son Tag, Custom Fields y 'Created via Source' (manual / form / API); no existe un filtro fiable 'Canal / última fuente = WhatsApp' como pide el nodo. (2) Contact Created solo dispara en el momento de CREACIÓN del contacto: un cliente antiguo que escribe de nuevo meses después jamás re-entra al workflow (independientemente del re-enrollment), por lo que el Guard IF del nodo 2 nunca ejecutará su rama NONE (lógica muerta) y —más grave para el negocio— los clientes recurrentes (reparaciones, sustituciones: el core de Térmycal) no generarán nueva oportunidad en el pipeline; ese lead vuelve a perderse, que es el problema raíz que el proyecto debía resolver. La mecánica real de GHL para 'WhatsApp entrante' es el trigger 'Customer Replied' con filtro Reply Channel = WhatsApp, que dispara con CADA mensaje entrante de contactos nuevos y existentes.

> Evidencia: wdx6zenj7a: 'Trigger | Contact Created · Filtro | Canal / última fuente = WhatsApp' y contexto: 'si vuelve a escribir meses después, el Guard IF del nodo 2 protege su fecha original' — imposible, porque el trigger no vuelve a disparar. wdx6zenj7f: 'Protege contra re-entradas: si el contacto ya existía y vuelve a escribir…'.

**Recomendación:** Cambiar el trigger de LS01 a 'Customer Replied' con filtro Reply Channel = WhatsApp. Mantener el guard de fecha_primer_contacto tal cual (ahora sí tendrá sentido) y añadir un guard de oportunidad (IF: sin oportunidad abierta en Comercial Termical → crear oportunidad; si existe → skip) para no duplicar oportunidades con cada mensaje.

**Matiz del verificador:** Matiz: la frase "ese lead vuelve a perderse" es algo excesiva — el bot Conversation AI atiende la conversación con independencia de LS01 (opera "en paralelo", wdx6zenj71) y los tags pide-presupuesto/pide-visita seguirían notificando a Termical vía SP-N/SP-V; lo que se pierde es la oportunidad en pipeline, la trazabilidad y los pasos Move Opportunity de SP-N/SP-V (sin oportunidad que mover). Precisión a la recomendación: al migrar a Customer Replied hay que también cambiar el "Allow re-enrollment: OFF" documentado (tarea wdx6zenj7a y descripción del padre wdx6zenj71) a re-entrada permitida, o el guard de oportunidad recomendado nunca se evaluará más de una vez por contacto.

### 33. Follow-up nativo del bot en día 3 y día 5: no se entregará por la ventana 24h (el bot no envía plantillas Meta) y 'añadir tag frio' no es un ajuste del Auto Follow-Up
**Área:** 01 Bot Conversation AI — follow-up por inactividad · **Tareas:** wdx6zenj6t

El Auto Follow-Up de Conversation AI existe como feature, pero envía mensajes de sesión generados por el bot, nunca plantillas aprobadas de Meta. Con WhatsApp como ÚNICO canal de la cuenta (telefonía/SMS fuera del alcance por decisión 11 del diseño), los follow-ups de día 3 y día 5 caen siempre fuera de la ventana de 24h y Meta rechazará la entrega; el 'Dynamic Channel Switching' del feature tampoco ayuda porque no hay canal alternativo. Además, el Auto Follow-Up no tiene entre sus ajustes 'añadir tag y detener': aplicar el tag frio requiere un workflow. Solo el follow-up de 6h de inactividad es viable como nativo (aún dentro de ventana). La afirmación de la tarea de que 'es mejor que un workflow separado' invierte la realidad para los toques de día 3 y 5.

> Evidencia: wdx6zenj6t: 'Sección | Conversation AI → Follow-up settings (nativo del bot) … 3º follow-up | Día 5 → añadir tag frio y detener' y contexto: 'El follow-up nativo del bot es mejor que un workflow separado para conversaciones inconclusas'.

**Recomendación:** Dejar nativo solo el follow-up de 6h. Construir día 3 y día 5 como workflow de GHL (Customer Replied + Waits con condición de no-respuesta) usando 2 templates Meta nuevas (añadirlas a S03, ver hallazgo de plantillas) y cerrar con acción Add Tag 'frio'.

**Matiz del verificador:** Dos matices menores que no cambian el veredicto: (1) la mención a "Dynamic Channel Switching" como parte del feature es secundaria y no totalmente verificable, pero irrelevante aquí porque el único canal conversacional es WhatsApp (el email existe en la cuenta para proformas, pero en conversaciones inconclusas por inactividad el email normalmente aún no está capturado, y en todo caso el bot opera sobre WhatsApp). (2) El follow-up de 6h es viable solo si la inactividad se mide desde el último mensaje entrante del contacto (6h < 24h), que es el comportamiento estándar. La recomendación del auditor es coherente con el patrón ya usado en SP06 y requiere efectivamente añadir 2 templates a S03, que hoy solo contempla 7 (ninguno para inactividad). Severidad "mayor" adecuada: fallo silencioso de entrega y retrabajo, sin bloquear el go-live.

### 34. Base + IVA 21% + Total no se puede calcular dentro de la plantilla D&C: las plantillas no tienen fórmulas y solo existe el campo valor_estimado
**Área:** 00 Setup S09 + 03 Sales Pipeline SP04 — plantilla D&C · **Tareas:** wdx6zenj5p, wdx6zenj4v, wdx6zenjaq

Las plantillas de Documents & Contracts insertan merge fields tal cual; no soportan fórmulas ni cálculos sobre ellos. Con un único campo Monetary (valor_estimado = base sin IVA, según S04: 'Importe (+IVA) — lo escribe el bot desde la KB') es imposible que la proforma muestre las tres líneas Base / IVA 21% / Total que replica el formato real de sus presupuestos. La mecánica real de GHL: calcular ANTES del envío con la acción de workflow 'Math Operation' y guardar los resultados en campos de contacto que la plantilla mergee, o usar el bloque de productos/pricing de D&C con tax (descartado por diseño: 'Sin Product List ni Payments: todo por merge de campos'). Tal cual, S09 (9-10 jul) se topará con el problema en plena construcción y SP04 no tendrá los importes correctos para la validación crítica S11-1.

> Evidencia: wdx6zenj5p: 'Importe: valor_estimado → Base + IVA 21% + Total | Merge (Monetary)' y 'Sin Product List ni Payments: todo por merge de campos'. wdx6zenj4v solo define valor_estimado como campo monetario único.

**Recomendación:** Añadir en S04 dos campos de contacto (valor_iva, valor_total) y en SP04 dos nodos 'Math Operation' entre el guard y el Send Document (valor_iva = valor_estimado × 0,21; valor_total = valor_estimado + valor_iva); mergear los tres campos en la plantilla S09. Verificar en S11-1 el formato monetario resultante (decimales, símbolo €).

**Matiz del verificador:** Severidad "mayor" correcta (no crítica): existe degradación elegante documentada a flujo A (S11-1 / SP04: "si falla → todo opera en flujo A"), y en flujo A Termical edita el documento a mano, así que el gap afecta específicamente a la automatización del flujo B (~80% de casos, partida Proforma €430). Matices: (a) el hallazgo se sostiene bajo cualquier lectura de valor_estimado (base o total): con un solo campo nunca se pueden derivar las otras dos líneas dentro de la plantilla; (b) aplicar la recomendación cambia la anatomía documentada de SP04 de 8 a 10 nodos — habría que actualizar también la tarea padre wdx6zenj96, CLAUDE.md y el diagrama técnico de Figma, no solo S04/S09; (c) los nuevos campos valor_iva y valor_total deben crearse en el folder Proforma de CONTACTO (mismo motivo que valor_estimado: el merge de D&C lee contacto).

### 35. El IF '¿Existe appointment asociado en calendario Trabajos?' no es una condición disponible en los workflows de GHL
**Área:** 04 Active Projects — AP01 · **Tareas:** wdx6zenjc7, wdx6zenjc2

El IF/Else de GHL evalúa campos de contacto, tags, custom fields y datos de oportunidad; no existe ninguna condición que consulte si el contacto tiene una cita creada en un calendario concreto. El nodo, tal como está descrito, no se puede configurar y AP01 quedará bloqueado en construcción (10 jul). Mecánica real: un workflow auxiliar con trigger 'Appointment Status' filtrado al calendario Trabajos que aplique un tag o campo (p. ej. trabajo-agendado) cuando se crea la cita, y AP01 —tras un Wait corto para dar margen a que Termical registre la cita— evalúa ese tag en el IF; o invertir la arquitectura: la confirmación al cliente sale del workflow de cita (SP03 ya escucha el calendario Trabajos) y AP01 se limita a la rama 'falta agendar'.

> Evidencia: wdx6zenjc7: 'Action type | IF / Else · Condition | ¿Existe appointment asociado en calendario Trabajos?'.

**Recomendación:** Redefinir el nodo: workflow puente 'Appointment Status (calendario Trabajos) → Add Tag trabajo-agendado' + en AP01 'Wait 30-60 min → IF Contact Tag incluye trabajo-agendado' (rama NO → recordatorio interno). Documentarlo en la subtarea antes del 10 jul.

**Matiz del verificador:** Dos matices menores: (1) el calendario "Trabajos" sí está previsto en el diseño (S06 lo define como "Trabajos / instalaciones"), así que el problema es exclusivamente el tipo de condición del IF, no la referencia al calendario; (2) la recomendación afirma que "SP03 ya escucha el calendario Trabajos", pero SP03 se dispara por Appointment Confirmed sin filtro de calendario documentado (cubriría también el calendario Visitas), de modo que el workflow puente —o la variante de mover la confirmación a SP03— necesita añadir explícitamente el filtro de calendario para no etiquetar/confirmar citas de visita como trabajos. La severidad "mayor" es adecuada: bloquea/obliga a rediseñar AP01 (10 jul) pero AP01 es una red de seguridad, no rompe el go-live completo.

### 36. PS02 vence el 14 jul pero la conexión de la ficha GBP —dependencia dura reconocida— no tiene tarea en ClickUp y está planificada para después del sprint
**Área:** 05 Reviews — PS02 + dependencia GBP · **Tareas:** wdx6zenjd3, wdx6zenjd4, wdx6zenjd2

Las tres mecánicas de reseñas requieren Google Business Profile conectado en la subcuenta: la auto-respuesta IA de Reputation (existe en GHL como Review AI, pero solo opera sobre fuentes conectadas), la notificación por nueva reseña (trigger 'Review Received', también dependiente de la integración) y el {{link reseña Google}} que AP02 envía a los clientes 4-5. Según el CLAUDE.md, la conexión de GBP está en el 'onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla (él no pasa claves)', es decir, fuera del sprint 8-15 jul y sin fecha, y en las 20 dependencias de ClickUp la única de PS02 es PS02←AP02. Resultado: PS02 (due 14 jul) no se podrá configurar ni probar en fecha, y el template de agradecimiento de AP02 saldrá sin link real de reseña.

> Evidencia: wdx6zenjd4 (contexto): 'Dependencia dura: la ficha GBP debe estar conectada. Sin conexión, este módulo no funciona.' wdx6zenjd2: 'Requiere el link de reseña de la ficha GBP (conectada en onboarding con el cliente)'. CLAUDE.md §12: 'Onboarding posterior con el cliente: conectar GBP…'. Dependencias §5: solo 'PS02←AP02'.

**Recomendación:** Crear tarea 'Conectar GBP con el cliente (sesión guiada por pantalla)' con fecha ≤13 jul y dependencias PS02←GBP y AP02+PS01←GBP; si el cliente no puede antes del 14, reprogramar PS02 explícitamente fuera del sprint para no falsear el plan.

**Matiz del verificador:** Matiz sobre AP02 (wdx6zenjd2): el {{link reseña Google}} no exige técnicamente la integración GBP en GHL — el link público de reseña de la ficha (g.page/r/…/review) puede obtenerse y cargarse como custom value sin la sesión de onboarding, así que esa parte es mitigable en fecha con un workaround; el bloqueo duro sin alternativa es PS02 (auto-respuesta Review AI y notificación de nueva reseña, wdx6zenjd4/wdx6zenjd8). La recomendación sigue siendo válida, pero la dependencia AP02←GBP propuesta sería "blanda" (solo el valor del link), mientras que PS02←GBP sí es dura.

### 37. PS02 vence el 14 jul pero su dependencia dura (conectar Google Business Profile) no tiene tarea ni fecha: está planificada como 'onboarding posterior'
**Área:** gestión / dependencias — 🌟 05 · Reviews · **Tareas:** wdx6zenjd3 [PS02] Respuesta IA a reseñas de Google (Reputación), wdx6zenjd4 Config Reputation: activar auto-respuesta IA a nuevas reseñas

La tarea padre y la subtarea 1 reconocen que sin la ficha GBP conectada el módulo Reputation no funciona, pero en ClickUp no existe ninguna tarea para esa conexión (no está entre las 24 tareas padre del folder ni en las 20 dependencias). Según el CLAUDE.md, la conexión de GBP se hará 'guiado por pantalla' con el cliente en un onboarding POSTERIOR al sprint, sin fecha. Resultado: el 14 jul Oliver no podrá activar ni probar la auto-respuesta IA ni la notificación de reseñas; la fecha de PS02 es inviable tal como está planificado y la dependencia solo existe como texto en la descripción, no como bloqueo real en ClickUp.

> Evidencia: Tarea PS02: 'Ficha Google Business Profile conectada al sistema (la conecta el CLIENTE guiado en la llamada de onboarding — no pasa claves)'. Subtarea wdx6zenjd4: 'Dependencia dura: la ficha GBP debe estar conectada. Sin conexión, este módulo no funciona.' CLAUDE.md §12: 'Onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla (él no pasa claves)'.

**Recomendación:** Crear una tarea 'Conectar Google Business Profile (llamada guiada con el cliente)' con fecha ≤13 jul y marcarla como bloqueante (waiting_on) de PS02; si la llamada de onboarding no puede adelantarse, mover PS02 fuera del sprint y documentar que queda pendiente de esa llamada, en vez de mantener una fecha que se incumplirá.

**Matiz del verificador:** Matiz menor: no todo PS02 es inviable el 14 jul — la parte estática (subtarea wdx6zenjd5, tono de las respuestas IA, y dejar en borrador el workflow de notificación) puede prepararse sin GBP conectado; lo imposible sin la conexión es activar la auto-respuesta y probar/validar el módulo (subtareas wdx6zenjd4 y wdx6zenjd8), que es el núcleo de la tarea. Además, PS02 tiene prioridad "low" en ClickUp, lo que sugiere que el equipo ya la trata como blanda, pero eso no está reflejado ni en la fecha ni en una dependencia formal. La recomendación del auditor es válida con una precisión: si se crea la tarea de conexión GBP con fecha ≤13 jul, requiere adelantar la llamada de onboarding con el cliente al sprint, cosa que hoy no está prevista en ningún documento.

### 38. La auto-respuesta IA se activa sin filtro de estrellas ni modo (Suggestive/Auto-Pilot): la IA respondería en público reseñas negativas sin aprobación humana
**Área:** reglas del proyecto / viabilidad GHL — 🌟 05 · Reviews · **Tareas:** wdx6zenjd4 Config Reputation: activar auto-respuesta IA a nuevas reseñas

La subtarea solo define como alcance 'incluir reseñas solo-estrellas', pero no acota a qué ratings responde la IA en automático ni en qué modo arranca. GHL Reputation permite configurar la respuesta IA por rango de estrellas y en modo sugerido (borrador para aprobar) o auto-pilot. Tal como está escrita, un técnico activaría auto-respuesta para TODAS las reseñas, incluidas las de 1-3 estrellas — que el propio PS02 admite que pueden colarse pese al filtro de PS01 ('Especialmente útil si una reseña negativa se cuela pese al filtro de PS01'). Una IA agradeciendo automáticamente una reseña de 1 estrella daña la reputación del cliente y choca con la regla de arquitectura de que nada se envía sin aprobación humana; PS02 es la excepción aprobada para agradecer, no para gestionar insatisfechos en público.

> Evidencia: Subtarea wdx6zenjd4: 'Alcance | Incluir reseñas solo-estrellas (sin comentario)' (único alcance definido; no hay fila de rating ni de modo). CLAUDE.md §0: 'El sistema nunca envía nada sin aprobación humana ("la última palabra la tiene el humano" — Henry). Regla de arquitectura, no de estilo.' CLAUDE.md §4 dec. 9: '1-3 notificación interna (gestionar insatisfecho)'.

**Recomendación:** Añadir a la tabla de la subtarea: auto-respuesta IA solo para reseñas 4-5 estrellas; para 1-3 estrellas modo sugerido/manual (borrador que aprueba Termical) apoyado en la notificación interna de wdx6zenjd8. Replicar el patrón ya decidido para el bot (arranque Suggestive → Auto-Pilot tras validar el tono).

**Matiz del verificador:** Dos matices de precisión: (1) la subtarea SÍ define una fila "Modo" ("Respuesta automática con IA"), es decir, no omite el modo sino que fija implícitamente full-auto sin distinguir Suggestive vs Auto-Pilot ni acotar ratings — el problema es la falta de acotación, no la ausencia total del campo; (2) la invocación de la regla §0 ("nunca sin aprobación humana") debe leerse acotada: la dec. 9 del CLAUDE.md ("PS02: IA responde reseñas") ya aprueba la auto-respuesta como excepción para agradecer (el padre wdx6zenjd3 dice "La IA responde agradeciendo" en el contexto de clientes 4-5 traídos por PS01), por lo que la violación de §0 aplica específicamente al caso no filtrado de reseñas 1-3, tal como el propio hallazgo ya matiza. La recomendación (4-5 en Auto-Pilot, 1-3 en Suggestive/manual apoyado en wdx6zenjd8, replicando el patrón Suggestive→Auto-Pilot de la dec. 1 del bot) es coherente con las capacidades reales de GHL Review AI.

### 39. Contradicción de objeto para estado_proforma: CLAUDE.md lo define como campo de Oportunidad, las subtareas de SP04 lo configuran como campo de Contacto
**Área:** Sales Pipeline · SP04 (exactitud vs diseño) · **Tareas:** wdx6zenjam Guard IF: estado_proforma = enviada → STOP, wdx6zenjar Update Field: estado_proforma = enviada

El diseño v2.0 sitúa estado_proforma (y requiere_visita) a nivel de Oportunidad, pero el guard de SP04 especifica 'Condition object: Contact' y el nodo 4 usa 'Update Contact Field'. Son objetos distintos en GHL: si S04/S09 crean el campo en Oportunidad siguiendo el CLAUDE.md, el técnico que construya SP04 no lo encontrará entre los campos de Contacto (y viceversa), causando retrabajo o un guard mal montado. Nota de viabilidad: con trigger 'Contact Tag Added' (contexto de contacto), la variante Contact es la más robusta y directa en GHL; la variante Oportunidad además es ambigua si el contacto tiene varias oportunidades.

> Evidencia: CLAUDE.md §4 Custom Fields: 'Oportunidad: requiere_visita, estado_proforma (borrador/revisada/enviada)'. Subtarea wdx6zenjam: 'Condition object | Contact · Field | estado_proforma'. Subtarea wdx6zenjar: 'Action type | Actualizar datos de campo (Update Contact Field)'.

**Recomendación:** Decidir explícitamente el objeto (recomendado: Contacto, coherente con el trigger por tag de contacto y con que el merge de D&C lee contacto) y alinear CLAUDE.md, S04 y las dos subtareas para que digan lo mismo.

**Matiz del verificador:** El hallazgo se queda corto en un punto que agrava el problema: la tarea S04 (wdx6zenj4v), citada por el padre SP04 como dependencia ("S04 campo estado_proforma"), NO incluye estado_proforma (ni requiere_visita) en su descripción — solo crea los campos de contacto de los folders General y Proforma. Es decir, hoy ninguna tarea de ClickUp especifica la creación de estado_proforma en ningún objeto: la contradicción es a tres bandas (CLAUDE.md=Oportunidad, SP04=Contacto, S04=ausente). La corrección debe incluir, además de alinear el objeto (recomendado Contacto), añadir explícitamente la creación de estado_proforma y requiere_visita a S04.

### 40. SP06: el trigger dice cubrir también 'Presupuesto formal enviado', pero ambos guards solo comprueban 'Proforma enviada' → los seguimientos nunca saldrán para presupuestos formales
**Área:** Sales Pipeline · SP06 (lógica interna) · **Tareas:** wdx6zenjbc Trigger: Stage Changed → Proforma enviada, wdx6zenjbj Guard IF: ¿sigue en la misma etapa?, wdx6zenjbr Guard IF: ¿sigue igual?

El trigger (y el parent SP06) declaran que el workflow aplica a las etapas 'Proforma enviada' y 'Presupuesto formal enviado'. Sin embargo, los dos guards de salida evalúan 'Etapa actual es igual a "Proforma enviada"' con rama NONE → STOP. Una oportunidad que entre por 'Presupuesto formal enviado' llegará al primer guard (día 2) en una etapa distinta de 'Proforma enviada' y hará STOP silencioso: jamás recibirá seguimiento 1 ni 2. La mitad del alcance declarado del workflow queda inoperante sin que nadie lo note.

> Evidencia: wdx6zenjbc: 'Etapa | Proforma enviada (también aplica a "Presupuesto formal enviado")'. wdx6zenjbj: 'Operator | es igual a "Proforma enviada" ... Rama NONE | STOP (el lead ya avanzó)'.

**Recomendación:** O bien limitar el trigger solo a 'Proforma enviada' (y decidir aparte si el presupuesto formal lleva seguimiento), o bien cambiar los guards a la condición 'etapa actual = etapa de entrada' usando operador incluido-en ['Proforma enviada','Presupuesto formal enviado'] — teniendo en cuenta que un salto de Proforma enviada a Presupuesto formal enviado sí debe cortar la primera cadena.

**Matiz del verificador:** Matiz de impacto: 'la mitad del alcance declarado' es exacto en número de etapas pero no en volumen — ~80% de los casos (flujo B) entran por 'Proforma enviada' y sí reciben seguimiento; el hueco afecta sobre todo a flujo A / presupuestos formales (aerotermia, alto presupuesto). Además, la recomendación del operador incluido-en ['Proforma enviada','Presupuesto formal enviado'] tiene el efecto lateral que el propio auditor reconoce: un salto de Proforma enviada a Presupuesto formal enviado ya no cortaría la primera cadena; la solución limpia en GHL es duplicar el workflow (uno por etapa, cada guard contra su propia etapa) o limitar el trigger a 'Proforma enviada'.

### 41. El procedimiento del Flujo A no actualiza estado_proforma = enviada, dejando sin efecto el guard anti-duplicados de SP04 justo en el escenario que dice proteger
**Área:** Sales Pipeline · Flujo A (completitud / regla anti-duplicados) · **Tareas:** wdx6zenjby [Flujo A], wdx6zenjam Guard IF: estado_proforma = enviada → STOP

El contexto del guard de SP04 afirma que protege contra el caso 'si el flujo A ya envió la proforma manualmente'. Pero los 4 pasos documentados del Flujo A (generar desde plantilla → editar → enviar por email → mover a 'Proforma enviada') no incluyen poner estado_proforma = enviada. Resultado: si Termical envía una proforma por flujo A y luego (por confusión o segundo aviso de SP-N) añade el tag aprobar-proforma, el guard verá estado_proforma ≠ enviada y SP04 enviará una SEGUNDA proforma automática al cliente — exactamente el duplicado que la arquitectura por tag+guard quiere impedir.

> Evidencia: wdx6zenjam: 'Si Termical añade el tag dos veces, o si el flujo A ya envió la proforma manualmente, este Guard impide un segundo envío al cliente'. wdx6zenjby, tabla de pasos: '1 Abrir Documents & Contracts... 2 Editar detalle_trabajo... 3 Enviar manualmente por email · 4 Mover la oportunidad a "Proforma enviada"' — sin paso de actualización de estado_proforma.

**Recomendación:** Añadir al procedimiento del Flujo A un paso 3-bis: 'Marcar estado_proforma = enviada en la ficha' (o automatizarlo con un mini-WF disparado por Document Sent / por la etapa como solo-update de campo, que no envía nada y respeta la regla de triggers de envío por tag).

**Matiz del verificador:** Dos matices. (a) El duplicado no ocurre solo: requiere que Termical añada aprobar-proforma después de un envío por Flujo A (por confusión o por un resumen de SP-N previo); el guard sí funciona para su otro caso declarado (tag añadido dos veces tras un primer envío de SP04, porque el propio SP04 pone estado_proforma = enviada en su nodo 4). Aun así, "mayor" es adecuada: es una defensa documentada como existente pero inoperativa justo en uno de los dos escenarios que dice cubrir, y el arreglo es barato (paso 3-bis manual en wdx6zenjby o mini-WF de solo-update disparado por Document Sent/etapa, sin acciones de envío, compatible con la regla "trigger de envío siempre por tag"). (b) Detalle adicional detectado al verificar, para registrar como hallazgo separado: el guard wdx6zenjam configura Condition object = Contact, pero según CLAUDE.md estado_proforma es campo de OPORTUNIDAD ("Oportunidad: requiere_visita, estado_proforma"), inconsistencia que podría hacer fallar el IF por sí sola.

### 42. SP03 nodo 5 descrito como 'rama paralela' que 'sale directo del trigger': los workflows de GHL son lineales y, en el orden listado, el aviso interno llegaría 2 h antes de la cita en vez de al crearla
**Área:** Sales Pipeline · SP03 (viabilidad GHL / orden de nodos) · **Tareas:** wdx6zenjb9 Aviso interno de la cita a Termical, wdx6zenjb0 [SP03]

La subtarea del aviso interno dice ser 'rama paralela al recordatorio (sale directo del trigger)', pero un workflow de GHL ejecuta acciones en secuencia única (If/Else crea ramas excluyentes, no paralelas): no existe la mecánica de sacar una segunda rama simultánea del trigger. Si el técnico lo construye en el orden del parent (nodo 5, después de 'Wait hasta 2 h antes'), Termical recibiría el aviso de cita confirmada solo 2 horas antes de la visita, no en el momento de crearla, perdiendo su función ('mantiene a Termical al tanto de su agenda'). La instrucción es contradictoria e inejecutable tal cual.

> Evidencia: wdx6zenjb9: 'Rama paralela al recordatorio (sale directo del trigger)'. Parent wdx6zenjb0, tabla de nodos: '4 | Wait + Send | Wait hasta 2 h antes → recordatorio ... 5 | Notificación | Aviso interno de la cita a Termical'.

**Recomendación:** Reordenar: colocar el aviso interno como nodo 2 (inmediatamente tras el trigger, antes de los waits) y renumerar; o extraerlo a un workflow separado con el mismo trigger. Actualizar la tabla del parent y el texto de la subtarea.

**Matiz del verificador:** Matiz de severidad: el propio parent indica que el trigger es "la cita la crea Termical manualmente — el bot no agenda", por lo que el aviso interno notifica a Termical de una cita que él mismo acaba de crear; su valor es confirmatorio y el impacto funcional de recibirlo 2 h antes es modesto (no rompe el sistema ni bloquea el go-live). El hallazgo es real como instrucción contradictoria/inejecutable que causará confusión o retrabajo al constructor, pero la severidad está en el límite mayor/menor; la corrección es trivial (reordenar como nodo 2 y renumerar, o separar en workflow propio con el mismo trigger).

### 43. SP03: la confirmación de cita como 'mensaje libre' asume que crear la cita abre ventana de 24 h — la ventana de WhatsApp depende del último mensaje ENTRANTE del lead, y fallará en silencio en casos frecuentes
**Área:** Sales Pipeline · SP03 (viabilidad GHL / ventana WhatsApp 24 h) · **Tareas:** wdx6zenjb5 Send WhatsApp: confirmación con día y rango horario, wdx6zenjb2 Trigger: Appointment Confirmed

La subtarea justifica el mensaje libre con 'cita recién creada, dentro de ventana', pero la ventana de 24 h de WhatsApp/Meta se abre solo con mensajes entrantes del cliente, no con eventos internos como crear una cita. Casos habituales fuera de ventana: Termical cuadra la visita por llamada telefónica y registra la cita después; registra la cita al día siguiente; y sobre todo las citas del calendario 'Trabajos/instalaciones' (incluido en el trigger), donde el último WhatsApp del cliente puede tener días. En todos ellos el envío libre falla silenciosamente y el cliente se queda sin confirmación, mientras el propio parent solo exige templates para los recordatorios.

> Evidencia: wdx6zenjb5: 'Tipo | Mensaje libre (cita recién creada, dentro de ventana)'. Parent wdx6zenjb0: 'S03 Templates Meta aprobados (recordatorios fuera de ventana 24 h lo requieren)' — la confirmación queda excluida del requisito.

**Recomendación:** Configurar también la confirmación como Template Meta (añadir 'confirmación de cita' a la lista de plantillas de S03, que ya está en curso y vence el 10-jul), o documentar explícitamente el fallback si se decide asumir el riesgo.

**Matiz del verificador:** Matiz importante que cambia el arreglo pero no el defecto: la afirmación "la confirmación queda excluida del requisito" solo es cierta dentro de SP03. La tarea S03 (wdx6zenj4k) YA incluye el template nº 1 "Confirmación de cita (día + rango horario) | Uso: SP03" en su tabla, por lo que la recomendación de "añadir la confirmación a la lista de plantillas de S03" ya está satisfecha. El problema real es una INCONSISTENCIA interna: S03 planifica una plantilla de confirmación para SP03, pero la especificación del nodo (wdx6zenjb5) ordena "Mensaje libre" y el parent wdx6zenjb0 excluye la confirmación del requisito de templates. Corrección concreta: editar wdx6zenjb5 para que el nodo 2 use el template nº 1 de S03 (ya en curso, vence 10-jul) y alinear la nota de dependencias del parent. Severidad "mayor" se sostiene por el fallo silencioso de cara al cliente, aunque el coste de corrección es mínimo al existir ya la plantilla planificada.

### 44. S03 identifica los 7 templates pero no incluye su texto, categoría Meta ni variables — no se puede enviar a aprobación sin redactarlos desde cero
**Área:** CALIDAD DE DESCRIPCIÓN — 00 · Setup · **Tareas:** wdx6zenj4k [S03] Templates Meta WhatsApp

La tarea lista correctamente 7 templates con su workflow de destino (SP03 x3, SP06 x2, AP02+PS01 x2), pero para enviarlos a Meta se necesita el copy exacto con placeholders {{n}}, la categoría (Utility/Marketing, que condiciona aprobación y coste) y los botones si los hay. Sin el texto cerrado, Oliver debe redactarlo el 9 jul sin material revisado, con riesgo de rechazo de Meta y un ciclo extra de 24-48 h que rompería el vencimiento del 10 jul del que dependen SP03, SP06 y AP02.

> Evidencia: La descripción solo indica: "Todos los textos en el tono del negocio (cercano, frases cortas). El template de encuesta debe permitir respuesta numérica simple 1-5" — no contiene ningún texto de template.

**Recomendación:** Redactar y adjuntar a la tarea antes del 9 jul el copy definitivo de los 7 templates con variables, categoría Meta propuesta y botones (especialmente la mecánica de respuesta 1-5 de la encuesta), revisado por el equipo.

**Matiz del verificador:** El detalle "redactarlos desde cero" y "sin material revisado" es impreciso: 5 de los 7 templates YA tienen borrador de copy con variables en subtareas del mismo folder — confirmación "¡Confirmado, {{First Name}}! Nos vemos el {{fecha de la cita}} en la franja de {{rango horario}}..." (wdx6zenjb5), seguimiento 1 "Hola {{First Name}}, ¿pudiste ver el presupuesto?..." (wdx6zenjbn), seguimiento 2 (wdx6zenjbt), encuesta 1-5 "Del 1 al 5, ¿cómo valoras el servicio? (1 = mal · 5 = genial)" (wdx6zenjcx) y agradecimiento+reseña (wdx6zenjd2). Lo que falta de verdad es: (a) texto de los 2 recordatorios de SP03, (b) categoría Meta y botones de los 7, y (c) consolidación/referencia de ese copy en S03, que está asignada a Oliver mientras los borradores viven en subtareas de workflows de Henry y Germán. La recomendación sigue siendo válida pero es consolidar y completar, no redactar desde cero; con ese matiz la severidad "mayor" es defendible solo por el riesgo de plazo (aprobación Meta 24-48 h con vencimiento 10 jul), aunque el esfuerzo real es menor al descrito. Nota adicional: el template 1 (confirmación de cita) figura en S03 como template Meta pero su subtarea wdx6zenjb5 lo configura como "Mensaje libre... dentro de ventana" — inconsistencia a resolver al consolidar.

### 45. S08: el formulario interno no captura identidad del contacto (nombre, teléfono, email) pese a que su caso de uso son leads que aún no existen en el CRM
**Área:** COMPLETITUD / VIABILIDAD GHL — 00 · Setup · **Tareas:** wdx6zenj5j [S08] Formulario interno Proforma

El caso de uso declarado es un lead que NO vino por el bot (visita, llamada, conocido), es decir, un contacto que normalmente no existe todavía en GHL. Los 7 campos listados son todos custom fields del folder Proforma; sin nombre/teléfono/email el submission del formulario no puede crear ni machear el contacto en GHL, y sin email la proforma del flujo posterior (que sale por email) no puede enviarse. Tal como está descrito, el formulario no genera un contacto usable.

> Evidencia: Descripción de S08: "Campos (mapear a custom fields del folder Proforma) tipo_servicio · tipo_aparato · litros_capacidad · paquete_interes · valor_estimado · direccion_servicio · detalle_trabajo (opcional)" — no figura ningún campo estándar de contacto, y el propio propósito dice: "para cuando el lead NO vino por el bot (visita, llamada, conocido)".

**Recomendación:** Añadir Nombre, Teléfono y Email al formulario (sigue siendo rellenable en <60 s) y ajustar el título "7 campos" para que el ejecutor no lo tome como límite literal.

**Matiz del verificador:** Matiz de precisión: en GHL el submission sin email/teléfono SÍ crea un contacto (uno anónimo nuevo por envío, o con sticky contact activo adjunta los datos al contacto cacheado del dispositivo de Termical, que sería el equivocado), así que más que "no puede crear el contacto" el problema es que crea contactos inutilizables o contamina el equivocado — el efecto práctico es el mismo. La severidad "mayor" es correcta y no debe subirse a crítica: solo rompe la vía formulario interno/flujo A y causa retrabajo, mientras que el flujo B vía bot (~80% del volumen) no depende de S08, por lo que no bloquea el go-live.

### 46. S09 asume que la plantilla D&C calcula Base + IVA 21% + Total a partir de un único merge field, pero D&C no hace aritmética sobre merge fields
**Área:** VIABILIDAD GHL — 00 · Setup · **Tareas:** wdx6zenj5p [S09] Plantilla D&C Proforma Termical

Los merge fields de Documents & Contracts solo insertan valores: con un único valor_estimado (Monetary) la plantilla no puede mostrar el importe del IVA ni el Total calculados, y la decisión de diseño excluye el elemento Product List (que sí calcula impuestos). En el flujo B el documento se envía automáticamente sin edición humana, así que saldría con el bloque de importe incompleto o incorrecto — justo el flujo del ~80% de los casos.

> Evidencia: Fila de la plantilla en S09: "Importe: valor_estimado → Base + IVA 21% + Total | Merge (Monetary) — decisión 7/7: precios '+IVA'" junto con "Sin Product List ni Payments: todo por merge de campos". CLAUDE.md §4 decisión 5: "La proforma muestra Base + IVA 21% + Total".

**Recomendación:** Definir el mecanismo antes de construir S09/SP04: por ejemplo, que SP04 calcule iva_calculado y total_estimado con la acción Math Operation de workflows y los escriba en campos de contacto que la plantilla mergea (habría que añadirlos a S04), o mostrar solo Base con leyenda fija "+ 21% IVA = Total". Incluir la comprobación explícitamente en S11-1.

**Matiz del verificador:** Dos matices que no cambian el veredicto: (a) el flujo A no se ve afectado porque Termical edita el documento antes de enviarlo y puede escribir los importes a mano — el defecto es exclusivo del flujo B, como el propio hallazgo indica; (b) la severidad "mayor" (no crítica) es correcta: existe degradación elegante a flujo A y la corrección es barata (GHL sí ofrece la acción Math Operation en workflows para calcular iva/total en campos nuevos de contacto que S04 tendría que añadir). Ojo adicional: S11-1 tal como está redactada valida fidelidad de merge, spam y anti-duplicados, pero NO la completitud aritmética del bloque de importe, por lo que el defecto podría superar la validación pre-go-live si no se añade explícitamente, como recomienda el hallazgo.

### 47. No existe tarea ni paso de redirecciones 301 para no perder el SEO existente del dominio
**Área:** 06 One-page Web · completitud / SEO · **Tareas:** wdx6zenjde, wdx6zenjdr, wdx6zenjdx

Al apuntar los DNS de termosycalentadoresgranada.com a GHL, todas las URLs antiguas del WordPress indexadas en Google pasarán a devolver 404 (la one-page solo tiene una ruta). Ni el padre [WEB], ni la subtarea de SEO local, ni la de publicación contemplan mapear las URLs indexadas y configurar redirecciones (GHL lo soporta en Sites → URL Redirects). El dominio es exact-match con historial; perder esa autoridad contradice el objetivo mismo de la subtarea de SEO local.

> Evidencia: La tabla de subtareas del padre solo lista 4 ítems y el último es «Publicar en el dominio (cuando lleguen DNS) + dar de baja WordPress»; la subtarea SEO solo cubre «Title / meta description · Google Maps · Schema · Keywords». Ninguna menciona redirecciones ni URLs antiguas.

**Recomendación:** Añadir una subtarea antes de publicar: inventariar URLs indexadas (site:termosycalentadoresgranada.com y/o Search Console del cliente), configurar redirecciones 301 en GHL (Sites → URL Redirects) hacia la one-page o sus anclas, y mantener/verificar la propiedad en Search Console tras el cambio de DNS.

**Matiz del verificador:** Dos matices: (1) según CLAUDE.md §1 el WordPress ya está «caído», por lo que parte de las URLs indexadas probablemente ya devuelven error hoy y la equidad SEO ya se está erosionando — la severidad «mayor» es defendible por la pérdida difícil de revertir, pero está en el límite con «menor» dado que la web es un adicional de €420 orientado a Maps/WhatsApp; precisamente por el WordPress caído, las redirecciones convienen cuanto antes, no solo al publicar. (2) La subtarea wdx6zenjdx deja sin decidir el dominio de publicación («termosycalentadoresgranada.com o termical.com — confirmar cuál»); si se elige termical.com, el mapeo de redirecciones desde el dominio antiguo (a nivel dominio completo) se vuelve aún más crítico. Detalle menor: en la UI actual de GHL los URL Redirects viven en Settings → Domains → URL Redirects (no siempre bajo «Sites»), sin impacto en la recomendación.

### 48. «Dar de baja el WordPress» sin salvaguarda del registro del dominio ni de la zona DNS
**Área:** 06 One-page Web · calidad de descripción / riesgo operativo · **Tareas:** wdx6zenjdx

El cliente tiene dominio y hosting contratados juntos («dominio+hosting los tiene él», CLAUDE.md §1). La instrucción del paso 4 no aclara que la baja debe ser SOLO del hosting/instalación WordPress. Si el cliente cancela el paquete completo, o si la zona DNS está alojada en ese mismo hosting, al darlo de baja se caen los registros CNAME/A hacia GHL (web nueva fuera) y los registros de correo del dominio configurados en S01. En el peor caso se pierde el registro del propio dominio.

> Evidencia: Subtarea wdx6zenjdx, paso 4: «Dar de baja el WordPress actual (tras validar que la nueva funciona)» — sin ninguna mención a conservar el registro del dominio ni a dónde queda la gestión DNS tras la baja.

**Recomendación:** Reescribir el paso: «cancelar únicamente el plan de hosting/WordPress; mantener activo el registro del dominio», y añadir un paso previo: verificar dónde está alojada la zona DNS y, si depende del hosting, migrarla (al registrador o a Cloudflare) antes de cancelar, revalidando después que la web GHL y el correo del dominio siguen resolviendo.

**Matiz del verificador:** Dos matices de precisión: (1) el hallazgo dice «sin ninguna mención a conservar el registro del dominio» — correcto, pero conviene reconocer que la tarea SÍ contiene una salvaguarda parcial (no dar de baja hasta validar la web nueva) y que el contexto menciona «El cliente tiene dominio y hosting comprados por él mismo» como dato, aunque sin convertirlo en instrucción; el gap real es la ausencia de la salvaguarda dominio/zona DNS, no la ausencia total de salvaguardas. (2) El riesgo es contingente, no seguro: depende de dónde esté alojada la zona DNS y de cómo ejecute la baja el cliente; el correo personal del cliente es Gmail, así que lo afectado sería el dominio de envío de GHL (SPF/DKIM de S01) y la web, tal como el hallazgo indica. La recomendación propuesta (cancelar solo el hosting + verificar/migrar la zona DNS antes) es correcta y accionable.


## 🟡 Menores

### 49. AP01 declara dependencias (S06 y Pipeline) en su descripción pero no tiene ninguna dependencia creada en ClickUp
**Área:** 🔴 04 · Active Projects — AP01 · **Tareas:** wdx6zenjc2 [AP01] Trabajo agendado

La descripción de la tarea padre lista 'Dependencias: S06 Calendarios · Pipeline', pero el campo dependencies de la tarea en ClickUp está vacío, y AP01 tampoco aparece en la lista de 20 dependencias del CLAUDE.md §5. Hoy las fechas coinciden por casualidad (S05/S06 el 8 jul, AP01 el 10 jul), pero si S06 se desliza nadie lo verá bloqueando AP01. AP02 sí tiene su dependencia de S03 correctamente creada, lo que confirma que en AP01 es una omisión.

> Evidencia: Tarea wdx6zenjc2, descripción: '## Dependencias — S06 Calendarios · Pipeline'; su registro ClickUp devuelve "dependencies": []. CLAUDE.md §5: 'Dependencias creadas (20...)' — AP01 no figura en la lista.

**Recomendación:** Crear en ClickUp las dependencias waiting_on AP01←S06 y AP01←S05 (y AP01←S03 si se añade la plantilla Meta de confirmación).

**Matiz del verificador:** El argumento 'AP02 sí la tiene, lo que confirma que en AP01 es una omisión' es impreciso: el patrón es sistémico, no exclusivo de AP01. LS01 (wdx6zenj71), SP-V (wdx6zenj8d) y SP-N (wdx6zenj8u) también declaran dependencias en su sección '## Dependencias' (S04·S05·S02, S05·Bot·S06 y Bot·S05 respectivamente) y tienen "dependencies": [] — ninguna figura tampoco en la lista de 20. Esto sugiere que las 20 dependencias fueron una selección deliberada de ruta crítica y que ClickUp es consistente con CLAUDE.md; la inconsistencia real es interna a las tareas (descripción vs. relaciones creadas). El riesgo práctico además es bajo: S05/S06 son tareas de día 1 'sin bloqueos' (CLAUDE.md §12) con 2 días de margen sobre AP01. Si se corrige, conviene hacerlo como criterio uniforme (también LS01, SP-V, SP-N) o bien alinear las descripciones con la política de solo-ruta-crítica, no solo parchear AP01.

### 50. El link de reseña de Google depende de la conexión GBP planificada para DESPUÉS del sprint y ninguna validación S11 lo cubre
**Área:** 🔴 04 · Active Projects — AP02+PS01 · **Tareas:** wdx6zenjd2 (4-5) Agradecimiento + link reseña Google + tag resena-solicitada, wdx6zenjck [AP02 + PS01] Cierre → encuesta-filtro → reseña

El nodo 6 envía '{{link reseña Google}}', que requiere la ficha de Google Business Profile conectada; según el CLAUDE.md la conexión de GBP es parte del 'onboarding posterior' con el cliente, fuera del sprint 8-15 jul en el que se construye y valida AP02 (13 jul) y S11 (14-15 jul). Si el workflow se activa en go-live sin el custom value poblado, los clientes 4-5 recibirían el agradecimiento con el link vacío o roto, y las 5 validaciones de S11 no incluyen comprobar este link.

> Evidencia: Tarea wdx6zenjd2: 'Requiere el link de reseña de la ficha GBP (conectada en onboarding con el cliente)'. CLAUDE.md §12: 'Onboarding posterior con el cliente: conectar GBP/redes guiado por pantalla'. CLAUDE.md §4 'Validaciones críticas pre-go-live (S11)': las 5 validaciones no mencionan el link de reseña.

**Recomendación:** Añadir a S11 (o como gate explícito de activación de AP02) la verificación de que el custom value del link de reseña está poblado; mantener el workflow en borrador/desactivado hasta completar el onboarding de GBP.

**Matiz del verificador:** Dos matices que refuerzan y precisan el hallazgo: (a) el hueco es doble — no solo la conexión GBP queda para después del sprint, sino que el placeholder "{{link reseña Google}}" no está definido en ninguna tarea de setup (S07 Custom Values no lo incluye), así que hoy no existe tarea que cree NI que rellene ese valor; (b) técnicamente el link de reseña de Google (URL con Place ID) puede obtenerse sin conectar GBP a GHL, por lo que una mitigación aún más simple que la propuesta es pedir el link al cliente y añadirlo como custom value dentro del sprint (p.ej. en S07), además del gate en S11/activación de AP02. Nótese también que PS02 (wdx6zenjd3) comparte la misma dependencia de GBP, aunque esa tarea sí la documenta explícitamente.

### 51. Mensaje duplicado al cliente: el bot dice 'en breves momentos te contactamos' y el workflow SP-V envía después el mismo WhatsApp
**Área:** Bot IA — Prompt Objetivo (Flujo 3) vs workflow SP-V · **Tareas:** wdx6zenj69 — Prompt — Objetivo (flujos y reglas de derivación)

El prompt Objetivo instruye al bot a responder la frase de cortesía Y aplicar el tag pide-visita; ese mismo tag dispara SP-V, cuyo primer nodo según el diseño es enviar por WhatsApp exactamente ese mensaje. Todo lead que pida visita recibiría el aviso dos veces seguidas (una del bot, otra del workflow), lo que se percibe como sistema robotizado y habrá que retocar en rodaje.

> Evidencia: wdx6zenj69: 'Flujo 3 · Visita/avería | NUNCA agendar: "en breves momentos te contactamos para cuadrar día y hora 👍" → tag `pide-visita`'. CLAUDE.md decisión 4: 'Tag `pide-visita` → WF SP-V: WA "en breves momentos te contactamos" + notificación'.

**Recomendación:** Decidir un único emisor del mensaje: o el bot lo dice y SP-V queda solo con la notificación interna, o el bot solo aplica el tag y la frase la envía SP-V. Documentarlo en ambas tareas (Objetivo y SP-V) para que no lo implementen duplicado.

**Matiz del verificador:** Dos matices de precisión: (a) el duplicado ocurre en el Flujo 3 (visita/avería), no en "todo lead que pida visita": el Flujo 4 (aerotermia) también aplica `pide-visita` pero ahí el bot solo "explica que requiere estudio" sin decir la frase, por lo que ese camino recibiría el mensaje una sola vez (el de SP-V) — cualquier solución debe contemplar ambos caminos: si se quita el Send WhatsApp de SP-V, el lead de aerotermia se queda sin la frase de confirmación. (b) El Send WhatsApp es el nodo 2 de SP-V (el nodo 1 es el trigger), es decir, la primera acción, no literalmente "el primer nodo".

### 52. La descripción del padre declara dependencias de S04 (custom fields) y S05 (tags) que no existen ni en ClickUp ni en el grafo de 20 dependencias del CLAUDE.md
**Área:** Bot IA — Gestión de dependencias · **Tareas:** wdx6zenj5w — [BOT] Conversation AI — configuración completa

La descripción lista 4 dependencias (S02, S04, S05, S10), pero en ClickUp la tarea solo tiene 2 waiting_on (S02 wdx6zenj4e y S10 wdx6zenj5t), igual que el CLAUDE.md ('BOT←S02 · BOT←S10'). Las dependencias de S04 y S05 son funcionalmente reales (Bot Goals escribe en los custom fields de S04 y aplica tags de S05): si S04/S05 se retrasaran, nada en el tracker frenaría al BOT. Hoy no hay riesgo de fecha (S04/S05 vencen el 8 jul y BOT arranca el 10), pero la incoherencia doc/tracker puede confundir.

> Evidencia: Descripción de wdx6zenj5w: 'Dependencias: S02 WhatsApp API conectada · S04 Custom fields · S05 Tags · S10 KB cargada (FAQs mínimo)'. Dependencias reales de la tarea en ClickUp: solo depends_on wdx6zenj4e (S02) y wdx6zenj5t (S10). CLAUDE.md §5: 'BOT←S02 · BOT←S10'.

**Recomendación:** Crear en ClickUp las dependencias BOT←S04 y BOT←S05 (waiting_on) para que tracker y descripción coincidan, o corregir la descripción si se decide no formalizarlas.

**Matiz del verificador:** Matiz mínimo: la sección "Dependencias" de la descripción podría leerse como lista de prerrequisitos funcionales y no como declaración de vínculos del tracker, y el grafo de 20 dependencias parece deliberadamente mínimo (S04/S05 son tareas de día 1 sin bloqueos previos, riesgo práctico casi nulo). Aun así, la incoherencia entre descripción, tracker y CLAUDE.md es objetiva y la recomendación (formalizar BOT←S04 y BOT←S05 o corregir la descripción) es válida.

### 53. El gate de pruebas no incluye escenarios para dos reglas de oro (intento de agendar cita y petición de humano) ni para el procesado de imágenes
**Área:** Bot IA — Pruebas conversacionales (cobertura del gate) · **Tareas:** wdx6zenj6v — Pruebas conversacionales en Suggestive (pre-Auto-Pilot)

La matriz tiene 7 escenarios pero ninguno verifica: (1) que el bot NO agende cuando el cliente propone día/hora ('¿puedes venir el martes a las 10?') — la regla no negociable más importante del diseño; (2) el flujo 5 'pide humano' → tag derivado-humano; (3) el envío de una foto del aparato, pese a que la subtarea de Ajustes declara las imágenes 'clave para la cualificación' y hay toggle específico. Siendo este el gate previo a Auto-Pilot, las reglas críticas quedarían sin validar formalmente.

> Evidencia: wdx6zenj6v lista solo: precio termo 80L, calentador roto, aerotermia, olor a gas, proforma completa, financiación y audio de voz. CLAUDE.md decisión 4: 'AGENDADO 100% MANUAL… el bot NUNCA agenda ni accede al calendario'; wdx6zenj60: 'Procesar imágenes | ON (fotos del aparato — clave para la cualificación)'.

**Recomendación:** Añadir 3 escenarios al gate: 'cliente propone día y hora concretos' → el bot no compromete cita y aplica pide-visita; 'quiero hablar con una persona' → tag derivado-humano y el bot deja de insistir; 'cliente envía foto del calentador' → el bot la interpreta y continúa la cualificación.

**Matiz del verificador:** Matiz: el escenario 2 de la matriz ('Se me ha roto el calentador' → 'te contactamos para cuadrar' + tag pide-visita) ya ejercita parcialmente el flujo 3 y la conducta de no-agendar en su variante pasiva; lo que falta es la variante adversarial en la que el cliente propone día y hora concretos (el caso con mayor riesgo de que el bot comprometa una cita). Los otros dos huecos (flujo 5 derivado-humano y foto del aparato) no tienen cobertura alguna ni en el gate ni en S11. Además, en el escenario de foto el tag esperado sería pide-presupuesto dentro del flujo 2 de cualificación (no existe tag específico de fotos), como bien orienta la recomendación.

### 54. S11 punto 3 valida 'SP02 Notas de voz', un workflow que no existe en ninguna lista ni en el diseño (referencia fantasma)
**Área:** Setup (00) — S11 Validaciones · **Tareas:** wdx6zenj5u [S11] Validaciones pre-go-live

La validación 3 de S11 se refiere a 'SP02 Notas de voz', pero no existe ningún workflow SP02 en el CLAUDE.md (la anatomía salta de SP-N/SP-V a SP03/SP04/SP06) ni tarea alguna en las 7 listas que configure notas de voz salientes. Parece el residuo de un módulo que se cayó del alcance (la propia degradación dice 'o descartar módulo'). Oliver (asignado, due 15 jul) intentará validar algo que nadie ha construido.

> Evidencia: S11: '3 | SP02 Notas de voz: GHL envía audio como adjunto, no como nota de voz nativa — validar cómo se ve en móvil real | Texto personal + audio adjunto, o descartar módulo'. CLAUDE.md §4 solo enumera: 'LS01 … LS02 … SP-N … SP04 … SP-V … SP03 … SP06 … AP01 … AP02+PS01 … PS02'.

**Recomendación:** Editar S11: eliminar la validación 3 o reformularla sin el código SP02 aclarando si las notas de voz salientes están o no en el alcance; si están, crear la tarea correspondiente.

**Matiz del verificador:** Dos matices: (1) la referencia fantasma no es un error de transcripción a ClickUp — el propio CLAUDE.md §4 la incluye en su lista de validaciones S11 ("3. SP02 notas de voz: GHL manda audio como adjunto, no nota de voz nativa — validar en móvil real"), por lo que el residuo proviene del diseño v2.0 y habría que corregirlo también allí, no solo en la tarea; (2) no está claro que el módulo "se cayó del alcance": el presupuesto aprobado (CLAUDE.md §2) incluye un adicional "voz €180" dentro de los Adicionales €790, así que las notas de voz podrían ser un entregable pagado sin tarea ni diseño — al reformular S11-3 el equipo debe decidir explícitamente si ese adicional está en alcance (y crear la tarea correspondiente) o documentar su descarte. La recomendación del auditor sigue siendo válida con ese añadido.

### 55. El CLAUDE.md declara '44 subtareas' pero en ClickUp hay 61 (y la propia suma por workflow del doc da 61)
**Área:** Documentación — CLAUDE.md §3 y §5 · **Tareas:** Folder Termical 1000460000001977 (todas las subtareas)

El folder tiene 85 tareas = 24 padres + 61 subtareas. Las cifras por workflow que el propio doc declara (BOT 8 + LS01 5 + LS02 3 + SP-V 4 + SP-N 3 + SP04 8 + SP03 5 + SP06 8 + AP01 4 + AP02 6 + PS02 3 + WEB 4) suman 61, y los rangos de IDs del §5 cuadran todos con la realidad. El total '44' que aparece dos veces es simplemente erróneo y puede hacer creer en futuras auditorías o handoffs que sobran 17 subtareas o que alguien añadió trabajo fuera de diseño.

> Evidencia: CLAUDE.md §3: 'ClickUp completo (7 listas, 24 tareas padre, 44 subtareas, 20 dependencias…)' y §5: 'Subtareas (44 en total, formato skill "1 nodo = 1 subtarea"…)'. Conteo real vía clickup_filter_tasks: 85 tareas, 24 padres, 61 subtareas.

**Recomendación:** Corregir '44' por '61' en las dos menciones del CLAUDE.md (y en el doc de Drive si replica la cifra).

**Matiz del verificador:** Severidad "menor" correcta: el doc se contradice a sí mismo (su tabla del §5 ya suma 61), así que ClickUp no diverge del diseño; solo hay que corregir la cifra "44"→"61" en las líneas 38 y 133 de /home/user/termycal/CLAUDE.md y, si replica la cifra, en el doc de Drive "Termical — Diseño Técnico GHL v2.0".

### 56. Numeración de workflows con huecos (SP01, SP02, SP05 no existen) y dos esquemas mezclados (SP-N/SP-V nemónicos vs SP03/SP04/SP06 numéricos)
**Área:** Nomenclatura de workflows · **Tareas:** wdx6zenj8d [SP-V], wdx6zenj8u [SP-N], wdx6zenjb0 [SP03], wdx6zenj96 [SP04], wdx6zenjba [SP06], wdx6zenjck [AP02 + PS01]

La serie Sales Pipeline mezcla códigos nemónicos (SP-N, SP-V) con numéricos que arrancan en SP03 y saltan SP05, sin que ningún documento explique la equivalencia (¿SP01=SP-N? ¿SP02=notas de voz descartadas? ¿SP05=?). El hueco ya produjo una referencia colgante real: S11 valida un 'SP02' inexistente. PS01 tampoco tiene tarea propia (vive fusionado en 'AP02 + PS01' en la lista 04, mientras la lista 05 se llama 'PS02 Reputación'). Para un equipo de 3 personas mapeando templates (S03 referencia 'SP03', 'SP06', 'AP02+PS01') y validaciones a workflows, los huecos invitan a error.

> Evidencia: CLAUDE.md §4: 'LS01 … LS02 … SP-N … SP04 … SP-V … SP03 … SP06 … AP01 … AP02+PS01 … PS02' — no existen SP01, SP02 ni SP05. S11 referencia 'SP02 Notas de voz' (inexistente).

**Recomendación:** No renumerar en pleno sprint: añadir al CLAUDE.md (y como comentario fijado en la lista 03) una tabla de equivalencias que aclare que SP01/SP02/SP05 no existen y por qué, y qué cubre cada código.

**Matiz del verificador:** Dos matices: (1) la referencia a "SP02" no vive solo en CLAUDE.md sino también en la tarea viva de ClickUp wdx6zenj5u, lo que refuerza el hallazgo; además, su columna "Si falla" dice "…o descartar módulo", lo que sugiere que SP02 fue un módulo de notas de voz considerado y nunca formalizado — exactamente el tipo de ambigüedad (¿descartado?, ¿pendiente?) que la tabla de equivalencias recomendada debería resolver. (2) Imprecisión leve: la lista 05 no se llama "PS02 Reputación" a secas sino "🌟 05 · Reviews — PS02 Reputación"; no cambia la conclusión.

### 57. S05 dice crear '7 tags' y omite el tag frio, que el diseño incluye y que SP06 y el follow-up del bot aplican
**Área:** Setup (00) — Tags · **Tareas:** wdx6zenj52 [S05] Tags + Pipeline, wdx6zenjbw Add Note + Add Tag: frio, wdx6zenj6t Follow-up por inactividad

El CLAUDE.md define 8 tags (los 7 base '+ frio de follow-ups'), pero S05 instruye 'Crear los 7 tags del sistema' listando solo 7. El tag frio lo aplican la subtarea 8 de SP06 ('Add Tag: frio') y el follow-up por inactividad del bot. Aunque GHL autocrea tags al aplicarlos desde un workflow, si SP06 y el bot lo escriben con variantes distintas (Frio/frío/frio) se rompe la consistencia que el propio S05 exige ('crear exactos').

> Evidencia: CLAUDE.md §4 Tags: '`lead-whatsapp` · `lead-web` · `pide-presupuesto` · `pide-visita` · `derivado-humano` · `aprobar-proforma` · `resena-solicitada` (+ `frio` de follow-ups)'. S05: 'Crear los 7 tags del sistema' — frio no aparece en su lista.

**Recomendación:** Añadir frio a la lista de S05 (8 tags) para crearlo de una vez con la grafía exacta.

**Matiz del verificador:** Matiz al detalle: el riesgo de variantes (Frio/frío/frio) no está en la documentación — las tres menciones en ClickUp ya usan la grafía idéntica 'frio' — sino en la implementación: al no crearse en S05, el tag lo teclearán por separado dos personas distintas (Germán en SP06 el 13 jul, Henry en el bot el 10-11 jul), y la propia subtarea wdx6zenjbw escribe 'frío' con acento en el texto de la nota interna, lo que facilita el tipeo inconsistente. La recomendación de añadir frio a S05 (8 tags, se ejecuta el 8 jul antes que ambos consumidores) es correcta y de coste cero.

### 58. La transición Suggestive → Auto-Pilot (decisión §4.1, a 1-2 semanas del arranque) no tiene tarea ni recordatorio — cae fuera del sprint
**Área:** Bot Conversation AI (01) — post-sprint · **Tareas:** wdx6zenj5w [BOT] Conversation AI, wdx6zenj6v Pruebas conversacionales en Suggestive

La decisión de arquitectura fija arranque en Suggestive y paso a Auto-Pilot tras 1-2 semanas de rodaje con el cliente (~21-29 jul). Existe la subtarea de pruebas pre-Auto-Pilot, pero ninguna tarea con fecha para ejecutar el rodaje supervisado y el switch, que quedan después del 15 jul. Sin ese hito, el bot puede quedarse en Suggestive indefinidamente, lo que obliga a Termical a aprobar cada respuesta y anula el objetivo del proyecto (atender WhatsApp mientras instala).

> Evidencia: CLAUDE.md §4.1: 'Arranque **Suggestive** → Auto-Pilot tras 1-2 semanas'. BOT: 'pasa a **Auto-Pilot** tras validación con el cliente (1-2 semanas de rodaje)' — no hay tarea con fecha posterior al 15 jul en ninguna lista.

**Recomendación:** Crear una tarea 'Rodaje Suggestive + switch a Auto-Pilot' con due ~2 semanas después del go-live (o incluirla en la tarea de onboarding), dependiente de S11 y de las pruebas conversacionales.

**Matiz del verificador:** Dos matices: (a) el rodaje no está totalmente sin rastro — la subtarea wdx6zenj6v lo menciona explícitamente en su contexto como gate pre-Auto-Pilot; lo que falta es un hito con fecha posterior al 15 jul y la acción del switch en sí (la subtarea, sin fecha propia, cerraría nominalmente con su padre el 11 jul, antes del go-live). (b) La frase "anula el objetivo del proyecto" es algo exagerada: durante el rodaje de 1-2 semanas la supervisión humana es intencional; el riesgo real es la ausencia de un hito que cierre ese rodaje, no el modo Suggestive en sí. La recomendación (tarea de rodaje+switch con due ~2 semanas post-go-live, dependiente de S11 y de wdx6zenj6v) es coherente; encajaría también con el "onboarding posterior" de CLAUDE.md §12, que tampoco tiene tarea en ClickUp.

### 59. El borrado de la carpeta Termycal duplicada en Drive es un pendiente declarado sin tarea
**Área:** Housekeeping — Google Drive · **Tareas:** (sin tarea en ClickUp)

El CLAUDE.md lo marca dos veces como pendiente (§6 y §12) pero no hay tarea en ninguna lista. El riesgo práctico es que alguien del equipo encuentre la carpeta duplicada de la raíz y trabaje sobre copias obsoletas del Diseño Técnico v2.0, la KB o el Catálogo, divergiendo de la fuente de verdad en Omnia › Clientes durante el sprint.

> Evidencia: CLAUDE.md §6: '⚠️ PENDIENTE menor: existe carpeta Termycal DUPLICADA en la raíz del Drive personal (17Q6zAuykhvZ1EiVynIkA6HuFyS5msxjG) con copias de los 4 docs — borrar manualmente'. §12 Housekeeping: 'Borrar carpeta Drive duplicada de la raíz'.

**Recomendación:** Borrar la carpeta duplicada ya (2 minutos, cuenta german.borrello@omibu.com) o crear una tarea mínima asignada a Germán con due 8 jul para que no se pierda.

**Matiz del verificador:** Matiz sobre el riesgo descrito: la carpeta duplicada está en la raíz del Drive PERSONAL de la cuenta conectada (german.borrello@omibu.com), no en la unidad compartida Omnia › Clientes, por lo que el escenario de que "alguien del equipo" trabaje sobre copias obsoletas es plausible pero especulativo — la exposición práctica se limita a quien navegue esa raíz personal (principalmente Germán) o a una futura sesión de IA con el Drive MCP conectado que encuentre los duplicados en una búsqueda. El hecho central (pendiente declarado dos veces sin tarea) está confirmado; la recomendación de borrarla ya o crear una tarea mínima para Germán es proporcionada.

### 60. S05 (tags+pipeline) no bloquea a ninguna tarea en el grafo y S04 solo bloquea S08/S09: los workflows que escriben campos y tags no tienen esas aristas pese a declararlas en sus descripciones
**Área:** dependencias · **Tareas:** [S05] wdx6zenj52, [S04] wdx6zenj4v, [BOT] wdx6zenj5w, [LS02] wdx6zenj7x, [AP01] wdx6zenjc2

S05 tiene cero dependencias entrantes y salientes aunque todos los workflows disparan por sus tags o mueven sus etapas. BOT declara depender de S04 y S05 pero en ClickUp solo tiene BOT←S02 y BOT←S10; LS02 declara 'S04 Custom fields · S05 Pipeline' y solo tiene LS02←WEB; AP01 declara 'S06 Calendarios · Pipeline' y no tiene ninguna dependencia. El riesgo de fechas es bajo (S04/S05/S06 vencen el 8 jul, antes que todos los workflows), pero si el día 1 se desliza el grafo no lo señalará a nadie.

> Evidencia: wdx6zenj52 con dependencies:[]; wdx6zenj5w descripción: 'Dependencias: S02 WhatsApp API conectada · S04 Custom fields · S05 Tags · S10 KB cargada (FAQs mínimo)' vs solo BOT←S02 y BOT←S10 en ClickUp; wdx6zenj7x descripción: 'Lista 06: one-page publicada con formulario · S04 Custom fields · S05 Pipeline' vs solo LS02←WEB; wdx6zenjc2 descripción: 'Dependencias: S06 Calendarios · Pipeline' con dependencies:[].

**Recomendación:** Crear BOT←S04, BOT←S05, LS02←S04, LS02←S05 y AP01←S06, y colgar de S05 los workflows que disparan por tag/etapa (SP-N, SP-V, SP04, SP06, AP01, AP02) para que el grafo refleje el diseño.

**Matiz del verificador:** Matiz: el grafo de ClickUp coincide exactamente con la sección "Dependencias creadas (20)" del CLAUDE.md (S05 no aparece en ninguna de las 20 aristas y S04 solo en S09←S04 y S08←S04), de modo que la omisión es consistente con el documento de handoff y no un fallo de carga: la inconsistencia real es entre las descripciones de las propias tareas (que declaran esas dependencias) y el grafo. Al corregir, además de BOT←S04, BOT←S05, LS02←S04, LS02←S05 y AP01←S06, convendría añadir AP01←S05, ya que la "Pipeline" que AP01 declara como dependencia (trigger Opportunity Stage Changed → "Trabajo agendado") se crea en S05; la lista completa de workflows a colgar de S05 (SP-N, SP-V, SP04, SP06, AP02) es recomendación válida pero opcional dado el bajo riesgo de fechas.

### 61. S11 solo depende de SP04 y BOT, pero sus 5 validaciones tocan piezas de S09, S03, AP02, LS02 y Flujo A que no la bloquean
**Área:** dependencias · **Tareas:** [S11] wdx6zenj5u, [AP02+PS01] wdx6zenjck, [SP03] wdx6zenjb0, [LS02] wdx6zenj7x, [Flujo A] wdx6zenjby

La batería de S11 valida: D&C+merge+correo (cubierto vía SP04), captura del bot (cubierto vía BOT), notas de voz, firma digital desde el móvil (S09) y la encuesta 1-5 — cuyo IF vive en AP02+PS01 (due 13 jul) con template de S03. Ni AP02, ni SP03, ni SP06, ni LS02, ni Flujo A bloquean a S11 en ClickUp: si cualquiera se retrasa, S11 figura desbloqueada y la validación arrancaría el 14 con piezas sin terminar.

> Evidencia: Dependencias reales de wdx6zenj5u: solo S11←wdx6zenj96 (SP04) y S11←wdx6zenj5w (BOT); validación 5 de S11: 'Encuesta 1-5: la respuesta numérica se captura correctamente para el IF del workflow' — el 'Router IF: IF nota: 1-3 → interno · 4-5 → reseña' es el nodo 4 de wdx6zenjck.

**Recomendación:** Añadir S11←AP02, S11←SP03, S11←LS02 y S11←FlujoA (waiting_on) para que la ventana 14-15 solo se abra con todos los flujos entregados.

**Matiz del verificador:** El alcance del hallazgo debe recortarse. (1) S09 NO es una pieza descubierta: en ClickUp existe SP04←S09 (wdx6zenj96 depends_on wdx6zenj5p) y S11←SP04, por lo que S09 bloquea a S11 transitivamente — la firma digital (validación 4) y los merge fields de la plantilla (validación 1) quedan cubiertos por esa cadena. (2) Ninguna de las 5 validaciones de S11 toca LS02, SP03 ni Flujo A: "flujo A" aparece solo como fallback ("Si falla → todo opera en flujo A") y LS02/SP03 no se mencionan; recomendar S11←LS02, S11←SP03 y S11←FlujoA no se sustenta en el texto de S11 y sería a lo sumo una sugerencia de gate de go-live. (3) La corrección accionable sustentada es una sola dependencia: S11←AP02 (wdx6zenjck), que además arrastra S03 transitivamente porque AP02←S03 ya existe. (4) Nota: la propia S11 declara degradación elegante para la validación 5 ("Botones/opciones en lugar de número libre"), lo que refuerza que la severidad correcta es "menor".

### 62. La validación S11-3 se refiere a 'SP02 Notas de voz', un módulo que no existe como tarea en ninguna lista del plan
**Área:** alcance/grafo · **Tareas:** [S11] wdx6zenj5u

Tanto la tarea S11 como el propio CLAUDE.md citan SP02 (envío de notas de voz) en la validación 3, pero entre las 24 tareas padre y los 10 workflows del diseño v2.0 (LS01, LS02, SP-N, SP04, SP-V, SP03, SP06, AP01, AP02+PS01, PS02) no hay ningún SP02. O el módulo quedó fuera al pasar al diseño v2.0 y la validación es huérfana, o falta crear y agendar la tarea que lo construye — en cuyo caso también faltarían sus dependencias y fechas en el sprint.

> Evidencia: wdx6zenj5u, fila 3 de la tabla: 'SP02 Notas de voz: GHL envía audio como adjunto, no como nota de voz nativa — validar cómo se ve en móvil real'; CLAUDE.md §Validaciones: '3. SP02 notas de voz: GHL manda audio como adjunto...'; tabla de tareas padre del §5 del CLAUDE.md sin ninguna tarea SP02.

**Recomendación:** Decidir explícitamente: si el módulo de notas de voz sigue en alcance, crear la tarea SP02 con fechas y dependencias (S02, templates si aplica); si no, eliminar la fila 3 de S11 para no validar algo que no se construirá.

**Matiz del verificador:** El detalle del auditor plantea una falsa dicotomía ("la validación es huérfana O falta crear la tarea SP02 con sus dependencias y fechas"). En realidad la funcionalidad de notas de voz SÍ está en alcance y SÍ tiene tarea que la construye: es un ajuste del bot Conversation AI, no un workflow. Evidencia: decisión 1 del CLAUDE.md ("Voice notes ON, imágenes ON, wait 10-15s, máx 15 msgs") y la subtarea del BOT wdx6zenj60 "Ajustes: voice notes ON · imágenes ON · wait 10-15s · máx 15 mensajes". Además el grafo ya cubre la validación: S11 depende de BOT (S11←BOT). Por tanto NO falta crear ninguna tarea SP02 ni sus dependencias; la corrección correcta es solo editorial: renombrar la fila 3 de S11 (y la línea correspondiente del CLAUDE.md) para referirla al ajuste "voice notes" del BOT en lugar de al inexistente "SP02". La validación en sí debe conservarse, no eliminarse.

### 63. Oliver acumula 4 frentes el jueves 9 jul: S03 URGENT (7 templates de la ruta crítica) compite el mismo día con LS01, SP-V y la WEB en curso
**Área:** carga por persona · **Tareas:** [S03] wdx6zenj4k, [LS01] wdx6zenj71, [SP-V] wdx6zenj8d, [WEB] wdx6zenjde, [S06] wdx6zenj54, [S07] wdx6zenj5a

El 8 jul Oliver tiene S06 + S07 + el arranque de WEB (8→13); el 9 jul debe redactar y enviar los 7 templates Meta (S03, URGENT, cuya demora retrasa SP03/SP06/AP02), construir LS01 (5 nodos) y SP-V (4 nodos) —ambas 9→9— y continuar la WEB. Los dos workflows del 9 además no pueden probarse hasta que Germán cierre S02 ese mismo día (ver hallazgo de LS01/SP-V/SP-N), así que compiten con la tarea más urgente del sprint sin poder cerrarse de verdad.

> Evidencia: Tareas de 89242515: S03 start 1783580400000 (9 jul, priority 'urgent'), LS01 start=due 1783580400000, SP-V start=due 1783580400000, WEB start 1783494000000 → due 1783926000000.

**Recomendación:** Mover LS01 y SP-V al 10 jul (siguen llegando antes de la activación del bot el 11) y dejar el 9 de Oliver monográfico para S03; la WEB tiene margen hasta el 13.

**Matiz del verificador:** Dos matices: (1) SP-V no declara S02 como dependencia en su tarjeta (lista S05 · Bot · S06); su acople a S02 es real solo para probar el nodo 2 'Send WhatsApp'. Además, la prueba end-to-end de SP-V depende del bot (que aplica el tag pide-visita) y el BOT no arranca hasta el 10 jul, lo que refuerza aún más que SP-V puede moverse al 10 sin pérdida alguna. (2) La carga del 9 es real pero cuantitativamente moderada: LS01 y SP-V son workflows pequeños (5 y 4 nodos) y la WEB tiene holgura hasta el 13, por lo que la severidad no debe subirse de 'menor'.

### 64. AP01 quiere mergear {{fecha}} y {{rango}} de la cita en un workflow disparado por cambio de etapa, donde no hay appointment en contexto
**Área:** 04 Active Projects — AP01 (merge fields) · **Tareas:** wdx6zenjch, wdx6zenjc4

Los merge fields de cita ({{appointment.start_time}}, etc.) solo se rellenan en workflows cuyo trigger es de appointment. AP01 se dispara por 'Opportunity Stage Changed → Trabajo agendado' (wdx6zenjc4), sin cita en contexto, por lo que {{fecha}} y {{rango}} saldrían vacíos y el cliente recibiría 'Te esperamos el  en la franja  '. Esto refuerza que la confirmación con datos de la cita debe vivir en un workflow disparado por la cita (SP03), no en AP01.

> Evidencia: wdx6zenjch: 'Texto | "¡Genial, {{First Name}}! Queda confirmado tu trabajo. Te esperamos el {{fecha}} en la franja {{rango}}…"' con trigger padre 'Opportunity Stage Changed → Trabajo agendado'.

**Recomendación:** Mover la confirmación con fecha/rango al workflow de cita (SP03 ya cubre el calendario Trabajos) o eliminar los placeholders de fecha del texto de AP01.

**Matiz del verificador:** Dos matices: (a) {{fecha}} y {{rango}} ni siquiera son merge fields válidos de GHL ni campos definidos en el proyecto — no es solo que salgan vacíos por falta de cita en contexto, es que no tienen ninguna fuente de datos posible en este workflow; (b) dado que SP03 nodo 2 ya envía la confirmación con día y rango al confirmarse la cita, el nodo 4 de AP01 es además parcialmente redundante: la corrección más limpia es reformular el texto de AP01 sin fecha/rango (confirmación genérica) o eliminar el nodo, en vez de duplicar la confirmación de SP03, evitando que el cliente reciba dos mensajes de confirmación.

### 65. Doble confirmación al cliente para trabajos: SP03 escucha ambos calendarios y AP01 rama SÍ vuelve a confirmar lo mismo
**Área:** 03 Sales Pipeline SP03 + 04 Active Projects AP01 — duplicidad · **Tareas:** wdx6zenjb2, wdx6zenjch

SP03 se dispara con 'Appointment Status = Confirmed' en 'Visitas/diagnóstico + Trabajos/instalaciones' y envía confirmación inmediata con día y rango. Cuando Termical además mueve la etapa a 'Trabajo agendado', AP01 (rama SÍ del guard) envía una segunda confirmación casi idéntica. El cliente final recibe dos WhatsApp de confirmación por el mismo trabajo, lo que contradice el tono cuidado del sistema y puede confundir.

> Evidencia: wdx6zenjb2: 'Calendarios | Visitas/diagnóstico + Trabajos/instalaciones'. wdx6zenjch: 'Queda confirmado tu trabajo. Te esperamos el {{fecha}}…' (contexto: 'Confirma al cliente que el trabajo… queda cerrado en agenda').

**Recomendación:** Definir un único emisor de la confirmación de trabajo (sugerido: SP03, que sí tiene el contexto de la cita) y dejar en AP01 únicamente la rama de control interno 'falta agendar'.

**Matiz del verificador:** Dos matices: (1) la duplicación depende del orden de acciones de Termical — si mueve la etapa ANTES de crear la cita, AP01 cae en rama NO (aviso interno) y solo habrá una confirmación cuando SP03 dispare; el doble envío ocurre en el orden esperado (cita primero, etapa después). (2) Refuerzo a la recomendación: en GHL un workflow con trigger Opportunity Stage Changed no tiene en contexto los merge fields de la cita, por lo que {{fecha}} y {{rango}} en wdx6zenjch no resolverían de forma fiable de todos modos — la confirmación con datos de cita debe vivir en SP03 y AP01 quedarse solo con la rama de control interno "falta agendar".

### 66. La confirmación de cita como 'mensaje libre' fallará para leads sin sesión de WhatsApp abierta (web o teléfono)
**Área:** 03 Sales Pipeline — SP03 confirmación · **Tareas:** wdx6zenjb5, wdx6zenj4k

La ventana de 24h solo existe si el CLIENTE escribió por WhatsApp en las últimas 24h. Un lead del formulario web (LS02) o uno que cuadró la visita por teléfono no tiene sesión abierta, y Meta rechaza cualquier mensaje libre: la confirmación nunca llega. Además hay incoherencia interna: S03 ya prepara el template #1 'Confirmación de cita (día + rango horario)' precisamente para SP03, pero el nodo indica 'mensaje libre'. Los templates aprobados también se entregan dentro de ventana, así que usarlo siempre no tiene costo funcional.

> Evidencia: wdx6zenjb5: 'Tipo | Mensaje libre (cita recién creada, dentro de ventana)' vs. wdx6zenj4k tabla: '1 | Confirmación de cita (día + rango horario) | SP03'.

**Recomendación:** Configurar el nodo con el template Meta #1 siempre (o anteponer la acción 'WhatsApp Customer Service Window Check' para elegir libre vs template), y alinear la descripción de la subtarea con S03.

**Matiz del verificador:** Dos matices: (1) el fallo es incluso más amplio de lo descrito — también un lead de WhatsApp puede estar fuera de ventana si su último mensaje entrante fue >24h antes de que Termical registre la cita manualmente (p. ej. cuadró la visita por teléfono tras el primer contacto), por lo que la severidad "menor" es conservadora, no inflada; (2) en la recomendación, GHL no tiene una acción nativa de workflow llamada literalmente "WhatsApp Customer Service Window Check" — la solución fiable es la otra propuesta: configurar el nodo con el template Meta #1 siempre y alinear la subtarea wdx6zenjb5 con S03.

### 67. Citas creadas con menos de 24h de antelación: el Wait '1 día antes' queda en el pasado y con el default enviaría el recordatorio equivocado al instante
**Área:** 03 Sales Pipeline — SP03 recordatorios · **Tareas:** wdx6zenjb6, wdx6zenjb7

El Wait de GHL relativo a la hora de la cita existe y es viable, pero cuando el momento configurado ya pasó (cita de avería creada para el mismo día o el siguiente, caso frecuente en Térmycal), el paso ofrece 3 comportamientos: continuar al siguiente paso, saltar a un paso concreto, u omitir las comunicaciones salientes hasta el próximo wait. La subtarea no fija ninguno; con 'continuar', el cliente recibiría el template 'recordatorio 1 día antes' segundos después de la confirmación, con un texto que no corresponde ('mañana').

> Evidencia: wdx6zenjb6: 'Action type 1 | Wait Until → 🏷️ fecha de la cita − 1 día' — sin mención de la opción 'if the timing of this wait step is already in the past'.

**Recomendación:** Especificar en ambas subtareas la opción 'skip all outbound communication actions till next wait' para los waits de −1 día y −2 h, y probar en S11 con una cita creada para el mismo día.

**Matiz del verificador:** Matiz menor: el número exacto de comportamientos que ofrece GHL en el ajuste (2 o 3 opciones, según versión de la UI — la de "saltar a un paso concreto" es más reciente) no es verificable desde aquí, pero no afecta al fondo: la opción recomendada ("skip all outbound communication actions till next wait") existe y el comportamiento sin configurar produce el envío inmediato. En wdx6zenjb7 (−2 h) el impacto es menor que en wdx6zenjb6 porque solo aplica a citas creadas con <2 h de antelación y el texto "en 2 horas" es menos incongruente; el caso grave es el template "1 día antes". Añadir además la prueba de cita mismo-día a la tabla de S11 (wdx6zenj5u), que hoy no la incluye.

### 68. El ejemplo de respuesta usa merge fields de contacto ({{nombre}}, {{aparato}}) que no existen en el contexto de respuesta a reseñas de GHL
**Área:** exactitud / viabilidad GHL — 🌟 05 · Reviews · **Tareas:** wdx6zenjd5 Ajustar tono de las respuestas IA (marca TÉRMYCAL)

El ejemplo de tono incluye '{{aparato}}', pero una reseña de Google no está vinculada al contacto de GHL ni a sus custom fields: la respuesta IA de Reputation no puede saber qué aparato se instaló, y además el campo del diseño se llama `tipo_aparato`, no `aparato`. '{{nombre}}' solo existe como nombre del reseñador que devuelve Google, no como merge field de contacto. Si el técnico intenta montar una plantilla con esos placeholders, saldrán literales o vacíos en respuestas públicas. La configuración real de tono en Reviews AI se hace con instrucciones de estilo/negocio, no con merge fields de contacto.

> Evidencia: Subtarea wdx6zenjd5: 'Ejemplo | "¡Gracias por tu confianza, {{nombre}}! Un placer ayudarte con tu {{aparato}}. Cualquier cosa, aquí estamos 🔧"'. CLAUDE.md Custom Fields: 'Folder Proforma: tipo_servicio, tipo_aparato, litros_capacidad…' (no existe campo `aparato`).

**Recomendación:** Reescribir el ejemplo sin referencias al aparato ni a datos de contacto (p. ej. '¡Gracias por tu confianza! Un placer haberte ayudado. Cualquier cosa, aquí estamos 🔧') y aclarar que el tono se configura como instrucciones de estilo para la IA (cercano, agradecido, castellano de España), no como plantilla con merge fields.

**Matiz del verificador:** Matiz: la parte del nombre sí es alcanzable en la práctica — la IA de Reviews dispone del nombre del reseñador que devuelve Google y suele incluirlo de forma natural en la respuesta, sin necesidad de merge field; el elemento genuinamente irrealizable es {{aparato}} (la reseña no está ligada al contacto ni a `tipo_aparato`). Además, el ejemplo probablemente pretende ser solo ilustrativo del tono, pero al usar sintaxis {{...}} de merge field en una subtarea de configuración literal el riesgo de confusión es real. La recomendación del auditor (reescribir sin placeholders y aclarar que el tono se configura como instrucciones de estilo) es correcta.

### 69. La subtarea de notificación interna no aclara que es un workflow aparte (trigger 'Review Received' + Internal Notification), ni define destinatario/canal, y usa merge fields inventados
**Área:** calidad de descripción / viabilidad GHL — 🌟 05 · Reviews · **Tareas:** wdx6zenjd8 Notificación interna al recibir nueva reseña

La descripción mezcla vocabulario de workflow ('Action type: Internal Notification', 'Disparo: Nueva reseña recibida') sin decir que hay que CREAR un workflow nuevo con el trigger de reseña recibida de GHL (a diferencia de los nodos 1-2, que son configuración del módulo Reputation), ni le da nombre. Tampoco especifica a quién llega la notificación ni por qué canal (email / push de la app / SMS interno), cuando el objetivo es que Alejandro la vea en el móvil. Además, '{{estrellas}}' y '{{texto}}' no son merge fields reales del trigger de reseñas de GHL (los reales son del tipo review rating / review body / reviewer name); copiados tal cual saldrían como texto literal.

> Evidencia: Subtarea wdx6zenjd8: 'Action type | Internal Notification · Disparo | Nueva reseña recibida · Contenido | "⭐ Nueva reseña de {{nombre}}: {{estrellas}} — {{texto}}"' — no menciona crear workflow, ni nombre, ni destinatario/canal. CLAUDE.md §4: 'PS02 Reputación IA (3)' con anatomía completa exigida en las tareas.

**Recomendación:** Completar la subtarea: 'Crear workflow "PS02 - Notificación nueva reseña" con trigger Review Received (fuente Google, todas las estrellas) → acción Send Internal Notification tipo push/email al usuario de Termical', y sustituir los placeholders por los merge fields reales del trigger de reseñas de GHL. Alternativamente, documentar el uso del aviso nativo de Reputation → Settings si se prefiere no crear workflow.

**Matiz del verificador:** Dos matices que refuerzan el hallazgo: (a) también '{{nombre}}' es un placeholder inventado (en contexto de reseña el campo real sería el reviewer name del trigger, no un merge field de contacto en español); (b) la falta de subtarea 'Trigger: ...' en PS02 es una desviación verificable del formato '1 nodo = 1 subtarea' que sí cumplen los otros 9 workflows del folder, lo que hace el hallazgo más sólido de lo que el auditor planteó. La recomendación de nombrar el workflow ('PS02 - Notificación nueva reseña') y fijar canal push+email (coherente con wdx6zenj8z, para que Alejandro lo vea en el móvil) es la corrección adecuada.

### 70. SP03: en citas creadas con menos de 1 día (o 2 h) de antelación, los Wait Until quedan en el pasado y GHL los salta → el cliente recibe confirmación y recordatorios seguidos
**Área:** Sales Pipeline · SP03 (viabilidad GHL / citas de corto plazo) · **Tareas:** wdx6zenjb6 Wait hasta 1 día antes → recordatorio, wdx6zenjb7 Wait hasta 2 h antes → recordatorio

En GHL, si un contacto llega a un Wait configurado a un momento ya pasado (cita − 1 día cuando la cita es hoy o mañana temprano), avanza inmediatamente al siguiente paso. En un negocio de averías y reparaciones donde las visitas de mismo día o día siguiente son la norma (3-4 reparaciones por mañana), muchos leads recibirían confirmación + 'recordatorio 1 día antes' + incluso 'recordatorio 2 h antes' casi consecutivos, lo que resulta spam y quema templates de pago. Ninguna subtarea contempla este caso.

> Evidencia: wdx6zenjb6: 'Wait Until → fecha de la cita − 1 día' y wdx6zenjb7: 'Wait Until → fecha de la cita − 2 horas', sin condición de proximidad. Contexto del parent: 'las reparaciones son 3-4 por mañana'.

**Recomendación:** Añadir tras cada Wait un Guard IF sobre el tiempo restante hasta la cita (o usar la opción de saltar el envío si el momento ya pasó), de modo que el recordatorio de 1 día solo salga si la cita está a más de ~20 h, y el de 2 h solo si queda margen real.

**Matiz del verificador:** Matiz de precisión: el apilamiento de los tres mensajes (confirmación + recordatorio 1 día + recordatorio 2 h) casi consecutivos solo se da si la cita se crea con menos de ~2 h de antelación; en el caso más frecuente (cita creada por la mañana para esa tarde o el día siguiente temprano) lo que se duplica es confirmación + "recordatorio 1 día antes" seguidos, mientras el de 2 h sí sale a su hora. El fondo del hallazgo y la recomendación (guard IF sobre el tiempo restante hasta la cita antes de cada envío) se mantienen.

### 71. SP03 escucha también el calendario 'Trabajos/instalaciones' y AP01 envía su propia confirmación al pasar a 'Trabajo agendado' → doble confirmación WhatsApp por la misma instalación
**Área:** Sales Pipeline · SP03 (solape con AP01) · **Tareas:** wdx6zenjb2 Trigger: Appointment Confirmed, wdx6zenjc2 [AP01] (referencia cruzada)

El trigger de SP03 incluye ambos calendarios ('Visitas/diagnóstico + Trabajos/instalaciones'). Para un trabajo aprobado, la secuencia real es: Termical crea la cita en Trabajos (dispara SP03 → confirmación + recordatorios) y mueve la oportunidad a 'Trabajo agendado' (dispara AP01, cuyo nodo 4 es 'Send WhatsApp: confirmación al cliente' en la rama SÍ del guard de cita creada). El cliente recibe dos confirmaciones casi idénticas por el mismo trabajo. Los recordatorios 1 día/2 h para instalaciones sí tienen sentido; la duplicada es la confirmación.

> Evidencia: wdx6zenjb2: 'Calendarios | Visitas/diagnóstico + Trabajos/instalaciones'. AP01 (wdx6zenjc2), tabla de nodos: '4 | Send WhatsApp | Send WhatsApp: confirmación al cliente (rama SÍ)'.

**Recomendación:** Definir una sola fuente de confirmación por tipo de cita: p. ej. filtrar el envío de confirmación de SP03 al calendario Visitas (manteniendo recordatorios para ambos) o eliminar el Send WhatsApp de AP01 dejándolo solo como red de seguridad interna.

**Matiz del verificador:** Matiz de precisión: la doble confirmación ocurre solo en el camino feliz (la cita en Trabajos ya existe cuando la oportunidad pasa a "Trabajo agendado" → rama SÍ del guard). Si Termical mueve la etapa antes de agendar, AP01 va por la rama NO (recordatorio interno) y solo llega la confirmación de SP03 cuando cree la cita. Además, el propio "Contexto" de AP01 lo define como "Red de seguridad", lo que refuerza la recomendación del auditor de eliminar el Send WhatsApp de la rama SÍ (o filtrar la confirmación de SP03 por calendario) dejando AP01 solo con la alerta interna.

### 72. SP04 nodo 7: el aviso WhatsApp post-envío confía en estar 'habitualmente' en ventana de 24 h, pero el disparo depende de cuándo apruebe Termical y fallará en silencio si aprueba tarde
**Área:** Sales Pipeline · SP04 (ventana WhatsApp 24 h) · **Tareas:** wdx6zenjaw Send WhatsApp (opcional): "Te lo he enviado al correo"

SP04 se dispara cuando Termical añade el tag aprobar-proforma, algo que puede ocurrir horas después de la notificación de SP-N (está instalando durante el día) o a la mañana siguiente. Si han pasado más de 24 h desde el último mensaje entrante del lead, el mensaje libre no se entrega y no hay fallback: el cliente no se entera de que la proforma está en su correo, que es justo lo que este nodo quiere evitar ('reduce que el presupuesto se quede sin ver en la bandeja').

> Evidencia: wdx6zenjaw: 'Tipo | Mensaje libre (aún en ventana 24 h habitualmente)'.

**Recomendación:** Usar un Template Meta 'proforma enviada al correo' (añadirlo al lote de S03, que ya gestiona la aprobación de Meta esta semana) en lugar del mensaje libre, o al menos documentar que el aviso puede no entregarse fuera de ventana.

**Matiz del verificador:** Dos matices que acotan el impacto sin invalidar el hallazgo: (a) el nodo 7 está marcado "opcional" en SP04 y la proforma en sí viaja por email (nodo 3 Send Document), que no depende de la ventana de 24 h — solo se pierde el aviso, no el envío; (b) SP06 (wdx6zenjba) envía un seguimiento por Template Meta al día 2 con trigger Stage Changed → "Proforma enviada" (etapa que SP04 fija en el nodo 5), así que el peor caso real es que el lead tarde ~2 días en enterarse de que tiene la proforma en el correo, no que nunca se entere. Con esos matices, la severidad "menor" asignada es la correcta y la recomendación (añadir un template "proforma enviada al correo" al lote de S03, que aún no lo contempla, o documentar la limitación) sigue siendo pertinente.

### 73. S05 crea solo 7 tags: falta el tag `frio` de los follow-ups (SP06)
**Área:** EXACTITUD — 00 · Setup · **Tareas:** wdx6zenj52 [S05] Tags + Pipeline

El diseño define 8 tags; SP06 aplica `frio` a los leads sin respuesta tras el seguimiento del día 5. Si no se pre-crea en el setup, se creará ad hoc al montar SP06 con riesgo de deriva de nombre (p. ej. "frío" con tilde o "lead-frio"), rompiendo la consistencia que la propia tarea exige.

> Evidencia: Tarea S05: "Crear los 7 tags del sistema" con la lista "lead-whatsapp · lead-web · pide-presupuesto · pide-visita · derivado-humano · aprobar-proforma · resena-solicitada". CLAUDE.md §4: "`lead-whatsapp` · ... · `resena-solicitada` (+ `frio` de follow-ups)".

**Recomendación:** Añadir `frio` a la lista de S05 y corregir el conteo a 8 tags.

**Matiz del verificador:** El riesgo de deriva de nombre que cita el auditor está parcialmente mitigado: SP06 ya especifica el nombre exacto `frio` (sin tilde) tanto en la tabla de nodos como en el nombre de la subtarea wdx6zenjbw, y en GHL la acción "Add Tag" crea el tag automáticamente si no existe, por lo que no hay rotura funcional. El hallazgo queda como inconsistencia de completitud/conteo en S05 frente al diseño (7 vs 8 tags); la recomendación de añadir `frio` a S05 y corregir el conteo sigue siendo válida y la severidad "menor" es correcta.

### 74. S05: los nombres de etapa llevan anotaciones que pueden colarse en el pipeline ("Conversando (bot)", "Cerrado (ganado/perdido)")
**Área:** EXACTITUD — 00 · Setup · **Tareas:** wdx6zenj52 [S05] Tags + Pipeline

Si el técnico crea las etapas literalmente como están escritas, los nombres derivan del diseño y cualquier workflow, filtro o reporte que referencie "Conversando" o "Cerrado" exactos no coincidirá. Además, "(ganado/perdido)" se gestiona en GHL con el estado won/lost de la oportunidad, no con el nombre de la etapa, lo que la anotación no aclara.

> Evidencia: Tarea S05: "1. Nuevo lead → 2. Conversando (bot) → ... → 9. Cerrado (ganado/perdido)" frente a CLAUDE.md §4: "Nuevo lead → Conversando → Visita agendada → Proforma enviada → Presupuesto formal enviado → Aprobado → Trabajo agendado → Completado → Cerrado".

**Recomendación:** Dejar en la tabla de la tarea los 9 nombres exactos sin paréntesis y mover las aclaraciones ("etapa del bot", "cierre con won/lost") al bloque Contexto.

**Matiz del verificador:** Matiz al detalle: el impacto de "cualquier workflow... que referencie Conversando o Cerrado no coincidirá" es hipotético — revisados los workflows del folder, los triggers/movimientos por etapa usan "Completado" (AP02), "Trabajo agendado" (AP01), "Proforma enviada"/"Presupuesto formal enviado" (SP06) y "Nuevo lead" (LS01); ninguno referencia "Conversando" ni "Cerrado". Además, en GHL las etapas se eligen por dropdown en el builder, así que no habría fallo de coincidencia al construir: el riesgo real es la deriva de nomenclatura frente al diseño/diagramas/reportes y la confusión del técnico al montar el cierre (posibles dos etapas o nombre anotado). La recomendación del auditor (nombres limpios en la tabla, aclaraciones al bloque Contexto) sigue siendo válida.

### 75. S03: el título y la descripción exigen "DÍA 1" pero la tarea está planificada 9→10 jul (días 2-3) por la dependencia de la WABA
**Área:** GESTIÓN — 00 · Setup · **Tareas:** wdx6zenj4k [S03] Templates Meta WhatsApp

Contradicción interna: los templates no pueden enviarse a aprobación hasta que exista la WABA (S02 vence el 9), así que el "hacerlo el primer día" es inejecutable tal como está escrito y puede generar confusión o falsa sensación de retraso. El margen real para la aprobación de Meta (24-48 h) queda ajustado contra SP03 (10→13) y SP06 (13).

> Evidencia: Nombre de la tarea: "[S03] Templates Meta WhatsApp — enviar a aprobación DÍA 1" y descripción: "bloquean recordatorios y seguimientos — hacerlo el primer día", frente a start_date 9 jul (1783580400000) / due 10 jul (1783666800000) y la dependencia S03←S02 del CLAUDE.md §5.

**Recomendación:** Reformular el título a "enviar a aprobación en cuanto esté la WABA (9 jul)" y adelantar la redacción de los textos al día 8 para enviar el 9 a primera hora (enlaza con el hallazgo de los textos faltantes).

**Matiz del verificador:** Matiz: las fechas de ClickUp (9→10) son las correctas dada la dependencia de la WABA; lo defectuoso es solo el título/descripción, no la planificación. Además, la parte de la tarea que sí es ejecutable el día 1 es la redacción de los 7 textos (no requiere WABA), lo que refuerza la recomendación del auditor de separar "redactar el 8" de "enviar a aprobación el 9". La tarea ya tiene prioridad "urgent" en ClickUp, así que la urgencia no depende del "DÍA 1" del título y puede eliminarse sin perder señal.

### 76. S10: la descripción sigue marcando TODO el catálogo como bloqueado cuando la familia de calentadores de gas ya se recibió el 7/7
**Área:** CALIDAD DE DESCRIPCIÓN — 00 · Setup · **Tareas:** wdx6zenj5t [S10] Knowledge Base

La descripción y el título marcan el catálogo completo con ⛔ "esperando el correo del cliente", pero la primera familia (calentadores de gas, con precios reales y paquetes orientativos 478/578/356 € +IVA) ya llegó y está integrada según el comentario de la propia tarea. Quien ejecute S10 el 8-9 jul guiándose por la descripción puede dejar fuera de la KB la única familia con precios disponibles.

> Evidencia: Descripción S10: "el catálogo de paquetes está ⛔ bloqueado esperando el correo del cliente" y fila 2 "⛔ Esperando cliente"; comentario 1000460000029951 en la misma tarea: "cuando se cargue la KB, esta familia ya se puede meter"; CLAUDE.md §8: "FAMILIA CALENTADORES DE GAS (recibida 7/7 por email+PDF)".

**Recomendación:** Actualizar la descripción: cargar FAQs v2 + familia calentadores de gas ya recibida; dejar como bloqueado solo termos eléctricos y calderas (y confirmar los 2-3 modelos "estrella").

**Matiz del verificador:** Dos matices: (a) el riesgo de que el ejecutor "deje fuera la única familia con precios" está atenuado porque la información correcta está en la propia tarea como comentario visible (el asignado de S10, Germán, es además el autor del comentario), así que es desactualización de descripción, no ausencia de información; (b) el ⛔ no debe eliminarse por completo, solo matizarse a "parcial": siguen genuinamente bloqueadas por el cliente las familias de termos eléctricos (la más vendida) y calderas, y falta confirmar los 2-3 modelos "estrella" (CLAUDE.md §8 y §12), tal como ya apunta la recomendación del auditor.

### 77. S01: due 9 jul para dominio+correo depende de los accesos DNS del cliente, que no tienen fecha comprometida
**Área:** GESTIÓN — 00 · Setup · **Tareas:** wdx6zenj47 [S01] Subcuenta + dominio + correo

El correo del dominio es requisito de la validación crítica S11-1 ("el email sale del dominio sin caer en spam") y del envío automático de SP04; también WEB←S01 y LS02←WEB cuelgan de S01. Si el cliente no envía los DNS el 8, la fecha del 9 es incumplible y el retraso se arrastra por la cadena SP04 (10-13) → S11 (14-15) sin que la tarea defina un plan B.

> Evidencia: Descripción S01: "⛔ BLOQUEADO parcialmente: accesos DNS del dominio (el cliente los envía — tarea suya acordada el 7/7)"; CLAUDE.md §12: "⛔ Accesos DNS del dominio (bloquea correo del dominio, publicación web)".

**Recomendación:** Separar el entregable en dos ítems con fechas distintas (subcuenta: 8 jul, sin bloqueo · dominio+correo: condicionado a DNS) y fijar fecha límite y plan B de entregabilidad si el 10 jul no hay DNS (escalar al cliente vía Víctor/Samuel).

**Matiz del verificador:** Matiz: la frase "sin que la tarea defina un plan B" es cierta para la tarea S01, pero el diseño global sí contempla una degradación parcial documentada en CLAUDE.md S11-1 ("Si falla → todo opera en flujo A"), que mitigaría el impacto sobre el envío de proformas (SP04) aunque NO cubre la publicación web (WEB←S01 y LS02←WEB seguirían bloqueadas) ni fija fecha de escalado al cliente. Además, la tarea ya reconoce la condicionalidad ("cuando lleguen accesos"), por lo que el problema es de planificación (fecha dura sobre entregable externo sin compromiso, sin split subcuenta/dominio) y la severidad "menor" es adecuada, no inflada.

### 78. S02 no advierte las consecuencias de migrar el número a la Cloud API: baja de la app WhatsApp Business y pérdida del historial de chats
**Área:** CALIDAD DE DESCRIPCIÓN / VIABILIDAD GHL — 00 · Setup · **Tareas:** wdx6zenj4e [S02] WhatsApp Business API

Conectar el 644 96 24 21 a la WhatsApp Business API exige dar de baja el número de la app WhatsApp Business; el cliente pierde el historial de conversaciones y desde ese momento solo atiende por la bandeja de GHL (web/app). Para un negocio unipersonal cuyo canal principal es WhatsApp es un cambio operativo irreversible que hay que pactar y preparar, no solo "coordinar en horario de baja actividad". Además la migración requiere que el cliente reciba el código de verificación en su móvil (coordinación en vivo).

> Evidencia: Contexto de S02: "El cliente usa hoy WhatsApp Business (app). Coordinar la migración en horario de baja actividad." — no menciona la desconexión de la app, la pérdida del historial ni la verificación con el cliente.

**Recomendación:** Añadir a la tarea: avisar al cliente del cambio, exportar/backup del historial de chats antes de migrar, coordinar el código de verificación y verificar que tiene la app móvil de GHL operativa para atender desde el día de la migración.

**Matiz del verificador:** Matiz sobre "cambio operativo irreversible": no es inevitablemente así. Meta ofrece el modo "coexistencia" (WhatsApp Business App + Cloud API simultáneos, con sincronización de hasta ~6 meses de historial), soportado por GHL desde 2025 para números elegibles (onboarding por QR desde la app actualizada). Si el número del cliente es elegible, podría conservar la app y el historial reciente. Esto no refuta el hallazgo — la tarea tampoco menciona ni elige esa vía, y ambas rutas requieren coordinación en vivo con el cliente — pero la recomendación debería incluir: evaluar primero la opción de coexistencia y, solo si no aplica, ejecutar el plan de migración clásica con backup de historial y aviso previo.

### 79. S11 valida el módulo "SP02 Notas de voz" que no tiene ninguna tarea de construcción en el plan
**Área:** COMPLETITUD — 00 · Setup · **Tareas:** wdx6zenj5u [S11] Validaciones pre-go-live

La validación 3 de S11 (14-15 jul) presupone un módulo SP02 de notas de voz, pero SP02 no existe entre las 24 tareas padre de ClickUp ni en la anatomía de los 10 workflows del diseño. El 14 jul Oliver no tendrá nada que validar porque nadie construye ese módulo (la partida "voz €180" del presupuesto adicional).

> Evidencia: Fila 3 de S11: "SP02 Notas de voz: GHL envía audio como adjunto, no como nota de voz nativa — validar cómo se ve en móvil real"; CLAUDE.md §4 lista los workflows "LS01 · LS02 · SP-N · SP04 · SP-V · SP03 · SP06 · AP01 · AP02+PS01 · PS02" — sin SP02 — y §5 no contiene ninguna tarea SP02.

**Recomendación:** Crear la tarea de construcción de SP02 (asignada y fechada antes del 14 jul) o decidir formalmente descartar el módulo y marcar la fila 3 de S11 como condicional.

**Matiz del verificador:** La frase "el 14 jul Oliver no tendrá nada que validar" exagera: la validación 3 es ejecutable manualmente (enviar un audio desde la conversación GHL a un móvil real) sin workflow construido, y la propia fila ya contempla "descartar módulo" como fallback. El problema real y accionable es la inconsistencia: S11 referencia un ID de módulo (SP02) que no existe en ningún lugar del plan y la partida cobrada "voz €180" no tiene tarea de construcción, por lo que aunque la validación pase no habrá tarea para construir/entregar el módulo antes del go-live. Severidad "menor" es correcta; la recomendación del auditor (crear la tarea SP02 o descartar formalmente y marcar la fila 3 como condicional) sigue siendo válida.

### 80. S09: la cabecera "Presupuesto Nº" asume numeración correlativa que Documents & Contracts no genera de forma nativa
**Área:** VIABILIDAD GHL — 00 · Setup · **Tareas:** wdx6zenj5p [S09] Plantilla D&C Proforma Termical

La fuente indicada para el número es "Custom Values / doc", pero un custom value es estático (no incrementa por documento) y D&C no ofrece un merge field de número secuencial de presupuesto. El formato real del cliente que la plantilla debe replicar lleva número correlativo, así que en el flujo B automático el documento saldría sin número o con uno fijo.

> Evidencia: Fila 1 de la plantilla en S09: "Logo TÉRMYCAL + 'Presupuesto' + Nº + fecha | Custom Values / doc"; CLAUDE.md §4: "Cabecera 'Presupuesto Nº + fecha'" y "replica formato REAL de sus presupuestos".

**Recomendación:** Definir el mecanismo de numeración antes de construir la plantilla (p. ej. identificador basado en fecha/hora vía merge, o numeración manual solo en flujo A) y comprobarlo en la prueba end-to-end de S11-1.

**Matiz del verificador:** Matiz de precisión: el documento no saldría "sin número" en sentido estricto, sino con el texto estático que contenga la plantilla (número fijo o placeholder), que es justamente la inconsistencia. En el flujo A (manual, ~20%) el número sí puede añadirse a mano al editar cada documento, por lo que el impacto real se concentra en el flujo B. Alternativas viables ya alineadas con la recomendación: identificador basado en fecha (p. ej. merge de fecha AAAAMMDD como pseudo-número) o mover la numeración al módulo Estimates de GHL (que sí autoincrementa), aunque esto último cambiaría la decisión de diseño de usar D&C con firma.

### 81. La elección del dominio de publicación sigue abierta y no está registrada como pendiente del cliente
**Área:** 06 One-page Web · gestión / decisión abierta · **Tareas:** wdx6zenjde, wdx6zenjdx

Las tareas dejan sin decidir si se publica en termosycalentadoresgranada.com o en termical.com. Esa decisión condiciona el title/NAP/schema de la subtarea SEO, el correo del dominio de S01 y qué accesos DNS concretos reclamar al cliente el día 1. En CLAUDE.md §12 los pendientes del cliente incluyen «⛔ Accesos DNS del dominio» pero no la confirmación del dominio a usar.

> Evidencia: Subtarea wdx6zenjdx, paso 2: «Publicar la one-page en termosycalentadoresgranada.com (o termical.com — confirmar cuál)»; el padre repite la ambigüedad: «para publicar bajo termosycalentadoresgranada.com o termical.com».

**Recomendación:** Cerrar la decisión al reclamar los DNS (8-9 jul). Para SEO conviene el dominio con historial (termosycalentadoresgranada.com) y redirigir termical.com con 301. Registrar la decisión en la tarea y en los pendientes del cliente.

**Matiz del verificador:** Dos matices: (1) la ambigüedad no es un descuido inadvertido — la propia subtarea la señaliza con «confirmar cuál» —, de modo que el gap real es que esa confirmación no figura como pendiente del cliente en CLAUDE.md §12 ni está cerrada en S01; (2) el detalle exagera ligeramente el impacto en la subtarea SEO: en wdx6zenjdr el title («Termos, calentadores y calderas en Granada — TÉRMYCAL») y el NAP (nombre/dirección/teléfono) no dependen del dominio; lo que sí depende es la URL de publicación/canonical, el campo url del schema y el correo del dominio de S01.

### 82. Dependencia mal citada en el padre: «S05 formulario/pipeline»
**Área:** 06 One-page Web · exactitud / dependencias · **Tareas:** wdx6zenjde

En el diseño, S05 es «Tags+Pipeline» y el formulario interno es S08 (que además pertenece al Flujo A, no al formulario de la web: el form de la one-page se crea en el propio funnel). La cita del padre puede llevar al técnico a buscar el formulario en la tarea equivocada. La propia tarea [LS02] lo cita bien («S04 Custom fields · S05 Pipeline»).

> Evidencia: Descripción del padre wdx6zenjde: «S05 formulario/pipeline para conectar LS02» vs CLAUDE.md §5: «[S05] Tags+Pipeline … [S08] Formulario interno».

**Recomendación:** Corregir la línea a «S05 pipeline + S04 custom fields para que LS02 pueda mapear campos y crear la oportunidad» y aclarar que el formulario web se construye dentro de la propia one-page (subtarea 1).

**Matiz del verificador:** Matiz que acota el alcance: el error está solo en el texto de la descripción, no en el grafo formal de dependencias de ClickUp (las dependencias reales del padre son WEB←S01 y LS02←WEB, correctas), así que no hay impacto en cronograma ni bloqueos — es puramente documental. Además, la recomendación puede afinarse: S05 sigue siendo prerrequisito legítimo de LS02 no solo por el pipeline sino también por los tags (LS02 añade `lead-web`, definido en S05 Tags+Pipeline); la corrección debería decir «S05 tags+pipeline + S04 custom fields» y aclarar que el formulario web se construye en la subtarea 1 de la propia one-page.

### 83. Mapeo de campos del formulario sin especificar: «descripción» no existe como custom field del diseño
**Área:** 06 One-page Web · exactitud / custom fields · **Tareas:** wdx6zenjdm, wdx6zenjdh

La subtarea pide como campos mínimos «nombre, teléfono, tipo_aparato, descripción», pero en el diseño el campo de texto libre es detalle_trabajo (multi line, opcional) — «descripción» no existe. Sin una tabla de mapeo explícita, el técnico puede crear en el form builder campos sueltos o un custom field duplicado en vez de reutilizar tipo_aparato (dropdown de S04) y detalle_trabajo, rompiendo el merge posterior de la proforma D&C que lee del contacto.

> Evidencia: Subtarea wdx6zenjdm: «Campos mínimos | nombre, teléfono, tipo_aparato, descripción» vs CLAUDE.md: «Folder Proforma: tipo_servicio, tipo_aparato, … detalle_trabajo (multi line opcional)».

**Recomendación:** Añadir la tabla de mapeo: «descripción del problema» → detalle_trabajo · «tipo de aparato» → tipo_aparato (custom field dropdown creado en S04), e indicar que en el form builder de GHL se deben arrastrar los custom fields existentes, no crear campos nuevos.

**Matiz del verificador:** Matiz sobre el impacto: «rompiendo el merge posterior de la proforma» exagera — el merge de D&C no se rompe; lo que ocurre es que el dato del formulario no llega a detalle_trabajo, campo que además es opcional y que en el flujo B el bot re-captura por WhatsApp (el propio contexto de wdx6zenj86 dice que el mapeo «ahorra la re-captura por el bot»). Es pérdida de datos/duplicación de campos, no rotura del flujo. Refuerzo adicional del hallazgo: el mapeo parcial de LS02 (wdx6zenj86) menciona tipo_servicio, que ni siquiera figura entre los «campos mínimos» del form en wdx6zenjdm — la tabla de mapeo recomendada debería alinear también ese campo entre WEB y LS02.

### 84. La verificación contra el trigger de LS02 no es ejecutable dentro del plazo de [WEB]
**Área:** 06 One-page Web · gestión / secuencia · **Tareas:** wdx6zenjdm

[WEB] vence el 13 jul (due 1783926000000) pero [LS02] se construye el 13→14 jul (due 1784012400000) y además LS02 espera a WEB (dependencia registrada). El paso de «verificar que el nombre/ID del form coincide con el filtro del trigger de LS02» no puede completarse dentro de WEB porque ese trigger aún no existirá cuando WEB deba cerrarse.

> Evidencia: Subtarea wdx6zenjdm, Contexto: «Verificar que el nombre/ID del form coincide con el filtro configurado en el trigger de LS02» + fechas: [WEB] due 13 jul vs [LS02] start 13 jul → due 14 jul y dependencia LS02←WEB.

**Recomendación:** Reformular la subtarea de WEB como «crear el formulario con el nombre acordado (p. ej. “Form One-page Termical”) y documentar su ID», y mover la verificación del match form↔trigger al cierre de LS02 o a las validaciones S11.

**Matiz del verificador:** Matiz que reduce aún más el riesgo operativo: en GHL el filtro del trigger «Form Submitted» se selecciona de un dropdown de formularios ya existentes, así que el orden form (WEB) → trigger (LS02) es el natural y el match form↔trigger queda garantizado de facto al construir LS02 (subtarea wdx6zenj82). El defecto es solo de redacción/ubicación del paso de verificación —no de secuenciación del plan— por lo que la severidad "menor" es correcta y la recomendación del auditor (reformular la subtarea de WEB como «crear el form con nombre acordado y documentar su ID» y mover la verificación a LS02 o a S11) es apropiada.

### 85. Las marcas listadas para la web no coinciden con el catálogo recibido del cliente
**Área:** 06 One-page Web · exactitud / contenido · **Tareas:** wdx6zenjdh

La subtarea de diseño propone «Ariston, Cointra, Junkers, Thermor, Baxi...», pero el catálogo real recibido el 7/7 trabaja Ariston, HTW y Bosch. Publicar marcas que no instala (y omitir dos que sí) puede generar consultas que el bot/KB no puede atender y desaprovecha las marcas reales.

> Evidencia: Subtarea wdx6zenjdh: «Marcas | Ariston, Cointra, Junkers, Thermor, Baxi...» vs CLAUDE.md §8: «Aparatos: Ariston Next Evo X … HTW LowNox … Bosch Therm 3600 S … Ariston Akros R X … Bosch T 4204».

**Recomendación:** Confirmar con el cliente si la sección es «marcas que reparamos» (puede ser amplia) o «marcas que instalamos» (limitarla al catálogo); en cualquier caso incluir HTW y Bosch, que son las del catálogo real.

**Matiz del verificador:** Matiz al detalle: no puede afirmarse categóricamente que el cliente «no instala» Cointra/Junkers/Thermor/Baxi, porque el catálogo recibido solo cubre la 1ª familia (calentadores de gas) y quedan pendientes termos eléctricos y calderas, donde esas marcas son plausibles (el propio comentario de S10 dice «Pendiente del cliente (irá enviando): termos eléctricos, calderas»). Además, la lista termina en «...», lo que sugiere contenido ilustrativo aún no final. Lo objetivamente verificable es la omisión de HTW y Bosch y la ausencia de fuente para las otras marcas; el riesgo de «consultas que el bot no puede atender» es especulativo (la KB ya cubre reparaciones sin proforma previa). La recomendación de confirmar con el cliente el alcance de la sección sigue siendo la acción correcta.

### 86. Keyword «fontanero Granada» fuera del alcance del negocio
**Área:** 06 One-page Web · SEO / alcance del negocio · **Tareas:** wdx6zenjdr

TÉRMYCAL hace termos, calentadores, calderas y aerotermos; no fontanería general. Posicionar «fontanero Granada» atraería leads de fontanería que ni el bot (KB sin servicios de fontanería) ni el cliente pueden atender, ensuciando el pipeline con leads no cualificados.

> Evidencia: Subtarea wdx6zenjdr: «Keywords | termo Granada, calentador gas Granada, caldera Granada, fontanero Granada» vs CLAUDE.md §1: «TÉRMYCAL — termos, calentadores, calderas, aerotermos».

**Recomendación:** Sustituir por keywords del alcance real: «instalación calentador Granada», «reparación termo eléctrico Granada», «aerotermia Granada», «cambiar termo Granada».

**Matiz del verificador:** Matiz doble que reduce aún más el impacto práctico: (1) una one-page nueva con «SEO local básico» difícilmente posicionará para una keyword tan competida y genérica como «fontanero Granada», así que el efecto real de ensuciar el pipeline sería marginal a corto plazo; (2) en España parte de las búsquedas de «fontanero» sí corresponden a averías de termo/calentador, por lo que la keyword es adyacente al negocio, no totalmente ajena. Aun así, es inconsistente con el alcance definido y con la KB del bot; la recomendación de sustituirla por keywords de intención específica (instalación calentador Granada, reparación termo eléctrico Granada, aerotermia Granada, cambiar termo Granada) es acertada y de coste cero.

### 87. Schema LocalBusiness sin especificar el mecanismo real en GHL (no hay soporte nativo)
**Área:** 06 One-page Web · viabilidad GHL · **Tareas:** wdx6zenjdr

GHL no tiene una opción nativa de «schema markup»: el JSON-LD de LocalBusiness debe inyectarse a mano como custom code (header/footer tracking code del site o un elemento HTML personalizado en la página). La subtarea solo dice «Schema: LocalBusiness (NAP…)» sin el cómo, y un técnico puede perder tiempo buscando una función que no existe o dejarlo sin implementar.

> Evidencia: Subtarea wdx6zenjdr: «Schema | LocalBusiness (NAP: nombre, dirección, teléfono coherentes con la ficha GBP)» — sin indicación de dónde ni cómo se inserta en GHL.

**Recomendación:** Precisar en la subtarea: «insertar script JSON-LD LocalBusiness en el Header Tracking Code del site/funnel» e incluir la plantilla del JSON con los datos NAP (TÉRMYCAL, Avda. Don Bosco 38, Granada 18007, 644 962 421) y validarlo con la herramienta de resultados enriquecidos de Google.

**Matiz del verificador:** Impacto acotado: un técnico con experiencia en GHL resolvería igualmente vía Header Tracking Code o elemento Custom Code (ambas rutas válidas, a nivel site o página), y la subtarea está además supeditada al bloqueo DNS del cliente, así que no hay riesgo de retraso — la severidad "menor" es correcta, no inflarla. La recomendación es viable tal cual: todos los datos NAP para la plantilla JSON-LD constan en CLAUDE.md (TÉRMYCAL, Avda. Don Bosco 38, Granada 18007, tel. 644 962 421) y deben cuadrar con la ficha GBP que se conectará en el onboarding.


## 💡 Sugerencias

### 88. El Wait de 4 horas sin ventana horaria puede enviar la encuesta de madrugada
**Área:** 🔴 04 · Active Projects — AP02+PS01 · **Tareas:** wdx6zenjcv Wait: 4 horas

Los trabajos pueden terminar en la franja de tarde (el diseño define rangos hasta 18-20); si Termical marca 'Completado' a las 19-20h, la encuesta saldría entre las 23:00 y la 01:00. Un WhatsApp comercial a esas horas daña la experiencia justo antes de pedir la valoración. GHL permite restringir la continuación del workflow a una ventana horaria en el paso Wait/ajustes del workflow.

> Evidencia: Tarea wdx6zenjcv: 'Action type | Wait · Duración | 4 horas' (sin restricción horaria). CLAUDE.md §4 decisión 4: franjas de visita hasta '18-20'.

**Recomendación:** Configurar el Wait (o el ajuste de ventana del workflow) para que el envío solo ocurra dentro de un horario razonable, p. ej. 9:00-21:00, difiriendo al día siguiente si el wait vence de noche.

**Matiz del verificador:** Imprecisión aritmética menor en el detalle: si Termical marca "Completado" a las 19-20h, el envío caería entre las 23:00 y las 00:00, no hasta la 01:00 (para eso tendría que marcarlo hacia las 21:00, escenario igualmente posible dado que el trigger es manual). El fondo del hallazgo no cambia.

### 89. SP06 enviará el seguimiento 2 a clientes que ya respondieron por WhatsApp si Termical no movió la etapa
**Área:** 03 Sales Pipeline — SP06 guards de salida · **Tareas:** wdx6zenjbj, wdx6zenjbr

Los guards de SP06 solo comprueban la etapa de la oportunidad. Si el cliente contesta al seguimiento 1 ('lo estoy pensando', 'ahora no puedo') y Termical no mueve la tarjeta —probable en un negocio unipersonal en obra—, el día 5 recibirá el seguimiento 2 como si lo hubieran ignorado. GHL lo resuelve añadiendo al mismo workflow un segundo trigger 'Customer Replied' (Reply Channel = WhatsApp) conectado a 'Remove From Workflow', o usando Waits con condición de respuesta del contacto.

> Evidencia: wdx6zenjbj: 'Condition object | Opportunity · Field | Etapa actual · Operator | es igual a "Proforma enviada"' — ninguno de los 8 nodos de SP06 contempla la respuesta del cliente como condición de salida.

**Recomendación:** Añadir a SP06 la salida por respuesta: trigger adicional 'Customer Replied' → Remove From Workflow (o Wait con rama de respuesta antes de cada envío). Es un nodo extra y evita perseguir a clientes que ya están conversando.

**Matiz del verificador:** Imprecisión en la mecánica GHL propuesta: en un workflow de GHL todos los triggers entran por el inicio de la misma secuencia de acciones; no se puede conectar un segundo trigger "Customer Replied" directamente a un "Remove From Workflow" dentro del mismo SP06 (el contacto re-entraría por el Wait de 2 días). Las soluciones correctas son: (1) activar el ajuste "Stop on Response" en la configuración del propio workflow SP06 — la más simple, cero nodos extra; (2) un workflow separado con trigger Customer Replied (canal WhatsApp) → Remove From Workflow apuntando a SP06; o (3) la alternativa que el hallazgo sí menciona bien: Wait con condición de respuesta del contacto y rama por timeout antes de cada envío.

### 90. SP06: los guards solo miran la etapa; un lead que respondió por WhatsApp pero cuya tarjeta no se movió seguirá recibiendo seguimientos y acabará marcado 'frio'
**Área:** Sales Pipeline · SP06 (guards de salida) · **Tareas:** wdx6zenjba [SP06], wdx6zenjbj Guard IF: ¿sigue en la misma etapa?, wdx6zenjbr Guard IF: ¿sigue igual?

Los checks de salida dependen 100% de que Termical mueva la oportunidad de etapa. Si el cliente contesta a la proforma o al seguimiento 1 ('cualquier duda te ayudo') pero Termical aún no movió la tarjeta —escenario probable en un negocio unipersonal que instala de día—, el día 5 le llegará igualmente el seguimiento 2 y se le añadirá nota + tag frio pese a estar en conversación activa.

> Evidencia: wdx6zenjba: '2 toques (día 2 y día 5) con checks de salida si el lead avanza de etapa' — no existe ningún check por respuesta del contacto.

**Recomendación:** Activar en la configuración del workflow SP06 la opción 'Stop on response' de GHL (saca al contacto del workflow cuando responde por cualquier canal), complementando los guards de etapa sin añadir nodos.

**Matiz del verificador:** Matiz a la recomendación: "Stop on Response" de GHL remueve al contacto cuando responde a un mensaje enviado DESDE ese workflow. Cubre el caso principal (responde al seguimiento 1 → no recibe seguimiento 2 ni tag frio), pero NO cubre la rama "contesta a la proforma antes del día 2", porque la proforma la envía SP04 por email y SP06 aún no ha enviado nada en ese momento. Para cubrir esa rama haría falta además una condición en los Guard IF (p. ej. última respuesta del contacto posterior al envío) o asumir que la mueve Termical. Aun así, activar Stop on Response en SP06 es una mejora de coste cero y la severidad "sugerencia" es correcta.

### 91. S01 no recoge los parámetros acordados de creación de la subcuenta (Business Name, timezone, tipo de cuenta, sin sample data)
**Área:** CALIDAD DE DESCRIPCIÓN — 00 · Setup · **Tareas:** wdx6zenj47 [S01] Subcuenta + dominio + correo

Los parámetros de la subcuenta se entregaron a Henry fuera de ClickUp; la tarea solo dice "Crear subcuenta Termical". Si otro miembro la ejecuta o el dato se pierde, la subcuenta puede crearse con timezone o sample data incorrectos, lo que luego contamina contactos y calendarios de prueba.

> Evidencia: CLAUDE.md §12: "Subcuenta: datos ya entregados a Henry (Business Name TÉRMYCAL, timezone Europe/Madrid, 'client's account', SIN sample data)"; la estructura de S01 solo contiene el ítem "1 | Crear subcuenta Termical".

**Recomendación:** Pegar en la descripción de S01 los 4 parámetros: Business Name TÉRMYCAL · timezone Europe/Madrid · tipo "client's account" · sin sample data.

**Matiz del verificador:** Matiz que reduce el riesgo práctico: S01 está asignada precisamente a Henry, que ya recibió los datos, y según CLAUDE.md §3 la subcuenta ya está "en creación" desde el 7/7, por lo que el ítem 1 puede estar ejecutándose antes de que otro miembro pudiera tomar la tarea. Aun así, la recomendación de pegar los 4 parámetros en la descripción es válida como salvaguarda documental de bajo costo.

### 92. Falta el paso de actualizar la URL del sitio web en la ficha de Google Business Profile tras publicar
**Área:** 06 One-page Web · completitud / GBP · **Tareas:** wdx6zenjdx, wdx6zenjdr

El objetivo declarado del cliente es que la web viva en Google Maps, pero ninguna subtarea contempla actualizar el campo «sitio web» de la ficha GBP a la nueva URL una vez publicada. Sin ese paso, Maps seguirá apuntando al WordPress caído (o a nada tras la baja).

> Evidencia: Subtarea wdx6zenjdr, Contexto: «El objetivo del cliente con la web es “ponerla en Google Maps para que la gente pregunte información”»; CLAUDE.md §12 solo prevé «conectar GBP/redes guiado por pantalla» en el onboarding, sin mencionar la URL.

**Recomendación:** Añadir un paso 5 en wdx6zenjdx: actualizar la URL del sitio en la ficha GBP tras publicar y validar (hacerlo en la sesión de onboarding guiada por pantalla, ya que el cliente no comparte claves).

**Matiz del verificador:** Matiz al escenario de fallo: wdx6zenjdx (paso 2) deja abierto publicar en termosycalentadoresgranada.com O termical.com. Si la one-page se publica en el MISMO dominio que ya figura en la ficha GBP, la URL de Maps seguiría resolviendo a la web nueva sin tocar la ficha (la «baja de WordPress» es del hosting, no del dominio). El paso a añadir debería formularse como «verificar y, si aplica, actualizar la URL del sitio en la ficha GBP tras publicar» — imprescindible sobre todo si se confirma termical.com como dominio o si la ficha no tiene URL cargada. La recomendación de hacerlo en la sesión de onboarding guiada por pantalla es coherente con la regla ya documentada (el cliente no comparte claves, PS02 y CLAUDE.md §12).

### 93. El formulario no captura email, pero la proforma del flujo B se envía por email
**Área:** 06 One-page Web · formulario / proforma · **Tareas:** wdx6zenjdh, wdx6zenjdm

Los campos definidos (nombre, teléfono, tipo de aparato, descripción) no incluyen email. El envío automático de la proforma D&C del flujo B es «por email automático» (decisión 3 del diseño), así que todo lead web que avance a presupuesto obligará a pedir el email después por WhatsApp. Capturarlo opcionalmente en el form ahorra ese paso.

> Evidencia: Subtarea wdx6zenjdh: «Formulario | Nombre, teléfono, tipo de aparato, descripción del problema» vs CLAUDE.md decisión 3: «bot captura campos+email+fotos … WF SP04 genera doc D&C y envía por email automático».

**Recomendación:** Añadir un campo email opcional al formulario (mapeado al campo email estándar del contacto), manteniendo teléfono como único obligatorio para no penalizar la conversión.

**Matiz del verificador:** Matiz: no es un hueco funcional que bloquee nada, porque el propio diseño (decisión 3) ya prevé que el bot capture el email dentro del flujo B («bot captura campos+email+fotos»), de modo que ningún lead debería llegar a SP04 sin email; el beneficio real es ahorrar un paso conversacional y cubrir al lead web que avance por flujo A o que tarde en responder por WhatsApp. Además, wdx6zenjdm habla de «campos mínimos», así que añadir email opcional no contradice esa subtarea: bastaría actualizar la lista de campos en wdx6zenjdh y el mapeo del nodo Update Fields de LS02 (wdx6zenj86).

### 94. Claim «financiación sin intereses» incompleto: existe comisión de apertura
**Área:** 06 One-page Web · contenido / cumplimiento publicitario · **Tareas:** wdx6zenjdh

La financiación de La Caixa es 0% TIN pero con comisión de apertura del 2% al 11% según plazo. Anunciar «sin intereses» a secas en la web puede considerarse publicidad engañosa según la normativa española de crédito al consumo (que exige comunicar la TAE, y con comisión la TAE no es 0%).

> Evidencia: Subtarea wdx6zenjdh: «Confianza | Diagnóstico profesional · financiación sin intereses» vs CLAUDE.md §9: «financiación La Caixa 0% TIN/TAE, comisión apertura: 3m-2% / 6m-3,5% / 12m-4,5% / 18m-6,5% / 24m-8,5% / 36m-11%».

**Recomendación:** Ajustar el claim a «financiación 0% TIN hasta 36 meses — consulta condiciones» o similar, evitando afirmar coste cero sin matizar la comisión de apertura.

**Matiz del verificador:** Dos matices: (1) el detalle del auditor afirma «la TAE no es 0%», pero la fuente citada (CLAUDE.md §9) dice literalmente «0% TIN/TAE»; como TAE 0% + comisión de apertura a cargo del consumidor es matemáticamente imposible, o bien el «/TAE» del CLAUDE.md es un error de transcripción, o bien la comisión la asume el comercio (arreglo habitual en financiación CaixaBank en punto de venta) y entonces el claim «sin intereses» sería correcto para el consumidor. Antes de reescribir el copy hay que verificar en la «Tabla de Financiación PDF» del cliente (recibida 5/7, CLAUDE.md §10) quién paga la comisión. (2) «Sin intereses» no es falso en sentido estricto (0% TIN = sin intereses); el problema es de omisión de un coste, no de afirmación falsa. La recomendación de matizar el claim («0% TIN, consulta condiciones») sigue siendo válida como medida prudente.

### 95. El due date del padre (13 jul) engloba la subtarea de publicación, que está bloqueada por el cliente sin ETA
**Área:** 06 One-page Web · gestión / fechas · **Tareas:** wdx6zenjde, wdx6zenjdx

El padre [WEB] vence el 13 jul incluyendo la subtarea 4, que depende de los accesos DNS del cliente (⛔ sin fecha comprometida). Si los DNS no llegan a tiempo, la tarea completa aparecerá vencida aunque las subtareas 1-3 (diseño, form, SEO) estén terminadas, distorsionando el seguimiento del sprint.

> Evidencia: Padre wdx6zenjde: due_date 1783926000000 (13 jul) con la subtarea «Publicar en el dominio (cuando lleguen DNS) + dar de baja WordPress»; CLAUDE.md §12: «⛔ Accesos DNS del dominio (bloquea correo del dominio, publicación web)».

**Recomendación:** Fechar las subtareas 1-3 dentro del 8-13 jul y dejar la subtarea 4 sin fecha (o con fecha condicionada a la recepción de DNS), de modo que el vencimiento del padre refleje solo el trabajo no bloqueado.

**Matiz del verificador:** Dos matices. Primero: las subtareas 1-3 no tienen fechas "mal puestas" — hoy no tienen ninguna fecha (due_date null en las 4), así que la corrección consiste en añadir fechas a 1-3, no en moverlas. Segundo: el efecto es algo mayor que solo cosmético en el reporting, porque existe la dependencia LS02←WEB (wdx6zenj7x waiting_on wdx6zenjde, confirmada en la tarea y en CLAUDE.md §5): mientras la subtarea 4 mantenga abierto el padre [WEB], [LS02] Formulario web (due 13→14 jul) seguirá formalmente "waiting on" una tarea que en la práctica solo necesita las subtareas 1-2 (web diseñada y formulario conectado), no la publicación en el dominio. Aun así sigue siendo sugerencia, no mayor: la dependencia es informativa en ClickUp y el equipo puede avanzar igualmente.


## Hallazgo refutado

- «El guard de AP01 referencia un calendario 'Trabajos' que no existe en el diseño» — FALSO: la tarea S06 sí crea el calendario de Trabajos/Instalaciones; la referencia es válida.