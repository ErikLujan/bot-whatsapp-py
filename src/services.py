import requests
import json
import threading
import resend
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from supabase import create_client, Client
from src.config import Config

# 1. Configuración de Clientes
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
resend.api_key = os.environ.get("RESEND_API_KEY")

# 2. Estado de memoria (Para saber si el usuario está en el menú o escribiendo un problema)
user_state = {}

def enviar_correo_ticket(ticket_id, problema, telefono_cliente):
    """
    Envía el correo usando Resend en un hilo separado (background)
    para no bloquear la respuesta de WhatsApp.
    """
    def _tarea_enviar_email():
        print(f"📧 [Resend] Preparando envío Ticket #{ticket_id}...")
        
        html_content = f"""
        <h1>🚨 Nuevo Ticket de Soporte #{ticket_id}</h1>
        <p><strong>Cliente:</strong> {telefono_cliente}</p>
        <p><strong>Problema:</strong> {problema}</p>
        <hr>
        <p><em>Enviado automáticamente por Bot Biomatrix</em></p>
        """

        try:
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": "eriklujan2005@gmail.com", # <--- TU CORREO
                "subject": f"🚨 Ticket #{ticket_id} - Biomatrix",
                "html": html_content
            })
            print(f"✅ [Resend] Correo enviado! ID: {r.get('id')}")
            
        except Exception as e:
            print(f"❌ [Resend] Error: {e}")

    # Lanzamos el hilo
    hilo = threading.Thread(target=_tarea_enviar_email)
    hilo.start()

def procesar_mensaje(texto, numero):
    """
    Cerebro del Bot: Maneja el menú y los estados de conversación.
    """
    texto = texto.lower().strip()
    estado_actual = user_state.get(numero, "MENU")

    # --- ESTADO 1: MENÚ PRINCIPAL ---
    if estado_actual == "MENU":
        if "reportar" in texto or "1" == texto:
            user_state[numero] = "ESPERANDO_PROBLEMA"
            return "🛠️ *Nuevo Ticket*\nPor favor, describí tu problema en un solo mensaje."
        
        elif "estado" in texto or "2" == texto:
            user_state[numero] = "ESPERANDO_ID"
            return "🔍 *Consultar Estado*\nEscribí el número de ID de tu ticket."
            
        else:
            return (
                "🤖 *Soporte Técnico Biomatrix*\n\n"
                "1️⃣ Reportar problema\n"
                "2️⃣ Consultar estado\n\n"
                "Responde con el número de la opción."
            )

    # --- ESTADO 2: CREANDO TICKET (Aquí estaba el detalle) ---
    elif estado_actual == "ESPERANDO_PROBLEMA":
        try:
            # A. Guardar en Supabase
            data = {"telefono": numero, "problema": texto, "estado": "Pendiente"}
            result = supabase.table("tickets").insert(data).execute()
            
            # B. Obtener ID generado
            ticket_id = result.data[0]['id']
            
            # C. ¡ENVIAR EL CORREO! (Esto es lo que agregué) 🚀
            enviar_correo_ticket(ticket_id, texto, numero)

            # D. Resetear estado y confirmar
            user_state[numero] = "MENU"
            return f"✅ Ticket #{ticket_id} creado correctamente.\nUn técnico ha sido notificado."
            
        except Exception as e:
            print(f"❌ Error creando ticket: {e}")
            user_state[numero] = "MENU"
            return "❌ Hubo un error guardando tu ticket. Intenta de nuevo."

    # --- ESTADO 3: CONSULTANDO ESTADO ---
    elif estado_actual == "ESPERANDO_ID":
        if texto.isdigit():
            response = supabase.table("tickets").select("*").eq("id", int(texto)).execute()
            user_state[numero] = "MENU"
            
            if response.data:
                ticket = response.data[0]
                return f"🎫 Ticket #{ticket['id']}\nEstado: *{ticket['estado']}*\nProblema: {ticket['problema']}"
            else:
                return "❌ No encontré un ticket con ese número."
        else:
            return "⚠️ Por favor, enviá solo el número del ticket (ej: 12)."
            
    return "No entendí."

def enviar_mensaje_whatsapp(texto, numero):
    """
    Envía la respuesta a WhatsApp.
    """
    print(f"\n>> ENVIANDO A {numero}: {texto}\n")

    token = Config.WHATSAPP_TOKEN
    id_numero = Config.PHONE_NUMBER_ID

    if token and id_numero:
        url = f"https://graph.facebook.com/v22.0/{id_numero}/messages"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # Corrección para Argentina (Solo si es necesario para la API de prueba)
        if "549" in numero:
            numero = numero.replace("549", "54")
        
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": texto}
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code != 200:
                print("❌ ERROR META:", response.text)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Error enviando a Meta: {e}")