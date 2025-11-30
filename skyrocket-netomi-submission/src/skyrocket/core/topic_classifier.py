import os
import json
import pandas as pd
from typing import List, Dict
from groq import Groq
from dotenv import load_dotenv
from collections import defaultdict
import random

load_dotenv()

class TopicClassifier:
    def __init__(self, topics_config: Dict, groq_api_key: str = None):
        self.topics = topics_config['topics']
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        self.few_shot_prompt = self._build_few_shot_prompt()
    
    def _build_few_shot_prompt(self) -> str:
        
        prompt_parts = [
            "You are a customer service query classifier. Classify queries into one of these topics:\n"
        ]
        
        for i, topic in enumerate(self.topics, 1):
            prompt_parts.append(
                f"{i}. **{topic['topic_name']}**: {topic['description']}"
            )
        
        prompt_parts.append("\n**Examples:**\n")
        
        for topic in self.topics[:8]:
            topic_name = topic['topic_name']
            examples = topic['representative_queries'][:3]
            
            for example in examples:
                prompt_parts.append(f"Query: \"{example}\"")
                prompt_parts.append(f"Topic: {topic_name}\n")
        
        prompt_parts.append(
            "\n**Task**: Classify the following query into ONE of the topics above.\n"
        )
        prompt_parts.append(
            "Respond with ONLY the topic name, nothing else.\n"
        )
        
        return "\n".join(prompt_parts)
    
    def classify_query(self, query: str) -> Dict[str, str]:
        classification_prompt = self.few_shot_prompt + f"\nQuery: \"{query}\"\nTopic:"
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise topic classifier. Respond only with the topic name."
                    },
                    {"role": "user", "content": classification_prompt}
                ],
                temperature=0.1,
                max_tokens=50
            )
            
            predicted_topic = completion.choices[0].message.content.strip()
            
            predicted_topic = predicted_topic.replace("**", "").strip()
            
            valid_topics = [t['topic_name'] for t in self.topics]
            
            if predicted_topic not in valid_topics:
                predicted_topic = self._fuzzy_match(predicted_topic, valid_topics)
            
            return {
                "topic_name": predicted_topic,
                "confidence": "high"
            }
            
        except Exception as e:
            print(f"Error classifying query: {e}")
            return {
                "topic_name": "Unknown",
                "confidence": "low"
            }
    
    def _fuzzy_match(self, prediction: str, valid_topics: List[str]) -> str:
        prediction_lower = prediction.lower()
        
        for topic in valid_topics:
            if topic.lower() in prediction_lower or prediction_lower in topic.lower():
                return topic
        
        return valid_topics[0] if valid_topics else "Unknown"
    
    def classify_batch(self, queries: List[str]) -> List[Dict]:
        
        print(f"Classifying {len(queries)} queries...")
        
        results = []
        for i, query in enumerate(queries):
            if i % 50 == 0 and i > 0:
                print(f"   Processed {i}/{len(queries)}...")
            
            result = self.classify_query(query)
            result['query'] = query
            results.append(result)
        
        return results
    
    def evaluate_accuracy(self, test_data: List[Dict]) -> Dict:
        print(f"Evaluating on {len(test_data)} test samples...")
        
        correct = 0
        predictions = []
        
        for item in test_data:
            pred = self.classify_query(item['query'])
            predictions.append(pred['topic_name'])
            
            if pred['topic_name'] == item['true_topic']:
                correct += 1
        
        accuracy = correct / len(test_data)
        
        print(f"\nFew-Shot Accuracy: {accuracy*100:.1f}%")
        
        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": len(test_data),
            "predictions": predictions
        }

def main():
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, 'data')
    
    topics_config_path = os.path.join(data_dir, "topic_discovery_results.json")
    if not os.path.exists(topics_config_path):
        print(f"topic_discovery_results.json not found at {topics_config_path}")
        print("Please run topic_discovery.py first.")
        return

    with open(topics_config_path, 'r') as f:
        topics_config = json.load(f)
    
    classifier = TopicClassifier(topics_config)
    
    test_samples = []
    for topic in topics_config['topics']:
        for query in topic['representative_queries'][3:]:
            test_samples.append({
                'query': query,
                'true_topic': topic['topic_name']
            })
    
    if test_samples:
        results = classifier.evaluate_accuracy(test_samples[:50])
        
        output_path = os.path.join(data_dir, "classification_results.json")
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to: {output_path}")
    else:
        print("No test samples available. Run topic_discovery.py first.")

if __name__ == "__main__":
    main()
