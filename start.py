#!/usr/bin/env python3
"""
Alternative start script for deployment
This is a fallback if crosswalk command fails
"""

import sys
import os
import subprocess
from pathlib import Path

if __name__ == "__main__":
    print("🚀 Starting via alternative deployment script...")
    try:
        # Run deploy.py directly to ensure it stays running
        print("💡 Running deploy.py directly...")
        result = subprocess.run([sys.executable, "deploy.py"], check=True)
        print("✅ Deployment completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed with exit code: {e.returncode}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)