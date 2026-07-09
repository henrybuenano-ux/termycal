# TÉRMYCAL — Arquitectura del CRM (KB interna del Operador CRM)

Todo lo listado aquí YA EXISTE en la subcuenta. Verificar antes de crear nada nuevo para no duplicar.

## Tags (8, minúsculas exactas, sensibles a mayúsculas)
lead-whatsapp · lead-web · pide-presupuesto · pide-visita · derivado-humano · aprobar-proforma · resena-solicitada · frio
- pide-presupuesto: lo aplica el flujo del bot cuando el lead pide precio → dispara notificación interna con resumen aprobable.
- aprobar-proforma: lo aplica EL DUEÑO desde la app (es su botón de aprobación) → dispara el envío automático de la proforma.
- pide-visita: dispara el aviso "en breves momentos te contactamos" + notificación interna (agendado manual).
- derivado-humano: el bot se aparta y avisa al dueño.
- frio: lo aplican los follow-ups por inactividad.

## Pipeline "Comercial Termical" (9 etapas en orden)
Nuevo lead → Conversando → Visita agendada → Proforma enviada → Presupuesto formal enviado → Aprobado → Trabajo agendado → Completado → Cerrado
- REGLA ANTI-DUPLICADOS: los envíos NUNCA se disparan por cambio de etapa; siempre por tag.

## Custom Fields de CONTACTO
Folder "General": fuente_contacto (dropdown: WhatsApp / Web / Llamada o visita (manual) / Reseña) · fecha_primer_contacto (date)
Folder "Proforma": tipo_servicio (instalación nueva / sustitución / reparación) · tipo_aparato (termo eléctrico / calentador gas / caldera / aerotermo) · litros_capacidad (50/80/100/150) · paquete_interes (texto) · valor_estimado (monetario, lo escribe el bot) · direccion_servicio (texto) · detalle_trabajo (texto largo, opcional) · estado_proforma (borrador / revisada / enviada — es el guard anti-duplicados del envío de proforma)
## Custom Fields de OPORTUNIDAD
requiere_visita (sí/no)

## Custom Values (carpeta "Termical — Proforma")
datos_fiscales · iban · diagnostico · metodos_pago · texto_rgpd · zona_servicio
Merge: {{ custom_values.nombre }} — los usa la plantilla de proforma.

## Calendarios (REGISTRO MANUAL — regla del cliente, no negociable)
- "Visitas": franjas de 2 horas — 10-12, 12-14, 16-18, 18-20. Para diagnósticos y visitas.
- "Instalaciones": bloqueos de mañana o día completo. Para trabajos.
- PROHIBIDO configurar reserva pública, auto-agendado o compartir links de booking. El dueño anota a mano. Motivo: protege su ruta diaria y su segunda agenda de Leroy Merlin.
- Recordatorios al cliente: 1 día antes + 2 horas antes de la cita (vía plantillas de WhatsApp aprobadas).

## Convenciones
- Campos nuevos: snake_case. Tags nuevos: minúsculas-con-guiones. Todo en español. Timezone: Europe/Madrid.
