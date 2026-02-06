"""Configuration and setup utility"""

import os
from pathlib import Path


def ensure_directories():
    """Create necessary directories if they don't exist"""
    
    directories = [
        "agents",
        "graph", 
        "utils",
        "outputs",
        "sample_data",
        "temp_uploads"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✓ All directories verified")


def check_dependencies():
    """Check if all required packages are installed"""
    
    required_packages = [
        "streamlit",
        "langchain",
        "langgraph",
        "pandas",
        "numpy",
        "matplotlib",
        "seaborn",
        "plotly",
        "python-dotenv",
        "scipy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies installed")
    return True


def check_env_file():
    """Check if .env file exists and has API key"""
    
    if not os.path.exists(".env"):
        print("❌ .env file not found")
        print("Create .env file with: cp .env.example .env")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "sk-or-v1-" not in content:
            print("⚠️ Warning: OPENROUTER_API_KEY not properly configured")
            return False
    
    print("✓ .env file configured")
    return True


def setup():
    """Run all setup checks"""
    
    print("🔧 Running setup checks...\n")
    
    ensure_directories()
    deps_ok = check_dependencies()
    env_ok = check_env_file()
    
    print("\n" + "=" * 50)
    
    if deps_ok and env_ok:
        print("✅ Setup complete! Ready to run:")
        print("   streamlit run app.py")
    else:
        print("⚠️ Please fix the issues above before running")
    
    print("=" * 50)


if __name__ == "__main__":
    setup()
