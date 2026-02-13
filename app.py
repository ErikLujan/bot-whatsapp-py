# app.py
from flask import Flask, request, jsonify
from src.config import Config
from src.services import procesar_mensaje, enviar_mensaje_whatsapp

app = Flask(__name__)

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # Verificación
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        if mode == "subscribe" and token == Config.VERIFY_TOKEN:
            return request.args.get("hub.challenge"), 200
        return "Error", 403

    # Recepción de Mensajes
    if request.method == "POST":
        try:
            data = request.get_json()
            entry = data["entry"][0]["changes"][0]["value"]
            
            if "messages" in entry:
                message = entry["messages"][0]
                numero = message["from"]
                texto = message["text"]["body"]
                
                # 1. Obtenemos la respuesta del cerebro
                respuesta_texto = procesar_mensaje(texto, numero)
                
                # 2. Enviamos la respuesta (Simulada por ahora)
                enviar_mensaje_whatsapp(respuesta_texto, numero)

            return jsonify({"status": "success"}), 200
        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"status": "error"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)