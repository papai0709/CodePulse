#!/usr/bin/env python3
"""
Test script for the unified application
Tests both standard and AI modes
"""

import requests
import json
import time

def test_app_import():
    """Test importing the unified app"""
    print("📱 Testing app import...")
    
    try:
        import app
        print("✅ App import successful")
        
        # Test Flask app instance
        flask_app = getattr(app, 'app', None)
        if flask_app:
            print("✅ Flask app instance found")
        else:
            print("❌ Flask app instance not found")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ App import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False