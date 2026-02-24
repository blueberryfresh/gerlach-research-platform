"""
Automated Package Creator for Big5 Personality LLMs
Automatically creates ZIP package (no user input needed)
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Files to include in the package
ESSENTIAL_FILES = [
    # Core application
    'composite_big5_llms.py',
    'unified_composite_web.py',
    'requirements.txt',
    
    # Documentation
    'START_HERE.txt',
    'INSTALLATION_AND_OPERATION_GUIDE.md',
    'QUICK_REFERENCE_CARD.txt',
    'README_FOR_SHARING.md',
    'SETUP_INSTRUCTIONS.md',
    'QUICK_START_GUIDE.md',
    'VALIDATION_SUMMARY.md',
    'COMPOSITE_PERSONALITIES_DOCUMENTATION.md',
    
    # Launchers
    'start_web.bat',
    'start_web_simple.bat',
    
    # Testing/Demo scripts
    'quick_composite_demo.py',
    'test_composite_personalities.py',
    'interactive_composite_test.py',
]

def create_zip_package():
    """Create and zip the package"""
    
    print("="*70)
    print("Big5 Personality LLMs - Package Creator")
    print("="*70)
    print()
    
    # Get current directory
    source_dir = Path.cwd()
    
    # Create package directory name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    package_name = f"Big5_Personality_LLMs_Package_{timestamp}"
    package_dir = source_dir / package_name
    
    # Remove old package if exists
    if package_dir.exists():
        print(f"Removing old package: {package_name}")
        shutil.rmtree(package_dir)
    
    # Create new package directory
    print(f"Creating package directory: {package_name}")
    package_dir.mkdir()
    
    # Copy files
    print("\nCopying files...")
    copied_count = 0
    missing_count = 0
    
    for filename in ESSENTIAL_FILES:
        source_file = source_dir / filename
        if source_file.exists():
            dest_file = package_dir / filename
            shutil.copy2(source_file, dest_file)
            print(f"  ✓ {filename}")
            copied_count += 1
        else:
            print(f"  ✗ {filename} (not found - skipping)")
            missing_count += 1
    
    print()
    print("="*70)
    print(f"Package folder created!")
    print(f"  Files copied: {copied_count}")
    if missing_count > 0:
        print(f"  Files missing: {missing_count}")
    print("="*70)
    print()
    
    # Calculate package size
    total_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    print(f"Package size: {size_mb:.2f} MB")
    print()
    
    # Create ZIP file
    print("Creating ZIP file...")
    zip_name = f"{package_name}.zip"
    zip_path = package_dir.parent / zip_name
    
    # Remove old ZIP if exists
    if zip_path.exists():
        zip_path.unlink()
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in package_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(package_dir.parent)
                zipf.write(file, arcname)
                print(f"  Adding: {file.name}")
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    print()
    print("="*70)
    print(f"✅ ZIP FILE CREATED SUCCESSFULLY!")
    print("="*70)
    print(f"  Name: {zip_name}")
    print(f"  Size: {zip_size:.2f} MB")
    print(f"  Location: {zip_path}")
    print("="*70)
    print()
    
    print("📤 NEXT STEPS:")
    print("1. Upload this ZIP file to Google Drive")
    print("2. Right-click → 'Get link' → 'Anyone with link can view'")
    print("3. Share the link with your research partner")
    print()
    print("📧 Include in your email:")
    print("   - Download link")
    print("   - Tell them to read START_HERE.txt first")
    print("   - Mention INSTALLATION_AND_OPERATION_GUIDE.md has full instructions")
    print()
    print("="*70)
    print("✅ Package ready to share!")
    print("="*70)
    
    return zip_path

if __name__ == "__main__":
    try:
        create_zip_package()
        print("\n✅ Done! Check the ZIP file before uploading.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nPress Enter to exit...")
    input()
