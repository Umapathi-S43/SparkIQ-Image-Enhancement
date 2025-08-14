from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
import logging
from typing import Dict, Any, Optional, List
from app.services.background_removal_service import BackgroundRemovalService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize service
background_service = BackgroundRemovalService()

class BackgroundRemovalRequest(BaseModel):
    image_url: HttpUrl
    model: Optional[str] = "birefnet-general"
    enhance_quality: Optional[bool] = True
    use_cache: Optional[bool] = True
    method: Optional[str] = "professional"  # "professional", "advanced", "standard", "ensemble", "sam_auto", "sam_guided", "yolo", "rembg_advanced"
    quality_level: Optional[str] = "ultra"  # "fast", "high", "ultra"

class BackgroundRemovalResponse(BaseModel):
    success: bool
    original_size: Optional[tuple] = None
    processed_size: Optional[tuple] = None
    s3_url: Optional[str] = None
    s3_key: Optional[str] = None
    format: Optional[str] = None
    ai_model: Optional[str] = None
    method: Optional[str] = None
    quality_level: Optional[str] = None
    gpu_used: Optional[bool] = None
    processing_mode: Optional[str] = None
    cached: Optional[bool] = None
    processing_time: Optional[float] = None
    enhance_quality: Optional[bool] = None
    storage: Optional[str] = None
    professional_service: Optional[bool] = None
    advanced_service: Optional[bool] = None
    error: Optional[str] = None

class ServiceStatusResponse(BaseModel):
    gpu_available: bool
    available_models: List[str]
    available_methods: List[str]
    cache_directory: str
    processing_mode: str
    s3_bucket: str
    s3_region: str
    s3_access: bool
    professional_service_available: bool
    advanced_service_available: bool
    professional_gpu_available: Optional[bool] = None
    professional_device: Optional[str] = None
    professional_methods: Optional[List[str]] = None
    professional_quality_levels: Optional[List[str]] = None
    expected_accuracy: Optional[str] = None
    advanced_gpu_available: Optional[bool] = None
    advanced_device: Optional[str] = None
    advanced_methods: Optional[List[str]] = None
    quality_levels: Optional[List[str]] = None

class S3StatsResponse(BaseModel):
    bucket_name: str
    total_objects: int
    total_size_bytes: int
    total_size_mb: float
    folder: str

@router.post("/remove-background", response_model=BackgroundRemovalResponse)
async def remove_background(request: BackgroundRemovalRequest) -> Dict[str, Any]:
    """
    Remove background from image URL with 95%+ accuracy using professional AI models
    
    - **image_url**: URL of the image to process
    - **model**: AI model to use (for standard method: birefnet-general, u2net, u2netp, u2net_human_seg, u2net_cloth_seg)
    - **enhance_quality**: Whether to enhance image quality before processing
    - **use_cache**: Whether to use caching for faster repeated processing
    - **method**: Removal method ("ultimate", "professional", "advanced", "standard", "ensemble", "sam_hq_auto", "sam_hq_guided", "yolo_v8x", "rembg_ultimate")
    - **quality_level**: Quality level for advanced methods ("fast", "high", "ultimate")
    """
    try:
        logger.info(f"🔄 Processing professional background removal for: {request.image_url}")
        logger.info(f"📋 Settings: model={request.model}, method={request.method}, quality={request.quality_level}, enhance={request.enhance_quality}, cache={request.use_cache}")
        
        # Validate method
        available_methods = background_service.get_available_methods()
        if request.method not in available_methods:
            logger.warning(f"⚠️ Invalid method {request.method}, using ultimate")
            request.method = "ultimate"
        
        # Validate model for standard method
        if request.method == "standard":
            available_models = background_service.get_available_models()
            if request.model not in available_models:
                logger.warning(f"⚠️ Invalid model {request.model}, using birefnet-general")
                request.model = "birefnet-general"
        
        # Validate quality level
        if request.quality_level not in ["fast", "high", "ultra"]:
            logger.warning(f"⚠️ Invalid quality level {request.quality_level}, using ultra")
            request.quality_level = "ultra"
        
        # Process the image
        result = background_service.process_image_url(
            str(request.image_url),
            model=request.model,
            enhance_quality=request.enhance_quality,
            use_cache=request.use_cache,
            method=request.method,
            quality_level=request.quality_level
        )
        
        if result["success"]:
            logger.info("✅ Professional background removal completed successfully")
            return BackgroundRemovalResponse(
                success=True,
                original_size=result["original_size"],
                processed_size=result["processed_size"],
                s3_url=result["s3_url"],
                s3_key=result["s3_key"],
                format=result["format"],
                ai_model=result["ai_model"],
                method=result["method"],
                quality_level=result["quality_level"],
                gpu_used=result["gpu_used"],
                processing_mode=result["processing_mode"],
                cached=result.get("cached", False),
                processing_time=result.get("processing_time", 0),
                enhance_quality=result.get("enhance_quality", True),
                storage=result.get("storage", "S3"),
                professional_service=result.get("professional_service", False),
                advanced_service=result.get("advanced_service", False)
            )
        else:
            logger.error(f"❌ Professional background removal failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in professional background removal endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during background removal"
        )

