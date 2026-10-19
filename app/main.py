"""FastAPI application for the Business Forecasting Dashboard. Author: Rayyan Anwar"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.concurrency import run_in_threadpool

from . import __author__, __version__
from .business import FREQS, InputError, analyse_table, forecast_csv, load_table, report_markdown
from .sample import generate_sales

MAX_BYTES = 5_000_000
ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="Business Forecasting Dashboard", version=__version__,
              description="Import history, get backtested forecasts with uncertainty and explicit assumptions. Author: Rayyan Anwar.",
              contact={"name": __author__}, license_info={"name": "MIT"})


@app.exception_handler(InputError)
async def on_input_error(_: Request, exc: InputError):
    return JSONResponse(status_code=422, content={"error": {"code": "invalid_input", "message": str(exc)}})


@app.get("/health")
def health():
    return {"status": "ok", "version": __version__, "author": __author__}


@app.get("/api/info")
def info():
    return {"name": "Business Forecasting Dashboard", "author": __author__, "version": __version__, "required_columns": ["date", "value"],
            "optional_columns": ["series"], "frequencies": list(FREQS), "max_upload_bytes": MAX_BYTES}


@app.get("/api/sample", response_class=PlainTextResponse)
def sample(seed: int = Query(0, ge=0, le=10_000), n_days: int = Query(730, ge=90, le=1500)):
    return PlainTextResponse(generate_sales(seed, n_days).to_csv(index=False), media_type="text/csv")


@app.post("/api/analyze")
async def analyze(request: Request, freq: str | None = Query(None, pattern="^[DWM]$"), horizon: int = Query(12, ge=1, le=60),
                  agg: str = Query("sum", pattern="^(sum|mean)$"), missing: str = Query("zero", pattern="^(zero|interpolate|ffill)$"),
                  level: float = Query(0.8, ge=0.5, le=0.95), season: int | None = Query(None, ge=1, le=366)):
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="upload too large (limit 5 MB)")
    body = await request.body()
    if len(body) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="upload too large (limit 5 MB)")
    try:
        text = body.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise InputError("file must be UTF-8 encoded CSV") from None

    def work():
        df, rep = load_table(text)
        res = analyse_table(df, rep, freq, horizon, agg, missing, level, season)
        res["forecast_csv"], res["report_markdown"] = forecast_csv(res), report_markdown(res)
        return res
    return await run_in_threadpool(work)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "frontend" / "index.html")
