from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="SparkIQ AI Image Enhancement API with Background Removal and S3 Storage",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request timing middleware
    @application.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request processed in {process_time:.4f} seconds")
        return response

    # Include API router
    application.include_router(api_router, prefix="/api/v1")

    return application

app = create_application()

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting up SparkIQ AI Image Enhancement API...")
    logger.info("📖 API Documentation: http://localhost:8000/docs")
    logger.info("👋 Hello Endpoint: http://localhost:8000/api/v1/hello")
    logger.info("🎨 Background Removal: http://localhost:8000/api/v1/ai/remove-background")
    logger.info("☁️ S3 Storage: Enabled with bucket 'sparkiq-image-upload'")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Shutting down SparkIQ AI Image Enhancement API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 