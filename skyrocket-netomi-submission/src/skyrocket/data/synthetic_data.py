import os
import json
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class SyntheticDataGenerator:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key)
    
    def generate_queries(self, topic_name: str, topic_description: str,
                        example_queries: List[str], n_queries: int = 50) -> List[str]:
        examples_text = "\n".join([f"- {q}" for q in example_queries[:5]])
        
        prompt = f"""Generate {n_queries} realistic customer service queries for the following topic:

**Topic**: {topic_name}
**Description**: {topic_description}

**Example Queries**:
{examples_text}

**Requirements**:
1. Queries should be natural and realistic (how real customers would ask)
2. Vary the phrasing, length, and specificity
3. Include different emotional tones (neutral, frustrated, polite, urgent)
4. Mix simple and complex scenarios
5. Include typos occasionally (realistic!)
6. Some queries should be very brief (3-5 words), others detailed

Return ONLY a JSON array of query strings:
["query 1", "query 2", ...]

Generate exactly {n_queries} queries."""
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at generating realistic customer service data for training ML models."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            generated_queries = json.loads(response_text)
            
            print(f"Generated {len(generated_queries)} queries for '{topic_name}'")
            
            return generated_queries
            
        except Exception as e:
            print(f"Error generating queries for '{topic_name}': {e}")
            return []
    
    def augment_low_volume_topics(self, topics_config: Dict, 
                                  threshold_percentile: float = 0.3,
                                  queries_per_topic: int = 50) -> Dict:
        topics = topics_config['topics']
        
        sorted_topics = sorted(topics, key=lambda x: x['count'])
        
        n_low_volume = max(2, int(len(topics) * threshold_percentile))
        low_volume_topics = sorted_topics[:n_low_volume]
        
        print("="*80)
        print("SYNTHETIC DATA GENERATION")
        print("="*80)
        print(f"\nIdentified {n_low_volume} low-volume topics requiring augmentation:")
        
        for topic in low_volume_topics:
            print(f"  - {topic['topic_name']}: {topic['count']} queries ({topic['percentage']:.1f}%)")
        
        print(f"\nGenerating {queries_per_topic} synthetic queries per topic using Groq...")
        
        augmented_data = {
            'low_volume_topics': [],
            'synthetic_queries': {},
            'total_generated': 0
        }
        
        for topic in low_volume_topics:
            topic_name = topic['topic_name']
            print(f"\nGenerating for '{topic_name}'...")
            
            synthetic_queries = self.generate_queries(
                topic_name=topic_name,
                topic_description=topic['description'],
                example_queries=topic['representative_queries'],
                n_queries=queries_per_topic
            )
            
            if synthetic_queries:
                augmented_data['low_volume_topics'].append(topic_name)
                augmented_data['synthetic_queries'][topic_name] = synthetic_queries
                augmented_data['total_generated'] += len(synthetic_queries)
                
                print(f"  Samples:")
                for i, query in enumerate(synthetic_queries[:3], 1):
                    print(f"    {i}. {query}")
        
        print(f"\n{'='*80}")
        print(f"Generated {augmented_data['total_generated']} synthetic queries total")
        print("="*80)
        
        return augmented_data

def main():
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        data_dir = os.path.join(base_dir, 'data')
        
        with open(os.path.join(data_dir, "topic_discovery_results.json"), 'r') as f:
            topics_config = json.load(f)
    except FileNotFoundError:
        print("Error: topic_discovery_results.json not found. Run topic_discovery.py first.")
        return
    
    generator = SyntheticDataGenerator()
    
    augmented_data = generator.augment_low_volume_topics(
        topics_config,
        threshold_percentile=0.3,
        queries_per_topic=50
    )
    
    output_path = os.path.join(data_dir, "synthetic_queries.json")
    with open(output_path, 'w') as f:
        json.dump(augmented_data, f, indent=2)
    
    print(f"\nSynthetic data saved to: {output_path}")
    
    all_synthetic = []
    for topic_name, queries in augmented_data['synthetic_queries'].items():
        for query in queries:
            all_synthetic.append({
                'query': query,
                'topic': topic_name,
                'synthetic': True
            })
    
    if all_synthetic:
        synthetic_df = pd.DataFrame(all_synthetic)
        csv_path = os.path.join(data_dir, "synthetic_queries.csv")
        synthetic_df.to_csv(csv_path, index=False)
        print(f"Synthetic queries CSV saved to: {csv_path}")

if __name__ == "__main__":
    main()
