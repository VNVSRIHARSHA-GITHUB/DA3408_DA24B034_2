import joblib
import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MODEL_PATH = "model.joblib"
CACHE_TTL_SECONDS = 300  

app = FastAPI(title="Spam Detection API (with cache)")

model = None


cache = redis.Redis(host="cache", port=6379, decode_responses=True)


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    label: str


@app.on_event("startup")
def load_model():
    global model
    model = joblib.load(MODEL_PATH)


@app.get("/healthz")
def healthz():
    if model is None:
        return JSONResponse(status_code=503, content={"status": "loading"})
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    cache_key = req.text

    cached = cache.get(cache_key)
    if cached is not None:
        return {"label": cached}

    label = model.predict([req.text])[0]
    cache.set(cache_key, label, ex=CACHE_TTL_SECONDS)
    return {"label": label}