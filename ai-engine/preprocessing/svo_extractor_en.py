import spacy

nlp = spacy.load("en_core_web_sm")

def extract_svo_en(sentence: str):
    doc = nlp(sentence)
    subjects = []
    verbs = []
    objects = []
    for token in doc:
        # 주어: nsubj, nsubjpass(수동태)
        if token.dep_ in ("nsubj", "nsubjpass"):
            subjects.append(token.text)
        # 동사: ROOT, aux(조동사)
        if token.dep_ == "ROOT" and token.pos_ == "VERB":
            verbs.append(token.text)
        # 목적어: dobj(직접), pobj(전치사 목적어), attr(속성), oprd(목적 보어)
        if token.dep_ in ("dobj", "attr", "oprd", "pobj"):
            objects.append(token.text)
        # 병렬 구조(예: and, or)
        if token.dep_ == "conj" and token.head.dep_ in ("dobj", "attr", "oprd", "pobj"):
            objects.append(token.text)
        if token.dep_ == "conj" and token.head.dep_ in ("nsubj", "nsubjpass"):
            subjects.append(token.text)
        if token.dep_ == "conj" and token.head.dep_ == "ROOT" and token.pos_ == "VERB":
            verbs.append(token.text)
    return {
        "S": subjects,
        "V": verbs,
        "O": objects
    }

def analyze_svo_en(text: str):
    """영어 텍스트의 SVO 분석"""
    try:
        doc = nlp(text)
        svo_result = extract_svo_en(text)
        
        return {
            "sentence": text,
            "language": "en",
            "svo": {
                "subject": svo_result["S"][0] if svo_result["S"] else "Subject",
                "verb": svo_result["V"][0] if svo_result["V"] else "Verb",
                "object": svo_result["O"][0] if svo_result["O"] else "Object"
            }
        }
    except Exception as e:
        print(f"영어 SVO 분석 오류: {e}")
        return {
            "sentence": text,
            "language": "en",
            "svo": {
                "subject": "Subject",
                "verb": "Verb",
                "object": "Object"
            }
        }


def analyze_svo_from_text(text: str):
    sentences = [sent.text.strip() for sent in nlp(text).sents]
    return [{"sentence": s, "svo": extract_svo_en(s)} for s in sentences]


# 테스트
if __name__ == "__main__":
    text = "John and Mary eat an apple and a banana. The book was read by Tom."
    import json
    print(json.dumps(analyze_svo_from_text(text), indent=2))