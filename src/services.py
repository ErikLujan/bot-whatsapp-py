import requests
import json
import threading
import resend
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from supabase import create_client, Client
from src.config import Config

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

resend.api_key = os.environ.get("RESEND_API_KEY")

user_state = {}

def generar_ticket_real(cliente_numero, problema_texto):
    """Guarda en Supabase y devuelve el ID. Si falla, devuelve uno fake."""
    print(f"💾 Intentando guardar ticket en Supabase...")
    
    if not supabase:
        print("⚠️ AVISO: No hay credenciales de Supabase. Usando ID temporal 9999.")
        return 9999

    try:
        datos = {
            "telefono": cliente_numero,
            "problema": problema_texto,
            "estado": "pendiente"
        }
        
        response = supabase.table("tickets").insert(datos).execute()
        
        if response.data:
            ticket_id = response.data[0]['id']
            print(f"✅ Guardado en Supabase con ID Real: {ticket_id}")
            return ticket_id
        
        return 9999

    except Exception as e:
        print(f"❌ Error guardando en Supabase: {e}")
        return 9999

def procesar_mensaje(texto, numero):
    texto = texto.lower().strip()
    estado_actual = user_state.get(numero, "MENU")

    if estado_actual == "MENU":
        if "reportar" in texto or "1" == texto:
            user_state[numero] = "ESPERANDO_PROBLEMA"
            return "🛠️ *Nuevo Ticket*\nPor favor, describí tu problema."
        
        elif "estado" in texto or "2" == texto:
            user_state[numero] = "ESPERANDO_ID"
            return "🔍 *Consultar Estado*\nEscribí el ID de tu ticket."
            
        else:
            return (
                "🤖 *Soporte Técnico*\n"
                "1️⃣ Reportar problema\n"
                "2️⃣ Consultar estado"
            )

    elif estado_actual == "ESPERANDO_PROBLEMA":
        data = {"telefono": numero, "problema": texto, "estado": "Pendiente"}
        result = supabase.table("tickets").insert(data).execute()
        ticket_id = result.data[0]['id']
        
        user_state[numero] = "MENU"
        return f"✅ Ticket #{ticket_id} creado correctamente."

    elif estado_actual == "ESPERANDO_ID":
        if texto.isdigit():
            response = supabase.table("tickets").select("*").eq("id", int(texto)).execute()
            user_state[numero] = "MENU"
            
            if response.data:
                ticket = response.data[0]
                return f"🎫 Ticket #{ticket['id']}: {ticket['estado']}"
            else:
                return "❌ No encontré ese ticket."
        else:
            return "⚠️ Por favor, enviá solo el número."
            
    return "No entendí."

def enviar_mensaje_whatsapp(texto, numero):
    """
    Envía el mensaje a la API Oficial de WhatsApp si hay credenciales.
    Siempre imprime en consola para debugging.
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
                print("❌ ERROR DETALLADO DE META:", response.text)

            response.raise_for_status()
        except Exception as e:
            print(f"❌ Error enviando a Meta: {e}")

def enviar_correo_ticket(ticket_id, problema, telefono_cliente):
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
                "to": "eriklujan2005@gmail.com",
                "subject": f"🚨 Ticket #{ticket_id} - Biomatrix",
                "html": html_content
            })
            print(f"✅ [Resend] Correo enviado! ID: {r.get('id')}")
            
        except Exception as e:
            print(f"❌ [Resend] Error: {e}")

    hilo = threading.Thread(target=_tarea_enviar_email)
    hilo.start()