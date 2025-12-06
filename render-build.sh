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
# Download using gdown with proper file ID
python -m gdown "1gtxzOlKkBGEv_A4AP3zzZOvYfvEoqdYo" -O best_defect_model.pth

# Verify the file was downloaded and is large enough (should be ~400MB)
if [ -f "best_defect_model.pth" ]; then
    FILE_SIZE=$(stat -f%z "best_defect_model.pth" 2>/dev/null || stat -c%s "best_defect_model.pth" 2>/dev/null)
    if [ "$FILE_SIZE" -gt 100000000 ]; then
        echo "✅ Model file downloaded successfully ($(du -h best_defect_model.pth | cut -f1))"
    else
        echo "❌ Downloaded file is too small ($FILE_SIZE bytes) - likely an error page"
        echo "💡 Please ensure the Google Drive file is publicly accessible"
        rm -f best_defect_model.pth
        exit 1
    fi
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
