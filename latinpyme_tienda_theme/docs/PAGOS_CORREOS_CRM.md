# Pagos, correo post-compra y CRM en Tienda LatinPyme

Documentación técnica de cómo está implementado hoy cada punto, basada en el código real del repositorio (`latinpyme_tienda_theme` + módulos nativos de Odoo 19 que usa). No se documentan aquí valores de configuración que solo existen en la base de datos (credenciales, plantillas editadas desde el backend) porque esta sesión no tuvo acceso al backend para verificarlos en vivo — se indica explícitamente en cada sección qué es código (verificable en git) y qué es configuración (verificable solo entrando a Odoo).

## 1. Pagos — Mercado Pago

### Qué es nativo de Odoo (no está en este repo)

Tienda usa el módulo oficial `payment_mercado_pago` de Odoo 19 (Enterprise), declarado como dependencia en `latinpyme_tienda_theme/__manifest__.py`. Todo el flujo de pago (crear la preferencia, redirigir al checkout de Mercado Pago, recibir la confirmación) es código nativo de Odoo, no de este módulo:

- `POST /payment/mercado_pago/payments` — crea la preferencia de pago cuando el cliente hace clic en pagar.
- `GET` (ruta de retorno) — a donde Mercado Pago redirige al cliente después de pagar.
- `POST /payment/mercado_pago/webhook` — la URL que Mercado Pago llama **de forma asíncrona**, por su cuenta, para avisar que un pago cambió de estado (aprobado, rechazado, etc.). Esta es la fuente de verdad real del estado del pago, no la redirección del navegador.

Cuando el webhook confirma un pago (`payment.transaction` pasa a estado `done`), Odoo automáticamente:
1. Concilia el pago con la orden (`sale.order`) asociada.
2. Confirma la orden (`action_confirm`), lo que dispara el correo de confirmación (ver sección 2).

Código relevante (`odoo-core-19/addons/sale/models/payment_transaction.py`, método `_post_process`): la confirmación de la orden y el envío del correo pasan **por transacción de pago**, no por un cron ni por acción manual — es automático en cuanto el webhook llega.

### Qué SÍ es personalizado en este repo

Solo un archivo, con un único ajuste: `latinpyme_tienda_theme/models/payment_transaction.py`.

Problema que resuelve: quando el carrito tiene 2+ productos, el checkout de Mercado Pago colapsa el resumen a la palabra genérica "Productos" (confirmado en vivo, sesión anterior) — Mercado Pago solo muestra un título legible cuando la preferencia tiene **un solo ítem**. La solución (decisión ya tomada por el usuario: "Híbrido: un solo ítem pero mejor formateado") sobreescribe `_mercado_pago_prepare_preference_request_payload` para armar un único ítem cuyo título concatena los nombres reales de los productos (ej. `"3 productos: Curso A, Curso B y Curso C"`), en vez de dejar el título por defecto de Odoo (la referencia interna de la orden, ej. `"S00224"`, que no le dice nada al cliente).

No se toca nada del manejo de credenciales, estados de transacción, ni el webhook — todo eso sigue siendo 100% código nativo.

### Diferencia staging vs. production en Odoo.sh

Staging y producción son **bases de datos separadas** en Odoo.sh (no comparten configuración). Eso significa que el proveedor de pago (`payment.provider`, registro de Mercado Pago) está configurado **dos veces, de forma independiente**, cada uno desde Ajustes → Pagos → Proveedores de pago en el backend de cada entorno:

- **Staging**: se probó en sesiones anteriores con credenciales de **sandbox** de Mercado Pago (pagos de prueba, sin dinero real).
- **Producción**: credenciales **reales/live**.

Esto no está en el código — es configuración pura de base de datos (API keys, modo test/live). Si necesitas confirmar o cambiar esas credenciales, es directamente en Ajustes → Pagos → Proveedores de pago → Mercado Pago, en cada entorno por separado. No pude capturar esa pantalla en esta sesión porque no tengo una sesión iniciada en el backend (ver nota al final).

## 2. Correo después de la compra

**100% nativo — no hay ninguna personalización de correo en este módulo.** Confirmado: no existe ningún `mail.template` propio, ni ninguna llamada a `send_mail`/`_message_post` en todo `latinpyme_tienda_theme`.

Flujo real (`odoo-core-19/addons/sale/models/sale_order.py`):

```
pago confirmado (webhook Mercado Pago)
  → payment.transaction._post_process()
    → sale.order.action_confirm() [con contexto send_email=True]
      → sale.order._send_order_confirmation_mail()
        → usa el mail.template "Confirmación de venta" (id técnico: mail_template_sale_confirmation)
```

Ese `mail.template` es completamente editable desde el backend: Ajustes → Técnico → Plantillas de correo, buscar "Confirmación de venta" (o desde Ventas → Configuración → Plantillas de correo si el menú técnico está desactivado). Ahí se controla el asunto, el cuerpo, y si se adjunta el PDF de la orden/factura — sin tocar código.

Si en algún momento se quiere personalizar el contenido de ese correo (logo, tono, información adicional), la vía correcta es **editar esa plantilla desde el backend**, no crear código nuevo — es exactamente el mismo patrón que ya usan para la factura y la orden en PDF (`invoice_templates.xml`, `saleorder_templates.xml` en este módulo personalizan el **PDF**, no el correo).

## 3. Conexión con CRM

**No existe.** Verificado en el código:
- `crm` no está en las dependencias del manifest (`depends`: `website`, `website_sale`, `account`, `sale`, `payment_mercado_pago` — sin `crm`).
- No hay una sola referencia a `crm.lead` en todo `latinpyme_tienda_theme`.

Lo que sí existe, y que a veces se confunde con "CRM", es el flujo de **Contactos** (`res.partner`): cuando un cliente compra, Odoo crea o actualiza un contacto con sus datos (nombre, dirección, teléfono, NIT) y la orden apunta a ese contacto — pero eso es el módulo de Contactos, no el pipeline de oportunidades de ventas (`crm.lead`) que es la app CRM propiamente dicha. Ese flujo contacto↔orden ya está documentado en detalle en `docs/flujo_ecommerce_tienda_res_partner.md`, en la raíz del repo `latinpyme-odoo` (repositorio distinto a este submódulo, y ese archivo puntual todavía no está subido a git — vive solo en la copia local), con el porqué de los bloqueos de edición de campos.

Si el objetivo es que cada compra genere automáticamente una oportunidad en el pipeline de CRM (para seguimiento comercial, no solo el registro contable de la venta), eso **no está construido** — sería una integración nueva a diseñar (instalar `crm`, decidir en qué momento crear el `crm.lead`, a qué equipo/vendedor asignarlo, etc.), no algo que ya exista y haya que "encontrar".

## 4. Limitaciones de este documento

- Todo lo de las secciones 1-3 marcado como "código" está verificado leyendo los archivos reales del repositorio (`git show` sobre `origin/production`), no es una suposición.
- Todo lo marcado como "configuración de backend" (credenciales de Mercado Pago, contenido exacto de la plantilla de correo activa hoy) **no se verificó en vivo** — esta sesión no tenía una sesión iniciada en el backend de Odoo.sh, así que no se pudieron capturar pantallas de esas configuraciones. Si se quiere una captura real de esas pantallas para completar la documentación visualmente, hay que compartir acceso a una sesión de backend ya autenticada (staging o producción) en el navegador que uso para las capturas.
