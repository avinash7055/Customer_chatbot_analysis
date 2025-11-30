import os
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from prefect import flow, task
from prefect.tasks import task_input_hash
import pandera as pa
from pandera import Column, DataFrameSchema, Check
from dotenv import load_dotenv

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from skyrocket.core.topic_classifier import TopicClassifier
from skyrocket.core.entity_extractor import EntityExtractor
from skyrocket.core.llm_judge import LLMJudge

load_dotenv()

queries_schema = DataFrameSchema({
    "query_id": Column(int, nullable=False),
    "query_text": Column(str, Check.str_length(min_value=1, max_value=1000)),
    "timestamp": Column(pa.DateTime, nullable=True),
})

responses_schema = DataFrameSchema({
    "query_id": Column(int, nullable=False),
    "query_text": Column(str),
    "response_text": Column(str),
    "timestamp": Column(pa.DateTime, nullable=True),
})

@task(name="Extract New Queries", retries=3, retry_delay_seconds=60)
def extract_new_queries(data_source: str, last_processed_date: datetime = None) -> pd.DataFrame:
    print(f"📥 Extracting new queries from {data_source}")
    
    df = pd.read_csv(data_source)
    
    if last_processed_date:
        if 'timestamp' in df.columns:
            df = df[pd.to_datetime(df['timestamp']) > last_processed_date]
    
    print(f"   Extracted {len(df)} new queries")
    return df

@task(name="Validate Data Quality", retries=2)
def validate_data_quality(df: pd.DataFrame, schema: DataFrameSchema) -> pd.DataFrame:
    print(f"✅ Validating data quality for {len(df)} rows")
    
    try:
        validated_df = schema.validate(df, lazy=True)
        print(f"   ✓ All quality checks passed")
        return validated_df
    except pa.errors.SchemaErrors as err:
        print(f"   ⚠️  Quality issues found:")
        print(err.failure_cases)
        
        clean_df = df.drop(err.failure_cases['index'].unique())
        print(f"   Dropped {len(df) - len(clean_df)} invalid rows")
        return clean_df

@task(name="Classify Topics", cache_key_fn=task_input_hash, cache_expiration=timedelta(hours=24))
def classify_topics(df: pd.DataFrame, topics_config_path: str) -> pd.DataFrame:
    print(f"🏷️  Classifying {len(df)} queries into topics")
    
    import json
    with open(topics_config_path, 'r') as f:
        topics_config = json.load(f)
    
    classifier = TopicClassifier(topics_config)
    
    topics = []
    for query in df['query_text']:
        result = classifier.classify_query(query)
        topics.append(result['topic_name'])
    
    df['topic'] = topics
    print(f"   ✓ Classification complete")
    
    return df

@task(name="Extract Entities")
def extract_entities(df: pd.DataFrame) -> pd.DataFrame:
    print(f"🔍 Extracting entities from {len(df)} queries")
    
    extractor = EntityExtractor()
    
    entities_list = []
    for query in df['query_text']:
        entities = extractor.extract_hybrid(query, use_groq=False)
        entities_json = {k: [e.value for e in v] for k, v in entities.items()}
        entities_list.append(entities_json)
    
    df['entities'] = [str(e) for e in entities_list]
    print(f"   ✓ Entity extraction complete")
    
    return df

@task(name="Evaluate Responses")
def evaluate_responses(df: pd.DataFrame) -> pd.DataFrame:
    print(f"⚖️  Evaluating {len(df)} responses")
    
    judge = LLMJudge()
    
    evaluated_df = judge.evaluate_dataset(
        df,
        query_col='query_text',
        response_col='response_text'
    )
    
    return evaluated_df

@task(name="Calculate Metrics")
def calculate_metrics(df: pd.DataFrame) -> Dict:
    print(f"📊 Calculating business metrics")
    
    metrics = {
        "total_queries": len(df),
        "containment_rate": (1 - df['escalation_needed'].sum() / len(df)) if 'escalation_needed' in df.columns else 0,
        "avg_quality_score": df['overall_quality'].mean() if 'overall_quality' in df.columns else 0,
        "hallucination_rate": df['hallucination'].sum() / len(df) if 'hallucination' in df.columns else 0,
        "top_topics": df['topic'].value_counts().head(5).to_dict() if 'topic' in df.columns else {},
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"   ✓ Metrics calculated")
    return metrics

@task(name="Check Quality Thresholds")
def check_quality_thresholds(metrics: Dict) -> bool:
    print(f"🎯 Checking quality thresholds")
    
    thresholds = {
        "containment_rate": 0.70,
        "avg_quality_score": 3.0,
        "hallucination_rate": 0.05
    }
    
    alerts = []
    
    for metric, threshold in thresholds.items():
        if metric in metrics:
            value = metrics[metric]
            
            if metric == "hallucination_rate":
                if value > threshold:
                    alerts.append(f"⚠️  {metric}: {value:.2%} exceeds threshold {threshold:.2%}")
            else:
                if value < threshold:
                    alerts.append(f"⚠️  {metric}: {value:.2%} below threshold {threshold:.2%}")
    
    if alerts:
        print(f"   Quality issues detected:")
        for alert in alerts:
            print(f"     {alert}")
        
        return False
    else:
        print(f"   ✓ All quality thresholds met")
        return True

@task(name="Save Results")
def save_results(df: pd.DataFrame, metrics: Dict, output_dir: str):
    print(f"💾 Saving results to {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_path = os.path.join(output_dir, f"processed_{timestamp}.csv")
    df.to_csv(data_path, index=False)
    
    metrics_path = os.path.join(output_dir, f"metrics_{timestamp}.json")
    import json
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"   ✓ Saved to {output_dir}")

@flow(name="Daily Customer Query Processing")
def daily_customer_query_pipeline(
    data_source: str = "data/queries.csv",
    topics_config: str = "data/topic_discovery_results.json",
    output_dir: str = "data/processed"
):
    print("="*80)
    print("DAILY CUSTOMER QUERY PROCESSING PIPELINE")
    print("="*80)
    
    raw_df = extract_new_queries(data_source)
    
    validated_df = raw_df
    
    classified_df = classify_topics(validated_df, topics_config)
    enriched_df = extract_entities(classified_df)
    
    if 'response_text' in enriched_df.columns:
        evaluated_df = evaluate_responses(enriched_df)
    else:
        evaluated_df = enriched_df
    
    metrics = calculate_metrics(evaluated_df)
    
    quality_ok = check_quality_thresholds(metrics)
    
    save_results(evaluated_df, metrics, output_dir)
    
    print("="*80)
    print(f"✅ Pipeline complete - Quality: {'PASS' if quality_ok else 'FAIL'}")
    print("="*80)
    
    return metrics

if __name__ == "__main__":
    metrics = daily_customer_query_pipeline()
    print(f"\n📊 Final Metrics: {metrics}")
