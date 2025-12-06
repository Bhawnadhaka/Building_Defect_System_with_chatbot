#!/usr/bin/env bash
# Render build script

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p chat_history
mkdir -p static/temp

echo "Build completed successfully!"
