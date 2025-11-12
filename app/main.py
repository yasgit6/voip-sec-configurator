from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import io
import zipfile
import logging
from datetime import datetime

from app.api.generate import generate_configs
from app.api.validators import validate_config_input

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="VoIP Security Configurator", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with configuration form"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
@limiter.limit("10/minute")
async def generate_config(
    request: Request,
    server_type: str = Form("asterisk"),
    sip_port: int = Form(5060),
    rtp_start: int = Form(10000),
    rtp_end: int = Form(20000),
    max_attempts: int = Form(3),
    ban_time: int = Form(3600),
    enable_ssh: bool = Form(False),
    enable_ipv6: bool = Form(False)
):
    """Generate security configurations"""
    try:
        # Validate inputs
        validation = validate_config_input(
            server_type, sip_port, rtp_start, rtp_end, max_attempts, ban_time
        )
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=validation["message"])
        
        # Generate configurations
        configs = generate_configs(
            server_type=server_type,
            sip_port=sip_port,
            rtp_start=rtp_start,
            rtp_end=rtp_end,
            max_attempts=max_attempts,
            ban_time=ban_time,
            enable_ssh=enable_ssh,
            enable_ipv6=enable_ipv6
        )
        
        # Create ZIP file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in configs.items():
                zip_file.writestr(filename, content)
        
        zip_buffer.seek(0)
        
        # Log the generation
        logger.info(f"Config generated for {server_type} on port {sip_port}")
        
        return FileResponse(
            zip_buffer,
            media_type='application/zip',
            filename=f"voip_security_configs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
    
    except Exception as e:
        logger.error(f"Error generating config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.get("/docs/custom")
async def custom_docs():
    """Custom API documentation"""
    return {
        "endpoints": {
            "/": "Home page with configuration form",
            "/generate": "POST endpoint to generate security configs",
            "/api/health": "Health check endpoint"
        },
        "parameters": {
            "server_type": "asterisk, freeswitch, or opensips",
            "sip_port": "SIP signaling port (default: 5060)",
            "rtp_start": "Start of RTP port range",
            "rtp_end": "End of RTP port range",
            "max_attempts": "Max login attempts before ban",
            "ban_time": "Ban duration in seconds"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
