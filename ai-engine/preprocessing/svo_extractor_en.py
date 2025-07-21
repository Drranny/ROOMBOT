import spacy

nlp = spacy.load("en_core_web_sm")

def extract_svo_en(sentence: str):
    doc = nlp(sentence)
    subjects = []
    verbs = []
    objects = []
    predicates = []
    
    for token in doc:
        # 주어: nsubj, nsubjpass(수동태)
        if token.dep_ in ("nsubj", "nsubjpass"):
            # 복잡한 주어 구조 처리
            subject_text = token.text
            # 주어의 수식어들도 포함
            for child in token.children:
                if child.dep_ in ("det", "amod", "compound", "prep", "pobj"):
                    subject_text = child.text + " " + subject_text
            subjects.append(subject_text)
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
    
    # 서술어 추출 (동사 + 형용사)
    for token in doc:
        if token.dep_ == "ROOT":
            if token.pos_ in ["VERB", "ADJ"]:
                predicates.append({
                    "text": token.text,
                    "pos": token.pos_,
                    "lemma": token.lemma_
                })
        # Be동사나 조동사도 포함
        elif token.dep_ in ["aux", "cop"] and token.pos_ in ["VERB", "AUX"]:
            predicates.append({
                "text": token.text,
                "pos": token.pos_,
                "lemma": token.lemma_
            })
    
    return {
        "S": subjects,
        "V": verbs,
        "O": objects,
        "P": predicates
    }

def extract_predicate_en(sentence: str):
    """영어 텍스트에서 서술어(동사, 형용사) 추출"""
    doc = nlp(sentence)
    predicates = []
    
    for token in doc:
        # 주요 서술어 (ROOT)
        if token.dep_ == "ROOT":
            if token.pos_ in ["VERB", "ADJ"]:
                predicates.append({
                    "text": token.text,
                    "pos": token.pos_,
                    "lemma": token.lemma_,
                    "dep": token.dep_
                })
        # Be동사 (copula)
        elif token.dep_ == "cop" and token.pos_ in ["VERB", "AUX"]:
            predicates.append({
                "text": token.text,
                "pos": token.pos_,
                "lemma": token.lemma_,
                "dep": token.dep_
            })
        # 보조동사
        elif token.dep_ == "aux" and token.pos_ in ["VERB", "AUX"]:
            predicates.append({
                "text": token.text,
                "pos": token.pos_,
                "lemma": token.lemma_,
                "dep": token.dep_
            })
        # 형용사 서술어
        elif token.dep_ == "acomp" and token.pos_ == "ADJ":
            predicates.append({
                "text": token.text,
                "pos": token.pos_,
                "lemma": token.lemma_,
                "dep": token.dep_
            })
    
    return predicates

def analyze_svo_en(text: str):
    """영어 텍스트의 SVO 분석 (서술어 포함)"""
    try:
        doc = nlp(text)
        svo_result = extract_svo_en(text)
        predicates = extract_predicate_en(text)
        
        # 서술어 정보 추가
        predicate_info = predicates[0] if predicates else {"text": "Verb", "pos": "VERB", "lemma": "verb"}
        
        # 목적어가 없는 경우 처리
        object_text = svo_result["O"][0] if svo_result["O"] else "없음"
        has_object = len(svo_result["O"]) > 0
        
        return {
            "sentence": text,
            "language": "en",
            "svo": {
                "subject": svo_result["S"][0] if svo_result["S"] else "Subject",
                "verb": svo_result["V"][0] if svo_result["V"] else predicate_info["text"],
                "object": object_text,
                "predicate_type": predicate_info["pos"],
                "has_object": has_object
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
                "object": "없음",
                "predicate_type": "VERB",
                "has_object": False
            }
        }


def analyze_svo_from_text(text: str):
    sentences = [sent.text.strip() for sent in nlp(text).sents]
    return [{"sentence": s, "svo": extract_svo_en(s)} for s in sentences]


# 테스트
if __name__ == "__main__":
    text = "John and Mary eat an apple and a banana. The book was read by Tom. The weather is beautiful."
    import json
    print(json.dumps(analyze_svo_from_text(text), indent=2))