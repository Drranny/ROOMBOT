from fastapi import APIRouter
from pydantic import BaseModel
from transformers import pipeline
from threading import Lock

router = APIRouter(prefix="/nli", tags=["nli"])

class NLIRequest(BaseModel):
    premise: str
    hypothesis: str

class NLIResponse(BaseModel):
    label: str
    score: float

# 모델 로딩 (스레드 안전)
nli_pipe = None
nli_lock = Lock()

def get_nli_pipe():
    global nli_pipe
    with nli_lock:
        if nli_pipe is None:
            nli_pipe = pipeline("text-classification", model="facebook/bart-large-mnli")
        return nli_pipe

@router.post("/", response_model=NLIResponse)
def nli_infer(req: NLIRequest):
    pipe = get_nli_pipe()
    input_text = f"{req.premise} </s></s> {req.hypothesis}"
    result = pipe(input_text, truncation=True)[0]
    label = result['label'].lower()
    score = float(result['score'])
    return NLIResponse(label=label, score=score)

@router.get("/health")
def health_check():
    return {"status": "healthy"} 