#!/bin/bash

# Yu-Gi-Oh! Deck Simulator Setup Script
# This script initializes the Python virtual environment and installs all dependencies.

# Exit on error
set -e

echo "🚀 Starting Yu-Gi-Oh! Deck Simulator Setup..."

# 1. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed. Please install Python 3.10+ and try again."
    exit 1
fi

# 2. Check for Node
if ! command -v node &> /dev/null; then
    echo "❌ Error: node is not installed. Please install Node.js 18+ and try again."
    exit 1
fi

# 3. Create/Update Python Virtual Environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Python virtual environment already exists."
fi

# 4. Install Python Dependencies
echo "🐍 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 5. Install Frontend Dependencies
echo "⚛️ Installing Frontend dependencies..."
cd frontend
npm install
cd ..

echo "✨ Setup complete! You can now run 'npm run dev' to start the application."
