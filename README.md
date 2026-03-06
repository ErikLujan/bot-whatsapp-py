# WhatsApp Technical Support Bot

Bot de soporte técnico automatizado integrado con la API oficial de WhatsApp (Meta). Permite a los clientes reportar problemas de hardware o software directamente desde WhatsApp, genera un ticket en base de datos y notifica al equipo técnico por email de forma asíncrona.

## Stack

- **Flask** — framework web y manejo del webhook
- **PostgreSQL (Supabase)** — persistencia de tickets
- **WhatsApp Cloud API (Meta)** — canal de comunicación con el cliente
- **Resend API** — envío transaccional de correos al equipo técnico
- **Gunicorn** — servidor WSGI para producción
- **Render** — deploy en la nube

## Cómo funciona

El bot gestiona el contexto de cada conversación mediante una máquina de estados en memoria. Cada usuario tiene un estado asociado que determina qué acción ejecutar según el mensaje recibido:

- **Menú principal** — el cliente elige entre reportar un problema o consultar un ticket existente.
- **Esperando descripción** — el cliente describe el problema y el sistema genera un ticket con ID único persistido en base de datos.
- **Consultando ID** — el cliente ingresa su ID de ticket y recibe el estado actual de su reparación en tiempo real.

Cada vez que se crea un ticket, se dispara una notificación por email al encargado del local en un hilo secundario (`threading`), lo que garantiza que el webhook de Meta responda en menos de un segundo sin bloquearse esperando el envío del correo.

## Estructura del proyecto

```
├── app.py          # Controlador de rutas y webhook
├── services.py     # Lógica de negocio, integración con APIs y base de datos
├── mensajes.py     # Textos del bot y plantillas HTML para los correos
├── .env.example
└── requirements.txt
```

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/whatsapp-support-bot.git
cd whatsapp-support-bot

# Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Variables de entorno

Creá un archivo `.env` en la raíz basándote en `.env.example`. Las variables necesarias son:

```env
# WhatsApp Cloud API
WHATSAPP_TOKEN=tu_token_de_acceso
WHATSAPP_PHONE_ID=id_del_numero_de_telefono
VERIFY_TOKEN=token_de_verificacion_del_webhook

# Supabase
SUPABASE_URL=url_del_proyecto
SUPABASE_KEY=anon_key

# Resend
RESEND_API_KEY=tu_api_key
SUPPORT_EMAIL=email_del_encargado
```

### Ejecutar en desarrollo

```bash
python app.py
```

Para recibir mensajes de WhatsApp en local necesitás exponer el servidor con una herramienta como [ngrok](https://ngrok.com/) y configurar la URL del webhook en el panel de Meta.

## Deploy

El proyecto está configurado para Render usando Gunicorn como servidor de producción. En Render configurá el **Start Command** como:

```bash
gunicorn app:app
```

Y cargá todas las variables del `.env` desde el panel **Environment** del servicio.
