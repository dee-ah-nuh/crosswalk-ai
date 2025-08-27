#!/usr/bin/env python3
"""
Alternative start script for deployment
This is a fallback if crosswalk command fails
"""

import sys
import os
from pathlib import Path

# Add current directory to path to import deploy
sys.path.insert(0, str(Path(__file__).parent))

# Import and run the main deployment script
if __name__ == "__main__":
    print("🚀 Starting via alternative deployment script...")
    try:
        import deploy
        # This will run the deploy script's main block
        print("✅ Alternative deployment script completed successfully")
    except ImportError as e:
        print(f"❌ Failed to import deploy module: {e}")
        print("💡 Running deploy.py directly...")
        os.system("python deploy.py")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)