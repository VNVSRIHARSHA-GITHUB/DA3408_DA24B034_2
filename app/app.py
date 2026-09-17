import joblib
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

MODEL_PATH = "model.joblib"
app = FastAPI(title="Spam Detection API")
_model = None

class PredictRequest(BaseModel):
    text: str

class PredictResponse(BaseModel):
    label: str

@app.on_event("startup")
def load_model():
    global _model
    _model = joblib.load(MODEL_PATH)

@app.get("/healthz")
def healthz():
    if _model is None:
        return JSONResponse(status_code=503, content={"status": "loading"})
    return {"status": "ok"}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    label = _model.predict([req.text])[0]
    return {"label": label}