"""
Read Test - SharePoint
Reads files from your synced SharePoint folder.
"""
from pathlib import Path

# Your SharePoint synced folder
SHAREPOINT_FOLDER = Path(r"C:\Users\J0102113\TotalEnergies\test_data_access - Documents")

print("="*70)
print("📖 Read Test - SharePoint")
print("="*70)

# Check if folder exists
print(f"\n📁 Target folder: {SHAREPOINT_FOLDER}")

if not SHAREPOINT_FOLDER.exists():
    print("❌ Folder not found!")
    exit(1)

print("✅ Folder exists!")

# List all files in SharePoint folder
print(f"\n📂 Files in SharePoint folder:")
print("-"*70)

files = list(SHAREPOINT_FOLDER.iterdir())

if not files:
    print("   (empty folder)")
else:
    for item in files:
        if item.is_file():
            size = item.stat().st_size
            print(f"   📄 {item.name} ({size} bytes)")
        elif item.is_dir():
            print(f"   📁 {item.name}/")

# Try to read hello_world.txt
hello_file = SHAREPOINT_FOLDER / "hello_world.txt"

print(f"\n📖 Reading: {hello_file.name}")
print("-"*70)

if not hello_file.exists():
    print("❌ File not found!")
    print("\nPlease run hello_sharepoint.py first to create the file.")
else:
    try:
        content = hello_file.read_text(encoding='utf-8')
        print(content)
        print("-"*70)
        print("✅ File read successfully!")
        
        # Stats
        lines = content.count('\n') + 1
        chars = len(content)
        print(f"\n📊 Stats:")
        print(f"   Lines: {lines}")
        print(f"   Characters: {chars}")
        print(f"   Size: {hello_file.stat().st_size} bytes")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

# Bonus: Test reading CSV if exists
print(f"\n📊 Looking for CSV files...")

csv_files = list(SHAREPOINT_FOLDER.glob("*.csv"))

if csv_files:
    print(f"✅ Found {len(csv_files)} CSV file(s):")
    
    for csv_file in csv_files:
        print(f"\n   📄 {csv_file.name}")
        
        # Try to read with pandas
        try:
            import pandas as pd
            df = pd.read_csv(csv_file, sep=';', decimal=',', nrows=5)
            print(f"      Rows (sample): {len(df)}")
            print(f"      Columns: {list(df.columns)}")
            print(f"\n      Preview:")
            print(f"      {df.to_string(index=False)}")
            print("      ✅ CSV read successfully!")
            
        except ImportError:
            print("      ⚠️  pandas not installed (pip install pandas)")
        except Exception as e:
            print(f"      ❌ Error: {e}")
else:
    print("   No CSV files found")
    print("\n   💡 To test CSV reading:")
    print("      1. Create a CSV in SharePoint (browser)")
    print("      2. Or copy a CSV to this folder")
    print("      3. Re-run this script")

print("\n" + "="*70)
print("🎉 READ TEST COMPLETE")
print("="*70)
print("\n✅ Python can read from SharePoint!")
print("\nNext steps:")
print("   - Your finance scripts can read bank CSVs from SharePoint")
print("   - Your finance scripts can write results to SharePoint")
print("   - Team can access shared dashboards")
