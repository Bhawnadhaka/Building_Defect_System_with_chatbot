#!/usr/bin/env bash
# Render build script

echo "========================================="
echo "Building Defect Detection System"
echo "========================================="

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📥 Downloading AI model from Google Drive..."
# Using wget as fallback if gdown fails
if ! gdown --fuzzy "https://drive.google.com/file/d/1gtxzOlKkBGEv_A4AP3zzZOvYfvEoqdYo/view?usp=sharing" -O best_defect_model.pth; then
    echo "⚠️ gdown failed, trying direct download..."
    wget --no-check-certificate "https://drive.google.com/uc?export=download&id=1gtxzOlKkBGEv_A4AP3zzZOvYfvEoqdYo" -O best_defect_model.pth
fi

# Verify the file was downloaded
if [ -f "best_defect_model.pth" ]; then
    echo "✅ Model file downloaded successfully ($(du -h best_defect_model.pth | cut -f1))"
else
    echo "❌ Failed to download model file!"
    exit 1
fi

echo ""
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p chat_history
mkdir -p static/temp

echo ""
echo "✅ Build completed successfully!"
echo "========================================="
