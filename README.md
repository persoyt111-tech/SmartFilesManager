# SmartFilesManager
Voici une description complète et professionnelle pour ton projet SmartFilesManager, parfaitement formatée pour le README.md de ton dépôt GitHub.

📁 SmartFilesManager
SmartFilesManager est un utilitaire d'automatisation intelligent conçu pour garder votre espace de travail propre et organisé. Le programme surveille en arrière-plan un dossier spécifique (comme votre dossier Téléchargements ou votre Bureau) et trie instantanément chaque nouveau fichier qui y apparaît en le déplaçant dans le sous-dossier approprié selon son type (Musique, Vidéos, Images, Documents, etc.).

Fini le désordre des dossiers "Téléchargements" saturés de fichiers en vrac !

✨ Fonctionnalités
Surveillance en Temps Réel : Détecte instantanément l'apparition de nouveaux fichiers grâce à un système de surveillance d'événements (sans analyser le disque en boucle pour économiser les ressources).

Tri Automatique par Extension : Classe les fichiers dès leur détection dans des répertoires dédiés :

🎵 Musique : .mp3, .wav, .flac, .aac...

🎬 Vidéos : .mp4, .mkv, .avi, .mov...

📸 Images : .jpg, .jpeg, .png, .gif, .svg...

Documents : .pdf, .docx, .xlsx, .pptx, .txt...

Gestion des Doublons : Si un fichier portant le même nom existe déjà dans le dossier de destination, l'outil le renomme intelligemment (ex: rapport(1).pdf) pour éviter toute perte de données.

Léger et Silencieux : S'exécute de manière transparente en arrière-plan avec un impact CPU et mémoire quasi nul.

🛠️ Comment ça marche ?
Le projet s'appuie sur un script ou une application qui écoute les signaux du système d'exploitation :

Écoute active (Watcher) : L'application est branchée sur le dossier choisi.

Analyse de l'extension : Dès qu'un fichier est complètement copié ou téléchargé, l'outil extrait son extension.

Routage : Il cherche la correspondance dans sa configuration et déplace proprement le fichier vers sa nouvelle maison.
