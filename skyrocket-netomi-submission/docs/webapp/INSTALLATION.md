# 🚀 Installation & Testing Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.9+ installed
- ✅ Virtual environment created (`venv` folder exists)
- ✅ GROQ_API_KEY in `.env` file
- ✅ Internet connection for API calls

## Step-by-Step Installation

### 1. Install FastAPI Dependencies

```bash
# Activate virtual environment
cd c:\Users\pc\OneDrive\Desktop\netomi\skyrocket-netomi-submission
venv\Scripts\activate

# Install new dependencies
pip install fastapi uvicorn[standard] python-multipart

# Verify installation
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed')"
python -c "import uvicorn; print(f'Uvicorn installed')"
```

### 2. Verify Existing Dependencies

```bash
# Check if all required packages are installed
pip list | findstr "groq pandas spacy sentence-transformers"

# If any are missing, install all:
pip install -r requirements.txt
```

### 3. Test Backend Server

```bash
# Navigate to backend
cd webapp\backend

# Start server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Test in browser:**
- Visit: `http://localhost:8000` → Should show JSON response
- Visit: `http://localhost:8000/docs` → Should show Swagger UI
- Visit: `http://localhost:8000/api/health` → Should show health status

### 4. Test Frontend

```bash
# Open in new terminal
cd c:\Users\pc\OneDrive\Desktop\netomi\skyrocket-netomi-submission\webapp\frontend

# Option 1: Direct file open
start index.html

# Option 2: Local server (recommended)
python -m http.server 8080
# Then visit: http://localhost:8080
```

## Quick Test Workflow

### Test 1: Health Check
```bash
# In browser or PowerShell:
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "SkyRocket Analytics API is running"
}
```

### Test 2: File Upload (via Frontend)

1. Open frontend in browser
2. Click "Browse Files" or drag & drop
3. Select: `c:\Users\pc\OneDrive\Desktop\netomi\SkyRocket Data_GenAI.xlsx`
4. Watch progress bar update
5. Wait for analysis to complete (10-20 minutes)
6. Explore dashboard

### Test 3: API Documentation

1. Visit: `http://localhost:8000/docs`
2. Expand `/api/upload` endpoint
3. Click "Try it out"
4. Upload a test file
5. See real-time response

## Troubleshooting

### Issue: "Module not found: fastapi"
**Solution:**
```bash
venv\Scripts\activate
pip install fastapi uvicorn[standard] python-multipart
```

### Issue: "Port 8000 already in use"
**Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or use different port:
uvicorn app:app --reload --port 8001
```

### Issue: "GROQ_API_KEY not found"
**Solution:**
```bash
# Check .env file exists
cd c:\Users\pc\OneDrive\Desktop\netomi\skyrocket-netomi-submission
type .env

# Should contain:
# GROQ_API_KEY=gsk_...
```

### Issue: Frontend can't connect to backend
**Solution:**
1. Verify backend is running: `http://localhost:8000/api/health`
2. Check browser console for CORS errors
3. Ensure you're using `http://localhost:8080` not `file://`
4. Clear browser cache

### Issue: Analysis fails
**Solution:**
1. Check backend console for errors
2. Verify file format (should have 'Queries' sheet)
3. Check GROQ_API_KEY is valid
4. Reduce sample sizes in `backend/app.py` for testing

## Performance Testing

### Test with Sample Data

Create a small test CSV:
```csv
Queries
How do I track my order?
What is your return policy?
I need to cancel my order
Where is my package?
```

Save as `test_queries.csv` and upload to test quickly.

### Expected Processing Times

| Dataset Size | Topic Discovery | Entity Extraction | Evaluation | Total |
|--------------|----------------|-------------------|------------|-------|
| 100 queries  | ~1 min         | ~30 sec          | ~2 min     | ~4 min |
| 1000 queries | ~3 min         | ~1 min           | ~8 min     | ~12 min |
| 6500 queries | ~10 min        | ~3 min           | ~15 min    | ~28 min |

## Automated Startup Script

For convenience, use the provided batch script:

```bash
# Just double-click:
start_webapp.bat

# Or run from command line:
cd c:\Users\pc\OneDrive\Desktop\netomi\skyrocket-netomi-submission
start_webapp.bat
```

This will:
1. ✅ Check virtual environment
2. ✅ Activate venv
3. ✅ Start backend server
4. ✅ Open frontend in browser
5. ✅ Show all URLs

## Verification Checklist

Before considering installation complete, verify:

- [ ] Backend starts without errors
- [ ] Can access `http://localhost:8000/docs`
- [ ] Frontend loads in browser
- [ ] Can drag & drop files
- [ ] Health check returns success
- [ ] Upload triggers progress bar
- [ ] Dashboard displays after analysis
- [ ] Charts render correctly
- [ ] Can download results

## Next Steps After Installation

1. **Upload Real Data**: Use the SkyRocket Data_GenAI.xlsx file
2. **Explore API Docs**: Test endpoints at `/docs`
3. **Customize**: Edit `styles.css` for branding
4. **Integrate**: Use API in your own applications
5. **Deploy**: Follow production deployment guide in README

## Getting Help

If you encounter issues:

1. **Check Logs**: Backend console shows detailed errors
2. **Browser Console**: Frontend errors appear here (F12)
3. **API Docs**: Test endpoints at `http://localhost:8000/docs`
4. **Documentation**: See `webapp/README.md` for details

## Success Indicators

You'll know everything is working when:

✅ Backend shows: "Uvicorn running on http://0.0.0.0:8000"
✅ Frontend shows: Beautiful dark theme with upload zone
✅ `/docs` shows: Interactive Swagger UI
✅ Upload works: Progress bar appears and updates
✅ Dashboard loads: Charts and tables display data

---

**You're ready to transform customer service with AI! 🚀**
