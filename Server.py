from flask import Flask, request, jsonify
from chatbot import enviar_mensaje

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pregunta = data.get("question", "")

    if not pregunta:
        return jsonify({"respuesta": "No se recibio ninguna pregunta."}), 400

    respuesta = enviar_mensaje(pregunta)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9559, debug=True)

