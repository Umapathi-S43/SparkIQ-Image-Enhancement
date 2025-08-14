from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter()

class HelloResponse(BaseModel):
    message: str
    status: str
    timestamp: str

@router.get("/hello", response_model=HelloResponse)
async def hello_endpoint() -> Dict[str, Any]:
    """
    Simple hello endpoint for testing purposes
    """
    try:
        import datetime
        
        logger.info("Hello endpoint called")
        
        response = HelloResponse(
            message="Hello from SparkIQ AI Image Enhancement API!",
            status="success",
            timestamp=datetime.datetime.now().isoformat()
        )
        
        logger.info("Hello endpoint response generated successfully")
        return response.dict()
        
    except Exception as e:
        logger.error(f"Error in hello endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error occurred"
        )

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    """
    try:
        logger.info("Health check endpoint called")
        return {"status": "healthy", "service": "SparkIQ AI Image Enhancement API"}
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Service unhealthy"
        ) 