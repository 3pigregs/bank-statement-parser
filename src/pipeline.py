"""
Master pipeline for personal finance analysis.
Runs full workflow: preprocess -> concatenate -> classify -> dashboard
Categorization (personal, optional) can be layered on top afterwards.
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

    # Step 2: Check for coverage gaps between exports (warning only, doesn't stop the pipeline)
    if not run_script(script_dir / 'check_data_gaps.py',
                     "Step 2: Check date coverage"):
        return

    # Step 3: Concatenate preprocessed files
    if not run_script(script_dir / 'concatenate_files.py',
                     "Step 3: Concatenate files"):
        return

    # Step 4: Classify generic transaction types (no personal data needed)
    if not run_script(script_dir / 'classify_type.py',
                     "Step 4: Classify transaction types"):
        return

    # Step 5: Create dashboard - works from Type alone, no personal data required
    if not run_script(script_dir / 'create_dashboard.py',
                     "Step 5: Create finance dashboard"):
        return

    # Step 6: Extract categories (reference only, optional personal enrichment)
    if not run_script(script_dir / 'extract_categories.py',
                     "Step 6: Extract transaction categories (reference)"):
        return

    # Step 7: Apply categories, only if a personal mapping exists
    mapping_file = project_root / 'data' / '03_final' / 'category_mapping.csv'

    if mapping_file.exists():
        if not run_script(script_dir / 'apply_categories.py',
                         "Step 7: Apply categories from mapping"):
            return
    else:
        print(f"\n{'='*70}")
        print("⚠️  Step 7: SKIPPED - No category mapping found (optional)")
        print('='*70)
        print(f"\nTo add personal categorization on top of the dashboard:")
        print(f"1. Review: data/03_final/transaction_categories.csv")
        print(f"2. Create: data/03_final/category_mapping.csv")
        print(f"   Format: Normalized,Category")
        print(f"3. Re-run pipeline")

    # Final summary
    print("\n" + "="*70)
    print("✨ PIPELINE COMPLETE!")
    print("="*70)

    print("\n📂 Generated files:")
    print("   📊 data/02_intermediate/*.csv - Preprocessed individual files")
    print("   💰 data/03_final/transactions_consolidated.csv - All transactions, with Type")
    print("   📈 data/03_final/finance_dashboard.html - Dashboard (always generated)")
    print("   📋 data/03_final/transaction_categories.csv - Reference (distinct merchants)")

    if mapping_file.exists():
        print("   🏷️  data/03_final/transactions_categorized.csv - With personal categories")
    else:
        print("   ⚠️  data/03_final/transactions_categorized.csv - NOT created (no mapping)")

    print("\n💡 Next steps:")
    if not mapping_file.exists():
        print("   • [Optional] Create category_mapping.csv for personal category breakdowns")
    else:
        print("   • Add new entries to category_mapping.csv as needed")
    print("   • Re-run pipeline when you add new CSV files")

    print("\n🌐 Open finance_dashboard.html in your browser!")


if __name__ == "__main__":
    main()
