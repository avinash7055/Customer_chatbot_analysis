# 🚀 Quick Start Guide - Netomi SkyRocket Submission

**Get running in 10 minutes!**

---

## ✅ Prerequisites

1. **Python 3.9+** installed
2. **Groq API Key** ([Get free key here](https://console.groq.com/))
3. **Excel file location:** `c:\Users\pc\OneDrive\Desktop\netomi\SkyRocket Data_GenAI.xlsx`

---

## 📋 Step-by-Step Setup

### Step 1: Install Dependencies (3 minutes)

```bash
# You're already creating the venv - let it finish, then:
cd c:\Users\pc\OneDrive\Desktop\netomi\skyrocket-netomi-submission

# Activate virtual environment
venv\Scripts\activate

# Install all packages
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 2: Configure Groq API Key (1 minute)

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your Groq API key
notepad .env
```

**In .env, replace:**
```
GROQ_API_KEY=your_groq_api_key_here
```

**With your actual key:**
```
GROQ_API_KEY=gsk_your_actual_groq_key_here
```

---

## 🎯 Running the Analysis

### Step 3: Prepare Data (1 minute)

```bash
cd src
python prepare_data.py
```

**✅ Expected Output:**
- `data/queries.csv` created (6,539 rows)
- `data/genai_responses.csv` created
- Statistical summary printed

**📁 Files Created:**
```
data/
├── queries.csv              ✅ Created automatically
└── genai_responses.csv      ✅ Created automatically
```

---

### Step 4: Run Topic Discovery (5-10 minutes)

```bash
python topic_discovery.py
```

**What happens:**
1. Generates embeddings for all queries
2. Clusters with HDBSCAN
3. Labels clusters with Groq LLM
4. Saves results to `data/topic_discovery_results.json`

**✅ Expected Output:**
```
10 Topics Discovered:
1. Order Cancellation (13.6%)
2. Tracking & Shipping (12.0%)
...
```

---

### Step 5: Extract Entities (2-3 minutes)

```bash
python entity_extractor.py
```

**What happens:**
- Extracts entities using spaCy + Groq
- Identifies ORDER_ID, TRACKING_NUMBER, etc.
- Saves to `data/entity_extraction_results.json`

---

### Step 6: Evaluate Responses (OPTIONAL - 8 mins for sample)

```bash
python llm_judge.py
```

**Note:** By default, processes **100 samples** (fast demo).

To run on **full dataset** (13 hours):
```python
# Edit llm_judge.py line ~270:
evaluated_df = judge.evaluate_dataset(
    responses_df,
    query_col='Query',
    response_col='response',
    sample_size=None  # <-- Change to None for full dataset
)
```

---

### Step 7: Launch Dashboard

```bash
cd ../dashboard
streamlit run app.py
```

**✅ Dashboard opens at:** http://localhost:8501

**Features:**
- Executive metrics (containment rate, quality, ROI)
- Topic distribution charts
- Quality analysis
- Entity insights
- Drift detection

---

## 🔧 Troubleshooting

### Issue: "Cannot find Excel file"

**Solution:**
```bash
# Verify Excel file location
dir c:\Users\pc\OneDrive\Desktop\netomi\SkyRocket*.xlsx

# If file is elsewhere, update path in prepare_data.py
```

### Issue: "GROQ_API_KEY not found"

**Solution:**
```bash
# Make sure .env file exists
dir .env

# Check it has your API key
type .env

# If not, copy from example
copy .env.example .env
notepad .env
```

### Issue: "Module not found"

**Solution:**
```bash
# Make sure venv is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: spaCy model not found

**Solution:**
```bash
python -m spacy download en_core_web_sm
```

---

## ⚡ Fast Demo Path (Skip LLM Judge)

If you want to see results quickly **without running the full LLM evaluation**:

```bash
# 1. Prepare data
cd src
python prepare_data.py

# 2. Topic discovery
python topic_discovery.py

# 3. Entity extraction
python entity_extractor.py

# 4. Skip llm_judge.py (takes long)

# 5. Launch dashboard (will show topic/entity data)
cd ../dashboard
streamlit run app.py
```

**Note:** Dashboard will show topic and entity insights. Response quality section requires running `llm_judge.py`.

---

## 📊 What Gets Created

After running all scripts:

```
data/
├── queries.csv                      ✅ 6,539 customer queries
├── genai_responses.csv              ✅ Query-response pairs
├── topic_discovery_results.json     ✅ 10 discovered topics
├── entity_extraction_results.json   ✅ Extracted entities
├── evaluated_responses.csv          ✅ Response quality scores (if llm_judge.py run)
└── evaluation_report.json           ✅ Summary metrics (if llm_judge.py run)
```

---

## 🎯 Minimal Working Demo (2 minutes)

**Fastest path to see something working:**

```bash
# 1. Activate venv
venv\Scripts\activate

# 2. Generate CSVs
cd src
python prepare_data.py

# 3. View the data
python
>>> import pandas as pd
>>> df = pd.read_csv("../data/queries.csv")
>>> print(df.head())
>>> exit()
```

**You've now validated:**
✅ Dependencies installed  
✅ Excel file found  
✅ Data extraction working  

---

## 💡 Pro Tips

### Run in Stages

Don't run everything at once on first try:

1. ✅ `prepare_data.py` - Quick, shows data stats
2. ✅ `topic_discovery.py` - 5-10 min, creates interesting results
3. ✅ `entity_extractor.py` - Fast, useful output
4. ⏳ `llm_judge.py` - LONG (start with sample_size=10 for testing)
5. ✅ Dashboard - Works with partial data

### Test with Small Samples

Edit any script's `main()` to limit data:

```python
# Example: topic_discovery.py
queries = queries_df['Queries'].dropna().tolist()[:100]  # Only 100 queries
```

### Monitor Groq API Usage

Check your Groq console for API usage:
https://console.groq.com/

---

## 🆘 Need Help?

**Check these files:**
- `README.md` - Full documentation
- `report/SkyRocket_Netomi_Report.md` - Complete analysis
- Code comments - Every function documented

**Common issues solved above:**
- Excel file not found ✅
- Groq API key missing ✅
- Module not installed ✅

---

## ✅ Success Checklist

After setup, you should have:

- [x] Virtual environment activated
- [x] All dependencies installed (`pip list | findstr groq`)
- [x] spaCy model downloaded
- [x] .env file with Groq API key
- [x] Excel file accessible
- [x] `data/queries.csv` created
- [x] Dashboard launches successfully

---

**🚀 You're ready to impress Netomi!**

**Next:** Run the scripts and explore the dashboard!
