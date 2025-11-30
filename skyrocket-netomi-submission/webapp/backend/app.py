import os
import sys
import json
import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pathlib import Path
import asyncio
from typing import Optional
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from skyrocket.data.prepare_data import prepare_data
from pdf_generator import generate_pdf_report
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="SkyRocket Analytics API",
    description="AI-Powered Customer Service Analytics Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
RESULTS_FOLDER = Path(__file__).parent / 'results'
DATA_FOLDER = Path(__file__).parent.parent.parent / 'data'
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}
MAX_FILE_SIZE = 50 * 1024 * 1024

UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)
DATA_FOLDER.mkdir(exist_ok=True)

analysis_state = {
    'status': 'idle',
    'progress': 0,
    'current_step': '',
    'results': None,
    'error': None
}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_types(obj):
    if isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(i) for i in obj]
    elif hasattr(obj, 'item'):
        return obj.item()
    elif pd.isna(obj):
        return None
    else:
        return obj

def run_analysis_sync(file_path: str, file_type: str):
    global analysis_state
    
    try:
        analysis_state['status'] = 'processing'
        analysis_state['progress'] = 0
        analysis_state['current_step'] = 'Preparing data...'
        
        print(f"\n{'='*80}")
        print("STEP 1: DATA PREPARATION")
        print(f"{'='*80}")
        
        queries_df, responses_df = prepare_data(file_path, output_dir=str(DATA_FOLDER))
        
        analysis_state['progress'] = 15
        analysis_state['current_step'] = 'Data preparation complete. Loading prepared data...'
        
        queries_csv = DATA_FOLDER / 'queries.csv'
        responses_csv = DATA_FOLDER / 'genai_responses.csv'
        
        if not queries_csv.exists() or not responses_csv.exists():
            raise FileNotFoundError("Prepared CSV files not found after data preparation")
        
        queries_df = pd.read_csv(queries_csv)
        responses_df = pd.read_csv(responses_csv)
        
        queries = queries_df['Queries'].dropna().tolist()
        
        analysis_state['progress'] = 20
        analysis_state['current_step'] = 'Running topic discovery...'
        
        print(f"\n{'='*80}")
        print("STEP 2: TOPIC DISCOVERY")
        print(f"{'='*80}")
        
        from skyrocket.core import topic_discovery
        topic_discovery.main()
        
        topic_results_file = DATA_FOLDER / 'topic_discovery_results.json'
        if topic_results_file.exists():
            with open(topic_results_file, 'r') as f:
                topic_results = json.load(f)
        else:
            topic_results = {'error': 'No topic discovery results found'}
        
        topic_results = convert_types(topic_results)
        
        analysis_state['progress'] = 40
        analysis_state['current_step'] = 'Extracting entities from GenAI responses...'
        
        print(f"\n{'='*80}")
        print("STEP 3: ENTITY EXTRACTION")
        print(f"{'='*80}")
        
        from skyrocket.core import entity_extractor
        entity_extractor.main()
        
        import glob
        entity_result_files = glob.glob(str(DATA_FOLDER / 'entity_extraction_results_*.json'))
        if entity_result_files:
            latest_entity_file = max(entity_result_files, key=os.path.getctime)
            with open(latest_entity_file, 'r') as f:
                entity_results = json.load(f)
        else:
            entity_results = {'error': 'No entity extraction results found'}
        
        entity_results = convert_types(entity_results)
        
        analysis_state['progress'] = 70
        
        print(f"\n{'='*80}")
        print("STEP 4: LLM JUDGE EVALUATION")
        print(f"{'='*80}")
        
        analysis_state['current_step'] = 'Evaluating responses with LLM Judge...'
        
        from skyrocket.core import llm_judge
        llm_judge.main()
        
        llm_judge_result_files = glob.glob(str(DATA_FOLDER / 'llm_judge_results_*.json'))
        if llm_judge_result_files:
            latest_judge_file = max(llm_judge_result_files, key=os.path.getctime)
            with open(latest_judge_file, 'r') as f:
                evaluation_results = json.load(f)
        else:
            evaluation_results = None
        
        evaluation_results = convert_types(evaluation_results) if evaluation_results else None
        
        analysis_state['progress'] = 90
        analysis_state['current_step'] = 'Finalizing results...'
        
        results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'data_summary': {
                'total_queries': len(queries),
                'unique_queries': queries_df['Queries'].nunique(),
                'total_responses': len(responses_df)
            },
            'topics': topic_results,
            'entities': entity_results,
            'evaluation': evaluation_results
        }
        
        results_file = RESULTS_FOLDER / 'latest_analysis.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        analysis_state['status'] = 'completed'
        analysis_state['progress'] = 100
        analysis_state['current_step'] = 'Analysis complete!'
        analysis_state['results'] = results
        
        print(f"\n{'='*80}")
        print("COMPLETE PIPELINE FINISHED SUCCESSFULLY")
        print(f"{'='*80}\n")
        
    except Exception as e:
        analysis_state['status'] = 'error'
        analysis_state['error'] = str(e)
        print(f"Error in analysis pipeline: {e}")
        import traceback
        traceback.print_exc()

async def run_analysis_pipeline(file_path: str, file_type: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_analysis_sync, file_path, file_type)

@app.get("/")
async def root():
    return {
        "message": "SkyRocket Analytics API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "SkyRocket Analytics API is running"
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    global analysis_state
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload .xlsx or .csv"
        )
    
    contents = await file.read()
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 50MB"
        )
    
    file_path = UPLOAD_FOLDER / file.filename
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    file_type = file.filename.rsplit('.', 1)[1].lower()
    
    analysis_state = {
        'status': 'processing',
        'progress': 0,
        'current_step': 'Starting analysis...',
        'results': None,
        'error': None
    }
    
    asyncio.create_task(run_analysis_pipeline(str(file_path), file_type))
    
    return {
        "message": "File uploaded successfully. Analysis started.",
        "filename": file.filename
    }

@app.get("/api/status")
async def get_status():
    return analysis_state

@app.get("/api/results")
async def get_results():
    if analysis_state['status'] == 'completed' and analysis_state['results']:
        return analysis_state['results']
    elif analysis_state['status'] == 'error':
        raise HTTPException(
            status_code=500,
            detail=analysis_state['error']
        )
    else:
        return JSONResponse(
            status_code=202,
            content={"message": "Analysis not yet completed"}
        )

@app.get("/api/results/download")
async def download_results():
    if analysis_state['status'] != 'completed' or not analysis_state['results']:
        raise HTTPException(
            status_code=404,
            detail="No results available"
        )
    
    pdf_buffer = generate_pdf_report(analysis_state['results'])
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=skyrocket-analysis-report.pdf"}
    )

@app.on_event("startup")
async def startup_event():
    print("=" * 80)
    print("SkyRocket Analytics Backend API")
    print("=" * 80)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Results folder: {RESULTS_FOLDER}")
    print("Server running on http://localhost:8000")
    print("API docs available at http://localhost:8000/docs")
    print("=" * 80)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
