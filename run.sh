#!/bin/bash
echo "🚀 Starting SparkIQ AI Image Enhancement API..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "👋 Hello Endpoint: http://localhost:8000/hello"
echo "🔍 Health Check: http://localhost:8000/health"
echo "=" * 50

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 