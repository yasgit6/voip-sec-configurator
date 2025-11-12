from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import io, zipfile
from .api.generate import generate_configs

app = FastAPI()
env = Environment(loader=FileSystemLoader("app/templates"))
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    tmpl = env.get_template("index.html")
    return tmpl.render()

@app.post("/generate")
async def generate(port: int = Form(...), max_attempts: int = Form(...)):
    # استدعاء مولد القواعد
    result = generate_configs(port=port, max_attempts=max_attempts)
    # حزم الملفات في zip للإرسال
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, 'w') as z:
        for name, content in result.items():
            z.writestr(name, content)
    mem.seek(0)
    return FileResponse(mem, media_type='application/zip', filename="voip_security_configs.zip")
