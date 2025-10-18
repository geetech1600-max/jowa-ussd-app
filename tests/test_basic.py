#!/usr/bin/env python3
"""
Basic test without database dependencies
"""

def test_basic_imports():
    """Test basic Python imports"""
    try:
        from flask import Flask, jsonify
        print("✅ Flask imports working!")
        return True
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False

def test_create_app():
    """Test if we can create a Flask app"""
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Jowa App Test"
            
        print("✅ Flask app creation working!")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Basic Jowa App Setup...")
    print("=" * 40)
    
    imports_ok = test_basic_imports()
    app_ok = test_create_app()
    
    print("=" * 40)
    if imports_ok and app_ok:
        print("🎉 Basic setup is working! You can now add database features.")
    else:
        print("❌ Basic setup failed. Check your Python environment.")