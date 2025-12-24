import instaloader
import os
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import time
from utils import (
    validate_username,
    extract_hashtags,
    extract_mentions,
    create_download_directory,
    generate_cache_key,
    save_cache,
    load_cache
)

class InstagramScraper:
    def __init__(self, use_cache: bool = True):
        """
        Initialiser le scraper Instagram
        
        Args:
            use_cache: Utiliser le cache pour éviter les requêtes répétées
        """
        self.loader = instaloader.Instaloader(
            download_pictures=True,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=True,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3,
            quiet=True  # Mode silencieux
        )
        
        # Configuration
        self.download_dir = "downloads"
        self.cache_dir = "cache"
        self.use_cache = use_cache
        self.rate_limit_delay = 2  # Secondes entre les requêtes
        
        # Créer les dossiers nécessaires
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.cache_dir, exist_ok=True)
    
    async def scrape_profile(self, username: str, max_posts: int = 5) -> List[Dict]:
        """
        Scraper les posts d'un profil Instagram
        
        Args:
            username: Nom d'utilisateur Instagram
            max_posts: Nombre maximum de posts à scraper
            
        Returns:
            Liste des données de posts
        """
        # Valider le username
        if not validate_username(username):
            raise ValueError(f"Invalid username: {username}")
        
        # Vérifier le cache
        if self.use_cache:
            cache_key = generate_cache_key(username, max_posts)
            cached_data = load_cache(cache_key, self.cache_dir)
            if cached_data:
                print(f"Using cached data for {username}")
                return cached_data
        
        try:
            print(f"Fetching profile: {username}")
            
            # Charger le profil
            profile = instaloader.Profile.from_username(
                self.loader.context, 
                username
            )
            
            # Vérifier si le profil est privé
            if profile.is_private:
                raise Exception(f"Profile {username} is private")
            
            # Créer le dossier de téléchargement
            user_dir = create_download_directory(username, self.download_dir)
            
            # Scraper les posts
            posts_data = await self._scrape_posts(profile, user_dir, max_posts)
            
            # Sauvegarder en cache
            if self.use_cache and posts_data:
                cache_key = generate_cache_key(username, max_posts)
                save_cache(cache_key, posts_data, self.cache_dir)
            
            return posts_data
        
        except instaloader.exceptions.ProfileNotExistsException:
            raise Exception(f"Profile {username} does not exist")
        except instaloader.exceptions.ConnectionException:
            raise Exception("Connection error. Please try again later.")
        except Exception as e:
            print(f"Error scraping profile: {str(e)}")
            raise Exception(f"Failed to scrape profile: {str(e)}")
    
    async def _scrape_posts(self, profile, user_dir: str, max_posts: int) -> List[Dict]:
        """
        Scraper les posts d'un profil
        
        Args:
            profile: Objet Profile d'Instaloader
            user_dir: Dossier de téléchargement
            max_posts: Nombre maximum de posts
            
        Returns:
            Liste des données de posts
        """
        posts_data = []
        post_count = 0
        
        print(f"Total posts available: {profile.mediacount}")
        
        for post in profile.get_posts():
            if post_count >= max_posts:
                break
            
            try:
                # Délai pour respecter le rate limiting
                if post_count > 0:
                    await asyncio.sleep(self.rate_limit_delay)
                
                # Télécharger l'image
                image_path = await self._download_image(post, user_dir)
                
                # Extraire les données du post
                post_data = {
                    "id": post.shortcode,
                    "caption": post.caption if post.caption else "",
                    "likes": post.likes,
                    "comments_count": post.comments,
                    "date": post.date_utc.isoformat(),
                    "image_path": image_path,
                    "is_video": post.is_video,
                    "hashtags": extract_hashtags(post.caption if post.caption else ""),
                    "mentions": extract_mentions(post.caption if post.caption else ""),
                    "location": post.location.name if post.location else None,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/"
                }
                
                # Extraire quelques commentaires
                comments = await self._extract_comments(post, max_comments=5)
                post_data["comments"] = comments
                
                posts_data.append(post_data)
                post_count += 1
                
                print(f"Scraped post {post_count}/{max_posts}: {post.shortcode}")
                
            except Exception as e:
                print(f"Error scraping post {post.shortcode}: {str(e)}")
                continue
        
        print(f"Successfully scraped {len(posts_data)} posts")
        return posts_data
    
    async def _download_image(self, post, user_dir: str) -> str:
        """
        Télécharger l'image d'un post
        
        Args:
            post: Objet Post d'Instaloader
            user_dir: Dossier de téléchargement
            
        Returns:
            Chemin du fichier téléchargé (relatif pour le frontend)
        """
        try:
            # Ne pas télécharger les vidéos
            if post.is_video:
                return ""
            
            filename = f"{post.shortcode}.jpg"
            filepath = os.path.join(user_dir, filename)
            
            # Télécharger seulement si le fichier n'existe pas
            if not os.path.exists(filepath):
                self.loader.download_pic(
                    filename=filepath,
                    url=post.url,
                    mtime=post.date_utc
                )
                print(f"Downloaded image: {filename}")
            else:
                print(f"Image already exists: {filename}")
            
            # Retourner le chemin relatif pour le frontend
            # Format: username/filename.jpg
            relative_path = os.path.join(os.path.basename(user_dir), filename)
            return relative_path.replace("\\", "/")  # Normaliser les chemins
        
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return ""
    async def _extract_comments(self, post, max_comments: int = 5) -> List[str]:
            """
            Extraire les commentaires d'un post
            
            Args:
                post: Objet Post d'Instaloader
                max_comments: Nombre maximum de commentaires à extraire
                
            Returns:
                Liste des commentaires
            """
            comments = []
            comment_count = 0
            
            try:
                for comment in post.get_comments():
                    if comment_count >= max_comments:
                        break
                    
                    if comment.text:
                        comments.append(comment.text)
                        comment_count += 1
            except Exception as e:
                print(f"Error extracting comments: {str(e)}")
            
            return comments
        
    def login(self, username: str, password: str) -> bool:
            """
            Se connecter à Instagram (optionnel mais recommandé)
            
            Args:
                username: Nom d'utilisateur Instagram
                password: Mot de passe
                
            Returns:
                True si succès, False sinon
            """
            try:
                self.loader.login(username, password)
                print(f"Successfully logged in as {username}")
                return True
            except Exception as e:
                print(f"Login failed: {str(e)}")
                return False
        
    def get_profile_info(self, username: str) -> Dict:
            """
            Obtenir les informations de base d'un profil
            
            Args:
                username: Nom d'utilisateur Instagram
                
            Returns:
                Dictionnaire avec les infos du profil
            """
            try:
                profile = instaloader.Profile.from_username(
                    self.loader.context, 
                    username
                )
                
                return {
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "biography": profile.biography,
                    "followers": profile.followers,
                    "following": profile.followees,
                    "posts_count": profile.mediacount,
                    "is_private": profile.is_private,
                    "is_verified": profile.is_verified,
                    "profile_pic_url": profile.profile_pic_url
                }
            except Exception as e:
                print(f"Error getting profile info: {str(e)}")
                return {}
        
    def cleanup_downloads(self, username: Optional[str] = None):
            """
            Nettoyer les fichiers téléchargés
            
            Args:
                username: Nom d'utilisateur spécifique (optionnel)
            """
            try:
                if username:
                    user_dir = os.path.join(self.download_dir, username)
                    if os.path.exists(user_dir):
                        import shutil
                        shutil.rmtree(user_dir)
                        print(f"Cleaned up downloads for {username}")
                else:
                    # Nettoyer tout
                    import shutil
                    if os.path.exists(self.download_dir):
                        shutil.rmtree(self.download_dir)
                        os.makedirs(self.download_dir, exist_ok=True)
                        print("Cleaned up all downloads")
            except Exception as e:
                print(f"Error cleaning up: {str(e)}")