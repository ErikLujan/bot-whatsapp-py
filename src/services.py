import requests
import json
import threading
import resend
import os

from supabase import create_client, Client
from src.config import Config
from src.mensajes import MENSAJES

supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
resend.api_key = os.environ.get("RESEND_API_KEY")

user_state = {}

def enviar_correo_ticket(ticket_id, problema, telefono_cliente):
    '''
    Summary: Prepara y despacha un correo electrónico notificando la creación de un ticket mediante la API de Resend utilizando un hilo secundario.
    Parameters: 
        ticket_id (int): El identificador numérico único del ticket en la base de datos.
        problema (str): La descripción del inconveniente técnico provista por el usuario.
        telefono_cliente (str): El número de teléfono desde el cual el usuario se comunicó.
    Return: None
    '''
    def _tarea_enviar_email():
        print(f"📧 [Resend] Preparando envío Ticket #{ticket_id}...")
        
        html_content = MENSAJES["email_html"].format(
            ticket_id=ticket_id, 
            telefono_cliente=telefono_cliente, 
            problema=problema
        )

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

def procesar_mensaje(texto, numero):
    '''
    Summary: Evalúa el texto ingresado por el usuario, gestiona el estado de la conversación y ejecuta operaciones en la base de datos según la etapa del menú.
    Parameters:
        texto (str): El contenido del mensaje enviado por el usuario.
        numero (str): El número telefónico que identifica de forma única al usuario.
    Return: str - El texto de respuesta que el bot enviará de vuelta al usuario por WhatsApp.
    '''
    texto = texto.lower().strip()
    estado_actual = user_state.get(numero, "MENU")

    if estado_actual == "MENU":
        if "reportar" in texto or "1" == texto:
            user_state[numero] = "ESPERANDO_PROBLEMA"
            return MENSAJES["pedir_problema"]
        
        elif "estado" in texto or "2" == texto:
            user_state[numero] = "ESPERANDO_ID"
            return MENSAJES["pedir_id"]
            
        else:
            return MENSAJES["bienvenida"]

    elif estado_actual == "ESPERANDO_PROBLEMA":
        try:
            data = {"telefono": numero, "problema": texto, "estado": "Pendiente"}
            result = supabase.table("tickets").insert(data).execute()
            
            ticket_id = result.data[0]['id']
            
            enviar_correo_ticket(ticket_id, texto, numero)

            user_state[numero] = "MENU"
            return MENSAJES["ticket_creado"].format(ticket_id=ticket_id)
            
        except Exception as e:
            print(f"❌ Error creando ticket: {e}")
            user_state[numero] = "MENU"
            return MENSAJES["error_ticket"]

    elif estado_actual == "ESPERANDO_ID":
        if texto.isdigit():
            response = supabase.table("tickets").select("*").eq("id", int(texto)).execute()
            user_state[numero] = "MENU"
            
            if response.data:
                ticket = response.data[0]
                return MENSAJES["estado_ticket"].format(
                    ticket_id=ticket['id'],
                    estado=ticket['estado'],
                    problema=ticket['problema']
                )
            else:
                return MENSAJES["ticket_no_encontrado"]
        else:
            return MENSAJES["formato_invalido"]
            
    return MENSAJES["no_entendido"]

def enviar_mensaje_whatsapp(texto, numero):
    '''
    Summary: Estructura el JSON requerido por la API de Meta y realiza una petición POST HTTP para enviar el mensaje final al cliente.
    Parameters:
        texto (str): El mensaje definitivo formateado que leerá el usuario.
        numero (str): El número de teléfono destinatario del mensaje.
    Return: None
    '''
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
                print("❌ ERROR META:", response.text)
            response.raise_for_status()
        except Exception as e:
            print(f"❌ Error enviando a Meta: {e}")