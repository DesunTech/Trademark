#!/usr/bin/env python3
"""
Main FastAPI application for trademark data extraction
This demonstrates how to integrate the trademark extraction system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from trademark_controller import trademark_router
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="Trademark Data Extraction API",
    description="API for extracting trademark data from PDF files and images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the trademark router
app.include_router(trademark_router, prefix="/api/v1", tags=["trademark"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Trademark Data Extraction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/trademark/health"
    }

@app.get("/health")
async def health_check():
    """General health check endpoint"""
    return {
        "status": "healthy",
        "message": "Trademark Data Extraction API is running"
    }

if __name__ == "__main__":
    # Run the server
    print("🚀 Starting Trademark Data Extraction API Server...")
    print("📄 API Documentation will be available at: http://localhost:8000/docs")
    print("🔗 Health check: http://localhost:8000/health")
    print("🏷️  Trademark health check: http://localhost:8000/api/v1/trademark/health")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 