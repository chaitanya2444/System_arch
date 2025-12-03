# Quick Start Guide

## What This Does

This system analyzes your Figma designs using AI and generates a comprehensive PDF report for developers containing:

✅ **Route Mapping** - Suggested URL paths for each screen (e.g., `/home`, `/dashboard`)
✅ **Feature Specifications** - Detailed requirements with user stories and API endpoints
✅ **Implementation Guide** - Step-by-step developer instructions organized by phases
✅ **User Flow Analysis** - How users navigate through your app
✅ **Technical Stack Recommendations** - Suggested frameworks and technologies
✅ **Design Assets** - Components, styles, fonts documentation

## Prerequisites

- Python 3.8+ installed
- Figma account with design file
- Google Gemini API key (optional but highly recommended)

## Setup (5 minutes)

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Your API Keys

**Figma Access Token** (Required):
1. Visit: https://www.figma.com/settings
2. Create a new personal access token
3. Copy the token (starts with `figd_`)

**Google Gemini API Key** (Optional but Recommended):
1. Visit: https://aistudio.google.com/app/apikey
2. Create API key
3. Copy the key (starts with `AIzaSy`)

Without Gemini API key, you'll get a basic report without AI-powered analysis.

## Running the Application

### Start Backend

```bash
cd backend
python main.py
```

Backend runs on: http://localhost:8000

### Start Frontend

**Option 1 - Python Server:**
```bash
cd frontend
python -m http.server 3000
```
Then open: http://localhost:3000

**Option 2 - Direct:**
Just open `frontend/index.html` in your browser

## Usage

1. **Open the Application**
   - Go to http://localhost:3000

2. **Fill in the Form:**
   - **Figma Link**: Paste your design URL
   - **Figma Token**: Enter your access token
   - **Gemini API Key**: Enter your Google AI key (for enhanced analysis)
   - **Additional Data**: (Optional) Add custom JSON metadata

3. **Generate PDF**
   - Click "Generate PDF"
   - Wait 30-60 seconds (AI analysis takes time)
   - Download your comprehensive report!

## Example Figma Links

Valid formats:
- `https://www.figma.com/file/abc123/MyDesign`
- `https://www.figma.com/design/abc123/MyDesign`

## What You'll Get

### With Gemini API Key (Enhanced):
- ✅ Complete route mapping for all pages
- ✅ Detailed feature specifications
- ✅ User stories and requirements
- ✅ API endpoints needed
- ✅ Phase-by-phase implementation guide
- ✅ User flow analysis
- ✅ Technical stack recommendations
- ✅ Design assets documentation

### Without Gemini API Key (Basic):
- ✅ Components list
- ✅ Styles inventory
- ✅ Fonts used
- ✅ Basic structure
- ⚠️ No AI-powered analysis

## Troubleshooting

**"Cannot connect to backend"**
→ Make sure backend is running on port 8000

**"Invalid Figma token"**
→ Check token hasn't expired and has access to your file

**"Module not found"**
→ Run: `pip install -r requirements.txt` in backend directory

**Slow PDF generation**
→ This is normal! AI analysis takes 30-60 seconds

## File Structure

```
System_arch/
├── backend/
│   ├── main.py                  # API server
│   ├── requirements.txt         # Dependencies
│   ├── models/schemas.py        # Data models
│   └── services/
│       ├── figma_service.py     # Figma integration
│       ├── gemini_service.py    # AI analysis
│       └── pdf_service.py       # PDF generation
├── frontend/
│   ├── index.html              # UI
│   ├── styles.css              # Styling
│   └── script.js               # Logic
└── generated_pdfs/             # Output folder
```

## Next Steps

1. **Test with a Simple Design**: Start with a small Figma file (2-3 pages)
2. **Review the PDF**: Check the route mappings and feature specs
3. **Use for Development**: Hand the PDF to your dev team as a blueprint
4. **Iterate**: Refine your Figma designs based on the analysis

## Tips for Best Results

1. **Name Your Pages Well**: Use descriptive names like "Login Page", "Dashboard", not "Frame 1"
2. **Organize Components**: Group related elements together
3. **Include All Screens**: Make sure all user flows are represented
4. **Use Consistent Naming**: Follow a naming convention throughout

## Support

- Full documentation: See `IMPLEMENTATION_GUIDE.md`
- Check backend console for detailed error messages
- Ensure your Figma file is not private/restricted

---

**That's it!** You're ready to turn your Figma designs into actionable development reports! 🚀
