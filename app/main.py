from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask
from pathlib import Path
import tempfile, shutil, os

from . import logikk

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def index():
    html = Path(__file__).with_name("static").joinpath("index.html").read_text(encoding="utf-8")
    return html


@app.post("/convert")
async def convert(csv: UploadFile = File(...), function: str = Form(...)):
    # 1) Valider filtype
    if not csv.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="csv must be .csv")

    # 2) Lag temp-katalog som vi RYDDER ETTERPÅ via BackgroundTask
    tmpd = Path(tempfile.mkdtemp(prefix="dk-"))

    prev_cwd = Path.cwd()
    try:
        # 3) Lagre opplasta CSV i temp-katalogen
        in_path = tmpd / csv.filename
        in_path.write_bytes(await csv.read())

        # 4) Sett logikk.globals (koden din forventer fil+ext i CWD)
        base, ext = os.path.splitext(csv.filename)
        logikk.fil = base
        logikk.ext = ext

        # 5) Kjør i temp-katalogen
        os.chdir(str(tmpd))

        # 6) Kjør riktig konvertering
        if function == "runRL":
            logikk.runRL()
            out_name = f"{base} RL tag.txt"
            media_type = "text/plain; charset=utf-16"
        elif function == "runMX":
            logikk.runMX()
            out_name = f"{base} MX tag.txt"
            media_type = "text/plain; charset=utf-16"
        elif function == "AllNames":
            logikk.AllNames()
            out_name = f"{base} AllNames.xlsx"
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        else:
            raise HTTPException(status_code=400, detail="Unknown function")

        out_path = tmpd / out_name
        if not out_path.exists():
            raise HTTPException(status_code=500, detail=f"Conversion failed; output missing: {out_name}")

        # 7) Rydd opp ETTER at svaret er sendt
        cleanup = BackgroundTask(lambda: shutil.rmtree(tmpd, ignore_errors=True))

        # 8) Returnér filen
        return FileResponse(
            path=str(out_path),
            media_type=media_type,
            filename=out_path.name,
            background=cleanup,
        )

    finally:
        # Viktig: bytt alltid tilbake til tidligere CWD.
        try:
            os.chdir(str(prev_cwd))
        except Exception:
            pass
        # Ikke slett tmpd her! BackgroundTask tar seg av det etter sending.
