# app.py
from flask import Flask, request, jsonify
import random
from config import Config 
from services import procesar_mensaje, enviar_mensaje_whatsapp, enviar_correo_ticket

app = Flask(__name__)

@app.route("/")
def home():
    return "El Bot de Biomatrix está VIVO 🤖 y listo para recibir mensajes."

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
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
                
                if "soporte" in texto or "ayuda" in texto or "humano" in texto:
                    ticket_id = random.randint(1000, 9999)
                    
                    mensaje_cliente = f"✅ Ticket #{ticket_id} generado.\n\nUn técnico humano ha sido notificado y revisará tu caso. Te contactaremos a la brevedad."
                    enviar_mensaje_whatsapp(mensaje_cliente, numero)
                    
                    print(f">> Generando alerta de correo para Ticket #{ticket_id}...")
                    enviar_correo_ticket(ticket_id, texto, numero)

                else:
                    respuesta_texto = procesar_mensaje(texto, numero)
                    
                    if respuesta_texto:
                        enviar_mensaje_whatsapp(respuesta_texto, numero)

            return jsonify({"status": "success"}), 200

        except Exception as e:
            print(f"❌ Error en el webhook: {e}")
            return jsonify({"status": "error"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)