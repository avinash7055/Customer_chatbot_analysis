import pandas as pd
import os
from pathlib import Path

def prepare_data(excel_path: str, output_dir: str = "data"):
    print("="*80)
    print("SkyRocket Data Preparation - Netomi AI Automation Engineer Submission")
    print("="*80)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\nLoading Excel file: {excel_path}")
    xl_file = pd.ExcelFile(excel_path)
    print(f"Sheets found: {xl_file.sheet_names}")
    
    print("\n1. Processing Queries sheet...")
    queries_df = pd.read_excel(excel_path, sheet_name='Queries')
    print(f"   Shape: {queries_df.shape}")
    print(f"   Columns: {list(queries_df.columns)}")
    
    queries_csv_path = os.path.join(output_dir, "queries.csv")
    queries_df.to_csv(queries_csv_path, index=False)
    print(f"  Saved to: {queries_csv_path}")
    
    print("\n2. Processing GenAI_responses sheet...")
    responses_df = pd.read_excel(excel_path, sheet_name='GenAI_responses')
    print(f"   Shape: {responses_df.shape}")
    print(f"   Columns: {list(responses_df.columns)}")
    
    responses_csv_path = os.path.join(output_dir, "genai_responses.csv")
    responses_df.to_csv(responses_csv_path, index=False)
    print(f"  Saved to: {responses_csv_path}")
    
    print("\n" + "="*80)
    print("INITIAL DATA EXPLORATION")
    print("="*80)
    
    print("\nQueries Dataset:")
    print(f"  Total queries: {len(queries_df):,}")
    print(f"  Null values: {queries_df['Queries'].isnull().sum()}")
    print(f"  Unique queries: {queries_df['Queries'].nunique():,}")
    print(f"  Duplicate rate: {(1 - queries_df['Queries'].nunique() / len(queries_df)) * 100:.2f}%")
    
    print("\n  Sample queries:")
    for i, query in enumerate(queries_df['Queries'].head(5), 1):
        print(f"   {i}. {query}")
    
    print("\nGenAI Responses Dataset:")
    print(f"  Total rows: {len(responses_df):,}")
    print(f"  Null values per column:")
    for col in responses_df.columns:
        null_count = responses_df[col].isnull().sum()
        print(f"      {col}: {null_count} ({null_count/len(responses_df)*100:.1f}%)")
    
    if 'category' in responses_df.columns:
        print("\n   Category distribution:")
        cat_counts = responses_df['category'].value_counts()
        for cat, count in cat_counts.head(10).items():
            print(f"    {cat}: {count:,} ({count/len(responses_df)*100:.1f}%)")
    
    if 'Sub Category' in responses_df.columns:
        print("\n   Top Sub-Categories:")
        subcat_counts = responses_df['Sub Category'].value_counts()
        for subcat, count in subcat_counts.head(10).items():
            print(f"    {subcat}: {count:,} ({count/len(responses_df)*100:.1f}%)")
    
    if 'flags' in responses_df.columns:
        print("\n   Flags distribution:")
        flag_counts = responses_df['flags'].value_counts()
        for flag, count in flag_counts.items():
            print(f"    {flag}: {count:,} ({count/len(responses_df)*100:.1f}%)")
    
    if 'response' in responses_df.columns:
        responses_df['response_length'] = responses_df['response'].astype(str).str.len()
        print("\n   Response length statistics:")
        print(f"    Mean: {responses_df['response_length'].mean():.0f} characters")
        print(f"    Median: {responses_df['response_length'].median():.0f} characters")
        print(f"    Min: {responses_df['response_length'].min():.0f} characters")
        print(f"    Max: {responses_df['response_length'].max():.0f} characters")
    
    print("\n" + "="*80)
    print("Data preparation complete")
    print("="*80)
    
    return queries_df, responses_df

if __name__ == "__main__":
    import sys
    
    excel_path = "../../../../SkyRocket Data_GenAI.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"Warning: Excel file not found at: {excel_path}")
        print(f"Looking in alternative locations...")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        excel_path = os.path.join(os.path.dirname(base_dir), "SkyRocket Data_GenAI.xlsx")
        
        if not os.path.exists(excel_path):
            print(f"ERROR: Cannot find 'SkyRocket Data_GenAI.xlsx'")
            print(f"Please ensure the Excel file is in the parent netomi directory.")
            print(f"Expected location: c:/Users/pc/OneDrive/Desktop/netomi/SkyRocket Data_GenAI.xlsx")
            sys.exit(1)
    
    print(f"Found Excel file: {os.path.abspath(excel_path)}\n")
    
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "data")
    queries_df, responses_df = prepare_data(excel_path, output_dir=output_dir)
