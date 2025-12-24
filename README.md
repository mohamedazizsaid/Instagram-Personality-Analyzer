# 🧠 Instagram Personality Analyzer

Une application full-stack qui analyse la personnalité des utilisateurs Instagram en utilisant l'IA (XLM-RoBERTa et Vision Transformer).

## 🌟 Fonctionnalités

- 📸 **Scraping Instagram** : Collecte automatique des posts, images et captions
- 🤖 **Analyse IA** : Utilise XLM-RoBERTa pour l'analyse de texte et ViT pour l'analyse d'images
- 📊 **Visualisation** : Graphiques radar et barres pour les traits de personnalité Big Five
- 💾 **Cache intelligent** : Évite les requêtes répétées
- 🎨 **Interface moderne** : UI responsive avec React et Tailwind CSS

## 🏗️ Architecture

```
instagram-personality-analyzer/                 # API FastAPI
  ├── app/
  │   ├── main.py         # Point d'entrée API
  │   ├── scraper.py      # Scraping Instagram
  │   ├── personality_analyzer.py  # Analyse IA
  │   └── utils.py        # Fonctions utilitaires
  └── requirements.txt

```

## 🚀 Installation

### Prérequis

- Python 3.8+
- Node.js 16+
- npm ou yarn

### Backend

```bash
# Cloner le projet
git clone <votre-repo>
cd instagram-personality-analyzer-web-scrapping

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python app/main.py
```

Le backend sera disponible sur `http://localhost:8000`



## 🎯 Utilisation

1. **Ouvrir l'application** : Allez sur `http://localhost:3000`
2. **Entrer une URL Instagram** : `https://www.instagram.com/username/`
3. **Cliquer sur "Analyze"** : L'application va :
   - Scraper les 30 derniers posts
   - Analyser les textes avec XLM-RoBERTa
   - Analyser les images avec Vision Transformer
   - Générer un profil de personnalité Big Five
4. **Voir les résultats** : 
   - Graphiques de personnalité
   - Échantillon de posts analysés
   - Statistiques détaillées

## 🧪 API Endpoints

### GET `/`
Vérifier le status de l'API

### POST `/analyze`
Analyser un profil Instagram

**Request:**
```json
{
  "instagram_url": "https://www.instagram.com/username/",
  "max_posts": 30
}
```

**Response:**
```json
{
  "personality_traits": {
    "Openness": 0.75,
    "Conscientiousness": 0.65,
    "Extraversion": 0.82,
    "Agreeableness": 0.70,
    "Neuroticism": 0.40
  },
  "posts_analyzed": 30,
  "sample_data": [...],
  "visualization": "data:image/png;base64,...",
  "dominant_trait": "Extraversion",
  "confidence": 0.82
}
```

## 📊 Traits de Personnalité Big Five

1. **Openness (Ouverture)** : Créativité, curiosité, ouverture aux nouvelles expériences
2. **Conscientiousness (Conscience)** : Organisation, responsabilité, autodiscipline
3. **Extraversion** : Sociabilité, énergie, enthousiasme
4. **Agreeableness (Amabilité)** : Compassion, coopération, confiance
5. **Neuroticism (Névrosisme)** : Stabilité émotionnelle, anxiété, vulnérabilité

## 🔧 Technologies Utilisées

### Backend
- **FastAPI** : Framework web moderne et rapide
- **Instaloader** : Scraping Instagram
- **Transformers** : Modèles IA (Hugging Face)
- **PyTorch** : Deep learning
- **XLM-RoBERTa** : Analyse de texte multilingue
- **Vision Transformer (ViT)** : Analyse d'images

## ⚠️ Limitations

- Instagram a des limites de rate limiting
- Les profils privés ne peuvent pas être analysés sans authentification
- Les modèles IA nécessitent ~2GB d'espace disque
- Le premier chargement des modèles peut prendre quelques minutes

## 📈 Améliorations Futures

- [ ] Support multi-utilisateurs avec authentification
- [ ] Comparaison de profils
- [ ] Export PDF des résultats
- [ ] Analyse de tendances temporelles
- [ ] Support d'autres réseaux sociaux (Twitter, TikTok)
- [ ] Fine-tuning des modèles sur des données de personnalité
- [ ] Mode batch pour analyser plusieurs profils

## 📄 Licence

MIT License - Voir le fichier LICENSE pour plus de détails

## 🙏 Remerciements

- [Hugging Face](https://huggingface.co/) pour les modèles pré-entraînés
- [Instaloader](https://instaloader.github.io/) pour le scraping Instagram
- [FastAPI](https://fastapi.tiangolo.com/) pour le framework backend

## 📞 Support

Pour toute question ou problème :
- Email : saidazizz132@gmail.com

---

**Note** : Cette application est destinée à des fins éducatives et de recherche. Respectez toujours les conditions d'utilisation d'Instagram et la vie privée des utilisateurs.