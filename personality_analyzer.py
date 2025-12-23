from transformers import AutoTokenizer, AutoModelForSequenceClassification, ViTImageProcessor, ViTForImageClassification
import torch
from PIL import Image
import numpy as np
from typing import Dict, List
import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns

class PersonalityAnalyzer:
    def __init__(self):
        print("Loading models...")
        
        # Charger XLM-RoBERTa pour l'analyse de texte
        self.text_tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-base")
        self.text_model = AutoModelForSequenceClassification.from_pretrained(
            "xlm-roberta-base",
            num_labels=5  # Big Five personality traits
        )
        
        # Charger Vision Transformer pour l'analyse d'images
        self.image_processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
        self.image_model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')
        
        # Traits de personnalité Big Five
        self.personality_traits = [
            "Openness",
            "Conscientiousness", 
            "Extraversion",
            "Agreeableness",
            "Neuroticism"
        ]
        
        print("Models loaded successfully")
    
    async def analyze(self, posts_data: List[Dict]) -> Dict:
        """Analyser la personnalité à partir des posts"""
        text_scores = await self._analyze_text(posts_data)
        image_scores = await self._analyze_images(posts_data)
        
        # Combiner les scores (moyenne pondérée)
        combined_scores = {}
        for trait in self.personality_traits:
            text_score = text_scores.get(trait, 0.5)
            image_score = image_scores.get(trait, 0.5)
            # 60% texte, 40% image
            combined_scores[trait] = (text_score * 0.6) + (image_score * 0.4)
        
        # Générer la visualisation
        visualization = self._generate_visualization(combined_scores)
        
        return {
            "traits": combined_scores,
            "text_scores": text_scores,
            "image_scores": image_scores,
            "visualization": visualization
        }
    
    async def _analyze_text(self, posts_data: List[Dict]) -> Dict[str, float]:
        """Analyser les textes (captions et commentaires)"""
        all_text = []
        
        for post in posts_data:
            if post.get("caption"):
                all_text.append(post["caption"])
            if post.get("comments"):
                all_text.extend(post["comments"])
        
        if not all_text:
            return {trait: 0.5 for trait in self.personality_traits}
        
        # Limiter le texte pour éviter les problèmes de mémoire
        text_sample = " ".join(all_text[:50])
        
        # Tokenizer et analyser
        inputs = self.text_tokenizer(
            text_sample,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.text_model(**inputs)
            logits = outputs.logits
            scores = torch.softmax(logits, dim=1)[0].numpy()
        
        # Mapper aux traits de personnalité
        text_scores = {}
        for i, trait in enumerate(self.personality_traits):
            text_scores[trait] = float(scores[i] if i < len(scores) else 0.5)
        
        return text_scores
    
    async def _analyze_images(self, posts_data: List[Dict]) -> Dict[str, float]:
        """Analyser les images"""
        image_features = []
        
        for post in posts_data:
            if post.get("image_path"):
                try:
                    image = Image.open(post["image_path"]).convert("RGB")
                    inputs = self.image_processor(images=image, return_tensors="pt")
                    
                    with torch.no_grad():
                        outputs = self.image_model(**inputs)
                        features = outputs.logits[0].numpy()
                        image_features.append(features)
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue
        
        if not image_features:
            return {trait: 0.5 for trait in self.personality_traits}
        
        # Moyenner les features
        avg_features = np.mean(image_features, axis=0)
        
        # Mapper aux traits (simplifié)
        image_scores = {}
        normalized = (avg_features - avg_features.min()) / (avg_features.max() - avg_features.min() + 1e-8)
        
        for i, trait in enumerate(self.personality_traits):
            idx = (i * len(normalized)) // len(self.personality_traits)
            image_scores[trait] = float(normalized[idx])
        
        return image_scores
    
    def _generate_visualization(self, scores: Dict[str, float]) -> str:
        """Générer un graphique radar des traits de personnalité"""
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # Préparer les données
        traits = list(scores.keys())
        values = list(scores.values())
        
        # Ajouter le premier point à la fin pour fermer le radar
        values += values[:1]
        
        # Calculer les angles
        angles = np.linspace(0, 2 * np.pi, len(traits), endpoint=False).tolist()
        angles += angles[:1]
        
        # Tracer
        ax.plot(angles, values, 'o-', linewidth=2, color='#4CAF50')
        ax.fill(angles, values, alpha=0.25, color='#4CAF50')
        ax.set_ylim(0, 1)
        
        # Labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(traits, size=12)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], size=10)
        ax.set_title('Personality Traits Analysis', size=16, pad=20)
        ax.grid(True)
        
        # Convertir en base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"