# PLAYBOOK — Crear "SuperAgentes" internos en GoHighLevel (Agent Studio)
> **Uso:** pega este documento completo en cualquier conversación de Claude (o síguelo tú a mano) para montar un agente operador interno en cualquier subcuenta de GHL, con su knowledge base, sin re-explicar nada.
> **Origen:** proceso validado en producción el 9 jul 2026 (subcuenta TÉRMYCAL, omnia). SuperAgents está en **Labs**: detalles de UI pueden cambiar.

---

## 1. QUÉ ES (contexto en 5 líneas)
Los **SuperAgents** de HighLevel (AI Agents → Agent Studio → botón de agente nuevo) son agentes de IA **internos**: no hablan con clientes finales, trabajan para el equipo dentro de la subcuenta. Se construyen describiendo lo que quieres en un builder de chat; el agente resultante tiene **Triggers**, **Skills** (~423 operaciones reales de la plataforma agrupadas por módulo), **Capabilities** (web search, generación de imágenes) y **Knowledge Base** propia. Se prueban con "Test Agent" y se activan con "Publish". No confundir con **Conversation AI** (ese es el bot de cara a clientes).

## 2. QUÉ PUEDE Y QUÉ NO (verificado en producción)
✅ **PUEDE** (skills de escritura): Calendarios (49 skills — los crea bien: nombre, slots, disponibilidad, sin booking), Contactos, Oportunidades, Custom Fields, Custom Values, Knowledge Bases, Forms, Surveys, Objects, Medias, Locations.
❌ **NO PUEDE** (verificado): **Conversation AI** (sus 7 skills son SOLO LECTURA: Get/List/Search — no crea ni configura bots) · **Workflows** (no existe el grupo de skills) · **Documents & Contracts** · **Reputation**. Esas áreas van por API interna o UI.
⚠️ **Detalles que deja por defecto y conviene pulir tras cada tarea** (por API o UI): en calendarios deja `googleInvitationEmails=true` y `allowReschedule/allowCancellation=true` — revisar según el caso.

## 3. RECETA PASO A PASO

### 3.1 Crear el agente
En "Build your own agent", pegar (personalizando lo marcado con ⟨⟩):
> Crea un agente operador interno para esta subcuenta (⟨NOMBRE NEGOCIO, sector, ciudad⟩). No habla con clientes finales: me asiste a mí ejecutando tareas de configuración del CRM que yo le pida por chat — crear y configurar calendarios, knowledge bases, campos, contactos y oportunidades. Debe pedirme confirmación antes de ejecutar cualquier acción que cree, modifique o borre algo, resumiendo lo que va a hacer.

El builder genera nombre, descripción e Instructions bastante buenas (proceso de confirmación, refuerzo para acciones destructivas, no inventar datos, no fingir ejecuciones). **Revisarlas y añadir el bloque del §3.4.**

### 3.2 Configurar el editor
- **Trigger:** solo `Chat Started` (agente a demanda; no dispararlo por eventos de contactos).
- **Skills:** NO marcar los 423. Marcar: Calendars, Contacts, Conversations, Conversation AI (lectura, útil para auditar), Custom Fields, Knowledge Bases, Objects, Opportunities, Forms, Surveys, Locations, Medias. **Desmarcar:** Payments, Invoices, Products, Proposals, Emails, Social Planner, Phone System, Funnels, Blogs, Courses, Campaigns (superficie de riesgo: dinero y publicación externa).
- **Capabilities:** Web search ON · Image generation OFF.
- **Knowledge Base:** crear una KB dedicada (§3.5) y conectarla. **NUNCA conectar esta KB interna a un bot de clientes.**

### 3.3 Regla de las skills
Las Instructions no bastan como control: **la skill que no está marcada no se puede ejecutar ni por error**. Recortar skills ES la medida de seguridad; las instructions son la segunda capa.

### 3.4 Bloque a AÑADIR al final de las Instructions (plantilla)
> CONTEXTO Y CONVENCIONES DE ESTA SUBCUENTA (obligatorias):
> - Zona horaria: ⟨tz⟩. Idioma: español.
> - Ya existen (NO duplicar, verificar antes de crear): ⟨tags exactos⟩ · pipeline ⟨nombre y etapas⟩ · custom fields ⟨lista o referencia a la KB⟩ · custom values ⟨carpeta⟩.
> - Convenciones: tags en minúsculas-con-guiones, campos en snake_case.
> - ⟨REGLAS DE CALENDARIO del negocio: manual vs booking, franjas, prohibiciones⟩
> - PROHIBIDO SIEMPRE: enviar mensajes/emails/SMS/WhatsApp a contactos; tocar pagos o facturas. Si la tarea lo requiere, decir que eso lo gestiona el equipo técnico.
> - ⟨Reglas del bot de clientes si existe: tono, qué nunca hace⟩

