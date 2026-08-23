"""
Extract distinct transactions with normalized names for categorization.
Removes dates, card numbers, and quotes from descriptions.
"""
import pandas as pd
import re
from pathlib import Path


def normalize_description(desc):
    """Clean transaction description for grouping."""
    # Remove quotes
    desc = desc.replace('"', '').replace("'", '')
    
    # Remove everything after specific keywords (like REF/REFERENCE)
    desc = re.sub(r'REF\s*:.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'REFERENCE\s*:.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'PRESTATIONS\s+.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'RMBT\s+.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'VIREMENT EHG\s+.*', '', desc, flags=re.IGNORECASE)
    
    # TotalEnergies salary normalization - if contains both patterns, simplify
    if 'VIREMENT DE TOTALENERGIES' in desc and 'VIR TotalEnergies' in desc:
        desc = 'VIREMENT DE TOTALENERGIES'
    
    # Remove dates (DD.MM.YY or DD/MM/YY format)
    desc = re.sub(r'\d{2}[./]\d{2}[./]\d{2}', '', desc)
    
    # Remove times and everything after RETRAIT DAB (ATM withdrawals)
    # Pattern: A HH:HH RETRAIT DAB [location] → RETRAIT DAB
    desc = re.sub(r'A\s+\d{2}H\d{2}\s+RETRAIT DAB.*', 'RETRAIT DAB', desc)
    
    # For VIREMENT INSTANTANE A [FIRSTNAME] [LASTNAME] - keep only first 2 words after "A"
    virement_match = re.match(r'(VIREMENT INSTANTANE A\s+\w+\s+\w+)', desc)
    if virement_match:
        desc = virement_match.group(1)
    
    # Remove EUR amounts (EUR XX,XX)
    desc = re.sub(r'EUR\s+[\d,\.]+', '', desc)
    
    # Remove card numbers
    desc = re.sub(r'CARTE NUMERO\s+\d+', '', desc)
    desc = re.sub(r'CARTE NO\s+\d+', '', desc)
    
    # Remove transaction IDs - handle various patterns:
    # P31296, CA143, P3A227 (alphanumeric codes)
    desc = re.sub(r'\b[A-Z]{1,3}\d+[A-Z0-9]*\b', '', desc)
    
    # Remove commas
    desc = desc.replace(',', '')
    
    # Remove repeated patterns (e.g., "TEXT TEXT TEXT" -> "TEXT")
    words = desc.split()
    if len(words) > 3:
        # Check if pattern repeats
        pattern_len = len(words) // 3
        if pattern_len > 0:
            pattern = ' '.join(words[:pattern_len])
            if desc.count(pattern) >= 2:
                desc = pattern
    
    # Remove extra spaces
    desc = ' '.join(desc.split())
    
    return desc.strip()


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_file = project_root / 'data' / '03_final' / 'transactions_consolidated.csv'
    output_file = project_root / 'data' / '03_final' / 'transaction_categories.csv'
    
    df = pd.read_csv(data_file, sep=';', decimal=',')
    
    # Add normalized description
    df['Normalized'] = df['Libellé'].apply(normalize_description)
    
    # Group by normalized name
    grouped = df.groupby('Normalized').agg({
        'Libellé': 'first',  # Keep one example
        'Montant': ['count', 'mean'],
        'Date': ['min', 'max']
    }).reset_index()
    
    grouped.columns = ['Normalized', 'Example', 'Count', 'Avg_Amount', 'First_Date', 'Last_Date']
    grouped = grouped.sort_values('Normalized')  # Sort alphabetically by normalized name
    
    # Add empty category column
    grouped['Category'] = ''
    
    # Reorder
    result = grouped[['Normalized', 'Category', 'Count', 'Avg_Amount', 'Example', 'First_Date', 'Last_Date']]
    
    result.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';', decimal=',')
    
    print(f"✅ {len(result)} distinct normalized transactions")
    print(f"💾 {output_file}")


if __name__ == "__main__":
    main()
