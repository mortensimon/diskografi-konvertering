from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import tempfile, shutil, os

from .converter import convert_to_idml

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    html = Path(__file__).with_name("static").joinpath("index.html").read_text(encoding="utf-8")
    return html

@app.post("/convert")
async def convert(csv1: UploadFile = File(...), csv2: UploadFile | None = None):
    if not csv1.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="csv1 må være .csv")
    if csv2 and not csv2.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="csv2 må være .csv")

    # lag midlertidig arbeidsområde
    tmpd = Path(tempfile.mkdtemp(prefix="dk-"))
    try:
        in1 = tmpd / csv1.filename
        in1.write_bytes(await csv1.read())

        in2 = None
        if csv2:
            in2 = tmpd / csv2.filename
            in2.write_bytes(await csv2.read())

        out_path = convert_to_idml(in1, in2, tmpd)
        if not out_path.exists():
            raise HTTPException(500, "Konverteringen feilet; ingen output")

        # returner filen for nedlasting
        return FileResponse(
            path=str(out_path),
            media_type="application/octet-stream",
            filename=out_path.name
        )
    finally:
        # rydd opp etter at responsen er sendt (enkelt og trygt for små filer)
        # For store filer/streaming: bruk BackgroundTasks
        shutil.rmtree(tmpd, ignore_errors=True)