@router.get("/models", response_model=List[str])
async def get_available_models() -> List[str]:
    """
    Get list of available AI models for background removal
    """
    try:
        models = background_service.get_available_models()
        logger.info(f"📋 Available models: {models}")
        return models
    except Exception as e:
        logger.error(f"❌ Error getting available models: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving available models"
        )

@router.get("/methods", response_model=List[str])
async def get_available_methods() -> List[str]:
    """
    Get list of available professional background removal methods
    """
    try:
        methods = background_service.get_available_methods()
        logger.info(f"📋 Available professional methods: {methods}")
        return methods
    except Exception as e:
        logger.error(f"❌ Error getting available methods: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving available methods"
        )

@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status() -> Dict[str, Any]:
    """
    Get detailed service status including professional models, GPU availability, and expected accuracy
    """
    try:
        status = background_service.get_service_status()
        logger.info("🔍 Professional service status requested")
        return status
    except Exception as e:
        logger.error(f"❌ Error getting service status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving service status"
        )

@router.get("/s3/stats", response_model=S3StatsResponse)
async def get_s3_stats() -> Dict[str, Any]:
    """
    Get S3 bucket statistics for background removed images
    """
    try:
        stats = background_service.get_s3_stats()
        if stats["success"]:
            logger.info("📊 S3 stats requested")
            return stats
        else:
            raise HTTPException(
                status_code=500,
                detail=f"S3 stats error: {stats.get('error', 'Unknown error')}"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting S3 stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving S3 statistics"
        )

@router.delete("/s3/delete/{s3_key:path}")
async def delete_s3_image(s3_key: str) -> Dict[str, str]:
    """
    Delete a specific image from S3
    
    - **s3_key**: The S3 object key to delete (e.g., background-removed/image_abc123.png)
    """
    try:
        logger.info(f"🗑️ Deleting S3 image: {s3_key}")
        
        result = background_service.s3_service.delete_image_from_s3(s3_key)
        
        if result["success"]:
            logger.info(f"✅ S3 image deleted: {s3_key}")
            return {"message": f"Image {s3_key} deleted successfully"}
        else:
            logger.error(f"❌ S3 deletion failed: {result['error']}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete image: {result['error']}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting S3 image: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting image from S3"
        )

@router.get("/health/background-removal")
async def background_removal_health() -> Dict[str, str]:
    """
    Health check for professional background removal service
    """
    try:
        logger.info("🔍 Professional background removal health check")
        
        # Basic health check without calling service status
        return {
            "status": "healthy",
            "service": "professional_background_removal",
            "cache_directory": str(background_service.cache_dir),
            "gpu_available": background_service.gpu_available,
            "models_loaded": len(background_service.get_available_models()),
            "methods_available": len(background_service.get_available_methods()),
            "s3_bucket": background_service.s3_service.bucket_name,
            "s3_region": background_service.s3_service.region,
            "professional_service": background_service.professional_available,
            "advanced_service": background_service.advanced_available,
            "expected_accuracy": "95%+ for complex objects"
        }
    except Exception as e:
        logger.error(f"❌ Professional background removal health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Professional background removal service unhealthy"
        )

@router.delete("/cache/clear")
async def clear_cache() -> Dict[str, str]:
    """
    Clear the background removal cache
    """
    try:
        import shutil
        cache_dir = background_service.cache_dir
        
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(exist_ok=True)
            logger.info("🗑️ Cache cleared successfully")
            return {"message": "Cache cleared successfully"}
        else:
            return {"message": "Cache directory does not exist"}
            
    except Exception as e:
        logger.error(f"❌ Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error clearing cache"
        )

@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    """
    try:
        cache_dir = background_service.cache_dir
        if cache_dir.exists():
            cache_files = list(cache_dir.glob("*.png"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                "cache_files": len(cache_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2)
            }
        else:
            return {
                "cache_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0
            }
            
    except Exception as e:
        logger.error(f"❌ Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving cache statistics"
        ) 