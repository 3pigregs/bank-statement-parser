"""
Master pipeline for personal finance analysis.
Runs full workflow: preprocess → concatenate → categorize → dashboard
"""
from pathlib import Path
import subprocess
import sys


def run_script(script_path: Path, description: str):
    """Run a Python script and handle errors."""
    print(f"\n{'='*70}")
    print(f"▶️  {description}")
    print('='*70)
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"\n❌ Error running {script_path.name}")
        return False
    
    print(f"✅ {description} completed")
    return True


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("\n" + "="*70)
    print("🚀 PERSONAL FINANCE PIPELINE")
    print("="*70)
    
    # Step 1: Preprocess raw files
    if not run_script(script_dir / 'preprocess_files.py', 
                     "Step 1: Preprocess raw CSV files"):
        return
    
    # Step 2: Concatenate preprocessed files
    if not run_script(script_dir / 'concatenate_files.py',
                     "Step 2: Concatenate files"):
        return
    
    # Step 3: Classify generic transaction types (no personal data needed)
    if not run_script(script_dir / 'classify_type.py',
                     "Step 3: Classify transaction types"):
        return

    # Step 4: Extract categories (reference only)
    print(f"\n{'='*70}")
    print("▶️  Step 4: Extract transaction categories (reference)")
    print('='*70)
    if not run_script(script_dir / 'extract_categories.py',
                     "   Generating transaction_categories.csv"):
        return

    # Step 5: Apply categories
    mapping_file = project_root / 'data' / '03_final' / 'category_mapping.csv'
    
    if mapping_file.exists():
        if not run_script(script_dir / 'apply_categories.py',
                         "Step 5: Apply categories from mapping"):
            return
    else:
        print(f"\n{'='*70}")
        print("⚠️  Step 5: SKIPPED - No category mapping found")
        print('='*70)
        print(f"\nTo enable categorization:")
        print(f"1. Review: data/03_final/transaction_categories.csv")
        print(f"2. Create: data/03_final/category_mapping.csv")
        print(f"   Format: Normalized,Category")
        print(f"3. Re-run pipeline")

    # Step 6: Create dashboard
    print(f"\n{'='*70}")
    print("▶️  Step 6: Create finance dashboard")
    print('='*70)
    
    if not run_script(script_dir / 'create_dashboard.py',
                     "   Generating dashboard"):
        return
    
    # Final summary
    print("\n" + "="*70)
    print("✨ PIPELINE COMPLETE!")
    print("="*70)
    
    print("\n📂 Generated files:")
    print("   📊 data/02_intermediate/*.csv - Preprocessed individual files")
    print("   💰 data/03_final/transactions_consolidated.csv - All transactions")
    print("   📋 data/03_final/transaction_categories.csv - Reference (269 types)")

    if mapping_file.exists():
        print("   🏷️  data/03_final/transactions_categorized.csv - With categories")
    else:
        print("   ⚠️  data/03_final/transactions_categorized.csv - NOT created (no mapping)")

    print("   📈 data/03_final/finance_dashboard.html - Dashboard")
    
    print("\n💡 Next steps:")
    if not mapping_file.exists():
        print("   1. Create category_mapping.csv to enable categorization")
        print("   2. Re-run: python src/pipeline.py")
    else:
        print("   • Add new categories to category_mapping.csv as needed")
        print("   • Re-run pipeline when you add new CSV files")
    
    print("\n🌐 Open finance_dashboard.html in your browser!")


if __name__ == "__main__":
    main()
