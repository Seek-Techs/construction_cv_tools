#!/usr/bin/env python
"""
Simple Flask app startup
"""
from web_app import app

if __name__ == '__main__':
    print("\n🌐 Web App Running on http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
