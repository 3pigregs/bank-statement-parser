"""
Apply categories from persistent mapping file to transactions.
Fallback: "Uncategorized" if not in mapping.
"""
import pandas as pd
import re
from pathlib import Path


def normalize_description(desc):
    """Clean transaction description (same logic as extract_categories.py)."""
    desc = desc.replace('"', '').replace("'", '')
    desc = re.sub(r'REF\s*:.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'REFERENCE\s*:.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'PRESTATIONS\s+.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'RMBT\s+.*', '', desc, flags=re.IGNORECASE)
    desc = re.sub(r'VIREMENT EHG\s+.*', '', desc, flags=re.IGNORECASE)
    
    if 'VIREMENT DE TOTALENERGIES' in desc and 'VIR TotalEnergies' in desc:
        desc = 'VIREMENT DE TOTALENERGIES'
    
    desc = re.sub(r'\d{2}[./]\d{2}[./]\d{2}', '', desc)
    desc = re.sub(r'A\s+\d{2}H\d{2}\s+RETRAIT DAB.*', 'RETRAIT DAB', desc)
    
    virement_match = re.match(r'(VIREMENT INSTANTANE A\s+\w+\s+\w+)', desc)
    if virement_match:
        desc = virement_match.group(1)
    
    desc = re.sub(r'EUR\s+[\d,\.]+', '', desc)
    desc = re.sub(r'CARTE NUMERO\s+\d+', '', desc)
    desc = re.sub(r'CARTE NO\s+\d+', '', desc)
    desc = re.sub(r'\b[A-Z]{1,3}\d+[A-Z0-9]*\b', '', desc)
    desc = desc.replace(',', '')
    
    words = desc.split()
    if len(words) > 3:
        pattern_len = len(words) // 3
        if pattern_len > 0:
            pattern = ' '.join(words[:pattern_len])
            if desc.count(pattern) >= 2:
                desc = pattern
    
    desc = ' '.join(desc.split())
    return desc.strip()


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    transactions_file = project_root / 'data' / '03_final' / 'transactions_consolidated.csv'
    mapping_file = project_root / 'data' / '03_final' / 'category_mapping.csv'
    output_file = project_root / 'data' / '03_final' / 'transactions_categorized.csv'
    
    # Load transactions
    print("📊 Loading transactions...")
    df = pd.read_csv(transactions_file, sep=';', decimal=',')
    print(f"✅ {len(df)} transactions")
    
    # Load category mapping (try both formats)
    if not mapping_file.exists():
        print(f"\n⚠️  Mapping file not found: {mapping_file}")
        print("Please create category_mapping.csv with columns: Normalized;Category")
        print("\nExample:")
        print("Normalized;Category")
        print("ACHAT CB CARREFOUR CITY;Groceries")
        print("VIREMENT DE TOTALENERGIES;Salary")
        return
    
    # Try semicolon first (Excel FR format), fallback to comma
    mapping = pd.read_csv(mapping_file, sep=';')
    if 'Normalized' not in mapping.columns:
        # Fallback to comma separator
        mapping = pd.read_csv(mapping_file, sep=',')
    
    print(f"✅ {len(mapping)} categories loaded")
    
    # Create lookup dictionary
    category_dict = dict(zip(mapping['Normalized'], mapping['Category']))
    
    # Normalize and categorize
    print("\n🔄 Applying categories...")
    df['Normalized'] = df['Libellé'].apply(normalize_description)
    df['Category'] = df['Normalized'].map(category_dict).fillna('Uncategorized')
    
    # Stats
    categorized = (df['Category'] != 'Uncategorized').sum()
    uncategorized = (df['Category'] == 'Uncategorized').sum()
    
    print(f"   ✅ Categorized: {categorized}")
    print(f"   ⚠️  Uncategorized: {uncategorized}")
    
    # Save
    output_columns = ['Date', 'Libellé', 'Montant', 'Balance']
    if 'Type' in df.columns:
        output_columns.append('Type')
    output_columns += ['Normalized', 'Category']
    output = df[output_columns]
    output.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';', decimal=',')
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Category summary
    print("\n📊 Categories used:")
    cat_summary = df[df['Category'] != 'Uncategorized']['Category'].value_counts()
    for cat, count in cat_summary.head(10).items():
        print(f"   {cat}: {count} transactions")
    
    if uncategorized > 0:
        print(f"\n💡 Tip: Add more entries to category_mapping.csv to reduce uncategorized transactions")


if __name__ == "__main__":
    main()