### 3.5 Knowledge Base del agente (formatos y trampas)
Fuentes aceptadas: Web crawler · FAQ · **Tables (CSV)** · Rich text · File upload (según rollout del feature — si no aparece File/Rich text, usar Tables).
**Estructura recomendada (validada):**
1. **Tabla "operador"** (~30-40 filas: seccion, tema, informacion): negocio, reglas de oro, arquitectura existente, calendarios, flujos.
2. **Tabla "catálogo/precios"** si aplica (tipo, item, precio, notas).
3. **Tabla "workflows"** (workflow, disparador, que_hace, notas_clave) — el agente no los crea, pero así no configura cosas incoherentes con ellos.
4. **Tabla "inventario CRM"** extraída EN VIVO por API (tags, pipeline+ID, campos con tipo/opciones/merge key, custom values): nombres exactos = cero duplicados.
5. **Un único Rich text narrativo** (~600 palabras): el viaje del cliente de punta a punta + los principios de diseño + cómo actuar ante peticiones típicas. Las tablas dan datos; el rich text da el "porqué".
**Trampas del CSV:** el validador rechaza CUALQUIER celda vacía ("rows have missing required fields") → rellenar todo (usar "—"). Guardar en UTF-8 con BOM para los acentos. No duplicar contenido entre fuentes (mete ruido al retrieval).
**Probar con "Test retrieval"** (botón flotante en la pantalla de la KB) antes de conectarla al agente.

### 3.6 Validar y publicar
1. **Test Agent** con una lectura: "lista los custom fields de contacto" (debe encontrar los reales, sin inventar).
2. Una pregunta de KB: algo transversal cuyo dato esté en las tablas.
3. Un encargo de escritura de bajo riesgo → debe RESUMIR el plan y PEDIR CONFIRMACIÓN antes de ejecutar.
4. Publish. **Verificar por API o UI todo lo que el agente diga haber creado** — es fiable pero deja defaults (§2).

## 4. FORMATO DE ENCARGO QUE FUNCIONA (plantilla)
Los encargos con contexto cerrado evitan que improvise:
> Necesito que crees ⟨cosa⟩ en esta subcuenta. Contexto importante: ⟨restricciones del negocio⟩. Antes de crear nada, muéstrame la configuración completa y espera mi confirmación. Si alguna parte no puedes hacerla con tus skills, NO la improvises: lístala al final como "pendiente manual".
> ⟨Especificación con todos los parámetros: nombres, duraciones, horarios, días, qué desactivar⟩
> Cuando termines dame el resumen con los IDs de lo creado.
Ejemplo real validado: 2 calendarios de registro manual con franjas de 2h — los creó exactos a la primera (solo hubo que pulir 3 flags por defecto).

## 5. DIVISIÓN DEL TRABAJO (patrón probado)
- **SuperAgent (chat):** calendarios, KBs, campos/values, contactos/oportunidades, consultas y auditorías de configuración.
- **API pública (token pit- + Private Integration):** tags, custom fields, custom values, calendarios (ajustes finos), lectura general. CLI útil: leadgenjay/gohighlevel-cli.
- **API interna (token Firebase vía extensión Chrome del CLI):** pipelines (la pública no los crea), workflows en DRAFT (espinas lineales; if/else mejor en UI), folders de custom fields (`/locations/{loc}/customFields/search?documentType=folder` para listar, PUT con parentId para mover).
- **Solo UI:** crear bots de Conversation AI, folders de custom fields (crear), D&C templates, publicar workflows (y siempre: revisión humana antes de publicar cualquier cosa).

## 6. PARA OTRA CONVERSACIÓN DE CLAUDE (handoff mínimo)
Pega este playbook + estos datos de la subcuenta destino:
- location_id, nombre del negocio y contexto en 3 líneas
- token pit- (Private Integration) y, si hay que tocar workflows/pipelines, el token de Firebase
- Lo que ya existe (o pídele que lo extraiga por API y genere la tabla de inventario del §3.5.4)
- Las reglas no negociables del proyecto
Y dile: "sigue el playbook para montar el operador interno de esta subcuenta".
