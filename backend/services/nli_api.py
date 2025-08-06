from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from threading import Lock

app = FastAPI(title="NLI API", description="Natural Language Inference Demo", version="1.0.0")

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

@app.post("/nli", response_model=NLIResponse)
def nli_infer(req: NLIRequest):
    pipe = get_nli_pipe()
    input_text = f"{req.premise} </s></s> {req.hypothesis}"
    result = pipe(input_text, truncation=True)[0]
    label = result['label'].lower()
    score = float(result['score'])
    return NLIResponse(label=label, score=score)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("🧠 NLI 서버를 시작합니다...")
    print("📍 서버 주소: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001) 