from flask import Flask, request, jsonify
from src.config import Config 
from src.services import procesar_mensaje, enviar_mensaje_whatsapp

app = Flask(__name__)

@app.route("/")
def home():
    '''
    Summary: Endpoint de prueba o "Health Check" para verificar desde el navegador que el servidor esté activo y corriendo.
    Parameters: Ninguno.
    Return: str - Un mensaje de texto simple indicando el estado del bot.
    '''
    return "El Bot de Biomatrix está VIVO 🤖 y listo para recibir mensajes."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    '''
    Summary: Endpoint principal que actúa como Webhook para la API de WhatsApp Cloud. Maneja tanto la verificación inicial de Meta (GET) como la recepción estructurada de nuevos mensajes (POST), delegando la toma de decisiones al módulo de servicios.
    Parameters: Ninguno.
    Return: tuple - Una respuesta de confirmación para Meta (texto plano para GET o un objeto JSON para POST) acompañada de un código de estado HTTP (200 o 403).
    '''
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        
        if mode == "subscribe" and token == Config.VERIFY_TOKEN:
            return challenge, 200
        return "Error de verificación", 403

    if request.method == "POST":
        try:
            data = request.get_json()
            entry = data["entry"][0]["changes"][0]["value"]
            
            if "messages" in entry:
                message = entry["messages"][0]
                numero = message["from"]
                
                texto = message.get("text", {}).get("body", "").lower()
                
                respuesta_texto = procesar_mensaje(texto, numero)
                
                if respuesta_texto:
                    enviar_mensaje_whatsapp(respuesta_texto, numero)

            return jsonify({"status": "success"}), 200

        except Exception as e:
            print(f"❌ Error en el webhook: {e}")
            return jsonify({"status": "error"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)