from .svo_extractor_en import analyze_svo_en
from .svo_extractor_ko import analyze_svo_ko

def analyze_svo(text: str, lang: str, api_key: str = None):
    if lang == "ko":
        return analyze_svo_ko(text, api_key)
    return analyze_svo_en(text)
