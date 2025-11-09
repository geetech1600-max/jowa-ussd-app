#!/usr/bin/env python3
"""
Render initialization script for JOWA deployment
"""
import os
import sys
import subprocess

def init_render():
    print("🚀 Initializing Render deployment for JOWA...")
    
    try:
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Initialize database using simple method
        print("🔄 Initializing database...")
        subprocess.check_call([sys.executable, "init_db.py"])
        
        print("✅ Render initialization complete!")
        return True
            
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = init_render()
    sys.exit(0 if success else 1)