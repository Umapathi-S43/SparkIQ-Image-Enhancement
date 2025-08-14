# SparkIQ AI Image Enhancement API

A powerful FastAPI-based image processing service with advanced AI-powered background removal capabilities.

## 🚀 Features

### Core Features

- **AI-Powered Background Removal** using state-of-the-art rembg models
- **Multiple AI Models** support for different use cases
- **GPU/CPU Detection** with automatic hardware optimization
- **High-Quality Processing** with image enhancement options
- **Caching System** for improved performance
- **Comprehensive Error Handling** and logging

### AI Models Available

- `birefnet-general` - Best general-purpose model (default)
- `u2net` - Universal background removal
- `u2netp` - Lightweight version of u2net
- `u2net_human_seg` - Specialized for human segmentation
- `u2net_cloth_seg` - Specialized for clothing segmentation

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- macOS (for development) or Linux/Windows
- GPU support (optional, for faster processing)

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd SparkIQ-Image-Enhancement

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### GPU Support (Optional)

For GPU acceleration, ensure you have:

- NVIDIA GPU with CUDA support (Linux/Windows)
- Apple Silicon with CoreML support (macOS)

## 📡 API Endpoints

### Background Removal

#### Remove Background

```http
POST /api/v1/ai/remove-background
```

**Request Body:**

```json
{
  "image_url": "https://example.com/image.jpg",
  "model": "birefnet-general",
  "enhance_quality": true,
  "use_cache": true
}
```

**Response:**

```json
{
  "success": true,
  "original_size": [400, 600],
  "processed_size": [400, 600],
  "filename": "processed_images/bg_removed_image_abc123.png",
  "format": "PNG",
  "ai_model": "birefnet-general",
  "gpu_used": true,
  "processing_mode": "GPU",
  "cached": false,
  "processing_time": 2.34,
  "enhance_quality": true
}
```

#### Get Available Models

```http
GET /api/v1/ai/models
```

#### Get Service Status

```http
GET /api/v1/ai/status
```

#### Health Check

```http
GET /api/v1/ai/health/background-removal
```

### Cache Management

#### Get Cache Statistics

```http
GET /api/v1/ai/cache/stats
```

#### Clear Cache

```http
DELETE /api/v1/ai/cache/clear
```

### Basic Endpoints

#### Hello Endpoint

```http
GET /api/v1/hello
```

#### Health Check

```http
GET /api/v1/health
```

## 🧪 Testing

### Run Comprehensive Tests

```bash
python test_advanced_features.py
```

### Manual Testing Examples

#### Basic Background Removal

```bash
curl -X POST "http://localhost:8000/api/v1/ai/remove-background" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
  }'
```

#### Advanced Background Removal with Options

```bash
curl -X POST "http://localhost:8000/api/v1/ai/remove-background" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400",
    "model": "u2net_human_seg",
    "enhance_quality": true,
    "use_cache": true
  }'
```

#### Check Service Status

```bash
curl http://localhost:8000/api/v1/ai/status
```

## 🔧 Configuration

### Environment Variables

- `LOG_LEVEL` - Logging level (default: INFO)
- `OUTPUT_DIR` - Output directory for processed images (default: processed_images)
- `CACHE_DIR` - Cache directory (default: cache)

### Model Selection Guide

| Model              | Best For               | Speed     | Quality   |
| ------------------ | ---------------------- | --------- | --------- |
| `birefnet-general` | General purpose        | Fast      | High      |
| `u2net`            | Universal use          | Medium    | Very High |
| `u2netp`           | Lightweight processing | Very Fast | Good      |
| `u2net_human_seg`  | Human portraits        | Fast      | Excellent |
| `u2net_cloth_seg`  | Clothing items         | Fast      | Excellent |

## 🚀 Performance Optimization

### Caching

- Automatic caching of processed images
- Cache key based on image URL and model
- Significant speed improvement for repeated requests

### Quality Enhancement

- Automatic image preprocessing
- Contrast and sharpness enhancement
- RGB mode conversion for consistency

### Hardware Acceleration

- Automatic GPU detection (CUDA/CoreML)
- Fallback to CPU processing
- Optimized for both development and production

## 📊 Monitoring

### Logging

- Comprehensive logging throughout the application
- Performance metrics and timing information
- Error tracking and debugging information

### Health Checks

- Service health monitoring
- Model availability checking
- Cache statistics

## 🔒 Error Handling

### Common Error Responses

- `400` - Invalid request (bad image URL, unsupported model)
- `500` - Internal server error
- `503` - Service unavailable

### Error Response Format

```json
{
  "detail": "Error description"
}
```

## 🏗️ Architecture

### Service Layer

- `BackgroundRemovalService` - Core processing logic
- Multiple model support with session management
- Caching and optimization features

### API Layer

- FastAPI with automatic OpenAPI documentation
- Request/response validation with Pydantic
- Comprehensive error handling

### File Management

- Automatic output directory creation
- Unique filename generation
- PNG format with transparency support

## 🚀 Deployment

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Recommended)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Performance Metrics

### Processing Times (CPU)

- Small images (400x400): ~2-3 seconds
- Medium images (800x600): ~4-6 seconds
- Large images (1200x800): ~8-12 seconds

### Processing Times (GPU)

- Small images (400x400): ~0.5-1 second
- Medium images (800x600): ~1-2 seconds
- Large images (1200x800): ~2-4 seconds

### Cache Performance

- Cached requests: ~0.1-0.3 seconds
- 90%+ speed improvement for repeated images

## 🔧 Troubleshooting

### Common Issues

#### LZMA Module Error (macOS)

```bash
# Reinstall Python with proper lzma support
brew install openssl readline sqlite3 xz zlib
pyenv uninstall 3.10.0
pyenv install 3.10.0
```

#### GPU Not Detected

- Ensure CUDA is installed (Linux/Windows)
- Check ONNX Runtime GPU support
- Verify GPU drivers are up to date

#### Memory Issues

- Reduce image size for processing
- Clear cache regularly
- Monitor system memory usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:

- Check the troubleshooting section
- Review the API documentation at `/docs`
- Open an issue on GitHub
