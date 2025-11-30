# 🚀 SkyRocket Analytics - Professional Web Application

A stunning, professional web application for AI-powered customer service analytics. Upload your Excel data and get comprehensive insights with topic discovery, entity extraction, and automated response evaluation.

## ✨ Features

- **Modern Professional UI** - Beautiful dark theme with glassmorphism and smooth animations
- **Drag & Drop Upload** - Easy file upload with progress tracking
- **Real-time Analysis** - Live progress updates during processing
- **Interactive Dashboard** - Dynamic charts, KPIs, and data tables
- **Comprehensive Analytics**:
  - Topic Discovery (AI-powered clustering)
  - Entity Extraction (Hybrid spaCy + Groq)
  - Response Evaluation (LLM-as-a-Judge)
  - Quality Metrics & Insights

## 🏗️ Architecture

```
webapp/
├── backend/
│   ├── app.py              # Flask API server
│   ├── requirements.txt    # Python dependencies
│   ├── uploads/            # Uploaded files
│   └── results/            # Analysis results
│
└── frontend/
    ├── index.html          # Main HTML
    ├── styles.css          # Professional CSS
    └── app.js              # JavaScript logic
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Groq API key ([Get one here](https://console.groq.com/))
- Modern web browser

### Installation

1. **Set up environment variables**
   ```bash
   # In the project root, ensure .env file has:
   GROQ_API_KEY=your_groq_api_key_here
   ```

2. **Install dependencies** (if not already installed)
   ```bash
   # From the project root directory
   cd c:\Users\pc\OneDrive\Desktop\netomi\skyrocket-netomi-submission
   
   # Install all dependencies
   pip install -r requirements.txt
   
   # Download spaCy model (if not already downloaded)
   python -m spacy download en_core_web_sm
   ```

3. **Start the backend server**
   ```bash
   cd webapp/backend
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   
   Server will start on `http://localhost:8000`
   
   **Bonus:** FastAPI provides automatic interactive API docs at:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

4. **Open the frontend**
   
   Simply open `webapp/frontend/index.html` in your browser, or use a local server:
   
   ```bash
   cd webapp/frontend
   
   # Using Python
   python -m http.server 8080
   
   # Using Node.js
   npx serve
   ```
   
   Then navigate to `http://localhost:8080`

## 📖 Usage

1. **Upload Data**
   - Click "Browse Files" or drag & drop your Excel file (.xlsx or .csv)
   - Supported format: SkyRocket Data_GenAI.xlsx with 'Queries' and 'GenAI_responses' sheets

2. **Watch Analysis Progress**
   - Real-time progress bar shows current step
   - Analysis includes:
     - Topic Discovery (~5-10 min)
     - Entity Extraction (~2-3 min)
     - Response Evaluation (~8-10 min for 100 samples)

3. **Explore Dashboard**
   - View KPIs: Total queries, containment rate, topics, quality scores
   - Interactive charts: Topic distribution, quality metrics
   - Detailed tables: Browse discovered topics with examples
   - Entity insights: See extracted entities and patterns
   - Quality metrics: Response evaluation scores

4. **Download Results**
   - Click "Download Report" to get JSON results
   - Use "New Analysis" to upload another file

## 🎨 Design Features

### Visual Excellence
- **Dark Theme** - Professional dark mode with vibrant accents
- **Glassmorphism** - Modern frosted glass effects
- **Smooth Animations** - Micro-interactions for better UX
- **Gradient Accents** - Eye-catching color gradients
- **Responsive Design** - Works on all screen sizes

### User Experience
- **Drag & Drop** - Intuitive file upload
- **Real-time Updates** - Live progress tracking
- **Interactive Charts** - Powered by Chart.js
- **Toast Notifications** - Clear feedback messages
- **Search & Filter** - Easy data exploration

## 🔧 API Endpoints

### FastAPI Backend

The backend provides a RESTful API with automatic documentation:

- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `POST /api/upload` - Upload file and start analysis
- `GET /api/status` - Get analysis progress
- `GET /api/results` - Get analysis results
- `GET /api/results/download` - Download results as JSON

**Interactive API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📊 Analysis Pipeline

The backend runs a comprehensive analysis pipeline:

1. **Data Loading** - Extracts queries and responses from Excel
2. **Topic Discovery** - Uses embeddings + HDBSCAN + Groq LLM labeling
3. **Entity Extraction** - Hybrid spaCy NER + Groq structured extraction
4. **Response Evaluation** - LLM-as-a-Judge scoring on 6 dimensions
5. **Results Compilation** - Aggregates all insights into JSON

## 🎯 Key Metrics

The dashboard displays:

- **Total Queries** - Number of customer queries analyzed
- **Containment Rate** - Percentage of queries resolved without escalation
- **Topics Discovered** - Number of semantic topic clusters
- **Quality Score** - Average response quality (1-5 scale)
- **Hallucination Rate** - Percentage of responses with hallucinations
- **Escalation Rate** - Percentage requiring human intervention

## 🔐 Security

- File size limit: 50MB
- Allowed extensions: .xlsx, .csv
- CORS enabled for local development
- Secure file handling with Werkzeug

## 🚀 Production Deployment

### Backend (FastAPI)

Deploy to any Python hosting platform:

```bash
# Using Uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4

# Using Gunicorn with Uvicorn workers
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker
docker build -t skyrocket-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key skyrocket-backend
```

### Frontend

Deploy static files to:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront
- Any static hosting service

Update `API_BASE_URL` in `app.js` to your production backend URL.

## 🛠️ Customization

### Styling

Edit `styles.css` to customize:
- Color scheme (CSS variables in `:root`)
- Spacing and typography
- Animations and transitions

### Analysis Parameters

Edit `backend/app.py` to adjust:
- Sample sizes for faster/slower processing
- Topic discovery parameters
- Entity extraction settings

## 📝 Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## 🤝 Support

For issues or questions:
1. Check the backend server is running on port 5000
2. Ensure GROQ_API_KEY is set in .env
3. Check browser console for errors
4. Verify file format matches expected structure

## 📜 License

Part of the SkyRocket Netomi Submission project.

---

**Made with ❤️ using Flask, Chart.js, and modern web technologies**

🚀 **Transform customer service with AI-powered analytics!**
