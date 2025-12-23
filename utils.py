import re
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
import hashlib
from urllib.parse import urlparse


def extract_username(url: str) -> str:
    """
    Extraire le nom d'utilisateur d'une URL Instagram
    
    Args:
        url: URL Instagram ou nom d'utilisateur
        
    Returns:
        Nom d'utilisateur
    """
    url = url.strip().rstrip('/')
    
    # Si c'est juste un nom d'utilisateur
    if not url.startswith('http'):
        return url
    
    # Parser l'URL
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    
    # Le username est généralement le premier élément du path
    if path_parts:
        return path_parts[0]
    
    raise ValueError("Cannot extract username from URL")


def validate_url(url: str) -> bool:
    """
    Valider une URL Instagram
    
    Args:
        url: URL à valider
        
    Returns:
        True si valide, False sinon
    """
    if not url:
        return False
    
    patterns = [
        r'^https?://(www\.)?instagram\.com/[\w\.]+/?$',
        r'^[\w\.]+$'  # Juste le username
    ]
    
    return any(re.match(pattern, url.strip()) for pattern in patterns)


def validate_username(username: str) -> bool:
    """
    Valider un nom d'utilisateur Instagram
    
    Args:
        username: Nom d'utilisateur à valider
        
    Returns:
        True si valide, False sinon
    """
    if not username or len(username) > 30:
        return False
    
    # Instagram usernames: lettres, chiffres, points, underscores
    pattern = r'^[\w\.]+$'
    return bool(re.match(pattern, username))


def calculate_confidence(scores: Dict[str, float]) -> float:
    """
    Calculer le score de confiance basé sur les traits de personnalité
    
    Args:
        scores: Dictionnaire des scores de traits
        
    Returns:
        Score de confiance (0-1)
    """
    if not scores:
        return 0.0
    
    # La confiance est basée sur le score maximum et la variance
    values = list(scores.values())
    max_score = max(values)
    
    # Calculer la variance
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    
    # Haute variance = plus de confiance (traits distincts)
    # Score maximum élevé = plus de confiance
    confidence = (max_score * 0.7) + (min(variance * 2, 0.3))
    
    return min(confidence, 1.0)


def format_date(date_string: str) -> str:
    """
    Formater une date au format lisible
    
    Args:
        date_string: Date en format ISO
        
    Returns:
        Date formatée
    """
    try:
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return date_string


def clean_text(text: str) -> str:
    """
    Nettoyer le texte pour l'analyse
    
    Args:
        text: Texte brut
        
    Returns:
        Texte nettoyé
    """
    if not text:
        return ""
    
    # Enlever les URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Enlever les mentions @
    text = re.sub(r'@[\w]+', '', text)
    
    # Enlever les hashtags multiples
    text = re.sub(r'#[\w]+', '', text)
    
    # Enlever les emojis (optionnel)
    # text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Enlever les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_hashtags(text: str) -> List[str]:
    """
    Extraire les hashtags d'un texte
    
    Args:
        text: Texte contenant des hashtags
        
    Returns:
        Liste des hashtags
    """
    if not text:
        return []
    
    hashtags = re.findall(r'#(\w+)', text)
    return list(set(hashtags))  # Enlever les doublons


def extract_mentions(text: str) -> List[str]:
    """
    Extraire les mentions d'un texte
    
    Args:
        text: Texte contenant des mentions
        
    Returns:
        Liste des mentions
    """
    if not text:
        return []
    
    mentions = re.findall(r'@(\w+)', text)
    return list(set(mentions))


def generate_cache_key(username: str, max_posts: int = 30) -> str:
    """
    Générer une clé de cache unique
    
    Args:
        username: Nom d'utilisateur
        max_posts: Nombre de posts
        
    Returns:
        Clé de cache
    """
    data = f"{username}_{max_posts}_{datetime.now().strftime('%Y%m%d')}"
    return hashlib.md5(data.encode()).hexdigest()


def save_cache(cache_key: str, data: Dict, cache_dir: str = "cache") -> bool:
    """
    Sauvegarder les données en cache
    
    Args:
        cache_key: Clé de cache
        data: Données à sauvegarder
        cache_dir: Répertoire de cache
        
    Returns:
        True si succès
    """
    try:
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving cache: {str(e)}")
        return False


