from fastapi import FastAPI

app = FastAPI(
    title="WatchTower API",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "WatchTower API is running"}