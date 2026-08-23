"""
Preprocess raw CSV files independently.
Balance anchor: first transaction date = header balance.
"""
import pandas as pd
import re
from pathlib import Path
from datetime import datetime


def extract_timestamp(filepath):
    match = re.search(r'T033(\d+)', filepath.name)
    if match:
        ts = int(match.group(1))
        return ts / 1000 if ts > 9999999999 else ts
    return 0


def parse_header_balance(filepath):
    with open(filepath, encoding='iso-8859-1') as f:
        for line in f:
            if 'Solde (EUROS)' in line or 'Solde' in line:
                parts = line.split(';')
                if len(parts) > 1:
                    try:
                        return float(parts[1].strip().replace(' ', '').replace(',', '.'))
                    except:
                        pass
    return None


def process_file(filepath, output_dir):
    # Get timestamp and create filename
    timestamp = extract_timestamp(filepath)
    date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    output_file = output_dir / f"{date_str}.csv"
    
    # Parse
    header_balance = parse_header_balance(filepath)
    df = pd.read_csv(filepath, encoding='iso-8859-1', delimiter=';', skiprows=6, header=0)
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    df['Montant'] = df['Montant(EUROS)'].str.replace(' ', '').str.replace(',', '.').astype(float)
    df = df[['Date', 'Libellé', 'Montant']].dropna(subset=['Date']).sort_values('Date', ascending=False)
    
    # Calculate balance from first transaction
    df['Balance'] = 0.0
    df.loc[0, 'Balance'] = header_balance
    for i in range(1, len(df)):
        df.loc[i, 'Balance'] = df.loc[i-1, 'Balance'] - df.loc[i-1, 'Montant']
    
    # Sort and recalculate forward
    df = df.sort_values('Date').reset_index(drop=True)
    for i in range(1, len(df)):
        df.loc[i, 'Balance'] = df.loc[i-1, 'Balance'] + df.loc[i, 'Montant']
    
    # Round balance to 2 decimals
    df['Balance'] = df['Balance'].round(2)
    
    # Save
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ {date_str}.csv ({len(df)} txn, {df['Date'].min().date()} to {df['Date'].max().date()})")


def main():
    script_dir = Path(__file__).parent
    raw_dir = script_dir.parent / 'data' / '01_raw'
    int_dir = script_dir.parent / 'data' / '02_intermediate'
    int_dir.mkdir(parents=True, exist_ok=True)
    
    print("🔄 Preprocessing files...")
    for filepath in sorted(raw_dir.glob('*.csv')):
        process_file(filepath, int_dir)
    print("✨ Done!")


if __name__ == "__main__":
    main()
