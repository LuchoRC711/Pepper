# -*- coding: utf-8 -*-

import qi
import httplib
import json
import time
import threading
import random

class PepperCliente:

    def __init__(self):
        self.pepper_ip = "192.168.0.106"
        self.servidor_ip = "192.168.122.1"
        self.servidor_puerto = 9559

        self.conectar_pepper()
        self.inicializar_servicios()

        self.escuchando = False
        self.ultimo_mensaje = ""

        self.palabras_guardadas = []
        self.max_palabras = 4

    def conectar_pepper(self):
        try:
            print("Conectando a Pepper en {}...".format(self.pepper_ip))
            self.session = qi.Session()
            self.session.connect("tcp://" + self.pepper_ip + ":9559")
            print("Conectado a Pepper!")
        except Exception as e:
            print("Error conectando a Pepper: " + str(e))
            raise

    def inicializar_servicios(self):
        try:
            self.tts = self.session.service("ALTextToSpeech")
            self.asr = self.session.service("ALSpeechRecognition")
            self.memory = self.session.service("ALMemory")

            self.asr.setLanguage("Spanish")
            self.tts.setLanguage("Spanish")

            vocabulario = [
                "gol", "pelota", "futbol", "pase", "arquero", "cancha", "equipo", "jugador", "entrenador",
                "hinchada", "torneo", "campeon", "crack", "golazo", "penal", "arbitro", "tarjeta", "ofensiva",
                "defensa", "centro", "cabezazo", "patear", "pasar", "marcar", "atacar", "jugar", "salir", "habla", "limpiar"
            ]

            try:
                self.asr.pause(True)
            except Exception as e:
                print("ASR ya estaba detenido o no disponible: {}".format(e))

            self.asr.setVocabulary(vocabulario, False)

            try:
                self.asr.pause(False)
            except Exception as e:
                print("Error al reanudar ASR: {}".format(e))

            print("Servicios inicializados!")
        except Exception as e:
            print("Error inicializando servicios: " + str(e))
            raise

    def decir(self, texto):
        try:
            if isinstance(texto, unicode):
                texto_str = texto.encode('utf-8')
            else:
                texto_str = str(texto)
            print("Pepper dice: " + texto_str)
            self.tts.say(texto_str)
        except Exception as e:
            print("Error hablando: " + str(e))

    def escuchar(self, timeout=7):
        print("Intentando escuchar...")
        try:
            self.asr.pause(False)
        except Exception as e:
            print("Advertencia al intentar reanudar ASR: {}".format(e))

        try:
            if self.escuchando:
                print("Ya estoy escuchando...")
            self.escuchando = True
            self.ultimo_mensaje = ""

            try:
                self.asr.unsubscribe("ChatbotASR_PepperCliente")
            except Exception:
                pass
            self.asr.subscribe("ChatbotASR_PepperCliente")
            print("Escuchando por hasta {} segundos...".format(timeout))

            self.subscriber_event_id = None

            def on_word_recognized(value):
                if value and len(value) > 0 and value[0]:
                    mensaje = value[0].strip()
                    confianza = value[1]
                    print("Palabra/Frase reconocida: '{}', confianza: {}".format(mensaje.encode('utf-8'), confianza))
                    if len(mensaje) > 1:
                        self.ultimo_mensaje = mensaje

            self.subscriber = self.memory.subscriber("WordRecognized")
            self.subscriber_event_id = self.subscriber.signal.connect(on_word_recognized)

            start_time = time.time()
            while self.escuchando and not self.ultimo_mensaje and (time.time() - start_time < timeout):
                time.sleep(0.1)

            self.detener_escucha_interna()
            return self.ultimo_mensaje if self.ultimo_mensaje else None

        except Exception as e:
            print("Error escuchando: " + str(e))
            self.detener_escucha_interna()
            return None
        finally:
            try:
                self.asr.pause(True)
            except Exception as e:
                print("Advertencia al intentar pausar ASR: {}".format(e))

    def detener_escucha_interna(self):
        if self.escuchando:
            print("Dejando de escuchar (internamente)...")
            try:
                self.asr.unsubscribe("ChatbotASR_PepperCliente")
            except Exception as e:
                print("Error al desuscribir ASR: {}".format(e))
            try:
                if self.subscriber and self.subscriber_event_id:
                    self.subscriber.signal.disconnect(self.subscriber_event_id)
            except Exception as e:
                print("Error al desconectar el subscriber de ALMemory: {}".format(e))
            self.escuchando = False
            self.subscriber_event_id = None

    def agregar_palabra(self, palabra):
        if len(self.palabras_guardadas) < self.max_palabras:
            self.palabras_guardadas.append(palabra)
            print("Palabra '{}' agregada. Total: {}/{}".format(palabra, len(self.palabras_guardadas), self.max_palabras))
            return True
        else:
            print("Ya tienes {} palabras guardadas. Di 'habla' para procesarlas.".format(self.max_palabras))
            return False

    def limpiar_palabras(self):
        self.palabras_guardadas = []
        print("Lista de palabras limpiada.")

    def crear_frase_completa(self):
        if self.palabras_guardadas:
            frase = " ".join(self.palabras_guardadas)
            print("Frase creada: '{}'".format(frase))
            return frase
        else:
            return ""

    def mostrar_estado_palabras(self):
        if self.palabras_guardadas:
            palabras_str = ", ".join(self.palabras_guardadas)
            estado = "Palabras guardadas ({}/{}): {}".format(
                len(self.palabras_guardadas),
                self.max_palabras,
                palabras_str
            )
        else:
            estado = "No hay palabras guardadas (0/{})".format(self.max_palabras)

        print(estado)
        return estado

    def enviar_al_chatbot(self, mensaje):
        try:
            print("Enviando al servidor: '{}' a {}:{}".format(mensaje, self.servidor_ip, self.servidor_puerto))
            conn = httplib.HTTPConnection(self.servidor_ip, self.servidor_puerto, timeout=15)
            headers = {'Content-Type': 'application/json'}
            data = json.dumps({"question": mensaje})

            conn.request("POST", "/chat", data, headers)
            response = conn.getresponse()

            print("Respuesta del servidor - Status: {}, Razon: {}".format(response.status, response.reason))
            respuesta_raw = response.read()
            print("Respuesta RAW del servidor: {}".format(respuesta_raw))
            if response.status == 200:
                try:
                    respuesta_data = json.loads(respuesta_raw.decode('utf-8'))
                except (UnicodeDecodeError, AttributeError):
                    respuesta_data = json.loads(respuesta_raw)

                return respuesta_data.get("respuesta", "No obtuve un campo 'respuesta' valido del servidor.")
            else:
                return "Error del servidor: {} {}".format(response.status, response.reason)
        except httplib.HTTPException as e:
            print("Error de HTTP enviando mensaje: " + str(e))
            return "No pude conectar con el servidor (Error HTTP)."
        except Exception as e:
            print("Error general enviando mensaje: " + str(e))
            return "No pude conectar con el servidor. Revisa la IP, puerto y si el servidor esta activo."
        finally:
            try:
                if 'conn' in locals() and conn:
                    conn.close()
            except Exception as e:
                print("Error cerrando conexion: " + str(e))

    def iniciar_chat_grabadora(self):
        print("=== PEPPER GRABADORA DE PALABRAS (modo futbolista) ===")
        self.decir("Hola crack, bienvenido a la cancha de las palabras.")
        time.sleep(1)
        self.decir("Pasame hasta 4 palabras clave, una por una como pases de gol.")
        time.sleep(1)
        self.decir("Cuando tengas todo listo, decime 'habla' y yo la meto al arco del chatbot.")
        time.sleep(1)
        self.decir("Tambien podes decir 'limpiar' para arrancar de nuevo. Dale, vamos al ataque!")

        while True:
            try:
                estado = self.mostrar_estado_palabras()
                if len(self.palabras_guardadas) < self.max_palabras:
                    self.decir("Decime la palabra numero {}.".format(len(self.palabras_guardadas) + 1))
                else:
                    self.decir("Ya tenes las 4. Decime 'habla' o 'limpiar'. Vos manejas el partido.")

                mensaje = self.escuchar(timeout=10)

                if mensaje:
                    mensaje_lower = mensaje.lower().strip()
                    print("Jugador dijo: " + mensaje)

                    if any(palabra in mensaje_lower for palabra in ['salir', 'terminar', 'hasta luego']):
                        self.decir(random.choice([
                            "Nos vemos crack, a romperla!",
                            "Hasta la proxima campeon!",
                            "Adios maquina, volve cuando quieras."
                        ]))
                        break

                    elif any(palabra in mensaje_lower for palabra in ['limpiar', 'borrar', 'reiniciar']):
                        self.limpiar_palabras()
                        self.decir("Tiramos todo al tacho. Empeza de nuevo papa.")

                    elif 'habla' in mensaje_lower:
                        if self.palabras_guardadas:
                            frase_completa = self.crear_frase_completa()
                            self.decir("Ahi va la jugada: {}".format(frase_completa))
                            respuesta = self.enviar_al_chatbot(frase_completa)
                            self.decir(respuesta)
                            self.limpiar_palabras()
                            self.decir("Buena jugada. Palabras borradas. Vamos por otra ronda!")
                        else:
                            self.decir("No tengo nada para patear. Dame aunque sea una palabra.")

                    else:
                        if self.agregar_palabra(mensaje):
                            if len(self.palabras_guardadas) < self.max_palabras:
                                self.decir("'{}' anotada. Mandame la proxima, crack.".format(mensaje))
                            else:
                                palabras_str = ", ".join(self.palabras_guardadas)
                                self.decir("Listo! Tus 4 jugadas son: {}. Decime 'habla' para lanzar el ataque.".format(palabras_str))
                        else:
                            self.decir("Ya tenes 4. Decime 'habla' o 'limpiar'. No te duermas.")

                else:
                    self.decir(random.choice([
                        "No escuche nada maestro, tirala de nuevo.",
                        "No entendi esa jugada, repetila.",
                        "Te fallo el micro? A ver otra vez."
                    ]))

            except KeyboardInterrupt:
                print("Interrumpido por el usuario.")
                self.decir("Listo crack, nos vemos!")
                break
            except Exception as e:
                print("Error en el bucle principal del chat: " + str(e))
                self.decir("Hubo una falta tecnica. Probemos otra vez.")
                time.sleep(1)

if __name__ == "__main__":
    try:
        cliente = PepperCliente()
        cliente.iniciar_chat_grabadora()
    except RuntimeError as e:
        print("Error de Runtime (posiblemente conexion a NaoQI fallida): {}".format(e))
    except Exception as e:
        print("Error fatal al iniciar el cliente Pepper: " + str(e))
    finally:
        print("Saliendo del programa cliente de Pepper.")



