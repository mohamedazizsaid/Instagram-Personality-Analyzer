from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from typing import Dict, List
from dotenv import load_dotenv
import os
from pathlib import Path
from scraper import InstagramScraper
from personality_analyzer import PersonalityAnalyzer
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(title="Instagram Personality Analyzer API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instances globales
scraper = InstagramScraper()
analyzer = PersonalityAnalyzer()

class AnalysisRequest(BaseModel):
    instagram_url: str

class AnalysisResponse(BaseModel):
    personality_traits: Dict[str, float]
    posts_analyzed: int
    sample_data: List[Dict]
    visualization: str
analysis_status: Dict[str, Dict] = {}
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

@app.get("/")
async def root():
    return {"message": "Instagram Personality Analyzer API", "status": "running"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_profile(request: AnalysisRequest):
    try:
        # Extraire le nom d'utilisateur de l'URL
        username = extract_username(request.instagram_url)
        
        # Scraper les données Instagram
        print(f"Scraping data for {username}...")
        scraped_data = await scraper.scrape_profile(username)
        
        if not scraped_data or len(scraped_data) == 0:
            raise HTTPException(status_code=404, detail="No data found for this profile")
        profile_info= await scraper.get_profile_info(username)
        # Analyser la personnalité
        print("Analyzing personality...")
        personality_results = await analyzer.analyze(scraped_data)
        
        # Préparer la réponse
        response = {
            "username": username,
            "personality_traits": personality_results["traits"],
            "posts_analyzed": len(scraped_data),
            "sample_data": scraped_data[:5],  # 5 premiers posts
            "visualization": personality_results["visualization"],
            "profile_info": profile_info
        }
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_username(url: str) -> str:
    """Extraire le nom d'utilisateur de l'URL Instagram"""
    url = url.rstrip('/')
    parts = url.split('/')
    
    # Format: https://www.instagram.com/username/
    if 'instagram.com' in url:
        for i, part in enumerate(parts):
            if part == 'instagram.com' and i + 1 < len(parts):
                return parts[i + 1]
    
    # Si c'est juste le nom d'utilisateur
    return parts[-1]
from fastapi.responses import StreamingResponse
import httpx

@app.get("/proxy/instagram-image")
async def proxy_instagram_image(url: str):
    """
    Proxy pour les images Instagram
    Usage: /proxy/instagram-image?url=ENCODED_URL
    """
    try:
        # Décoder l'URL
        decoded_url = url
        
        async with httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        ) as client:
            response = await client.get(decoded_url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code)
            
            return StreamingResponse(
                iter([response.content]),
                media_type=response.headers.get('content-type', 'image/jpeg')
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)