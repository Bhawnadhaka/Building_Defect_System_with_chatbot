#!/usr/bin/env bash
# Render build script - UPDATED VERSION

echo "========================================="
echo "Building Defect Detection System"
echo "========================================="

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📥 Downloading AI model..."
# UNCOMMENT ONE OF THESE METHODS:

# METHOD 1: Google Drive (Recommended)
# Replace YOUR_FILE_ID with your actual Google Drive file ID
# pip install gdown
# gdown "https://drive.google.com/uc?id=YOUR_FILE_ID" -O best_defect_model.pth

# METHOD 2: Direct URL (if you have one)
# curl -L "YOUR_DIRECT_URL_HERE" -o best_defect_model.pth

# METHOD 3: Hugging Face (if you upload there)
# pip install huggingface_hub
# python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='YOUR_USERNAME/YOUR_REPO', filename='best_defect_model.pth', local_dir='.')"

echo ""
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p chat_history
mkdir -p static/temp

echo ""
echo "✅ Build completed successfully!"
echo "========================================="
