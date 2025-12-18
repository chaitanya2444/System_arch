#!/usr/bin/env bash
# Render build script for System Architecture Backend

set -o errexit  # Exit on error

echo "🔧 Starting build process..."

# Install system dependencies
echo "📦 Installing system dependencies..."
apt-get update
apt-get install -y git

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

echo "✅ Build completed successfully!"
