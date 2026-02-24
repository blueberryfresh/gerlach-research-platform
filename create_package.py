"""
Automated Package Creator for Big5 Personality LLMs
Creates a clean, shareable package for your research partner
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Files to include in the package
ESSENTIAL_FILES = [
    # Core application
    'composite_big5_llms.py',
    'unified_composite_web.py',
    'requirements.txt',
    
    # Documentation
    'START_HERE.txt',  # First file to read
    'INSTALLATION_AND_OPERATION_GUIDE.md',  # Main guide for users
    'QUICK_REFERENCE_CARD.txt',  # Quick reference
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

def create_package():
    """Create a clean package for sharing"""
    
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
    print(f"Package created successfully!")
    print(f"  Location: {package_dir}")
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
    
    # Instructions
    print("Next steps:")
    print("1. Review the package folder to ensure everything looks correct")
    print("2. Right-click the folder → 'Send to' → 'Compressed (zipped) folder'")
    print(f"3. Upload '{package_name}.zip' to Google Drive")
    print("4. Share the link with your research partner")
    print()
    print("Your partner should:")
    print("1. Download and extract the ZIP")
    print("2. Read README_FOR_SHARING.md")
    print("3. Follow SETUP_INSTRUCTIONS.md")
    print()
    print("="*70)
    
    return package_dir

def create_zip_package():
    """Create and zip the package in one step"""
    import zipfile
    
    package_dir = create_package()
    
    print("\nCreating ZIP file...")
    zip_name = f"{package_dir.name}.zip"
    zip_path = package_dir.parent / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in package_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(package_dir.parent)
                zipf.write(file, arcname)
                print(f"  Adding: {file.name}")
    
    zip_size = zip_path.stat().st_size / (1024 * 1024)
    print()
    print("="*70)
    print(f"ZIP file created: {zip_name}")
    print(f"Size: {zip_size:.2f} MB")
    print(f"Location: {zip_path}")
    print("="*70)
    print()
    print("✅ Ready to upload to Google Drive!")
    print()
    
    return zip_path

if __name__ == "__main__":
    try:
        print("\nChoose packaging option:")
        print("1. Create folder only (you zip it manually)")
        print("2. Create folder AND zip file (recommended)")
        print()
        
        choice = input("Enter choice (1 or 2): ").strip()
        print()
        
        if choice == "1":
            create_package()
        elif choice == "2":
            create_zip_package()
        else:
            print("Invalid choice. Running option 2 (create and zip)...")
            create_zip_package()
        
        print("\n✅ Done! Check the package before sharing.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")
