import os
import json
import pandas as pd
from typing import Dict, List
from dataclasses import dataclass, asdict
from groq import Groq
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

@dataclass
class ResponseEvaluation:
    query: str
    response: str
    accuracy: int
    empathy: int
    completeness: int
    hallucination: bool
    escalation_needed: bool
    bias: bool
    reasoning: str
    overall_quality: float

class LLMJudge:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_api_key)
        
        self.evaluation_prompt_template = self._load_evaluation_prompt()
    
    def _load_evaluation_prompt(self) -> str:
        return """You are an expert evaluator of customer service responses. Evaluate the following query-response pair on multiple dimensions.

**Customer Query:**
{query}

**Generated Response:**
{response}

**Evaluation Criteria:**

1. **Accuracy** (1-5): Is the response factually correct and relevant to the query?
   - 5: Completely accurate and on-point
   - 4: Mostly accurate with minor issues
   - 3: Partially accurate
   - 2: Mostly inaccurate
   - 1: Completely inaccurate or irrelevant

2. **Empathy** (1-5): Does the response show understanding and care for the customer's concern?
   - 5: Highly empathetic, warm, and understanding
   - 4: Shows good empathy
   - 3: Neutral tone
   - 2: Slightly cold or dismissive
   - 1: Completely impersonal or rude

3. **Completeness** (1-5): Does the response fully address all aspects of the query?
   - 5: Thoroughly addresses everything
   - 4: Addresses most points
   - 3: Addresses some points
   - 2: Misses important points
   - 1: Barely addresses the query

4. **Hallucination** (true/false): Does the response contain fabricated or unverifiable information?
   - true: Contains made-up details, false promises, or unverifiable claims
   - false: All information appears reasonable and verifiable

5. **Escalation Needed** (true/false): Should this be escalated to a human agent?
   - true: Complex issue, high emotion, system limitations, requires human judgment
   - false: Can be resolved by automated system

6. **Bias** (true/false): Does the response show unfair treatment or discrimination?
   - true: Shows bias based on demographic factors or makes unfair assumptions
   - false: Treats customer fairly and neutrally

**Respond in JSON format:**
```json
{{
  "accuracy": <1-5>,
  "empathy": <1-5>,
  "completeness": <1-5>,
  "hallucination": <true/false>,
  "escalation_needed": <true/false>,
  "bias": <true/false>,
  "reasoning": "<brief explanation of your evaluation>"
}}
```

Provide only the JSON, nothing else."""
    
    def evaluate_response(self, query: str, response: str) -> ResponseEvaluation:
        prompt = self.evaluation_prompt_template.format(
            query=query,
            response=response
        )
        
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert customer service quality evaluator. You provide objective, consistent assessments based on clear criteria."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            response_text = completion.choices[0].message.content.strip()
            
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            eval_data = json.loads(response_text)
            
            overall_quality = (
                eval_data.get('accuracy', 3) +
                eval_data.get('empathy', 3) +
                eval_data.get('completeness', 3)
            ) / 3.0
            
            return ResponseEvaluation(
                query=query,
                response=response,
                accuracy=eval_data.get('accuracy', 3),
                empathy=eval_data.get('empathy', 3),
                completeness=eval_data.get('completeness', 3),
                hallucination=eval_data.get('hallucination', False),
                escalation_needed=eval_data.get('escalation_needed', False),
                bias=eval_data.get('bias', False),
                reasoning=eval_data.get('reasoning', ''),
                overall_quality=overall_quality
            )
            
        except Exception as e:
            print(f"Warning: Error evaluating response: {e}")
            return ResponseEvaluation(
                query=query,
                response=response,
                accuracy=3,
                empathy=3,
                completeness=3,
                hallucination=False,
                escalation_needed=False,
                bias=False,
                reasoning=f"Error during evaluation: {str(e)}",
                overall_quality=3.0
            )
    
    def evaluate_dataset(self, df: pd.DataFrame, 
                        query_col: str = 'Query',
                        response_col: str = 'response',
                        sample_size: int = None) -> pd.DataFrame:
        if sample_size:
            df = df.head(sample_size)
        
        print(f"Evaluating {len(df)} responses with Groq LLM-as-a-Judge...")
        print(f"Model: llama-3.1-8b-instant")
        print(f"Estimated time: ~{len(df) * 0.5:.0f} seconds")
        
        evaluations = []
        
        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating"):
            query = str(row[query_col])
            response = str(row[response_col])
            
            eval_result = self.evaluate_response(query, response)
            evaluations.append(eval_result)
        
        eval_df = pd.DataFrame([asdict(e) for e in evaluations])
        
        result_df = df.copy()
        result_df['accuracy'] = eval_df['accuracy']
        result_df['empathy'] = eval_df['empathy']
        result_df['completeness'] = eval_df['completeness']
        result_df['hallucination'] = eval_df['hallucination']
        result_df['escalation_needed'] = eval_df['escalation_needed']
        result_df['bias'] = eval_df['bias']
        result_df['overall_quality'] = eval_df['overall_quality']
        result_df['judge_reasoning'] = eval_df['reasoning']
        
        self._print_summary(result_df)
        
        return result_df
    
    def _print_summary(self, df: pd.DataFrame):
        
        print(f"\n{'='*80}")
        print("LLM-AS-A-JUDGE EVALUATION SUMMARY")
        print('='*80)
        
        print(f"\nQuality Scores (1-5 scale):")
        print(f"  Accuracy:     {df['accuracy'].mean():.2f} ± {df['accuracy'].std():.2f}")
        print(f"  Empathy:      {df['empathy'].mean():.2f} ± {df['empathy'].std():.2f}")
        print(f"  Completeness: {df['completeness'].mean():.2f} ± {df['completeness'].std():.2f}")
        print(f"  Overall:      {df['overall_quality'].mean():.2f} ± {df['overall_quality'].std():.2f}")
        
        print(f"\nIssue Flags:")
        hallucination_rate = df['hallucination'].sum() / len(df) * 100
        escalation_rate = df['escalation_needed'].sum() / len(df) * 100
        bias_rate = df['bias'].sum() / len(df) * 100
        
        print(f"   Hallucination Rate:  {hallucination_rate:.1f}% ({df['hallucination'].sum()} cases)")
        print(f"   Escalation Needed:   {escalation_rate:.1f}% ({df['escalation_needed'].sum()} cases)")
        print(f"   Bias Detected:       {bias_rate:.1f}% ({df['bias'].sum()} cases)")
        
        print(f"\nContainment Metrics:")
        containment_rate = (1 - escalation_rate / 100) * 100
        print(f"  Containment Rate: {containment_rate:.1f}%")
        print(f"  Successfully resolved without human: {len(df) - df['escalation_needed'].sum()}/{len(df)}")
        
        print(f"\nQuality Distribution:")
        quality_excellent = (df['overall_quality'] >= 4.0).sum()
        quality_good = ((df['overall_quality'] >= 3.0) & (df['overall_quality'] < 4.0)).sum()
        quality_poor = (df['overall_quality'] < 3.0).sum()
        
        print(f"  Excellent (4.0+): {quality_excellent} ({quality_excellent/len(df)*100:.1f}%)")
        print(f"  Good (3.0-4.0):   {quality_good} ({quality_good/len(df)*100:.1f}%)")
        print(f"  Poor (<3.0):      {quality_poor} ({quality_poor/len(df)*100:.1f}%)")

