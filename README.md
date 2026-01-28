# DubSync : La solution open-source de doublage vidéo multilingue avec synchronisation labiale.

Fonctionnement : 

DubSync, s'appuie sur une pipeline sophistiquée intégrant les meilleurs outils open-source actuels pour sa fonction :

• FFmpeg :
 
Le principal framework multimédia, capable de décoder, encoder, transcoder, multiplexer, démultiplexer, diffuser, filtrer et lire à peu près tout ce que les humains et les machines ont créé.
 
 • Demucs :
 
Un modèle de séparation de sources musicales de pointe, actuellement capable de séparer la batterie, la basse et les voix du reste de l'accompagnement.

• Whisper : 

Un modèle de reconnaissance vocale à usage général. 

• Chatterbox :

Une famille de trois modèles de synthèse vocale (text-to-speech) open-source de pointe développée par Resemble AI.

• LatentSync :

Un outil avancé de synchronisation labiale alimenté par l'IA qui utilise des modèles de diffusion latente pour obtenir un alignement audiovisuel précis.

Il fonctionne en analysant le contenu audio et en générant des mouvements de lèvres correspondants dans l'espace latent, garantissant des résultats naturels pour tout contenu vidéo.

Instructions d'installation et d'utilisation :

Pour utiliser DubSync, veuillez exécuter l’ensemble des scripts suivants dans l’ordre :

    1. requirements.py : Télécharge et installe l’ensemble des dépendances Python nécessaires.
    
    2. softwares.py : Télécharge et installe l’ensemble des logiciels tiers indispensables au fonctionnement de DubSync.
    
    3. DubSync.py : Application. 	

<img width="807" height="1027" alt="DubSync" src="https://github.com/user-attachments/assets/18e85263-709e-4d00-b0f1-4ce965228fa0" />

https://github.com/user-attachments/assets/278057da-29e0-44b4-b911-f72cbff1b1b1
