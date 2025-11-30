import os
import json
from typing import List, Dict
from dataclasses import dataclass
from collections import defaultdict
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Entity:
    type: str
    value: str
    context: str

class EntityExtractor:
    
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not found. Please set it in .env or pass it as an argument.")
            
        self.groq_client = Groq(api_key=self.groq_api_key)
    
    
    def _get_prompt_path(self) -> str:
        possible_roots = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')),
            os.path.abspath('.')
        ]
        
        for root in possible_roots:
            prompt_path = os.path.join(root, 'config', 'prompts', 'entity_extraction.txt')
            if os.path.exists(prompt_path):
                print(f"Found prompt at: {prompt_path}")
                return prompt_path
        
        error_msg = (
            "Error: Prompt template not found. Tried the following locations:\n"
            f"  1. {os.path.join(possible_roots[0], 'config', 'prompts', 'entity_extraction.txt')}\n"
            f"  2. {os.path.join(possible_roots[1], 'config', 'prompts', 'entity_extraction.txt')}\n"
            "\nPlease ensure the file exists in one of these locations."
        )
        print(error_msg)
        return os.path.join(possible_roots[0], 'config', 'prompts', 'entity_extraction.txt')
    
    def _load_prompt_template(self) -> str:
        return """Extract structured entities from this customer service query. Focus on domain-specific entities.

ENTITY TYPES TO EXTRACT:
1. ORDER_ID - Order numbers, order identifiers (e.g.,
2. TRACKING_NUMBER - Shipment tracking codes (e.g., 1Z999AA10123456784)
3. PRODUCT_NAME - Specific products mentioned by name
4. ACCOUNT_ID - Customer account numbers or IDs
5. EMAIL - Email addresses
6. PHONE - Phone numbers
7. AMOUNT - Monetary amounts (e.g., $29.99, 50 dollars)
8. DATE - Specific dates mentioned
9. LOCATION - Addresses, cities, states, countries

QUERY: "{query_text}"

OUTPUT FORMAT (JSON array):
[
  {{
    "type": "<entity_type>",
    "value": "<extracted_value>",
    "confidence": "high | medium | low"
  }},
  ...
]

INSTRUCTIONS:
- Extract ALL entities you can identify with reasonable confidence
- If no entities are found, return empty array []
- Use "high" confidence for exact matches (emails, numbers)
- Use "medium" confidence for likely matches (product names from context)
- Use "low" confidence for ambiguous extractions
- Be precise - extract the EXACT value, not surrounding context

EXAMPLES:

Query: "I want to track my order #12345 shipped to New York"
Output:
[
  {{"type": "ORDER_ID", "value": "#12345", "confidence": "high"}},
  {{"type": "LOCATION", "value": "New York", "confidence": "high"}}
]

Query: "The iPhone 14 Pro I ordered for $999 hasn't arrived"
Output:
[
  {{"type": "PRODUCT_NAME", "value": "iPhone 14 Pro", "confidence": "high"}},
  {{"type": "AMOUNT", "value": "$999", "confidence": "high"}}
]

Now extract entities from the query above and return ONLY the JSON array."""

    def extract_entities(self, text: str, verbose: bool = False) -> Dict[str, List[Entity]]:
        if not text or not text.strip():
            return {}
            
        try:
            prompt_template = self._load_prompt_template()
            
            prompt = prompt_template.format(query_text=text)
            
            if verbose:
                print("\n=== PROMPT (first 200 chars) ===")
                print(prompt[:200] + ("..." if len(prompt) > 200 else ""))
                print("==============================\n")
            
        except Exception as e:
            print(f"Error preparing prompt: {str(e)}")
            print("Falling back to simple prompt...")
            prompt = f"""Extract entities from this text and return a JSON array with 'type', 'value', and 'confidence' for each entity. Text: "{text}"""
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a precise entity extraction system for customer service data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
                max_tokens=500
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            try:
                response_data = json.loads(response_text)
                if isinstance(response_data, dict) and 'entities' in response_data:
                    entity_list = response_data['entities']
                elif isinstance(response_data, list):
                    entity_list = response_data
                else:
                    entity_list = []
                    
            except json.JSONDecodeError:
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                elif not response_text.startswith('['):
                    start = response_text.find('[')
                    end = response_text.rfind(']') + 1
                    if start >= 0 and end > start:
                        response_text = response_text[start:end]
                
                try:
                    entity_list = json.loads(response_text)
                except json.JSONDecodeError:
                    print(f"Failed to parse Groq response as JSON: {response_text[:200]}...")
                    return {}
            
            entities_by_type = defaultdict(list)
            
            for item in entity_list if isinstance(entity_list, list) else []:
                if not isinstance(item, dict):
                    continue
                    
                entity_type = item.get('type', '').strip().upper()
                entity_value = str(item.get('value', '')).strip()
                confidence = item.get('confidence', 'medium').lower()
                
                if entity_type and entity_value and confidence in ('high', 'medium'):
                    entity = Entity(
                        type=entity_type,
                        value=entity_value,
                        context=text
                    )
                    entities_by_type[entity_type].append(entity)
            
            return dict(entities_by_type)
            
        except Exception as e:
            print(f"Error in Groq extraction: {str(e)}")
            return {}
    
    
    def extract_from_dataset(self, texts: List[str], sample_size: int = None) -> Dict:
        if sample_size and sample_size > 0:
            texts = texts[:sample_size]
        
        total_texts = len(texts)
        print(f"Extracting entities from {total_texts} texts using Groq LLM...")
        
        all_entities_by_type = defaultdict(list)
        entity_counts = defaultdict(int)
        
        for i, text in enumerate(texts, 1):
            if i % max(10, total_texts // 10) == 0 or i == 1 or i == total_texts:
                print(f"   Processed {i}/{total_texts} texts...")
            
            entities = self.extract_entities(text)
            
            for entity_type, entity_list in entities.items():
                all_entities_by_type[entity_type].extend(entity_list)
                entity_counts[entity_type] += len(entity_list)
        
        unique_examples = {
            entity_type: list({e.value for e in entity_list[:10]})
            for entity_type, entity_list in all_entities_by_type.items()
        }
        
        results = {
            "total_texts": total_texts,
            "entity_types_found": len(entity_counts),
            "total_entities": sum(entity_counts.values()),
            "entity_counts": dict(entity_counts),
            "examples": unique_examples
        }
        
        print(f"\n{'='*80}")
        print("ENTITY EXTRACTION RESULTS (Groq LLM)")
        print('='*80)
        print(f"Total texts processed: {results['total_texts']:,}")
        print(f"Total entities found: {results['total_entities']:,}")
        print(f"Unique entity types: {results['entity_types_found']}")
        
        if entity_counts:
            print("\nEntity type breakdown:")
            for entity_type, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True):
                examples = ", ".join(f'"{ex}"' for ex in unique_examples[entity_type][:2])
                if len(unique_examples[entity_type]) > 2:
                    examples += f" and {len(unique_examples[entity_type]) - 2} more"
                print(f"  • {entity_type}: {count:,} (e.g., {examples})")
        
        return results