def load_cache(cache_key: str, cache_dir: str = "cache", max_age_hours: int = 24) -> Optional[Dict]:
    """
    Charger les données depuis le cache
    
    Args:
        cache_key: Clé de cache
        cache_dir: Répertoire de cache
        max_age_hours: Âge maximum du cache en heures
        
    Returns:
        Données ou None si cache expiré/inexistant
    """
    try:
        cache_file = os.path.join(cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        # Vérifier l'âge du fichier
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        age = datetime.now() - file_time
        
        if age.total_seconds() > max_age_hours * 3600:
            return None
        
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {str(e)}")
        return None


def calculate_engagement_rate(likes: int, comments: int, followers: int) -> float:
    """
    Calculer le taux d'engagement
    
    Args:
        likes: Nombre de likes
        comments: Nombre de commentaires
        followers: Nombre de followers
        
    Returns:
        Taux d'engagement (0-1)
    """
    if followers == 0:
        return 0.0
    
    total_engagement = likes + (comments * 2)  # Les commentaires comptent double
    rate = total_engagement / followers
    
    return min(rate, 1.0)


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normaliser les scores entre 0 et 1
    
    Args:
        scores: Dictionnaire de scores
        
    Returns:
        Scores normalisés
    """
    if not scores:
        return {}
    
    values = list(scores.values())
    min_val = min(values)
    max_val = max(values)
    
    if max_val == min_val:
        return {k: 0.5 for k in scores.keys()}
    
    normalized = {}
    for key, value in scores.items():
        normalized[key] = (value - min_val) / (max_val - min_val)
    
    return normalized


def merge_scores(text_scores: Dict[str, float], 
                 image_scores: Dict[str, float],
                 text_weight: float = 0.6) -> Dict[str, float]:
    """
    Fusionner les scores texte et image
    
    Args:
        text_scores: Scores de l'analyse textuelle
        image_scores: Scores de l'analyse d'images
        text_weight: Poids du texte (0-1)
        
    Returns:
        Scores fusionnés
    """
    merged = {}
    image_weight = 1.0 - text_weight
    
    all_keys = set(text_scores.keys()) | set(image_scores.keys())
    
    for key in all_keys:
        text_val = text_scores.get(key, 0.5)
        image_val = image_scores.get(key, 0.5)
        merged[key] = (text_val * text_weight) + (image_val * image_weight)
    
    return merged


def get_trait_description(trait: str, score: float) -> str:
    """
    Obtenir une description d'un trait de personnalité
    
    Args:
        trait: Nom du trait
        score: Score du trait (0-1)
        
    Returns:
        Description textuelle
    """
    descriptions = {
        "Openness": {
            "high": "Highly creative, curious, and open to new experiences. Enjoys exploring ideas and art.",
            "medium": "Balanced between tradition and innovation. Open to new experiences but also values routine.",
            "low": "More conventional and practical. Prefers familiar experiences and proven methods."
        },
        "Conscientiousness": {
            "high": "Highly organized, responsible, and goal-oriented. Plans ahead and follows through.",
            "medium": "Generally organized with some flexibility. Balances planning with spontaneity.",
            "low": "More spontaneous and flexible. Prefers going with the flow rather than strict planning."
        },
        "Extraversion": {
            "high": "Outgoing, energetic, and socially engaged. Draws energy from social interactions.",
            "medium": "Ambivert - comfortable in both social and solitary settings.",
            "low": "More reserved and introspective. Prefers quiet environments and smaller groups."
        },
        "Agreeableness": {
            "high": "Highly cooperative, compassionate, and friendly. Values harmony and helping others.",
            "medium": "Balanced between cooperation and independence. Can be both supportive and assertive.",
            "low": "More independent and analytical. Prioritizes logic over emotions in decision-making."
        },
        "Neuroticism": {
            "high": "More emotionally sensitive and reactive. May experience stress more intensely.",
            "medium": "Emotionally balanced with normal stress responses. Generally stable mood.",
            "low": "Emotionally stable and calm. Handles stress well and maintains composure."
        }
    }
    
    level = "high" if score > 0.6 else "low" if score < 0.4 else "medium"
    return descriptions.get(trait, {}).get(level, "No description available.")


def create_download_directory(username: str, base_dir: str = "downloads") -> str:
    """
    Créer un répertoire de téléchargement pour un utilisateur
    
    Args:
        username: Nom d'utilisateur
        base_dir: Répertoire de base
        
    Returns:
        Chemin du répertoire créé
    """
    user_dir = os.path.join(base_dir, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def cleanup_old_downloads(base_dir: str = "downloads", days: int = 7) -> int:
    """
    Nettoyer les anciens téléchargements
    
    Args:
        base_dir: Répertoire de base
        days: Nombre de jours à conserver
        
    Returns:
        Nombre de fichiers supprimés
    """
    if not os.path.exists(base_dir):
        return 0
    
    deleted_count = 0
    cutoff_time = datetime.now().timestamp() - (days * 86400)
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {file_path}: {str(e)}")
    
    return deleted_count