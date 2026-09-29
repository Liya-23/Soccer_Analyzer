#!/bin/bash
set -e

echo "🔴 Soccer Match Analyzer"
echo "========================"
echo ""

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Ready to analyze!"
echo ""
echo "Starting server on http://localhost:8888"
echo "Press Ctrl+C to stop"
echo ""

python app.py --debug
