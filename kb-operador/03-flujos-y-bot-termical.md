# TÉRMYCAL — Flujos y bot (KB interna del Operador CRM)

## Bot de clientes: "Recepcionista Termical" (Conversation AI)
- Habla castellano de España, tono cercano andaluz-neutro. Voice notes ON, imágenes ON, espera 10-15s, máx 15 mensajes.
- Arranca en modo Suggestive (supervisado); pasará a Auto-Pilot tras 1-2 semanas de rodaje validado.
- QUÉ HACE: responde FAQs desde su propia KB (precios, financiación, garantías, zona), captura datos del lead a custom fields (Bot Goals), pide FOTOS del aparato/ubicación, estima SOLO termos eléctricos, calentadores de gas y calderas (con extras 100-200 € como orientativo).
- QUÉ NO HACE NUNCA: agendar citas ni tocar calendarios · enviar proformas · cerrar precio con extras · estimar aerotermia · atender urgencias con riesgo (olor a gas → derivación inmediata a humano).
- Su KB (FAQs + catálogo de precios) es SEPARADA de esta. Esta KB interna jamás se conecta al Recepcionista.

## Flujo de proforma (dual)
- Flujo B (~80% de casos, AUTOMÁTICO tras aprobación): el bot captura campos + email + fotos → tag pide-presupuesto → notificación interna con resumen → el dueño aplica el tag aprobar-proforma desde la app (2 taps) → workflow genera el documento de proforma y lo envía por email. Guard: estado_proforma=enviada bloquea reenvíos.
- Flujo A (bajo presupuesto / aerotermia / extras, MANUAL): el dueño genera desde plantilla, edita y envía a mano.
- La proforma lleva firma digital (válida desde cualquier móvil) y validez de 15 días.

## Reseñas (encuesta-filtro)
Al completar un trabajo: encuesta 1-5 por WhatsApp ANTES de dar el link de Google → 1-3: notificación interna para gestionar al insatisfecho (no se le da link) · 4-5: agradecimiento + link de reseña + tag resena-solicitada. Las reseñas se responden con IA supervisada.

## Seguimientos
- Post-proforma: día 2 y día 5 (plantillas WhatsApp aprobadas), con guards que abortan si la oportunidad avanzó de etapa. Si no responde: nota + tag frio.
- Inactividad del bot: 6 horas / día 3 / día 5 → tag frio y parar.

## Fuera de alcance (FASE 2 — no construir ahora)
Facturación automática + Verifactu · suma automática de extras por IA · integración con la agenda de Leroy Merlin · telefonía (número español sin Twilio; mitigación: buzón de voz con locución que deriva a WhatsApp).
