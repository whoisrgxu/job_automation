#!/usr/bin/env python3
"""
Setup script for LinkedIn job scraper
"""
import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up LinkedIn Job Scraper")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your pip installation.")
        sys.exit(1)
    
    # Install Playwright browsers
    if not run_command("playwright install chromium", "Installing Playwright browser"):
        print("❌ Failed to install Playwright browser.")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        try:
            with open('env_example.txt', 'r') as src, open('.env', 'w') as dst:
                dst.write(src.read())
            print("✅ .env file created. Please edit it with your credentials.")
        except Exception as e:
            print(f"⚠️  Could not create .env file: {e}")
            print("Please manually copy env_example.txt to .env and edit it.")
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit config.py to customize your search parameters")
    print("2. Edit .env file with your LinkedIn credentials (optional)")
    print("3. Add proxy servers to config.py (optional but recommended)")
    print("4. Run: python run_scraper.py")
    print("\nFor testing proxies, run: python test_proxies.py")


if __name__ == "__main__":
    main()
