"""
GBP Audit Bot API - FastAPI Application

Main entry point for the GBP Audit Bot backend.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, grid, search, projects, reports
from app.config import get_settings
from app.services.scheduler import init_scheduler, shutdown_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    logger.info("Starting GBP Audit Bot API...")
    init_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down GBP Audit Bot API...")
    shutdown_scheduler()


app = FastAPI(
    title="GBP Audit Bot API",
    description="""
    🗺️ **GBP Audit Bot** - Sistema de monitoramento de rankings locais via Geogrid.
    
    ## Funcionalidades
    
    * **Grid Generation** - Gerar coordenadas de grade (3x3, 5x5, 7x7)
    * **SERP Search** - Buscar posição do negócio em cada ponto da grade
    * **Metrics** - ARP (Average Rank Position), Top 3, Visibility Score
    * **Reports** - Comparativo semanal com análise de IA
    * **PDF Export** - Relatório PDF com heatmap e métricas
    * **WhatsApp** - Envio automático para grupos de clientes
    
    ## Autenticação
    
    Todas as rotas requerem autenticação via JWT Bearer token.
    Faça login em `/auth/login` para obter o token.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(grid.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(reports.router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "GBP Audit Bot API",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check."""
    from app.services.scheduler import scheduler
    
    return {
        "status": "healthy",
        "database": "connected",  # TODO: Add actual DB check
        "serp_api": "configured" if settings.scale_serp_api_key else "not_configured",
        "whatsapp_api": "configured" if settings.whatsapp_api_url else "not_configured",
        "scheduler": "running" if scheduler and scheduler.running else "stopped"
    }