def main():
    import pandas as pd
    import datetime
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    data_dir = os.path.join(base_dir, 'data')
    
    os.makedirs(data_dir, exist_ok=True)
    
    responses_path = os.path.join(data_dir, "genai_responses.csv")
    if not os.path.exists(responses_path):
        print(f"Error: genai_responses.csv not found at {responses_path}")
        print("Please ensure the file exists in the data directory.")
        return
    
    try:
        print("\nLoading and preparing data...")
        
        df = pd.read_csv(responses_path)
        
        print(f"\nAvailable columns in genai_responses.csv: {', '.join(df.columns.tolist())}")
        
        query_col = next((col for col in df.columns if 'query' in col.lower()), None)
        response_col = next((col for col in df.columns if 'response' in col.lower()), None)
        
        if not query_col or not response_col:
            print("\nError: Could not find required columns in genai_responses.csv")
            print("Looking for columns containing 'query' and 'response' (case-insensitive)")
            print("\nAvailable columns:")
            for col in df.columns:
                print(f"- {col}")
            return
            
        print(f"Using columns: '{query_col}' as query, '{response_col}' as response")
        
        print("\nCombining query and response text for better context...")
        df['combined_text'] = "Query: " + df[query_col].astype(str) + " \nResponse: " + df[response_col].astype(str)
        
        all_texts = df['combined_text'].dropna().tolist()
        
        if not all_texts:
            print("Error: No valid query-response pairs found in genai_responses.csv")
            return
            
        print(f"\nFound {len(all_texts)} query-response pairs for entity extraction")
        
        print("\nInitializing Groq-based entity extractor...")
        try:
            extractor = EntityExtractor()
            print("Groq client initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Groq client: {str(e)}")
            print("Please ensure you have set the GROQ_API_KEY environment variable")
            return
        
        batch_size = 10
        results = {
            "total_texts": len(all_texts),
            "entity_types_found": 0,
            "total_entities": 0,
            "entity_counts": {},
            "examples": {},
            "extractions": []
        }
        
        total_batches = (len(all_texts) + batch_size - 1) // batch_size
        print(f"\nStarting entity extraction with Groq LLM...")
        print(f"Total batches to process: {total_batches}")
        
        for i in range(0, len(all_texts), batch_size):
            batch = all_texts[i:i + batch_size]
            current_batch = i // batch_size + 1
            print(f"\nProcessing batch {current_batch}/{total_batches} "
                  f"(items {i+1}-{min(i + batch_size, len(all_texts))})...")
            
            for j, text in enumerate(batch):
                is_first = (i == 0 and j == 0)
                
                batch_results = extractor.extract_entities(text, verbose=is_first)
                
                for entity_type, entities in batch_results.items():
                    if entity_type not in results["entity_counts"]:
                        results["entity_counts"][entity_type] = 0
                        results["examples"][entity_type] = set()
                    
                    results["entity_counts"][entity_type] += len(entities)
                    results["examples"][entity_type].update(e.value for e in entities)
                    results["total_entities"] += len(entities)
                    
                    if len(results["extractions"]) < 100:
                        results["extractions"].extend([{"type": e.type, "value": e.value} for e in entities])
            
            print(f"   Processed {min(i + len(batch), len(all_texts))}/{len(all_texts)} "
                  f"({(min(i + len(batch), len(all_texts)) / len(all_texts) * 100):.1f}%)")
            print(f"   Entities found so far: {results['total_entities']} "
                  f"({len(results['entity_counts'])} types)")
        
        results["examples"] = {k: list(v)[:10] for k, v in results["examples"].items()}
        results["entity_types_found"] = len(results["entity_counts"])
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(data_dir, f"entity_extraction_results_{timestamp}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*80}")
        print("ENTITY EXTRACTION COMPLETE")
        print('='*80)
        print(f"Processed {results['total_texts']:,} query-response pairs")
        print(f"Found {results['total_entities']:,} total entities")
        print(f"Detected {results['entity_types_found']} unique entity types")
        
        if results["entity_counts"]:
            print("\nTop entity types:")
            for entity_type, count in sorted(
                results["entity_counts"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]:
                examples = ", ".join(f'"{ex}"' for ex in results["examples"][entity_type][:2])
                if len(results["examples"][entity_type]) > 2:
                    examples += f" and {len(results['examples'][entity_type]) - 2} more"
                print(f"   • {entity_type}: {count:,} (e.g., {examples})")
        
        print(f"\nResults saved to: {output_path}")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

