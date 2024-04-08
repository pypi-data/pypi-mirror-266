from pathlib import Path
from subprocess import PIPE, Popen

from fastapi import FastAPI

app = FastAPI()


@app.post("/convert")
async def convert(file: str, dest: str = None):
    path = Path(file)

    if not path.exists():
        folder = "/data/komodo"
        path = Path(folder) / file
        if not path.exists():
            return {"error": "File not found"}

    if dest is None:
        dest = path.parent

    if not Path(dest).exists():
        return {"error": "Destination folder not found"}

    process = Popen(["pdf2htmlEX", "--dest-dir", str(dest), str(path)], stdout=PIPE, stderr=PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        return {"error": stderr}
    return {"output": stdout}

# curl -X POST http://localhost:8050/convert -H "Content-Type: application/json" -d '{"file": "sample.pdf"}'
# curl -X POST http://localhost:8050/convert?file=/data/komodo/users/ryan@kmdo.app/collections/a49a6647/2b5e026d.pdf
