import qi
import httplib
import json
import time
import sys

PEPPER_IP = "192.168.0.106"      # IP de tu robot Pepper
SERVER_IP = "192.168.122.1"      # IP de tu PC que corre Server.py
SERVER_PORT = 9559

try:
    session = qi.Session()
    session.connect("tcp://{}:9559".format(PEPPER_IP))
    print("Conectado a Pepper.")
except Exception as e:
    print("Error al conectar con Pepper: {}".format(e))
    sys.exit(1)
try:
    tts = session.service("ALTextToSpeech")
    asr = session.service("ALSpeechRecognition")
    memory = session.service("ALMemory")
except Exception as e:
    print("Error al obtener servicios de voz: {}".format(e))
    sys.exit(1)

# =======================
# CONFIGURAR ASR LIBRE
# =======================
try:
    asr.setLanguage("Spanish")
    asr.setWordSpotting(True)
except Exception as e:
    print("Error al configurar ASR: {}".format(e))
    sys.exit(1)

# =======================
# ENVIAR PREGUNTA AL SERVIDOR
# =======================
def enviar_pregunta(mensaje):
    try:
        conn = httplib.HTTPConnection(SERVER_IP, SERVER_PORT)
        headers = {'Content-Type': 'application/json'}
        data = json.dumps({"question": mensaje})
        conn.request("POST", "/chatbot", data, headers)
        response = conn.getresponse()
        respuesta = json.loads(response.read())["respuesta"]
        return respuesta
    except Exception as e:
        return "Error al comunicar con el servidor: {}".format(e)

# =======================
# CALLBACK CUANDO SE RECONOCE VOZ
# =======================
def on_word_recognized(value):
    if isinstance(value, list) and len(value) > 0:
        frase = value[0]
        print("Reconocido:", frase)

        if len(frase.strip()) < 3:
            return  # Ignora ruido

        respuesta = enviar_pregunta(frase)
        print("Respuesta:", respuesta)
        tts.say(respuesta)

        if "salir" in frase.lower() or "adios" in frase.lower():
            asr.unsubscribe("PepperChat")
            print("Sesión finalizada.")
            sys.exit(0)

# =======================
# SUSCRIPCIÓN Y BUCLE
# =======================
try:
    memory.subscribeToEvent("WordRecognized", "PepperChat", "on_word_recognized")
    asr.subscribe("PepperChat")
    print("Pepper escuchando libremente...")
except Exception as e:
    print("Error al iniciar reconocimiento de voz: {}".format(e))
    sys.exit(1)

# Mantener activo
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    asr.unsubscribe("PepperChat")
    print("Desactivado manualmente.")

