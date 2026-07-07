from fastapi import FastAPI

from app.routes import summarise, classify, history, tone

app = FastAPI(title="AI Assistant Service", version="1.0.0")

app.include_router(summarise.router)
app.include_router(classify.router)
app.include_router(history.router)
app.include_router(tone.router)


@app.get("/health")
def health():
    return {"status": "ok"}