def main():
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
        print("\nLoading GenAI responses data...")
        df = pd.read_csv(responses_path)
        
        print(f"\nAvailable columns: {', '.join(df.columns.tolist())}")
        
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
        
        print("\nInitializing LLM Judge with Groq...")
        try:
            judge = LLMJudge()
            print("Groq client initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Groq client: {str(e)}")
            print("Please ensure you have set the GROQ_API_KEY environment variable")
            return
        
        print(f"\nStarting LLM Judge evaluation...")
        eval_df = judge.evaluate_dataset(
            df,
            query_col=query_col,
            response_col=response_col,
            sample_size=100
        )
        
        results = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_evaluated': len(eval_df),
            'avg_accuracy': float(eval_df['accuracy'].mean()),
            'avg_empathy': float(eval_df['empathy'].mean()),
            'avg_completeness': float(eval_df['completeness'].mean()),
            'avg_overall_quality': float(eval_df['overall_quality'].mean()),
            'hallucination_rate': float(eval_df['hallucination'].mean() * 100),
            'escalation_rate': float(eval_df['escalation_needed'].mean() * 100),
            'containment_rate': float((1 - eval_df['escalation_needed'].mean()) * 100),
            'bias_rate': float(eval_df['bias'].mean() * 100),
            'quality_distribution': {
                'excellent': int((eval_df['overall_quality'] >= 4.0).sum()),
                'good': int(((eval_df['overall_quality'] >= 3.0) & (eval_df['overall_quality'] < 4.0)).sum()),
                'poor': int((eval_df['overall_quality'] < 3.0).sum())
            },
            'samples': eval_df.head(20).to_dict('records')
        }
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(data_dir, f"llm_judge_results_{timestamp}.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        csv_output_path = os.path.join(data_dir, f"llm_judge_evaluations_{timestamp}.csv")
        eval_df.to_csv(csv_output_path, index=False)
        
        print(f"\n{'='*80}")
        print("LLM JUDGE EVALUATION COMPLETE")
        print('='*80)
        print(f"Results saved to: {output_path}")
        print(f"Full evaluations saved to: {csv_output_path}")
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

        
if __name__ == "__main__":
    main()

