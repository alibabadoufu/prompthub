"""
Installation script for Deep Research dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path


def install_package(package):
    """Install a package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Install all required packages."""
    print("🔧 Installing Deep Research Dependencies")
    print("=" * 50)
    
    # Required packages
    packages = [
        "numpy>=1.24.0",
        "langgraph>=0.0.40", 
        "langchain>=0.1.0",
        "langchain-core>=0.1.0",
        "pathlib2>=2.3.0"
    ]
    
    success_count = 0
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        if install_package(package):
            print(f"✅ {package} installed successfully")
            success_count += 1
        else:
            print(f"❌ Failed to install {package}")
    
    print(f"\n📊 Installation Results: {success_count}/{len(packages)} packages installed")
    
    if success_count == len(packages):
        print("🎉 All dependencies installed successfully!")
        print("\nYou can now run:")
        print("  python3 test_deep_research.py")
        print("  python3 deep_research_demo.py")
        print("  python3 -m deep_research.main 'your query' --workspace /workspace")
    else:
        print("⚠️  Some packages failed to install. You may need to install them manually:")
        print("  pip install numpy langgraph langchain langchain-core pathlib2")
    
    return 0 if success_count == len(packages) else 1


if __name__ == "__main__":
    sys.exit(main())