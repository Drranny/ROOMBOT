from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import re
import urllib.parse

router = APIRouter()

class WikipediaMultiRequest(BaseModel):
    main_keyword: str
    keywords: List[str]

class WikipediaFilteredResponse(BaseModel):
    sentence: str
    url: str
    matched_keywords: List[str]

@router.post("/wikipedia/search", response_model=List[WikipediaFilteredResponse])
def search_wikipedia_multi(data: WikipediaMultiRequest):
    # 언어 자동 감지 (한글/영어)
    lang = "ko"
    if re.search(r'[a-zA-Z]', data.main_keyword):
        lang = "en"
    encoded_keyword = urllib.parse.quote(data.main_keyword)
    URL = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_keyword}"
    S = requests.Session()
    response = S.get(URL)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Wikipedia page not found")
    result = response.json()
    summary = result.get("extract", "")
    url = result.get("content_urls", {}).get("desktop", {}).get("page", "")
    sentences = re.split(r'[.!?\n]', summary)
    filtered = []
    for sent in sentences:
        matched = [kw for kw in data.keywords if kw in sent]
        if len(matched) >= 1:
            filtered.append(WikipediaFilteredResponse(sentence=sent.strip(), url=url, matched_keywords=matched))
    return filtered 