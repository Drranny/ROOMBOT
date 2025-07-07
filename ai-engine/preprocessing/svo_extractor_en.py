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

def analyze_svo_from_text(text: str):
    sentences = [sent.text.strip() for sent in nlp(text).sents]
    return [{"sentence": s, "svo": extract_svo_en(s)} for s in sentences]


# 테스트
if __name__ == "__main__":
    text = "John and Mary eat an apple and a banana. The book was read by Tom."
    import json
    print(json.dumps(analyze_svo_from_text(text), indent=2))