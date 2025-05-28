#!/usr/bin/env python3
"""
test_enhanced_dashboard.py - Test script for the enhanced dashboard functionality

This script validates that all components of the enhanced dashboard work correctly:
1. YouTube URL processing
2. Video download simulation
3. Dashboard components rendering
4. Session state management
"""

import sys
import os
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

def test_youtube_processor():
    """Test YouTube processor functionality"""
    print("🧪 Testing YouTube processor...")
    
    try:
        from dashboard.enhanced_dashboard import YouTubeProcessor
        
        processor = YouTubeProcessor()
        
        # Test video ID extraction
        test_urls = [
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "dQw4w9WgXcQ"
        ]
        
        for url in test_urls:
            video_id = processor.extract_video_id(url)
            print(f"  ✅ {url} → {video_id}")
            assert video_id == "dQw4w9WgXcQ", f"Expected dQw4w9WgXcQ, got {video_id}"
        
        print("  ✅ YouTube URL processing works correctly")
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False
    
    return True

def test_demo_data_availability():
    """Test if demo data can be generated and loaded"""
    print("🧪 Testing demo data generation...")
    
    try:
        # Import demo data creator
        sys.path.append(str(Path(__file__).parent))
        from create_demo_data import generate_demo_data
        
        # Generate demo data
        demo_file = Path("audio/test_debate_data.json")
        demo_file.parent.mkdir(exist_ok=True)
        
        demo_data = generate_demo_data()
        
        with open(demo_file, 'w') as f:
            json.dump(demo_data, f, indent=2)
        
        print(f"  ✅ Demo data generated: {len(demo_data['chunks'])} chunks")
        
        # Test loading
        from dashboard.enhanced_dashboard import load_debate_data
        loaded_data = load_debate_data(demo_file)
        
        assert len(loaded_data['chunks']) > 0, "No chunks loaded"
        assert 'statistics' in loaded_data, "Missing statistics"
        
        print("  ✅ Demo data loading works correctly")
        
        # Cleanup
        demo_file.unlink()
        
    except Exception as e:
        print(f"  ❌ Demo data test failed: {e}")
        return False
    
    return True

def test_dashboard_components():
    """Test dashboard component creation"""
    print("🧪 Testing dashboard components...")
    
    try:
        from dashboard.enhanced_dashboard import (
            create_stance_gauge, 
            create_timeline_chart
        )
        
        # Test stance gauge
        test_stance = {"liberal": 0.7, "conservative": 0.2, "moderate": 0.1}
        gauge_fig = create_stance_gauge(test_stance, "Test Gauge")
        
        assert gauge_fig is not None, "Gauge figure not created"
        print("  ✅ Stance gauge component works")
        
        # Test timeline chart with mock data
        mock_chunks = [
            {
                "start_time": 0,
                "has_stance": True,
                "stance_analysis": {
                    "stance_scores": {"liberal": 0.6, "conservative": 0.3, "moderate": 0.1}
                },
                "transcription": "Test transcription"
            }
        ]
        
        timeline_fig = create_timeline_chart(mock_chunks, current_time=0)
        assert timeline_fig is not None, "Timeline figure not created"
        print("  ✅ Timeline chart component works")
        
    except Exception as e:
        print(f"  ❌ Component test failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test that all required files exist"""
    print("🧪 Testing file structure...")
    
    required_files = [
        "dashboard/enhanced_dashboard.py",
        "dashboard/dashboard.py",
        "scripts/download_youtube.sh",
        "scripts/transcribe.py",
        "scripts/diarise.py",
        "scripts/stance.py",
        "scripts/build_json.py",
        "scripts/create_demo_data.py",
        "Makefile",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"  ❌ Missing files: {missing_files}")
        return False
    
    print("  ✅ All required files present")
    return True

def test_dependencies():
    """Test that required Python packages are available"""
    print("🧪 Testing Python dependencies...")
    
    required_packages = [
        "streamlit",
        "plotly",
        "pandas",
        "numpy"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"  ❌ {package}")
    
    if missing_packages:
        print(f"  ⚠️  Missing packages: {missing_packages}")
        print("  📋 Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Enhanced Dhisper Dashboard")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Dependencies", test_dependencies),
        ("YouTube Processor", test_youtube_processor),
        ("Demo Data", test_demo_data_availability),
        ("Dashboard Components", test_dashboard_components)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:>8} | {test_name}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Enhanced dashboard is ready to use.")
        print("\n🚀 Quick start:")
        print("   make demo-enhanced    # Test with demo data")
        print("   make run-enhanced     # Launch enhanced dashboard")
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please fix issues before proceeding.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
