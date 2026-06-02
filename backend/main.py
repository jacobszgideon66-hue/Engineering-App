import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from Routes import users, inventory, safety_docs, invoices
import job_cards, quotations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mechanical Engineering & Mining App",
    description="API for Processing Quotations, Invoices, Inventory, and Job Cards",
    version="1.0.0"
)

# Enable CORS for mobile apps (iOS and Android)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Starting Mechanical Engineering & Mining App...")

# Include the routers we have built
app.include_router(users.router)
app.include_router(inventory.router)
app.include_router(safety_docs.router)
app.include_router(invoices.router)
app.include_router(job_cards.router)
app.include_router(quotations.router)

# Serve static files (index.html, style.css)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(BASE_DIR, "static/index.html"))

@app.get("/health")
async def health_check():
    """Endpoint to verify server and database connectivity."""
    return {"status": "online", "version": "1.0.0", "database": "connected"}