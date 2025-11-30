# 🌐 SkyRocket Analytics - Professional Web Application

## Quick Start Guide

### Option 1: Automated Startup (Recommended)

Simply double-click `start_webapp.bat` in the project root. This will:
- Activate the virtual environment
- Start the Flask backend server
- Open the frontend in your default browser

### Option 2: Manual Startup

1. **Start Backend Server**
   ```bash
   # From project root
   cd skyrocket-netomi-submission
   
   # Activate virtual environment
   venv\Scripts\activate
   
   # Start FastAPI server with uvicorn
   cd webapp\backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Backend will run on `http://localhost:8000`
   
   **API Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

2. **Open Frontend**
   
   Simply open `webapp/frontend/index.html` in your browser
   
   Or use a local server:
   ```bash
   cd webapp\frontend
   python -m http.server 8080
   ```
   
   Then navigate to `http://localhost:8080`

## 📁 File Structure

```
webapp/
├── backend/
│   ├── app.py              # Flask API server
│   ├── uploads/            # Uploaded files (auto-created)
│   └── results/            # Analysis results (auto-created)
│
└── frontend/
    ├── index.html          # Main application
    ├── styles.css          # Professional styling
    └── app.js              # Application logic
```

## 🎯 How to Use

1. **Upload Your Data**
   - Click "Browse Files" or drag & drop your Excel file
   - Supported: `.xlsx` or `.csv` files
   - Expected format: SkyRocket Data_GenAI.xlsx structure

2. **Watch the Analysis**
   - Real-time progress bar shows current step
   - Complete analysis takes 10-20 minutes depending on data size

3. **Explore Results**
   - Interactive dashboard with charts and tables
   - Download results as JSON
   - Start new analysis anytime

## 🔧 Troubleshooting

### Backend won't start
- Ensure virtual environment is activated
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify GROQ_API_KEY is set in `.env` file
- Make sure port 8000 is not in use

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Try opening frontend via local server instead of file://
- Visit `http://localhost:8000/docs` to verify API is running

### Analysis fails
- Check that uploaded file has correct structure
- Verify GROQ_API_KEY is valid
- Check backend console for error messages

## 📊 Features

- **Modern UI/UX** - Professional dark theme with smooth animations
- **Real-time Progress** - Live updates during analysis
- **Interactive Charts** - Powered by Chart.js
- **Comprehensive Analytics**:
  - Topic Discovery (10 semantic clusters)
  - Entity Extraction (ORDER_ID, TRACKING_NUMBER, etc.)
  - Response Evaluation (LLM-as-a-Judge)
  - Quality Metrics & Insights

## 🚀 Next Steps

After exploring the dashboard:
- Download the JSON results for further analysis
- Upload different datasets to compare
- Integrate the API into your existing systems

For detailed documentation, see the main [README.md](README.md)

---

**Made with ❤️ for intelligent customer service automation**
