"""
Fraud Detection Script
Identifies suspicious transactions with random alphanumeric merchant codes.
"""
import pandas as pd
import re
from pathlib import Path


def is_suspicious_merchant(libelle):
    """
    Detect suspicious merchant codes.
    
    Patterns:
    - ACHAT CB followed by random alphanumeric string (no real merchant name)
    - Examples: 3KAYmqgRbSOO, 0qv5sShXwWIa
    """
    # Pattern: ACHAT CB followed by alphanumeric code
    pattern = r'ACHAT CB ([0-9a-zA-Z]+)'
    match = re.search(pattern, libelle)
    
    if not match:
        return False
    
    merchant_code = match.group(1)
    
    # Exclude known legitimate merchants (even partial matches)
    known_merchants = [
        'CARREFOUR', 'FRANPRIX', 'PICARD', 'MONOPRIX', 'AUCHAN',
        'SNCF', 'RATP', 'Spotify', 'Netflix', 'Amazon',
        'Nintendo', 'Apple', 'Google', 'Microsoft',
        'LEROY', 'IKEA', 'DECATHLON', 'FNAC',
        'RELAY', 'PHARMACIE', 'BOULANGERIE', 'PAUL'
    ]
    
    for merchant in known_merchants:
        if merchant.upper() in libelle.upper():
            return False
    
    # Check if merchant code looks random (mixed case + numbers, 8+ chars)
    # Real merchants usually have: ALL CAPS or readable words
    # Fraud codes: random mixed case like "FfYtIHZg4ELb", "3KAYmqgRbSOO"
    
    if len(merchant_code) >= 8:
        has_lowercase = any(c.islower() for c in merchant_code)
        has_uppercase = any(c.isupper() for c in merchant_code)
        has_numbers = any(c.isdigit() for c in merchant_code)
        
        # Random pattern: mixed case AND numbers
        if has_lowercase and has_uppercase and has_numbers:
            return True
        
        # Or: starts with number and has mixed case
        if merchant_code[0].isdigit() and has_lowercase and has_uppercase:
            return True
    
    return False


def detect_fraud(input_file, output_file=None, amount_threshold=5.0):
    """
    Detect potentially fraudulent transactions.
    
    Args:
        input_file: Path to transactions CSV
        output_file: Path to save flagged transactions (optional)
        amount_threshold: Flag transactions below this amount (default: 5€)
    """
    print("🔍 Fraud Detection Script")
    print("="*70)
    
    # Load data
    print(f"\n📂 Loading: {input_file}")
    df = pd.read_csv(input_file, sep=';', decimal=',')
    df['Date'] = pd.to_datetime(df['Date'])
    
    print(f"✅ {len(df)} transactions loaded")
    
    # Detect suspicious transactions
    print(f"\n🚨 Detecting suspicious patterns...")
    print(f"   Criteria: Random merchant codes + amount < {amount_threshold}€")
    
    suspicious = df[
        (df['Libellé'].apply(is_suspicious_merchant)) &
        (df['Montant'] < 0) &
        (df['Montant'] > -amount_threshold)
    ].copy()
    
    print(f"\n⚠️  Found {len(suspicious)} SUSPICIOUS transactions!")
    
    if len(suspicious) == 0:
        print("✅ No fraud detected - all transactions look legitimate")
        return
    
    # Sort by date
    suspicious = suspicious.sort_values('Date')
    
    # Summary
    print(f"\n📊 Fraud Summary:")
    print(f"   Count: {len(suspicious)} transactions")
    print(f"   Date range: {suspicious['Date'].min().date()} to {suspicious['Date'].max().date()}")
    print(f"   Total amount: {suspicious['Montant'].sum():.2f}€")
    print(f"   Average: {suspicious['Montant'].mean():.2f}€")
    
    # List all suspicious transactions
    print(f"\n🔴 SUSPICIOUS TRANSACTIONS:")
    print("-"*70)
    for _, row in suspicious.iterrows():
        print(f"{row['Date'].date()} | {row['Montant']:>7.2f}€ | {row['Libellé'][:60]}")
    
    # Extract suspicious merchant codes
    print(f"\n🏷️  Suspicious Merchant Codes:")
    codes = suspicious['Normalized'].unique()
    for code in codes:
        count = len(suspicious[suspicious['Normalized'] == code])
        total = suspicious[suspicious['Normalized'] == code]['Montant'].sum()
        print(f"   {code}: {count}x = {total:.2f}€")
    
    # Save report
    if output_file:
        suspicious.to_csv(output_file, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        print(f"\n💾 Saved to: {output_file}")
    
    # Recommendations
    print(f"\n⚡ RECOMMENDED ACTIONS:")
    print("   1. Review each transaction carefully")
    print("   2. Verify with your bank statement")
    print("   3. If fraudulent, contact your bank IMMEDIATELY")
    print("   4. Request card replacement if fraud confirmed")
    print("   5. File a dispute for unauthorized charges")
    
    print(f"\n💡 To categorize as fraud, add to category_mapping.csv:")
    for code in codes[:5]:  # Show first 5
        print(f"   {code};Fraud - Investigate")


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_file = project_root / 'data' / '03_final' / 'transactions_categorized.csv'
    output_file = project_root / 'data' / '03_final' / 'suspicious_transactions.csv'
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        print("Run the pipeline first: python src/pipeline.py")
        return
    
    detect_fraud(input_file, output_file, amount_threshold=5.0)
    
    print("\n" + "="*70)
    print("✅ Fraud detection complete!")


if __name__ == '__main__':
    main()
