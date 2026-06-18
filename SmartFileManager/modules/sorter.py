import os
import shutil
import hashlib

USER_HOME = os.path.expanduser("~")

DESTINATIONS = {
    "Images": os.path.join(USER_HOME, "Pictures"),
    "Videos": os.path.join(USER_HOME, "Videos"),
    "Audio": os.path.join(USER_HOME, "Music"),
    "Documents": os.path.join(USER_HOME, "Documents"),
    "Archives": os.path.join(USER_HOME, "Documents", "Archives"),
    "Developpement": os.path.join(USER_HOME, "Documents", "Developpement"),
    "Applications": os.path.join(USER_HOME, "Documents", "Applications"),
    "Divers": os.path.join(USER_HOME, "Documents", "Divers")
}

EXTENSION_MAP = {
    ".jpg": "Images", ".jpeg": "Images", ".png": "Images", ".gif": "Images", 
    ".bmp": "Images", ".tiff": "Images", ".webp": "Images", ".svg": "Images", 
    ".ico": "Images", ".psd": "Images", ".ai": "Images", ".heic": "Images",
    ".cr2": "Images", ".nef": "Images",
    
    ".mp4": "Videos", ".mkv": "Videos", ".avi": "Videos", ".mov": "Videos", 
    ".wmv": "Videos", ".flv": "Videos", ".webm": "Videos", ".mpeg": "Videos",
    ".mpg": "Videos", ".m4v": "Videos", ".3gp": "Videos",
    
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents", 
    ".xlsx": "Documents", ".xls": "Documents", ".pptx": "Documents", 
    ".ppt": "Documents", ".txt": "Documents", ".rtf": "Documents", 
    ".csv": "Documents", ".md": "Documents", ".epub": "Documents",
    ".mobi": "Documents", ".odt": "Documents", ".ods": "Documents",
    
    ".zip": "Archives", ".rar": "Archives", ".7z": "Archives", 
    ".tar": "Archives", ".gz": "Archives", ".iso": "Archives", 
    ".dmg": "Archives", ".bz2": "Archives",
    
    ".mp3": "Audio", ".wav": "Audio", ".flac": "Audio", ".aac": "Audio", 
    ".ogg": "Audio", ".m4a": "Audio", ".wma": "Audio", ".mid": "Audio",
    
    ".py": "Developpement", ".js": "Developpement", ".html": "Developpement", 
    ".css": "Developpement", ".json": "Developpement", ".xml": "Developpement", 
    ".java": "Developpement", ".cpp": "Developpement", ".c": "Developpement",
    ".h": "Developpement", ".cs": "Developpement", ".ts": "Developpement",
    ".sh": "Developpement", ".bat": "Developpement",
    
    ".exe": "Applications", ".msi": "Applications", ".apk": "Applications",
    ".deb": "Applications", ".rpm": "Applications"
}

def get_file_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def sort_file(file_path):
    if not os.path.exists(file_path):
        return "Fichier introuvable", None
    
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    if ext in [".crdownload", ".tmp", ".part", ".download"]:
        return f"Fichier temporaire ignore : {filename}", None
        
    category = EXTENSION_MAP.get(ext, "Divers")
    dest_dir = DESTINATIONS[category]
    
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)
    
    if os.path.exists(dest_path):
        new_hash = get_file_sha256(file_path)
        old_hash = get_file_sha256(dest_path)
        if new_hash and old_hash and new_hash == old_hash:
            try:
                os.remove(file_path)
                return f"Doublon detecte et supprime : {filename}", None
            except Exception as e:
                return f"Erreur suppression doublon {filename} : {e}", None
        else:
            counter = 1
            while os.path.exists(dest_path):
                filename = f"{name} ({counter}){ext}"
                dest_path = os.path.join(dest_dir, filename)
                counter += 1
    
    try:
        shutil.move(file_path, dest_path)
        return f"Deplace : {filename} -> {dest_dir}", category
    except Exception as e:
        return f"Erreur avec {filename} : {e}", None

def clear_destination_folder(category):
    if category not in DESTINATIONS:
        return "Categorie inconnue"
    
    folder_path = DESTINATIONS[category]
    if not os.path.exists(folder_path):
        return f"Le dossier {category} n'existe pas encore"
        
    errors = 0
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception:
            errors += 1
            
    if errors > 0:
        return f"Nettoyage de {category} termine avec {errors} elements verrouilles"
    return f"Le dossier {category} a ete completement vide"

def clear_all_destinations():
    total_errors = 0
    for category in DESTINATIONS:
        folder_path = DESTINATIONS[category]
        if os.path.exists(folder_path):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                try:
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                except Exception:
                    total_errors += 1
                    
    if total_errors > 0:
        return f"Nettoyage global termine avec {total_errors} elements impossibles a supprimer"
    return "Tous les dossiers de destination Windows ont ete integralement vides"