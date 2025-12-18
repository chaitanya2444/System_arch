# System Architecture Agent

A modern full-stack application that generates comprehensive PDF reports from Figma designs. Transform your Figma files into detailed system architecture documentation with just a few clicks.

## 🌟 Features

- **Figma Integration**: Seamlessly fetch design data from Figma using the official API
- **AI-Powered Analysis**: Enhanced PDF generation using Groq (Llama 3.3 70B) or Hugging Face APIs
- **Comprehensive PDFs**: Generate detailed architecture reports including:
  - Components and styles analysis
  - Font usage
  - Text elements
  - Project structure hierarchy
  - System architecture diagrams
  - Step-by-step implementation flow
- **Modern UI**: Beautiful, responsive web interface with glassmorphism design
- **Fast API**: RESTful backend built with FastAPI for high performance
- **Error Handling**: Robust validation and user-friendly error messages

## 🏗️ Architecture

```
System_arch/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── figma_service.py    # Figma API integration
│   │   └── pdf_service.py      # PDF generation
│   ├── generated_pdfs/         # Output directory
│   └── requirements.txt        # Python dependencies
└── frontend/
    ├── index.html              # Main HTML page
    ├── styles.css              # Styling
    └── script.js               # Frontend logic
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A Figma account with API access
- A modern web browser

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd c:\Users\rleel\OneDrive\Desktop\System_arch
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running the Application

#### 1. Start the Backend Server

```bash
cd backend
python main.py
```

The backend will start on `http://localhost:8000`

You can verify it's running by visiting: `http://localhost:8000/api/health`

#### 2. Start the Frontend

Open the frontend in your browser using one of these methods:

**Option A: Using Python's built-in server**
```bash
cd frontend
python -m http.server 3000
```
Then visit: `http://localhost:3000`

**Option B: Using Live Server (VS Code)**
- Install the "Live Server" extension in VS Code
- Right-click on `frontend/index.html`
- Select "Open with Live Server"

**Option C: Direct file access**
- Simply open `frontend/index.html` in your browser
- Note: Some features may require a local server

## 📖 Usage

1. **Get your Figma Access Token**:
   - Go to [Figma Account Settings](https://www.figma.com/settings)
   - Scroll to "Personal Access Tokens"
   - Click "Create a new personal access token"
   - Copy the token (it starts with `figd_`)

2. **Get your Figma File Link**:
   - Open your Figma file
   - Click "Share" in the top-right
   - Copy the link (format: `https://www.figma.com/file/...` or `https://www.figma.com/design/...`)

3. **Generate PDF**:
   - Open the frontend in your browser
   - Paste your Figma link
   - Enter your Figma access token

   - (Optional) Add additional JSON data for the report
   - Click "Generate PDF"
   - Wait for processing
   - Download your generated PDF!

## 🔧 API Documentation

### Endpoints

#### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "System Architecture Agent API",
  "version": "1.0.0"
}
```

#### `POST /api/generate-pdf`
Generate PDF from Figma design

**Request Body:**
```json
{
  "figma_link": "https://www.figma.com/file/abc123/MyDesign",
  "figma_token": "figd_xxxxxxxxxxxxxxxxxxxxx",

  "report_data": {
    "project_name": "My Project",
    "version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "PDF generated successfully",
  "pdf_url": "/api/download/project_architecture_1234567890.pdf",
  "pdf_filename": "project_architecture_1234567890.pdf"
}
```

#### `GET /api/download/{filename}`
Download generated PDF file

## 🎨 Customization

### Backend Configuration

Edit `backend/main.py` to customize:
- CORS settings
- Output directory
- API endpoints

### Frontend Styling

Edit `frontend/styles.css` to customize:
- Color scheme (CSS variables in `:root`)
- Animations
- Layout

## 🐛 Troubleshooting

### Backend won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify Python version: `python --version` (should be 3.8+)

### "Cannot connect to backend" error
- Ensure the backend server is running on `http://localhost:8000`
- Check the browser console for CORS errors
- Verify the API_BASE_URL in `script.js` matches your backend URL

### "Invalid Figma token" error
- Verify your token is correct and hasn't expired
- Ensure the token has access to the specific Figma file
- Check that the file is not private/restricted

### PDF generation fails
- Verify the Figma link format is correct
- Ensure you have read access to the Figma file
- Check backend logs for detailed error messages

## 🚀 Deploying to Render

### Prerequisites
- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Your code pushed to a GitHub repository

### Deployment Steps

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Create a new Web Service on Render**:
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `system-architecture-backend` (or your preferred name)
     - **Region**: Choose closest to your users
     - **Branch**: `main`
     - **Root Directory**: `backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `bash ../build.sh`
     - **Start Command**: `gunicorn main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120`

3. **Set Environment Variables** in Render Dashboard:
   - `ENVIRONMENT` = `production`
   - `GROQ_API_KEY` = `your_groq_api_key`
   - `HUGGINGFACE_API_KEY` = `your_huggingface_api_key`
   - `ALLOWED_ORIGINS` = `*` (or your specific frontend URL)

4. **Deploy**:
   - Click "Create Web Service"
   - Render will automatically build and deploy your application
   - Wait for deployment to complete (usually 2-5 minutes)

5. **Get your backend URL**:
   - After deployment, you'll get a URL like: `https://your-app-name.onrender.com`
   - Test it: `https://your-app-name.onrender.com/api/health`

### Update Frontend to Use Render Backend

After deploying, update your local frontend to connect to the Render backend:

1. Open `frontend/script.js`
2. Change line 2:
   ```javascript
   const API_BASE_URL = 'https://your-app-name.onrender.com';
   ```

3. Open `frontend/github-architecture.html`
4. Update line 434:
   ```javascript
   const response = await fetch('https://your-app-name.onrender.com/api/generate-github-architecture', {
   ```

5. Update line 469:
   ```html
   <a href="https://your-app-name.onrender.com${data.pdf_url}" class="download-btn" target="_blank">
   ```

### Important Notes

- **Free Tier Limitations**: 
  - Service spins down after 15 minutes of inactivity
  - First request after spin-down may take 30-60 seconds
  - Ephemeral storage (generated PDFs deleted on restart)
  
- **For Production**:
  - Upgrade to paid plan for persistent storage
  - Consider using cloud storage (S3, GCS) for PDFs
  - Update `ALLOWED_ORIGINS` to your specific frontend domain

- **Monitoring**:
  - View logs in Render Dashboard → Your Service → Logs
  - Check health: `https://your-app-name.onrender.com/api/health`

## 📝 License


This project is provided as-is for educational and personal use.

## 🤖 AI API Keys (For Testing)

The application uses pre-configured API keys stored in environment variables for AI analysis. No additional setup required for AI features.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- PDF generation powered by [ReportLab](https://www.reportlab.com/)
- Design data from [Figma API](https://www.figma.com/developers/api)
- AI analysis powered by [Groq](https://groq.com/) and [Hugging Face](https://huggingface.co/)
