import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from supabase import create_client, Client
from src.config import Config

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

user_state = {}

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
    # DATOS DE CONFIGURACIÓN (Lo ideal es ponerlos en Render/Variables de Entorno)
    # Tu correo (el que envía)
    REMITENTE = os.environ.get("EMAIL_SENDER")  
    # La contraseña de 16 letras que generaste
    PASSWORD = os.environ.get("EMAIL_PASSWORD") 
    # El correo del técnico (quien recibe la alerta)
    DESTINATARIO = "correo_del_tecnico@gmail.com" 

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = REMITENTE
    msg['To'] = DESTINATARIO
    msg['Subject'] = f"🚨 Nuevo Ticket #{ticket_id} - Soporte Biomatrix"

    # Cuerpo del correo
    cuerpo = f"""
    Hola Equipo,

    Se ha generado una nueva solicitud de soporte técnico.
    
    ------------------------------------------------
    🎫 Ticket ID: {ticket_id}
    📱 Cliente: {telefono_cliente}
    ⚠️ Problema reportado: {problema}
    ------------------------------------------------

    Por favor, contactar al cliente a la brevedad.
    """
    
    msg.attach(MIMEText(cuerpo, 'plain'))

    # Conexión con el servidor de Gmail
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Encriptar la conexión
        server.login(REMITENTE, PASSWORD)
        text = msg.as_string()
        server.sendmail(REMITENTE, DESTINATARIO, text)
        server.quit()
        print("✅ Correo de alerta enviado al técnico.")
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")