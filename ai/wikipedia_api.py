import httpx
from fastapi import HTTPException

async def get_wikipedia_summary(query: str):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code == 200:
        data = response.json()
        return {
            "title": data.get("title"),
            "description": data.get("extract"),
            "image": data.get("thumbnail", {}).get("source"),
            "url": data.get("content_urls", {}).get("desktop", {}).get("page")
        }
    elif response.status_code == 404:
        raise HTTPException(status_code=404, detail="Nessun risultato trovato.")
    else:
        raise HTTPException(status_code=500, detail="Errore nel contattare Wikipedia.")
