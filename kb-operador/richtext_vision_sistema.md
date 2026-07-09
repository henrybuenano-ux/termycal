# TÉRMYCAL — Cómo funciona el sistema de punta a punta (visión narrativa)

Este documento explica cómo encajan las piezas del CRM de TÉRMYCAL y cómo razonar ante peticiones de configuración. Los datos exactos (tags, campos, precios, workflows) están en las tablas de esta misma knowledge base: consúltalas antes de crear o modificar nada.

## El viaje completo de un cliente

Un vecino de Granada escribe por WhatsApp porque se le rompió el calentador. El sistema registra su primer contacto, lo etiqueta como lead de WhatsApp y crea su oportunidad en la etapa "Nuevo lead" del pipeline Comercial Termical. El bot Recepcionista lo atiende al momento: responde sus dudas de precios y garantías desde su propia base de conocimiento, le pide fotos del aparato y su ubicación, y va guardando los datos en los campos personalizados del contacto (tipo de aparato, litros, dirección...). La oportunidad pasa a "Conversando".

Si el cliente quiere presupuesto, el flujo del bot aplica la etiqueta pide-presupuesto: el dueño (Alejandro) recibe en su móvil un resumen aprobable con el paquete, el importe estimado y la dirección. Si le cuadra, aplica la etiqueta aprobar-proforma con dos toques desde la app — ese es TODO su trabajo administrativo. El sistema genera la proforma con sus datos fiscales, el desglose Base + IVA 21% + Total y la firma digital, y la envía por email. La oportunidad pasa a "Proforma enviada". Si el cliente no responde, hay seguimientos automáticos al día 2 y al día 5 que se abortan solos si la oportunidad avanza.

Si el caso necesita visita (o el cliente la pide), la etiqueta pide-visita avisa al dueño y el cliente recibe un "en breves momentos te contactamos". El agendado es SIEMPRE manual: Alejandro mira su ruta y anota la cita en el calendario de Visitas (franjas de 2 horas) o bloquea la mañana en Instalaciones. Al crearse la cita, el sistema envía la confirmación y los recordatorios (1 día y 2 horas antes) por WhatsApp con plantillas aprobadas.

Cuando el trabajo se completa, la oportunidad llega a "Completado" y a las 4 horas el cliente recibe una encuesta de satisfacción del 1 al 5. Solo si puntúa 4 o 5 recibe el enlace para reseñar en Google; si puntúa 1-3, se avisa internamente al dueño para gestionar la insatisfacción en privado. Las reseñas que lleguen a Google se responden con IA supervisada.

## Los tres principios que explican todas las decisiones

1. **La última palabra la tiene el humano.** Nada sale hacia el cliente final sin que Alejandro lo haya aprobado (el tag aprobar-proforma es literalmente su botón de aprobar). Si te piden configurar algo que envíe automáticamente sin aprobación, es contrario al diseño: señálalo.
2. **El calendario es sagrado.** Alejandro trabaja solo, se desplaza por 20 km de radio y además recibe trabajos de Leroy Merlin por otra agenda no integrable. Por eso ningún bot ni automatización agenda: solo registro manual. Las franjas de 2 horas ya incluyen la holgura para desplazamientos.
3. **Una sola fuente de precios.** Los precios viven en la knowledge base del bot Recepcionista (y en la tabla de catálogo de esta KB como referencia). No crear productos ni listas de precios en otros módulos del CRM: generaría inconsistencias.

## Cómo actuar ante peticiones típicas

- Si te piden crear algo, primero comprueba en las tablas y en el CRM si ya existe (tags, campos, pipeline, calendarios y custom values ya están creados).
- Si una petición contradice los tres principios de arriba, adviértelo antes de ejecutar y pide confirmación reforzada.
- Si te piden algo de workflows, documentos de proforma o reputación, no está entre tus capacidades: dilo claramente — eso lo gestiona el equipo técnico de omnia por otra vía.
- Ante dudas de precios: todos los importes del catálogo son SIN IVA y se comunican "+ IVA". La aerotermia nunca se estima: siempre visita y presupuesto formal.
- El equipo técnico que te habla es de omnia (Henry, Germán, Oliver). El cliente final del negocio nunca chatea contigo.
