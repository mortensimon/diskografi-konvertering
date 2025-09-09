from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from pathlib import Path
import tempfile, shutil, os

from . import logikk
import os

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def index():
    html = Path(__file__).with_name("static").joinpath("index.html").read_text(encoding="utf-8")
    return html

@app.post("/convert")
async def convert(csv: UploadFile = File(...), function: str = Form(...)):
    # validate upload
    if not csv.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="csv must be .csv")

    # temporary working dir
    tmpd = Path(tempfile.mkdtemp(prefix="dk-"))
    prev_cwd = Path.cwd()
    try:
        # save uploaded csv to tmp dir
        in_path = tmpd / csv.filename
        in_path.write_bytes(await csv.read())

        # configure logikk globals so its functions find the file by name
        base, ext = os.path.splitext(csv.filename)
        logikk.fil = base
        logikk.ext = ext

        # run in temp dir so logikk file reads succeed (logikk expects fil+ext in cwd)
        os.chdir(str(tmpd))

        # call appropriate function
        if function == "runRL":
            logikk.runRL()
            out_name = f"{base} RL tag.txt"
        elif function == "runMX":
            logikk.runMX()
            out_name = f"{base} MX tag.txt"
        else:  # AllNames
            logikk.AllNames()
            out_name = f"{base} AllNames.xlsx"

        out_path = tmpd / out_name
        if not out_path.exists():
            raise HTTPException(status_code=500, detail="Conversion failed; output missing")

        return FileResponse(
            path=str(out_path),
            media_type="application/octet-stream",
            filename=out_path.name
        )
    finally:
        # restore cwd and cleanup
        try:
            os.chdir(str(prev_cwd))
        except Exception:
            pass
        shutil.rmtree(tmpd, ignore_errors=True)
