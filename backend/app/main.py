from fastapi import FastAPI

app = FastAPI(title="Zippy Finance Voice Agent")

@app.get("/health")
def health():
    return {"status": "ok"}