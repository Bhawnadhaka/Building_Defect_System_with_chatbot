#!/usr/bin/env bash
# Render build script

echo "========================================="
echo "Building Defect Detection System"
echo "========================================="

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "📥 Downloading AI model from Hugging Face..."
# Download from Hugging Face (reliable and fast)
wget "https://huggingface.co/Bhawana285/building_defect_model/resolve/main/best_defect_model.pth" -O best_defect_model.pth

# Verify the file was downloaded and is correct size
if [ -f "best_defect_model.pth" ]; then
    FILE_SIZE=$(stat -c%s "best_defect_model.pth" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -gt 10000000 ]; then
        echo "✅ Model file downloaded successfully ($(du -h best_defect_model.pth | cut -f1))"
    else
        echo "❌ Downloaded file is too small ($FILE_SIZE bytes)"
        echo "⚠️ Continuing without model - chatbot features will still work"
        rm -f best_defect_model.pth
    fi
else
    echo "❌ Model file not found after download"
    echo "⚠️ Continuing without model - chatbot features will still work"
fi

echo ""
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p chat_history
mkdir -p static/temp

echo ""
echo "✅ Build completed successfully!"
echo "========================================="
