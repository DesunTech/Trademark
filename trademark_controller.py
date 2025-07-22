from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
from trademark_dal import TrademarkExtractor
from trademark_comparison import TrademarkComparator
from csv_manager import TrademarkCSVManager
import tempfile
import re
import base64

from dotenv import load_dotenv
load_dotenv()

# For demo purposes, we'll use a hardcoded API key or environment variable
# In production, you should get this from a secure configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your-groq-api-key-here")

trademark_router = APIRouter()
trademark_extractor = TrademarkExtractor(groq_api_key=GROQ_API_KEY)
trademark_comparator = TrademarkComparator()
csv_manager = TrademarkCSVManager()

"""
Trademark extraction endpoints for extracting trademark data from text, PDF, or images.
"""

@trademark_router.post("/extract/trademark/text")
async def extract_trademark_from_text(request: dict):
    """
    Extract trademark data from provided text.
    Expected input: {"text": "trademark document text here"}
    """
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        doc_type = trademark_extractor.classify_document(text)
        print(f"Document classified as: {doc_type}")
        
        trademark_data = trademark_extractor.extract_trademark_data_from_text(text)
        
        return {
            "document_type": doc_type,
            "trademark_data": trademark_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/extract/trademark/pdf")
async def extract_trademark_from_pdf(file: UploadFile = File(...)):
    """
    Extract trademark data from an uploaded PDF file.
    Returns an array of trademark data for each page.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_bytes = await file.read()
        
        # Extract trademark data from all pages
        trademarks_data = trademark_extractor.extract_from_pdf_bytes(file_bytes)
        
        return {
            "filename": file.filename,
            "total_pages": len(trademarks_data),
            "trademarks": trademarks_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/extract/trademark/image")
async def extract_trademark_from_image(file: UploadFile = File(...)):
    """
    Extract trademark data from an uploaded image file (JPG, PNG, etc.).
    """
    try:
        # Validate file type
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content and convert to base64
        file_bytes = await file.read()
        base64_image = base64.b64encode(file_bytes).decode("utf-8")
        
        # Extract text from image
        extracted_text = trademark_extractor.extract_from_base64_image(base64_image)
        
        if not extracted_text or not extracted_text.get("text"):
            raise HTTPException(status_code=400, detail="Could not extract text from image")
        
        # Extract structured trademark data
        trademark_data = trademark_extractor.extract_trademark_data_from_text(extracted_text["text"])
        
        return {
            "filename": file.filename,
            "extracted_text": extracted_text["text"],
            "trademark_data": trademark_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/extract/trademark/base64")
async def extract_trademark_from_base64(request: dict):
    """
    Extract trademark data from a base64 encoded image.
    Expected input: {"image": "base64-encoded-image-data"}
    """
    try:
        base64_image = request.get("image", "")
        if not base64_image:
            raise HTTPException(status_code=400, detail="Base64 image data is required")
        
        # Remove data URL prefix if present
        if base64_image.startswith('data:'):
            base64_image = base64_image.split(',')[1]
        
        # Extract text from image
        extracted_text = trademark_extractor.extract_from_base64_image(base64_image)
        
        if not extracted_text or not extracted_text.get("text"):
            raise HTTPException(status_code=400, detail="Could not extract text from image")
        
        # Extract structured trademark data
        trademark_data = trademark_extractor.extract_trademark_data_from_text(extracted_text["text"])
        
        return {
            "extracted_text": extracted_text["text"],
            "trademark_data": trademark_data,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/extract/trademark/pdf_with_comparison")
async def extract_and_compare_trademark_from_pdf(file: UploadFile = File(...), similarity_threshold: float = 50.0):
    """
    Extract trademark data from PDF and compare with existing CSV database.
    Returns extraction results plus similarity analysis.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Load existing trademarks from CSV
        trademark_comparator.load_existing_trademarks_from_csv(csv_manager.csv_file_path)
        
        # Read file content
        file_bytes = await file.read()
        
        # Extract trademark data from all pages
        trademarks_data = trademark_extractor.extract_from_pdf_bytes(file_bytes)
        
        # Compare each extracted trademark with existing database
        comparison_results = []
        for trademark in trademarks_data:
            comparison_report = trademark_comparator.generate_comparison_report(trademark, similarity_threshold)
            comparison_results.append(comparison_report)
        
        return {
            "filename": file.filename,
            "total_pages": len(trademarks_data),
            "extracted_trademarks": trademarks_data,
            "comparison_results": comparison_results,
            "similarity_threshold": similarity_threshold,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/compare/trademark")
async def compare_trademark_with_database(request: dict):
    """
    Compare a single trademark with existing database.
    Expected input: {"trademark": {...}, "similarity_threshold": 50.0}
    """
    try:
        trademark_data = request.get("trademark", {})
        similarity_threshold = request.get("similarity_threshold", 50.0)
        
        if not trademark_data:
            raise HTTPException(status_code=400, detail="Trademark data is required")
        
        # Load existing trademarks from CSV
        trademark_comparator.load_existing_trademarks_from_csv(csv_manager.csv_file_path)
        
        # Generate comparison report
        comparison_report = trademark_comparator.generate_comparison_report(trademark_data, similarity_threshold)
        
        return {
            "comparison_report": comparison_report,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/csv/upload")
async def upload_csv_database(file: UploadFile = File(...)):
    """
    Upload a CSV file with existing trademark data for comparison.
    Expected CSV columns: Client / Applicant, Application No., Trademark, Logo, Class, Status, Validity
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")
        
        # Read file content
        file_content = await file.read()
        
        # Save uploaded CSV as the main database
        with open(csv_manager.csv_file_path, 'wb') as f:
            f.write(file_content)
        
        # Verify the CSV structure and get stats
        stats = csv_manager.get_csv_stats()
        
        # Load into comparator for immediate use
        trademark_comparator.load_existing_trademarks_from_csv(csv_manager.csv_file_path)
        
        return {
            "message": f"CSV uploaded successfully as {csv_manager.csv_file_path}",
            "filename": file.filename,
            "csv_stats": stats,
            "expected_columns": csv_manager.fieldnames,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.get("/csv/stats")
async def get_csv_statistics():
    """
    Get statistics about the existing trademark database.
    """
    try:
        stats = csv_manager.get_csv_stats()
        return {
            "csv_file": csv_manager.csv_file_path,
            "statistics": stats,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.post("/csv/add_trademark")
async def add_trademark_to_csv(request: dict):
    """
    Add a new trademark to the CSV database.
    Expected input: {"trademark": {...}}
    """
    try:
        trademark_data = request.get("trademark", {})
        
        if not trademark_data:
            raise HTTPException(status_code=400, detail="Trademark data is required")
        
        csv_manager.append_trademark_to_csv(trademark_data)
        stats = csv_manager.get_csv_stats()
        
        return {
            "message": "Trademark added to CSV database",
            "updated_stats": stats,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@trademark_router.get("/trademark/health")
async def health_check():
    """
    Health check endpoint to verify the trademark extraction service is running.
    """
    return {
        "status": "healthy",
        "service": "trademark_extraction_and_comparison",
        "version": "1.0.0",
        "csv_file": csv_manager.csv_file_path
    } 