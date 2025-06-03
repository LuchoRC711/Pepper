import requests

API_KEY = 'sk-53751d5c6f344a5dbc0571de9f51313e'
API_URL = 'https://api.deepseek.com/v1/chat/completions'

def enviar_mensaje(mensaje, modelo='deepseek-chat'):
    headers = {
        'Authorization': 'Bearer {}'.format(API_KEY),
        'Content-Type': 'application/json'
    }

    # ⚽ Prompt futbolístico
    system_prompt = "Eres un comentarista de futbol profesional. Responde con entusiasmo y conocimiento cada vez que alguien diga palabras futboleras. Usa expresiones como 'tremendo golazo', 'jugada de lujo', 'la hinchada explota' y demas. Tu respuesta debe sonar como si estuvieras narrando un partido o hablando con otros apasionados del futbol."

    data = {
        'model': modelo,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': mensaje}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'Sin respuesta')
    except requests.exceptions.HTTPError as err:
        return "Error en la API: {}".format(err)
    except Exception as e:
        return "Error inesperado: {}".format(e)

