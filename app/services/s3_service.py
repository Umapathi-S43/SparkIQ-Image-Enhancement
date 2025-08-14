import boto3
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from io import BytesIO
from PIL import Image
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    """Service for handling S3 operations"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.aws_region
        self._initialize_s3_client()
    
    def _initialize_s3_client(self):
        """Initialize S3 client with AWS credentials"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region
            )
            
            # Test connection by checking if bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"✅ S3 client initialized successfully for bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found")
            raise
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"❌ S3 bucket '{self.bucket_name}' not found")
                raise
            elif error_code == '403':
                logger.error(f"❌ Access denied to S3 bucket '{self.bucket_name}'")
                raise
            else:
                logger.error(f"❌ S3 client initialization failed: {e}")
                raise
        except Exception as e:
            logger.error(f"❌ Unexpected error initializing S3 client: {e}")
            raise
    
    def upload_image_to_s3(self, image: Image.Image, original_filename: str = None, 
                          folder: str = "background-removed") -> Dict[str, Any]:
        """
        Upload image to S3 and return public URL
        
        Args:
            image: PIL Image object
            original_filename: Original filename for reference
            folder: S3 folder path
            
        Returns:
            Dict containing upload result with S3 URL
        """
        try:
            # Generate unique filename
            if original_filename:
                name = Path(original_filename).stem
            else:
                name = "image"
            
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{folder}/{name}_{unique_id}.png"
            
            # Convert image to bytes
            buffer = BytesIO()
            image.save(buffer, format='PNG', optimize=True)
            buffer.seek(0)
            
            # Upload to S3 with public read access
            logger.info(f"📤 Uploading image to S3: {filename}")
            
            self.s3_client.upload_fileobj(
                buffer,
                self.bucket_name,
                filename,
                ExtraArgs={
                    'ContentType': 'image/png',
                    'ACL': 'public-read',  # Make file publicly accessible
                    'CacheControl': 'max-age=31536000'  # Cache for 1 year
                }
            )
            
            # Generate public URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{filename}"
            
            logger.info(f"✅ Image uploaded successfully to S3: {s3_url}")
            
            return {
                "success": True,
                "s3_url": s3_url,
                "s3_key": filename,
                "bucket": self.bucket_name,
                "region": self.region,
                "content_type": "image/png",
                "public_access": True
            }
            
        except ClientError as e:
            logger.error(f"❌ S3 upload failed: {e}")
            return {
                "success": False,
                "error": f"S3 upload failed: {e}",
                "error_code": e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error uploading to S3: {e}")
            return {
                "success": False,
                "error": f"Upload error: {e}"
            }
    
    def delete_image_from_s3(self, s3_key: str) -> Dict[str, Any]:
        """
        Delete image from S3
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            Dict containing deletion result
        """
        try:
            logger.info(f"🗑️ Deleting image from S3: {s3_key}")
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            logger.info(f"✅ Image deleted successfully from S3: {s3_key}")
            
            return {
                "success": True,
                "deleted_key": s3_key
            }
            
        except ClientError as e:
            logger.error(f"❌ S3 deletion failed: {e}")
            return {
                "success": False,
                "error": f"S3 deletion failed: {e}",
                "error_code": e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error deleting from S3: {e}")
            return {
                "success": False,
                "error": f"Deletion error: {e}"
            }
    
    def get_image_url(self, s3_key: str) -> str:
        """
        Generate public URL for S3 object
        
        Args:
            s3_key: S3 object key
            
        Returns:
            Public URL for the object
        """
        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
    
    def check_bucket_access(self) -> Dict[str, Any]:
        """
        Check if we have proper access to the S3 bucket
        
        Returns:
            Dict containing access check result
        """
        try:
            # Try to list objects (limited to 1 to test access)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            
            return {
                "success": True,
                "bucket_name": self.bucket_name,
                "region": self.region,
                "access_level": "read_write",
                "object_count": response.get('KeyCount', 0)
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            return {
                "success": False,
                "error": f"Access check failed: {error_code}",
                "error_code": error_code
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Access check error: {e}"
            }
    
    def get_bucket_stats(self) -> Dict[str, Any]:
        """
        Get basic statistics about the S3 bucket
        
        Returns:
            Dict containing bucket statistics
        """
        try:
            # List all objects in the background-removed folder
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix="background-removed/"
            )
            
            objects = response.get('Contents', [])
            total_size = sum(obj['Size'] for obj in objects)
            
            return {
                "success": True,
                "bucket_name": self.bucket_name,
                "total_objects": len(objects),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "folder": "background-removed"
            }
            
        except ClientError as e:
            return {
                "success": False,
                "error": f"Stats retrieval failed: {e}",
                "error_code": e.response['Error']['Code'] if 'Error' in e.response else 'Unknown'
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Stats error: {e}"
            } 