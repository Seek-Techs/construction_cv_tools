#!/usr/bin/env python
"""
Quick Start: Web App Test
Launches the web interface for testing with real construction photos
"""

import sys
import os
import time
import webbrowser
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("\n" + "="*70)
print("CONSTRUCTION CV TOOL - WEB INTERFACE QUICK START")
print("="*70)
print()
print("🚀 Preparing to launch web application...")
print()

# Check if all dependencies are available
dependencies = {
    'Flask': 'flask',
    'TaskQueue': 'task_queue',
    'ReportGenerator': 'report_generator',
    'Measurement Extractor': 'measurement_extractor',
}

print("✅ Checking dependencies...")
for name, module in dependencies.items():
    try:
        __import__(module)
        print(f"   ✅ {name}")
    except ImportError as e:
        print(f"   ❌ {name}: {e}")
        print("\n   Run: pip install -r requirements.txt")
        sys.exit(1)

print()
print("✅ All dependencies ready!")
print()

# Create required directories
(project_root / "uploads").mkdir(exist_ok=True)
(project_root / "reports").mkdir(exist_ok=True)

print("📁 Created directories:")
print(f"   - uploads/  (for uploaded photos)")
print(f"   - reports/  (for generated reports)")
print()

# Launch web app
print("="*70)
print("🌐 LAUNCHING WEB APP")
print("="*70)
print()
print("📍 Web App URL: http://localhost:5000")
print()
print("📸 TESTING STEPS:")
print("   1. Upload a site photo (JPG/PNG)")
print("   2. Upload a blueprint image (JPG/PNG/PDF)")
print("   3. Watch the analysis progress in real-time")
print("   4. Download PDF/CSV reports")
print()
print("Sample photos available in:")
print(f"   - test_data/sample_site.jpg")
print(f"   - test_data/sample_blueprint.jpg")
print()
print("Or upload your own construction photos!")
print()
print("Press Ctrl+C to stop the server")
print()
print("="*70)
print()

# Start Flask app
time.sleep(1)

try:
    # Import and start
    from web_app import app
    
    print("✅ Web app initialized")
    print()
    
    # Try to open browser
    try:
        webbrowser.open('http://localhost:5000')
        print("🌐 Opening browser (check http://localhost:5000)")
    except:
        print("📍 Open browser to: http://localhost:5000")
    
    print()
    print("Starting Flask server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()
    
    app.run(debug=False, host='localhost', port=5000)
    
except KeyboardInterrupt:
    print("\n\n✅ Web app stopped")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
