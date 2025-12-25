"""
Instagram Personality Analyzer API
Analyse la personnalité des utilisateurs Instagram basée sur leurs posts,
images et textes en utilisant XLM-RoBERTa et Vision Transformer.
"""

__version__ = "1.0.0"
__author__ = "Said Mohamed Aziz"
__description__ = "Instagram Personality Analysis using AI"

from .main import app
from .scraper import InstagramScraper
from .personality_analyzer import PersonalityAnalyzer
from .models import (
    AnalysisRequest,
    AnalysisResponse,
    PersonalityTraits,
    PostData
)
from .utils import (
    extract_username,
    validate_url,
    calculate_confidence,
    format_date
)

__all__ = [
    "app",
    "InstagramScraper",
    "PersonalityAnalyzer",
    "AnalysisRequest",
    "AnalysisResponse",
    "PersonalityTraits",
    "PostData",
    "extract_username",
    "validate_url",
    "calculate_confidence",
    "format_date"
]