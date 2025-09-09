# converter.py
from pathlib import Path

def convert_to_idml(input_csv1: Path, input_csv2: Path | None, out_dir: Path) -> Path:
    """
    Kall pappas logikk her direkte (uten subprocess). Returner sti til IDML/ZIP.
    """
    # pseudo:
    # result = mymodule.run(input_csv1, input_csv2, out_dir)
    out_path = out_dir / "result.idml"
    # ... skriv ut result.idml ...
    return out_path
