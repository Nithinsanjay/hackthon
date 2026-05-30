import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from scraper import enrich_company


app = FastAPI()
RESULTS_FILE = Path("results.json")
results = []


class URLInput(BaseModel):
    url: str
    website_name: str | None = None


@app.on_event("startup")
def load_results():
    global results
    if RESULTS_FILE.exists() and RESULTS_FILE.stat().st_size > 0:
        try:
            results = json.loads(RESULTS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            results = []


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.post("/enrich")
def enrich(input: URLInput):
    data = enrich_company(input.url, input.website_name)
    results.append(data)
    RESULTS_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return data


@app.get("/results")
def get_results():
    return results
