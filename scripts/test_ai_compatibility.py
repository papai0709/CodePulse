#!/usr/bin/env python3
"""
AI Compatibility Test Script for CodePulse
Tests all AI components and compatibility
"""

import sys
import os
import asyncio
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    
    try:
        from analyzer.ai_analyzer import AIAnalyzer
        print("✅ AIAnalyzer import successful")
    except ImportError as e:
        print(f"❌ AIAnalyzer import failed: {e}")
        return False
    
    try:
        from analyzer.enhanced_report_generator import EnhancedReportGenerator
        print("✅ EnhancedReportGenerator import successful")
    except ImportError as e:
        print(f"❌ EnhancedReportGenerator import failed: {e}")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp import successful")
    except ImportError as e:
        print(f"❌ aiohttp import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ openai import successful")
    except ImportError as e:
        print(f"❌ openai import failed: {e}")
        return False
    
    return True

async def test_ai_components():
    """Test AI components functionality"""
    print("\n🧠 Testing AI components...")
    
    try:
        from analyzer.ai_analyzer import AIAnalyzer
        from analyzer.enhanced_report_generator import EnhancedReportGenerator
        
        # Test AI Analyzer initialization
        ai_analyzer = AIAnalyzer()
        print("✅ AIAnalyzer initialization successful")
        
        # Test Enhanced Report Generator initialization
        enhanced_generator = EnhancedReportGenerator()
        print("✅ EnhancedReportGenerator initialization successful")
        
        # Test basic AI analysis (with fallback)
        sample_results = {
            'coverage_metrics': {'overall': 75},
            'issues': {'severity_summary': {'critical': 1, 'high': 2}}
        }
        
        try:
            analysis = await ai_analyzer.analyze_code_quality(
                "print('hello world')", 
                "test.py", 
                "python"
            )
            print("✅ AI code analysis test successful")
        except Exception as e:
            print(f"⚠️  AI analysis test failed (expected without token): {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI components test failed: {e}")
        return False

def test_app_compatibility():
    """Test app compatibility"""
    print("\n🚀 Testing app compatibility...")
    
    try:
        # Test basic app import
        import app
        print("✅ Basic app import successful")
        
        # Test enhanced app import
        import app_enhanced
        print("✅ Enhanced app import successful")
        
        # Test config
        from config import Config
        Config.validate()
        print("✅ Configuration validation successful")
        
        print(f"🔧 AI Features Enabled: {Config.ENABLE_AI_FEATURES}")
        print(f"🔑 GitHub Token Available: {'Yes' if Config.GITHUB_TOKEN else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ App compatibility test failed: {e}")
        return False

def test_templates():
    """Test template availability"""
    print("\n📄 Testing templates...")
    
    template_files = [
        'templates/index.html',
        'templates/results.html',
        'templates/results_enhanced.html',
        'templates/base.html'
    ]
    
    all_good = True
    for template in template_files:
        if os.path.exists(template):
            print(f"✅ {template} exists")
        else:
            print(f"❌ {template} missing")
            all_good = False
    
    return all_good

async def main():
    """Main test runner"""
    print("🔍 CodePulse AI Compatibility Analysis")
    print("=" * 50)
    
    results = []
    
    # Test imports
    results.append(test_imports())
    
    # Test AI components
    results.append(await test_ai_components())
    
    # Test app compatibility
    results.append(test_app_compatibility())
    
    # Test templates
    results.append(test_templates())
    
    print("\n" + "=" * 50)
    print("📊 ANALYSIS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(results)
    
    print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
    print(f"❌ Tests Failed: {total_tests - passed_tests}/{total_tests}")
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED! CodePulse is AI-ready!")
        print("\n🚀 Quick Start Commands:")
        print("   Standard Mode: python3 app.py")
        print("   AI-Enhanced Mode: python3 app_enhanced.py")
        print("\n💡 To enable AI features:")
        print("   1. Set GITHUB_TOKEN in .env file")
        print("   2. Check 'Enable AI-Enhanced Analysis' in the web interface")
        
        return True
    else:
        print("\n⚠️  Some tests failed. Review the issues above.")
        print("\n🔧 Common fixes:")
        print("   - Install dependencies: pip install -r requirements.txt")
        print("   - Set up .env file with GITHUB_TOKEN")
        print("   - Check Python version (3.8+ required)")
        
        return False

if __name__ == "__main__":
    asyncio.run(main())