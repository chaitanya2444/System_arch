from fastapi import FastAPI, HTTPException, status, Form, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import traceback
import requests
import logging
from typing import Optional
from dotenv import load_dotenv
import asyncio
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from models.schemas import PDFGenerationRequest, PDFGenerationResponse
from services.figma_service import FigmaService
from services.pdf_service import PDFService
from services.groq_service import GroqService
from services.huggingface_service import HuggingFaceService
from services.diagram_service import DiagramService

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="System Architecture Agent API",
    description="API for generating system architecture PDFs from Figma designs",
    version="1.0.0",
    docs_url="/docs" if os.getenv('ENVIRONMENT') == 'development' else None,
    redoc_url="/redoc" if os.getenv('ENVIRONMENT') == 'development' else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Configure CORS for production
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Initialize services
figma_service = FigmaService()
pdf_service = PDFService(output_dir="generated_pdfs")

# Create generated_pdfs directory if it doesn't exist
os.makedirs("generated_pdfs", exist_ok=True)

# Mount static files for PDF downloads
app.mount("/pdfs", StaticFiles(directory="generated_pdfs"), name="pdfs")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "System Architecture Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "generate_pdf": "/api/generate-pdf (POST)",
            "download": "/api/download/{filename} (GET)"
        }
    }


@app.get("/api/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Comprehensive health check endpoint"""
    try:
        # Check API keys
        groq_key = os.getenv('GROQ_API_KEY')
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        
        # Check file system
        pdf_dir_exists = os.path.exists("generated_pdfs")
        
        health_status = {
            "status": "healthy",
            "service": "System Architecture Agent API",
            "version": "1.0.0",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "checks": {
                "groq_api_configured": bool(groq_key),
                "huggingface_api_configured": bool(hf_key),
                "pdf_directory_exists": pdf_dir_exists,
                "disk_space_available": True  # Could add actual disk space check
            }
        }
        
        # Determine overall health
        all_checks_pass = all(health_status["checks"].values())
        if not all_checks_pass:
            health_status["status"] = "degraded"
            
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/api/generate-pdf", response_model=PDFGenerationResponse)
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute
async def generate_pdf(
    request: Request,
    figma_link: str = Form(..., min_length=10, max_length=500),
    figma_token: str = Form(..., min_length=10, max_length=200),
    report_file: Optional[UploadFile] = File(None)
):
    """Generate PDF from Figma design with comprehensive validation"""
    client_ip = get_remote_address(request)
    logger.info(f"PDF generation request from {client_ip} for Figma link: {figma_link[:50]}...")
    """
    Generate enhanced PDF from Figma design with AI analysis

    Args:
        request: PDFGenerationRequest containing figma_link, figma_token, groq_api_key, and optional report_data

    Returns:
        PDFGenerationResponse with success status and PDF download URL
    """
    try:
        # Validate and handle uploaded file
        report_data = None
        if report_file:
            # Security validations
            if report_file.size > 10 * 1024 * 1024:  # 10MB limit
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="File size exceeds 10MB limit"
                )
            
            allowed_types = {
                'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'text/plain', 'application/json', 'text/markdown', 'text/csv'
            }
            
            if report_file.content_type not in allowed_types:
                logger.warning(f"Unsupported file type: {report_file.content_type}")
            
            try:
                file_content = await report_file.read()
                report_data = {
                    "filename": report_file.filename[:100],  # Limit filename length
                    "content_type": report_file.content_type,
                    "size": len(file_content),
                    "content": file_content.decode('utf-8', errors='ignore')[:2000]  # First 2000 chars
                }
                logger.info(f"File processed: {report_file.filename} ({len(file_content)} bytes)")
            except Exception as e:
                logger.error(f"Error processing uploaded file: {str(e)}")
                report_data = {"filename": report_file.filename, "error": "Could not process file"}
        
        # Parse Figma key from link
        try:
            figma_key = figma_service.parse_figma_key(figma_link)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

        # Fetch Figma data
        try:
            figma_data = figma_service.fetch_figma_data(figma_key, figma_token)
        except requests.HTTPError as e:
            # Handle specific HTTP errors from Figma API
            error_str = str(e)
            if "429" in error_str or "Too Many Requests" in error_str:
                status_code = status.HTTP_429_TOO_MANY_REQUESTS
            elif "403" in error_str or "Forbidden" in error_str:
                status_code = status.HTTP_403_FORBIDDEN
            elif "401" in error_str or "Unauthorized" in error_str:
                status_code = status.HTTP_401_UNAUTHORIZED
            elif "404" in error_str or "Not Found" in error_str:
                status_code = status.HTTP_404_NOT_FOUND
            else:
                status_code = status.HTTP_401_UNAUTHORIZED
            
            logger.error(f"Figma API error: {error_str}")
            raise HTTPException(
                status_code=status_code,
                detail=error_str
            )
        except ValueError as e:
            # Handle validation errors (e.g., empty token)
            logger.error(f"Figma token validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            # Handle other unexpected errors
            logger.error(f"Unexpected error fetching Figma data: {traceback.format_exc()}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch Figma data. Please check your access token and file permissions. Error: {str(e)}"
            )

        # Extract data from Figma
        document = figma_data.get('document')
        if not document:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid Figma data structure: missing document"
            )

        fonts = figma_service.extract_fonts(document)
        texts = figma_service.extract_texts(document)
        components = figma_service.extract_components(figma_data.get('components', {}))
        styles = figma_service.extract_styles(figma_data.get('styles', {}))

        # Get API keys from environment variables
        groq_api_key = os.getenv('GROQ_API_KEY')
        huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')
        
        # AI analysis with environment API keys
        # Priority: Groq > Hugging Face
        ai_analysis = None
        ai_provider = None

        if groq_api_key:
            try:
                print("🤖 Initializing Groq analysis...")
                groq_service = GroqService(groq_api_key)

                print("📊 Analyzing design with Groq...")
                ai_analysis = groq_service.analyze_complete_design(figma_data)
                ai_provider = "Groq Llama 3.3 70B"

            except Exception as e:
                print(f"Groq analysis error: {str(e)}")
                # Try Hugging Face as fallback
                if huggingface_api_key:
                    try:
                        print("🤖 Falling back to Hugging Face analysis...")
                        huggingface_service = HuggingFaceService(huggingface_api_key)
                        ai_analysis = huggingface_service.analyze_complete_design(figma_data)
                        ai_provider = "Hugging Face DialoGPT"
                    except Exception as hf_e:
                        print(f"Hugging Face fallback error: {str(hf_e)}")

        elif huggingface_api_key:
            try:
                print("🤖 Initializing Hugging Face analysis...")
                huggingface_service = HuggingFaceService(huggingface_api_key)

                print("📊 Analyzing design with Hugging Face...")
                ai_analysis = huggingface_service.analyze_complete_design(figma_data)
                ai_provider = "Hugging Face DialoGPT"

            except Exception as e:
                print(f"Hugging Face analysis error: {str(e)}")

        if ai_analysis:
            # Generate ASCII architecture diagram
            print("🎨 Generating ASCII system architecture diagram...")
            if groq_api_key:
                llm_service = GroqService(groq_api_key)
            elif huggingface_api_key:
                llm_service = HuggingFaceService(huggingface_api_key)
            else:
                llm_service = None
                
            diagram_service = DiagramService(llm_service=llm_service)
            ascii_diagram = diagram_service.generate_architecture_diagram(
                figma_link=figma_link,
                figma_data=figma_data,
                ai_analysis=ai_analysis
            )
            
            # Generate enhanced PDF with AI insights and ASCII diagram
            print("📄 Generating enhanced PDF report...")
            pdf_path = pdf_service.generate_enhanced_pdf(
                figma_data=figma_data,
                gemini_analysis=ai_analysis,
                fonts=fonts,
                texts=texts,
                components=components,
                styles=styles,
                ascii_diagram=ascii_diagram
            )

            message = f"Enhanced PDF with AI analysis and ASCII architecture diagram ({ai_provider}) generated successfully"
        else:
            # Fallback to basic PDF generation without AI analysis
            print("📄 Generating basic PDF report (no AI analysis)...")
            project_structure = figma_service.get_project_structure(document)
            features = figma_service.get_features(document)

            pdf_path = pdf_service.generate_pdf(
                figma_data=figma_data,
                report_data=report_data,
                fonts=fonts,
                texts=texts,
                components=components,
                styles=styles,
                project_structure=project_structure,
                features=features
            )

            message = "Basic PDF generated successfully (AI analysis unavailable - check API keys in environment)"

        # Get filename
        pdf_filename = os.path.basename(pdf_path)
        pdf_url = f"/api/download/{pdf_filename}"

        return PDFGenerationResponse(
            success=True,
            message=message,
            pdf_url=pdf_url,
            pdf_filename=pdf_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        # Log the full traceback for debugging
        logger.error(f"Unexpected error in PDF generation: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@app.get("/api/download/{filename}")
async def download_pdf(filename: str):
    """
    Download generated PDF file
    
    Args:
        filename: Name of the PDF file to download
        
    Returns:
        FileResponse with PDF file
    """
    file_path = os.path.join("generated_pdfs", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename
    )


if __name__ == "__main__":
    import uvicorn
    from config import settings
    
    # Production-ready server configuration
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
        workers=1 if settings.debug else 4
    )
