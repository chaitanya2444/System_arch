# Figma to Architecture Report - Implementation Guide

## Overview

This system analyzes Figma designs using AI (Google Gemini) and generates comprehensive PDF reports containing:
- **Route Mapping**: Suggested routes for each page/screen
- **Feature Specifications**: Detailed feature requirements with user stories
- **Implementation Guides**: Step-by-step developer instructions
- **User Flow Analysis**: How users navigate through the application
- **Technical Stack Recommendations**: Suggested technologies based on design
- **Design Assets**: Components, styles, fonts, and typography

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   Backend    │─────▶│  Figma API  │
│  (HTML/JS)  │      │  (FastAPI)   │      │             │
└─────────────┘      └──────┬───────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Groq API  │
                     │ (AI Analysis)│
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  PDF Report  │
                     │  (ReportLab) │
                     └──────────────┘
```

## Features

### 🎯 Core Features

1. **Figma Integration**
   - Connects to Figma REST API
   - Fetches complete design file data
   - Extracts components, styles, fonts, and text elements

2. **AI-Powered Analysis** (with Gemini API)
   - Analyzes design structure and purpose
   - Identifies application type and target users
   - Maps pages to suggested routes
   - Generates feature specifications
   - Creates user flow descriptions
   - Provides implementation guides with phases and steps
   - Recommends technical stack

3. **Comprehensive PDF Reports**
   - Professional layout with table of contents
   - Project overview and analysis
   - Page-by-page route mapping
   - Detailed feature specifications
   - User flow diagrams and descriptions
   - Phase-based implementation guide
   - Technical stack recommendations
   - Design assets documentation

4. **Flexible Operation Modes**
   - **Enhanced Mode**: With Gemini API key (full AI analysis)
   - **Basic Mode**: Without Gemini API key (design assets only)

## Installation

### Prerequisites

- Python 3.8+
- Node.js (optional, for frontend development)
- Figma account with API access
- Google Gemini API key (optional, for AI features)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd /home/kaushal/Downloads/System_arch/backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Setup

The frontend is a static HTML/CSS/JavaScript application. No build process required.

## Configuration

### Getting API Keys

#### 1. Figma Access Token

1. Go to [Figma Account Settings](https://www.figma.com/settings)
2. Scroll to "Personal Access Tokens"
3. Click "Create a new personal access token"
4. Give it a name (e.g., "Architecture Agent")
5. Copy the token (starts with `figd_`)

**Important**:
- The token must have access to the specific Figma file
- Make sure the file is not private/restricted

#### 2. Google Gemini API Key (Optional but Recommended)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIzaSy`)

**Note**: Without Gemini API key, the system will generate basic reports without AI analysis.

## Running the Application

### Start Backend Server

```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

Verify it's running:
```bash
curl http://localhost:8000/api/health
```

### Start Frontend

**Option 1: Python HTTP Server**
```bash
cd frontend
python -m http.server 3000
```
Then open: `http://localhost:3000`

**Option 2: VS Code Live Server**
- Install "Live Server" extension
- Right-click `frontend/index.html`
- Select "Open with Live Server"

**Option 3: Direct File Access**
- Open `frontend/index.html` in your browser
- Some features may require a local server

## Usage

### Basic Workflow

1. **Prepare Your Figma File**
   - Open your Figma design
   - Click "Share" → Copy link
   - Format: `https://www.figma.com/file/{key}/...` or `https://www.figma.com/design/{key}/...`

2. **Open the Application**
   - Navigate to `http://localhost:3000` (or wherever your frontend is hosted)

3. **Fill in the Form**
   - **Figma Link**: Paste your Figma file URL
   - **Figma Access Token**: Enter your Figma token
   - **Gemini API Key** (Optional): Enter your Google Gemini API key for AI analysis
   - **Additional Report Data** (Optional): Add custom JSON metadata

4. **Generate PDF**
   - Click "Generate PDF"
   - Wait for processing (may take 30-60 seconds with AI analysis)
   - Download your report

### Example Request (API)

```bash
curl -X POST http://localhost:8000/api/generate-pdf \
  -H "Content-Type: application/json" \
  -d '{
    "figma_link": "https://www.figma.com/file/abc123/MyDesign",
    "figma_token": "figd_xxxxxxxxxxxxxxxxxxxxx",
    "gemini_api_key": "AIzaSyxxxxxxxxxxxxxxxxxxxxx",
    "report_data": {
      "project_name": "E-Commerce Platform",
      "version": "1.0.0",
      "developer": "Your Name"
    }
  }'
```

## Report Contents

### With Gemini API Key (Enhanced Report)

1. **Table of Contents**
   - Quick navigation to all sections

2. **Project Overview**
   - AI-generated description
   - Application type identification
   - Target user analysis
   - Key features list

3. **Design Analysis**
   - Components inventory
   - Style system documentation
   - Typography analysis

4. **Pages & Route Mapping**
   - Each page/screen analyzed
   - Suggested route paths (e.g., `/home`, `/dashboard`)
   - Page purpose and functionality
   - User interactions
   - Connected pages
   - Implementation priority
   - Developer notes

