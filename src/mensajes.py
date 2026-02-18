MENSAJES = {
    "bienvenida": (
        "👋 ¡Hola! Bienvenido al canal de atención oficial de *Biomatrix Computación*.\n\n"
        "Es un placer saludarte. Soy tu asistente virtual y estoy aquí para ayudarte a gestionar "
        "tus consultas técnicas de forma rápida y organizada.\n\n"
        "Por favor, selecciona la opción que necesites respondiendo únicamente con el número correspondiente:\n\n"
        "1️⃣ *Reportar un problema técnico*\n"
        "2️⃣ *Consultar estado de reparación*"
    ),
    "pedir_problema": (
        "🛠️ *Nuevo Ticket de Soporte*\n\n"
        "Por favor, describe detalladamente el problema que presenta tu equipo en un solo mensaje. "
        "Cuanta más información nos brindes, más rápido podremos ayudarte."
    ),
    "ticket_creado": (
        "✅ ¡Excelente! Hemos registrado tu solicitud exitosamente bajo el *Ticket #{ticket_id}*.\n\n"
        "Un técnico especializado de nuestro equipo ha sido notificado y comenzará a analizar tu caso. "
        "Nos pondremos en contacto contigo a la brevedad."
    ),
    "error_ticket": (
        "❌ Lamentablemente ocurrió un error interno al intentar guardar tu solicitud. "
        "Por favor, aguarda unos minutos e intenta nuevamente."
    ),
    "pedir_id": (
        "🔍 *Consulta de Estado*\n\n"
        "Por favor, escribe únicamente el número de ID de tu ticket para poder buscarlo en nuestro sistema "
        "(por ejemplo: 12)."
    ),
    "estado_ticket": (
        "🎫 *Detalle de tu Solicitud*\n\n"
        "📌 *Ticket:* #{ticket_id}\n"
        "📊 *Estado actual:* {estado}\n"
        "📝 *Problema reportado:* {problema}\n\n"
        "Gracias por confiar en el equipo de Biomatrix."
    ),
    "ticket_no_encontrado": (
        "❌ Lo siento, no hemos podido localizar ningún registro con ese número en nuestra base de datos. "
        "Por favor, verifica el ID e intenta nuevamente."
    ),
    "formato_invalido": (
        "⚠️ El formato ingresado no es válido. Recuerda enviar únicamente el número de tu ticket."
    ),
    "no_entendido": (
        "🤔 Mis disculpas, no he logrado comprender tu respuesta. "
        "Por favor, ingresa una de las opciones válidas del menú principal."
    ),
    "email_html": """
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #0056b3;">🚨 Nuevo Ticket de Soporte #{ticket_id}</h2>
        <p>Se ha generado una nueva solicitud de asistencia técnica en el sistema de Biomatrix.</p>
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #0056b3; margin: 20px 0;">
            <p><strong>📱 Cliente (WhatsApp):</strong> {telefono_cliente}</p>
            <p><strong>📝 Problema reportado:</strong><br> {problema}</p>
        </div>
        <hr style="border: 0; border-top: 1px solid #eee;">
        <p style="font-size: 12px; color: #777;"><em>Mensaje generado y enviado automáticamente por el Bot de Biomatrix.</em></p>
    </div>
    """
}