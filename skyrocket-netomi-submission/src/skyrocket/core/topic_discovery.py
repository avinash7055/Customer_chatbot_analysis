import os
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN
from groq import Groq
from typing import List, Dict, Tuple
import json
from collections import defaultdict, Counter
from dotenv import load_dotenv

load_dotenv()

class TopicDiscoverer:
    def __init__(self, groq_api_key: str = None):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key)
        
    def generate_embeddings(self, queries: List[str]) -> np.ndarray:
        print(f"Generating embeddings for {len(queries)} queries...")
        embeddings = self.embedding_model.encode(queries, show_progress_bar=True)
        print(f"   Embedding shape: {embeddings.shape}")
        return embeddings
    
    def reduce_dimensions(self, embeddings: np.ndarray) -> np.ndarray:
        print(f"Reducing dimensions with UMAP...")
        umap_model = UMAP(
            n_components=5,
            n_neighbors=15,
            min_dist=0.0,
            metric='cosine',
            random_state=42
        )
        reduced = umap_model.fit_transform(embeddings)
        print(f"   Reduced shape: {reduced.shape}")
        return reduced
    
    def cluster_queries(self, reduced_embeddings: np.ndarray) -> np.ndarray:
        print(f"Clustering with HDBSCAN...")
        clusterer = HDBSCAN(
            min_cluster_size=50,
            min_samples=10,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        labels = clusterer.fit_predict(reduced_embeddings)
        
        unique_labels = set(labels)
        n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
        n_noise = list(labels).count(-1)
        
        print(f"   Clusters found: {n_clusters}")
        print(f"   Noise points: {n_noise} ({n_noise/len(labels)*100:.1f}%)")
        
        return labels
    
    def get_representative_queries(self, queries: List[str], labels: np.ndarray, 
                                   n_samples: int = 10) -> Dict[int, List[str]]:
        cluster_queries = defaultdict(list)
        
        for query, label in zip(queries, labels):
            if label != -1:
                cluster_queries[label].append(query)
        
        representatives = {}
        for label, cluster_list in cluster_queries.items():
            sample_size = min(n_samples, len(cluster_list))
            step = max(1, len(cluster_list) // sample_size)
            representatives[label] = cluster_list[::step][:sample_size]
        
        return representatives
    
    def _extract_json_from_response(self, text: str) -> dict:
        import re
        import json
        
        json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
            
        try:
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return json.loads(text[json_start:json_end])
        except:
            pass
            
        try:
            return json.loads(text)
        except:
            pass
            
        return None

    def label_cluster_with_groq(self, queries: List[str], cluster_id: int, max_retries: int = 2) -> Dict[str, str]:
        if not queries:
            return self._create_error_response(cluster_id, "No queries provided")
            
        queries_text = "\n".join([f"- {q}" for q in queries[:min(8, len(queries))]])
        
        prompt = """You are analyzing customer service queries. Below are representative queries from a cluster:

{queries}

Based on these queries, provide a JSON object with:
1. "topic_name": A concise topic name (2-4 words, e.g., "Order Cancellation", "Account Issues")
2. "description": A brief description of what customers in this cluster are asking about

IMPORTANT: Your response must be valid JSON with exactly these two fields. Example:
```json
{
  "topic_name": "Account Management",
  "description": "Customers need help with account-related issues"
}
        return {
            "topic_name": f"Topic {cluster_id}",
            "description": f"Error during labeling: {error_msg}",
            "cluster_id": cluster_id,
            "error": True
        }
             
    
    def discover_topics(self, queries: List[str], target_topics: int = 10) -> Dict:
        
        
        print("="*80)
        print("TOPIC DISCOVERY PIPELINE - Groq LLM Integration")
        print("="*80)
        
        
        embeddings = self.generate_embeddings(queries)
        
        
        reduced = self.reduce_dimensions(embeddings)
        
        
        labels = self.cluster_queries(reduced)
        
       
        print(f"\n Extracting representative queries...")
        representatives = self.get_representative_queries(queries, labels)
        
        
        print(f"\n Labeling clusters with  LLM ")
        topic_labels = {}
        
        
        cluster_sizes = Counter(labels)
        top_clusters = sorted(
            [c for c in cluster_sizes.keys() if c != -1],
            key=lambda x: cluster_sizes[x],
            reverse=True
        )[:target_topics]
        
        for cluster_id in top_clusters:
            print(f"   Labeling cluster {cluster_id} ({cluster_sizes[cluster_id]} queries)...")
            label_info = self.label_cluster_with_groq(
                representatives[cluster_id],
                cluster_id
            )
            topic_labels[cluster_id] = label_info
            import time
            time.sleep(2)  
        
        
        results = {
            "total_queries": len(queries),
            "n_topics": len(top_clusters),
            "topics": []
        }
        
        print(f"\n" + "="*80)
        print(f"DISCOVERED TOPICS")
        print("="*80)
        
        for rank, cluster_id in enumerate(top_clusters, 1):
            topic_info = {
                "rank": rank,
                "cluster_id": cluster_id,
                "topic_name": topic_labels[cluster_id]["topic_name"],
                "description": topic_labels[cluster_id]["description"],
                "count": cluster_sizes[cluster_id],
                "percentage": cluster_sizes[cluster_id] / len(queries) * 100,
                "representative_queries": representatives[cluster_id][:5]
            }
            results["topics"].append(topic_info)
            
            print(f"\n{rank}. {topic_info['topic_name']}")
            print(f"   {topic_info['description']}")
            print(f"   Volume: {topic_info['count']:,} queries ({topic_info['percentage']:.1f}%)")
            print(f"   Examples:")
            for i, q in enumerate(topic_info['representative_queries'], 1):
                print(f"      {i}. {q}")
        
        print("\n" + "="*80)
        print(f" Topic discovery complete: {len(top_clusters)} topics identified")
        print("="*80)
        
        return results

def main():

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, 'data')
    
    
    queries_path = os.path.join(data_dir, "queries.csv")
    if not os.path.exists(queries_path):
        print(f" queries.csv not found at {queries_path}")
        print("Please run prepare_data.py first.")
        return

    queries_df = pd.read_csv(queries_path)
    queries = queries_df['Queries'].dropna().tolist()
    
    print(f"Loaded {len(queries)} queries")
    
   
    discoverer = TopicDiscoverer()
    results = discoverer.discover_topics(queries, target_topics=10)
    
    
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(i) for i in obj]
        elif hasattr(obj, 'item'): 
            return obj.item()
        else:
            return obj

    results = convert_types(results)
    
    
    output_path = os.path.join(data_dir, "topic_discovery_results.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n Results saved to: {output_path}")
if __name__ == "__main__":
    main()
