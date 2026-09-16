# Plantillas de WhatsApp para crear en Meta — TÉRMYCAL

> Generado el 15-sep-2026 a partir de los 10 nodos SMS pendientes, leídos por API.
> **Son 10 plantillas.** Todas de categoría **Utility** (son transaccionales, no marketing)
> e idioma **Español (ES)**.

## Reglas de Meta que hay que respetar

1. Las variables son **posicionales**: `{{1}}`, `{{2}}`… No se ponen los merge fields de la
   plataforma; esos se mapean después, al configurar el nodo en el workflow.
2. **El cuerpo NO puede empezar ni terminar con una variable.** Tiene que haber texto
   alrededor.
3. **No puede haber dos variables seguidas** sin texto entre ellas.
4. Meta pide un **valor de ejemplo** por variable al crear la plantilla.

---

## 1 · `seguimiento_inactividad_d3`
**Dónde:** BOT-FU · Inactividad 3 días · nodo 0 · **144 caracteres**

```
Hola {{1}}, soy Sofía de TÉRMYCAL. Quedamos a medias con lo de su aparato — ¿lo retomamos? Respóndame por aquí y seguimos 👍
```
⚠️ *Cambiado el 16-sep: decía "soy Alejandro". Como el bot es Sofía, un mensaje firmado por
Alejandro tras una conversación con ella chirría. Las otras nueve plantillas no tienen este
problema: o son neutras, o hablan de cosas que hace Alejandro de verdad (el "en un rato estoy
contigo" del recordatorio es él, que es quien va).*

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |

---

## 2 · `despedida_inactividad_d5`
**Dónde:** BOT-FU · Inactividad 5 días · nodo 0 · **154 caracteres**

```
Hola {{1}}, no quiero ser pesado 😊 Dejo el tema aparcado. Cuando quieras retomar tu presupuesto, escríbeme por aquí y lo vemos. ¡Gracias!
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |

---

## 3 · `cita_confirmacion`
**Dónde:** SP03 · nodo 0 · **~200 caracteres**
*(corregido: le faltaban las tildes en "avísame por aquí")*

```
Confirmado, {{1}}! Nos vemos el {{2}} en la franja de {{3}} a {{4}}. Cualquier cambio, avísame por aquí.
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |
| {{2}} | `{{appointment.only_start_date}}` | 22/09/2026 |
| {{3}} | `{{appointment.only_start_time}}` | 10:00 |
| {{4}} | `{{appointment.only_end_time}}` | 12:00 |

---

## 4 · `cita_recordatorio_1dia`
**Dónde:** SP03 · nodo 3 · **182 caracteres**

```
Hola {{1}}, te recuerdo tu cita de mañana {{2}} en la franja de {{3}} a {{4}}. ¡Nos vemos!
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |
| {{2}} | `{{appointment.only_start_date}}` | 22/09/2026 |
| {{3}} | `{{appointment.only_start_time}}` | 10:00 |
| {{4}} | `{{appointment.only_end_time}}` | 12:00 |

---

## 5 · `cita_recordatorio_2h`
**Dónde:** SP03 · nodo 5 · **~145 caracteres**
⚠️ *El texto original empezaba con la variable — Meta lo rechaza. Se le añadió "Hola".*

```
Hola {{1}}, en un rato estoy contigo — franja de {{2}} a {{3}}. ¡Hasta ahora!
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |
| {{2}} | `{{appointment.only_start_time}}` | 10:00 |
| {{3}} | `{{appointment.only_end_time}}` | 12:00 |

---

## 6 · `proforma_aviso_envio`
**Dónde:** SP04 · nodo 10 · **~135 caracteres**
⚠️ *Empezaba con la variable — corregido con "Hola".*

```
Hola {{1}}, te acabo de enviar el presupuesto a tu correo ({{2}}). Cualquier duda me escribes por aquí 👍
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |
| {{2}} | `{{contact.email}}` | lucia@ejemplo.com |

---

## 7 · `proforma_seguimiento_d2`
**Dónde:** SP06 · nodo 4 · **117 caracteres**

```
Hola {{1}}, ¿pudiste ver el presupuesto que te envié? Si tienes cualquier duda me dices y lo vemos 👍
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |

---

## 8 · `proforma_seguimiento_d5`
**Dónde:** SP06 · nodo 9 · **154 caracteres**

```
Hola {{1}}, te escribo por última vez por lo del presupuesto — sigue en pie, y si hay que ajustar algo lo vemos sin compromiso. ¡Gracias!
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |

---

## 9 · `trabajo_confirmado`
**Dónde:** AP01 · nodo 3 · **~115 caracteres**
⚠️ *El texto original tenía **comillas dobles literales** al principio y al final — hay que
quitarlas. Y usaba `{{fecha}}` y `{{rango}}`, que **no son merge fields válidos**: hay que
mapearlos a los de la cita.*

```
¡Genial, {{1}}! Queda confirmado tu trabajo. Te esperamos el {{2}} en la franja {{3}}. Nos vemos 🔧
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |
| {{2}} | `{{appointment.only_start_date}}` | 22/09/2026 |
| {{3}} | `{{appointment.only_start_time}}` a `{{appointment.only_end_time}}` | 10:00 a 12:00 |

---

## 10 · `valoracion_link`
**Dónde:** AP02-RBD · nodo 1 · **~155 caracteres**
⚠️ *Era la peor: **empezaba Y terminaba** con variable. Meta la rechaza seguro.*

```
Hola {{1}}, ¡gracias por confiar en TÉRMYCAL! ¿Me ayudas valorando el servicio? Es un momento: {{2}} ¡Muchas gracias!
```

| Var | Mapea a | Ejemplo |
|---|---|---|
| {{1}} | `{{contact.first_name}}` | Lucía |
| {{2}} | `{{trigger_link.4YvqZfoC3PHxVYlg0h5F}}` | https://link.termycal.com/abc123 |

**Alternativa recomendada:** en vez de meter el enlace en el cuerpo, crear la plantilla con
un **botón de URL dinámica**. Los enlaces dentro del texto bajan la tasa de aprobación y
quedan peor en el móvil.

---

## Después de que Meta las apruebe

Cada plantilla da un `template_id`. Con esos 10 ids, el script
`scripts/migrar_sms_a_whatsapp.py` cambia los nodos de golpe — la forma del nodo WhatsApp
ya está validada, solo falta añadir el `template_id` y el mapeo de variables.
