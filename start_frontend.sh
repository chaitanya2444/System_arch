#!/bin/bash

# Start Frontend Server
# This script starts a simple HTTP server for the frontend

echo "🚀 Starting Frontend Server..."
echo "📁 Serving files from: $(pwd)/frontend"
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd frontend
python3 -m http.server 3000

