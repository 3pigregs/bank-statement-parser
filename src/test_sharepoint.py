"""
Hello World - SharePoint Test
Writes a test file to your synced SharePoint folder.
"""
from pathlib import Path
from datetime import datetime

# Your SharePoint synced folder
SHAREPOINT_FOLDER = Path(r"C:\Users\J0102113\TotalEnergies\test_data_access - Documents")

print("="*70)
print("👋 Hello World - SharePoint Test")
print("="*70)

# Check if folder exists
print(f"\n📁 Target folder: {SHAREPOINT_FOLDER}")

if not SHAREPOINT_FOLDER.exists():
    print("❌ Folder not found!")
    print("\nPlease check:")
    print("   1. Path is correct")
    print("   2. SharePoint is synced")
    print("   3. Folder name matches exactly")
    exit(1)

print("✅ Folder exists!")

# Create hello world file
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
content = f"""Hello World from Python!

This file was created by Python on {timestamp}

Test successful! 🎉

Your Python installation can write to SharePoint.
"""

output_file = SHAREPOINT_FOLDER / "hello_world.txt"

print(f"\n📝 Writing file: {output_file.name}")

try:
    output_file.write_text(content, encoding='utf-8')
    print("✅ File written successfully!")
    
    # Verify
    if output_file.exists():
        size = output_file.stat().st_size
        print(f"   Size: {size} bytes")
        print(f"   Path: {output_file}")
        
        print(f"\n📊 Content:")
        print("-"*70)
        print(content)
        print("-"*70)
        
        print(f"\n🎉 SUCCESS!")
        print(f"\nNext steps:")
        print(f"   1. Check SharePoint in browser - file should appear")
        print(f"   2. Wait ~30 seconds for OneDrive sync")
        print(f"   3. Go to: https://totalenergies.sharepoint.com/sites/test_data_access")
        print(f"   4. File 'hello_world.txt' should be there!")
        
    else:
        print("❌ File not found after writing!")
        
except PermissionError:
    print("❌ Permission denied!")
    print("\nPossible issues:")
    print("   - File is open in another program")
    print("   - OneDrive is syncing")
    print("   - No write permissions")
    print("\nSolutions:")
    print("   - Close any programs using this folder")
    print("   - Pause OneDrive sync temporarily")
    print("   - Check folder permissions")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)