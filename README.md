from pathlib import Path

# Contenido del README.md
readme_content = """# Chatbot de Pepper con Personalidad Futbolística usando DeepSeek

Este proyecto permite que el robot humanoide Pepper reconozca la voz del usuario, identifique palabras del mundo del fútbol y genere respuestas dinámicas con inteligencia artificial usando la API de DeepSeek.


## 🎯 Objetivo

Desarrollar una integración funcional entre el robot Pepper y un chatbot basado en IA (DeepSeek), donde la comunicación sea por voz y las respuestas tengan una personalidad de comentarista de fútbol.


## 🛠️ Componentes del Proyecto

- **`chatbot.py`**: Se conecta a la API de DeepSeek con un `prompt` configurado como comentarista deportivo.
- **`server.py`**: Actúa como servidor Flask en la PC, recibe peticiones de Pepper y las redirige al chatbot.
- **`cliente_pepe.py`**: Se ejecuta dentro de Pepper y le permite escuchar voz, reconocer palabras clave y hablar.
- **`coding utf 8.md`** (opcional): Alternativa visual o extendida del cliente con más funciones.


## 📶 Arquitectura

```plaintext
[Usuario habla con Pepper] 
        ↓
[cliente_pepe.py - reconoce voz] 
        ↓
[Envía frase al servidor Flask (server.py)] 
        ↓
[server.py llama a chatbot.py con la API de DeepSeek] 
        ↓
[DeepSeek responde con texto futbolero] 
        ↓
[Pepper habla la respuesta]

# Pepper
 5b5cb3d9ab351814f1a689d5cdd2ff03ab9a10f3
