import requests
import json

from supabase import create_client, Client
from src.config import Config

# --- INICIALIZACIÓN ---
supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

# Memoria temporal
user_state = {}

def procesar_mensaje(texto, numero):
    texto = texto.lower().strip()
    estado_actual = user_state.get(numero, "MENU")

    # --- LÓGICA DEL BOT ---
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
        # Guardar en Supabase
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
    # 1. LOG LOCAL (Para que sigas viendo en tu terminal)
    print(f"\n>> ENVIANDO A {numero}: {texto}\n")

    # 2. ENVÍO REAL A META
    token = Config.WHATSAPP_TOKEN
    id_numero = Config.PHONE_NUMBER_ID

    # Solo intentamos enviar si tenemos las credenciales configuradas
    if token and id_numero:
        url = f"https://graph.facebook.com/v22.0/{id_numero}/messages"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
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

            response.raise_for_status() # Lanza error si Meta rechaza el mensaje
            # print("✅ Enviado a WhatsApp correctamente")
        except Exception as e:
            print(f"❌ Error enviando a Meta: {e}")
            # Aquí podrías guardar el error en un log si quisieras