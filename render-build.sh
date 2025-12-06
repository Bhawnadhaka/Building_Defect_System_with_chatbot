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
# Download using gdown command with proper file ID
gdown 1gtxzOlKkBGEv_A4AP3zzZOvYfvEoqdYo -O best_defect_model.pth

# Verify the file was downloaded and is large enough (should be ~400MB)
if [ -f "best_defect_model.pth" ]; then
    FILE_SIZE=$(stat -c%s "best_defect_model.pth" 2>/dev/null || echo "0")
    if [ "$FILE_SIZE" -gt 100000000 ]; then
        echo "✅ Model file downloaded successfully ($(du -h best_defect_model.pth | cut -f1))"
    else
        echo "❌ Downloaded file is too small ($FILE_SIZE bytes) - likely an error page"
        echo "💡 Upload model to Hugging Face for reliable downloads"
        echo "📝 Instructions: https://huggingface.co/docs/hub/models-uploading"
        # Don't fail build - app will work without model (chatbot only)
        echo "⚠️ Continuing without model - chatbot features will still work"
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
