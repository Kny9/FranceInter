import os
import json
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import pygame

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erreur : Le fichier de configuration {CONFIG_FILE} est introuvable.")
        exit(1)

def detect_people_in_image(image_path, subscription_key, endpoint):
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

    with open(image_path, "rb") as image_stream:
        analysis = client.analyze_image_in_stream(image_stream, visual_features=["Objects"])

    person_count = sum(1 for obj in analysis.objects if obj.object_property.lower() == "person")
    return person_count

def play_audio(file_path):
    pygame.mixer.init()
    
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.play()
        
        while pygame.mixer.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"Erreur lors de la lecture de l'audio {file_path} : {e}")

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def detecter_distanciation(image_path, message_fr, message_en):
    config = load_config()
    max_persons_allowed = config.get("maxdepersonnes", 0)

    if max_persons_allowed < 1:
        print("Le nombre maximum de personnes autorisées n'est pas correctement configuré.")
        exit(1)

    if not os.path.isfile(image_path):
        print(f"Erreur : Le fichier {image_path} n'existe pas.")
        exit(1)

    vision_key = "14YYEW56iXO7f20JkFj41dPKHvZNH2DLi9E9ZaICzyuUxIGwsR27JQQJ99ALAC5T7U2XJ3w3AAAFACOG98T2"
    vision_endpoint = "https://vision-pour-services.cognitiveservices.azure.com/"

    print("\nAnalyse de l'image pour détecter les personnes...")
    detected_person_count = detect_people_in_image(image_path, vision_key, vision_endpoint)
    print(f"Nombre de personnes détectées : {detected_person_count}")

    if detected_person_count > max_persons_allowed:
        print("Distanciation sociale non respectée.")
        print("\nDiffusion des messages audio...")
        play_audio(message_fr)
        play_audio(message_en)
    else:
        print("Distanciation sociale respectée.")