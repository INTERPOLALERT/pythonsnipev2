"""
Python Version Checker for SuperGrokSnipV1
Run this to check your Python installation
"""

import sys
import platform
import subprocess

print("=" * 70)
print("  PYTHON VERSION CHECKER")
print("=" * 70)
print()

# Check Python version
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Python Version Info: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
print()

# Check if 64-bit
is_64bit = sys.maxsize > 2**32
print(f"64-bit Python: {'Yes' if is_64bit else 'No (32-bit)'}")
print()

# Check OS
print(f"Operating System: {platform.system()} {platform.release()}")
print(f"OS Version: {platform.version()}")
print()

# Check pip
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, text=True)
    print(f"pip: {result.stdout.strip()}")
except Exception as e:
    print(f"pip: NOT FOUND or ERROR - {e}")
print()

# Recommendations
print("=" * 70)
print("  RECOMMENDATIONS FOR THIS BOT")
print("=" * 70)
print()

major, minor = sys.version_info.major, sys.version_info.minor

if major == 3 and minor in [10, 11]:
    print("✅ Your Python version is PERFECT for this bot!")
    print(f"   Python {major}.{minor} fully supports all features.")
elif major == 3 and minor >= 12:
    print("⚠️  Warning: Python 3.12+ detected")
    print("   Some packages (like Prophet) may have issues.")
    print("   Bot will work but with limited AI features.")
elif major == 3 and minor < 10:
    print("❌ Python version too old")
    print("   Please upgrade to Python 3.10 or 3.11")
    print("   Download from: https://www.python.org/downloads/")
else:
    print("❌ Python 2 detected - NOT SUPPORTED")
    print("   Please install Python 3.10 or 3.11")

print()
print("=" * 70)
print()
print("Once you know your Python version, tell me and I'll configure")
print("the bot specifically for your setup.")
print()
input("Press ENTER to exit...")
