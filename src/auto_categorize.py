"""
Auto-categorize transactions using Claude API.
Generates category_mapping.csv from transaction_categories.csv
"""
import pandas as pd
import json
import os
from pathlib import Path

# Try to load from .env file
try:
    from dotenv import load_dotenv
    # Try different locations for .env file
    from pathlib import Path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Try loading from project root first, then current directory
    if (project_root / '.env').exists():
        load_dotenv(project_root / '.env')
    elif Path('.env').exists():
        load_dotenv()
    
except ImportError:
    print("⚠️  python-dotenv not installed (optional)")
    print("   Install with: pip install python-dotenv --break-system-packages")
    print("   Or set environment variable manually")
    pass

# Check if anthropic is installed
try:
    from anthropic import Anthropic
except ImportError:
    print("❌ Error: anthropic package not installed")
    print("\nInstall with:")
    print("   pip install anthropic --break-system-packages")
    exit(1)


def categorize_batch(client, transactions_batch):
    """Send batch of transactions to Claude for categorization."""
    
    # Prepare transaction list
    txn_list = "\n".join([
        f"{i+1}. {row['Normalized']} (avg: {row['Avg_Amount']:.2f}€, count: {row['Count']})"
        for i, row in enumerate(transactions_batch)
    ])
    
    prompt = f"""Categorize these banking transactions into appropriate categories.

Transactions:
{txn_list}

Instructions:
- Assign ONE category per transaction
- Use standard categories like: Groceries, Transport, Rent/Mortgage, Utilities, Healthcare, Entertainment, Shopping, Salary, Personal Transfer, Cash Withdrawal, Credit Card, Subscriptions, Dining, Insurance, Taxes, Education, Gifts, Clothing, Home Improvement, Professional Services
- Be consistent (e.g., all groceries → "Groceries")
- Consider transaction description and typical amount
- Respond ONLY with a JSON array of categories in order

Example response:
["Groceries", "Transport", "Salary", ...]

Categories:"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract text from response
        text = response.content[0].text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith('```'):
            text = text.split('\n', 1)[1]
            text = text.rsplit('```', 1)[0]
        
        # Parse JSON
        categories = json.loads(text)
        return categories, None
        
    except Exception as e:
        return None, str(e)


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    input_file = project_root / 'data' / '03_final' / 'transaction_categories.csv'
    output_file = project_root / 'data' / '03_final' / 'category_mapping.csv'
    
    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found")
        print("\n📋 Troubleshooting:")
        print("   1. Run diagnostic: python src/check_env.py")
        print("   2. Make sure .env file is in project root")
        print("   3. Make sure .env contains: ANTHROPIC_API_KEY=sk-ant-api03-...")
        print("\n🔧 Or install packages:")
        print("   pip install python-dotenv --break-system-packages")
        print("\n🌐 Get API key from: https://console.anthropic.com/")
        return
    
    client = Anthropic(api_key=api_key)
    
    print("🤖 AI-Powered Transaction Categorization")
    print("="*70)
    
    # Load transactions
    df = pd.read_csv(input_file)
    print(f"📊 Loaded {len(df)} transaction types")
    
    # Process in batches
    batch_size = 20
    all_categories = []
    
    print(f"\n🔄 Processing in batches of {batch_size}...")
    
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        print(f"   Batch {batch_num}/{total_batches} ({len(batch)} transactions)...", end=' ')
        
        categories, error = categorize_batch(client, batch.to_dict('records'))
        
        if error:
            print(f"❌\n")
            print(f"   Error: {error}")
            
            # If first batch fails, stop immediately
            if batch_num == 1:
                print(f"\n❌ Failed on first batch - stopping")
                print(f"\nCommon issues:")
                print(f"   • Check internet connection")
                print(f"   • Verify API key is correct")
                print(f"   • Check API credits at console.anthropic.com")
                return
            
            # If later batch fails, save partial progress
            print(f"\n⚠️  Saving partial progress ({len(all_categories)} categorized)...")
            
            # Fill remaining with Uncategorized
            remaining = len(df) - len(all_categories)
            all_categories.extend(['Uncategorized'] * remaining)
            break
        
        all_categories.extend(categories)
        print("✅")
    
    # Check if we have all categories
    if len(all_categories) != len(df):
        print(f"\n⚠️  Warning: Got {len(all_categories)} categories for {len(df)} transactions")
        # Fill any missing with Uncategorized
        while len(all_categories) < len(df):
            all_categories.append('Uncategorized')
    
    # Create mapping
    mapping = pd.DataFrame({
        'Normalized': df['Normalized'],
        'Category': all_categories
    })
    
    # Save
    mapping.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved to: {output_file}")
    
    # Summary
    print(f"\n📊 Category Summary:")
    cat_counts = mapping['Category'].value_counts()
    
    uncategorized_count = (mapping['Category'] == 'Uncategorized').sum()
    categorized_count = len(mapping) - uncategorized_count
    
    if uncategorized_count > 0:
        print(f"   ✅ Categorized: {categorized_count}")
        print(f"   ⚠️  Uncategorized: {uncategorized_count}")
        print()
    
    for cat, count in cat_counts.head(15).items():
        if cat != 'Uncategorized':
            print(f"   {cat}: {count}")
    
    print(f"\n✨ Done! You can now:")
    print(f"   1. Review/edit: {output_file}")
    if uncategorized_count > 0:
        print(f"   2. [Optional] Manually categorize the {uncategorized_count} uncategorized items")
        print(f"   3. Run: python src/apply_categories.py")
    else:
        print(f"   2. Run: python src/apply_categories.py")


if __name__ == "__main__":
    main()
