import json
import requests
import azure.cognitiveservices.speech as speechsdk
import distanciation
from flask import Flask, render_template, request, jsonify

CONFIG_FILE = "config.json"



def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"message": "", "maxdepersonnes": 0}
    
config = load_config()
message = config["message"]
    
def save_config(message, maxprsn):
    config = {"message": message, "maxdepersonnes": maxprsn}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def translator_message_azure(message, subscription_key, translator_endpoint, region):
    body = [{'text': message}]
    url = f"{translator_endpoint}/translate?api-version=3.0&from=fr&to=en"

    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': region,
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    translations = response.json()
    return translations[0]['translations'][0]['text']

def generate_audio_azure(message, language, output_file, subscription_key, region):
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    speech_config.speech_synthesis_language = language
    speech_config.speech_synthesis_voice_name = "fr-FR-DeniseNeural" if language == "fr-FR" else "en-US-AriaNeural"
    audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(message).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Fichier audio généré : {output_file}")
    else:
        print(f"Erreur lors de la génération de l'audio : {result.reason}")

def backoffice():
    print("Backoffice")
    config = load_config()
    print(f"Historique : {config['maxdepersonnes']}")
    message = input("Entrez le message à annoncer : ")

    while True:
        try:
            maxprsn = int(input("Entrez le nombre maximum de personnes autorisées dans le studio : "))
            if maxprsn < 1:
                print("Le nombre de personnes doit être supérieur à 0. Essayez encore.")
                continue
            break
        except ValueError:
            print("Veuillez entrer un nombre valide.")

    if not message:
        print("Aucun message trouvé, veuillez en saisir un nouveau.")


    save_config(message, maxprsn)
    print("\nConfiguration sauvegardée avec succès !")
    print(f"Message : {message}")
    print(f"Nombre de personnes : {maxprsn}")

    return message

translator_key = "DrElPAYWYhNaKmBlvxlyV0WcwDPnGlhi3DzLEXXm3bmhmf5crPDxJQQJ99AKAC5T7U2XJ3w3AAAbACOGcAVy"
translator_endpoint = "https://api.cognitive.microsofttranslator.com/"
translator_region = "francecentral"

speech_key = "5pIimKmnNHqxKhNfz25bjxjZLyDhnI5DZpAdrZVFaQL5LUUmrjnmJQQJ99AKAC5T7U2XJ3w3AAAYACOGZncG"
speech_region = "francecentral"

if __name__ == "__main__":
        message = backoffice()
        print("\nTraduction du message en anglais...")
        message_en = translator_message_azure(message, translator_key, translator_endpoint, translator_region)
        print(f"Message traduit en anglais : {message_en}")


        print("\nGénération des fichiers audio...")
        generate_audio_azure(message, "fr-FR", "message_fr.mp3", speech_key, speech_region)

        generate_audio_azure(message_en, "en-US", "message_en.mp3", speech_key, speech_region)
        print("Les fichiers audio ont été générés avec succès : 'message_fr.mp3' et 'message_en.mp3'.")

        image_path = input("Entrez le chemin de l'image à analyser : ").strip()
        message_fr = "message_fr.mp3"
        message_en = "message_en.mp3" 

        distanciation.detecter_distanciation(image_path, message_fr, message_en)

if __name__ == "__main__":
    import sys


    message = backoffice()
    print("\nTraduction du message en anglais...")
    message_en = translator_message_azure(message, translator_key, translator_endpoint, translator_region)
    print(f"Message traduit en anglais : {message_en}")

    print("\nGénération des fichiers audio...")
    generate_audio_azure(message, "fr-FR", "message_fr.mp3", speech_key, speech_region)
    generate_audio_azure(message_en, "en-US", "message_en.mp3", speech_key, speech_region)
    print("Les fichiers audio ont été générés avec succès.")
