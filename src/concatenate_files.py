"""
Concatenate preprocessed files.
For overlapping dates: keep data from latest file.
"""
import pandas as pd
from pathlib import Path


def concatenate_files(int_dir, output_file):
    """Concatenate all CSV files, keeping latest data for overlaps."""
    
    # Get all CSV files sorted by filename (date) - newest first
    csv_files = sorted(int_dir.glob('*.csv'), reverse=True)
    
    if not csv_files:
        print("⚠️  No files found in int directory")
        return None
    
    print(f"📂 Found {len(csv_files)} file(s):")
    for f in csv_files:
        print(f"   {f.name}")
    
    all_data = []
    seen_dates = set()
    
    # Process newest to oldest
    for filepath in csv_files:
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Keep only dates we haven't seen yet
        df_new = df[~df['Date'].isin(seen_dates)]
        
        if len(df_new) > 0:
            all_data.append(df_new)
            seen_dates.update(df_new['Date'])
            overlap = len(df) - len(df_new)
            print(f"   ✅ {filepath.name}: {len(df_new)} transactions kept, {overlap} overlaps excluded")
        else:
            print(f"   ⚠️  {filepath.name}: fully overlapped, skipped")
    
    # Concatenate and sort
    result = pd.concat(all_data, ignore_index=True).sort_values('Date').reset_index(drop=True)
    
    # Save
    result.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';', decimal=',')
    
    print(f"\n💾 Saved: {output_file}")
    print(f"✅ Total: {len(result)} transactions ({result['Date'].min().date()} to {result['Date'].max().date()})")
    
    return result


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    int_dir = project_root / 'data' / '02_intermediate'
    final_dir = project_root / 'data' / '03_final'
    final_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = final_dir / 'transactions_consolidated.csv'
    
    print("🔗 Concatenating files...\n")
    df = concatenate_files(int_dir, output_file)
    
    if df is not None:
        print(f"\n📈 Summary:")
        print(f"   Starting balance: {df['Balance'].iloc[0]:.2f}€")
        print(f"   Final balance: {df['Balance'].iloc[-1]:.2f}€")
        print(f"   Min balance: {df['Balance'].min():.2f}€")
        print(f"   Max balance: {df['Balance'].max():.2f}€")
    
    print("\n✨ Done!")


if __name__ == "__main__":
    main()