5. **Feature Specifications**
   - Feature descriptions
   - User stories
   - Technical requirements
   - Required API endpoints
   - Database models needed
   - Acceptance criteria

6. **User Flow**
   - Navigation patterns
   - User journey mapping
   - Decision points
   - Flow descriptions

7. **Implementation Guide**
   - Phase-based breakdown
   - Step-by-step instructions
   - Commands and code examples
   - Deliverables for each phase
   - Routing structure recommendations
   - State management suggestions
   - Testing strategy
   - Deployment considerations

8. **Technical Stack Recommendations**
   - Suggested frontend frameworks
   - Backend technologies
   - Database recommendations
   - Additional tools and libraries

### Without Gemini API Key (Basic Report)

1. Components list
2. Styles inventory
3. Fonts used
4. Text elements
5. Project structure hierarchy
6. Basic implementation steps

## API Endpoints

### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "System Architecture Agent API",
  "version": "1.0.0"
}
```

### Generate PDF
```
POST /api/generate-pdf
```

**Request Body:**
```json
{
  "figma_link": "string (required)",
  "figma_token": "string (required)",
  "gemini_api_key": "string (optional)",
  "report_data": "object (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Enhanced PDF with AI analysis generated successfully",
  "pdf_url": "/api/download/architecture_report_1234567890.pdf",
  "pdf_filename": "architecture_report_1234567890.pdf"
}
```

### Download PDF
```
GET /api/download/{filename}
```

Returns the PDF file for download.

## Troubleshooting

### Backend Issues

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "Port 8000 already in use"**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9
# Or use a different port
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Frontend Issues

**Error: "Cannot connect to backend"**
- Verify backend is running: `curl http://localhost:8000/api/health`
- Check CORS settings in `backend/main.py`
- Update `API_BASE_URL` in `frontend/script.js` if needed

### Figma Integration Issues

**Error: "Invalid Figma token"**
- Verify token hasn't expired
- Check token has access to the file
- Ensure file isn't private/restricted

**Error: "Invalid Figma link format"**
- Use format: `https://www.figma.com/file/{key}/...`
- Or: `https://www.figma.com/design/{key}/...`

### Gemini API Issues

**Error: "Failed to analyze design with Gemini AI"**
- Verify API key is correct
- Check you have quota remaining
- API key must be from Google AI Studio

**Slow processing**
- AI analysis takes 30-60 seconds for complex designs
- This is normal - Gemini analyzes each page individually

## Best Practices

### For Best Results

1. **Organize Your Figma File**
   - Use clear, descriptive names for pages/frames
   - Group related components
   - Use consistent naming conventions

2. **Page Naming**
   - Name pages by function: "Login", "Dashboard", "User Profile"
   - Avoid generic names like "Page 1", "Frame 2"

3. **Component Organization**
   - Create reusable components
   - Document component variants
   - Use descriptive component names

4. **Design Completeness**
   - Include all user flows
   - Show interaction states (hover, active, disabled)
   - Document navigation paths

### Security

1. **Never commit API keys** to version control
2. **Use environment variables** for production deployments
3. **Implement rate limiting** for production APIs
4. **Rotate access tokens** regularly

## Advanced Configuration

### Custom PDF Styling

Edit `backend/services/pdf_service.py` to customize:
- Colors and fonts
- Layout and spacing
- Section order
- Content formatting

### Modify AI Prompts

Edit `backend/services/gemini_service.py` to:
- Adjust analysis depth
- Change prompt templates
- Add new analysis sections
- Customize output format

### Environment Variables

Create a `.env` file for production:
```env
FIGMA_TOKEN=your_default_token
GEMINI_API_KEY=your_gemini_key
API_HOST=0.0.0.0
API_PORT=8000
```

## File Structure

```
System_arch/
├── backend/
│   ├── main.py                      # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── figma_service.py         # Figma API integration
│   │   ├── gemini_service.py        # Gemini AI analysis
│   │   └── pdf_service.py           # PDF generation
│   └── generated_pdfs/              # Output directory
├── frontend/
│   ├── index.html                   # Main UI
│   ├── styles.css                   # Styling
│   └── script.js                    # Frontend logic
├── README.md                        # Project overview
└── IMPLEMENTATION_GUIDE.md          # This file
```

## Contributing

To extend this system:

1. **Add new analysis features**: Extend `GeminiService` methods
2. **Enhance PDF layout**: Modify `PDFService.generate_enhanced_pdf()`
3. **Add new endpoints**: Update `main.py`
4. **Improve UI**: Edit `frontend/` files

## License

This project is provided as-is for educational and personal use.

## Support

For issues and questions:
1. Check this documentation
2. Review error messages in backend console
3. Check browser console for frontend errors
4. Verify API keys and permissions

---

**Built with:**
- FastAPI (Backend)
- Google Gemini AI (Analysis)
- Figma REST API (Design Data)
- ReportLab (PDF Generation)
- Vanilla JS (Frontend)
