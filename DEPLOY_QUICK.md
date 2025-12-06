# 🚀 Quick Deployment to Render

## FASTEST WAY - Just 5 Steps!

### Step 1: Push to GitHub (2 minutes)

```powershell
# In PowerShell, in your project directory:

git init
git add .
git commit -m "Initial commit"

# Go to github.com/new and create a repo named: building-defect-detection
# Then run (replace YOUR_USERNAME):

git remote add origin https://github.com/YOUR_USERNAME/building-defect-detection.git
git branch -M main
git push -u origin main
```

### Step 2: Upload Model File (2 minutes)

Since the model file is too large, upload it to Google Drive:

1. Upload `best_defect_model.pth` to Google Drive
2. Right-click → Share → Anyone with link can view
3. Get the file ID from the URL: `https://drive.google.com/file/d/FILE_ID_HERE/view`
4. Update `render-build.sh`:

```bash
# Add this line after pip install:
gdown --id YOUR_FILE_ID_HERE -O best_defect_model.pth
```

5. Add `gdown` to requirements.txt:
```
gdown==4.7.1
```

**OR** Use this direct download method:

```bash
# In render-build.sh, add:
pip install gdown
gdown "https://drive.google.com/uc?id=YOUR_FILE_ID" -O best_defect_model.pth
```

### Step 3: Create Render Service (3 minutes)

1. Go to https://render.com → Sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your `building-defect-detection` repo
4. Configure:
   - **Name**: `building-defect-ai`
   - **Build Command**: `bash render-build.sh`
   - **Start Command**: `gunicorn flask_app:app --bind 0.0.0.0:$PORT`
   - **Instance**: Free

### Step 4: Add Environment Variables (1 minute)

Click "Advanced" → Add these:

```
GEMINI_API_KEY = AIzaSyD2ssTYntdiqTxDZjwy3-q4JG3SSxFmMO4
FLASK_SECRET_KEY = your-random-secret-key
FLASK_ENV = production
```

### Step 5: Deploy! (10 minutes)

Click "Create Web Service" and wait for deployment.

**Your app will be live at**: `https://building-defect-ai.onrender.com`

---

## Alternative: Use Pre-uploaded Model

I can help you skip the model upload step if you:

1. Share your model file via WeTransfer/Dropbox
2. I'll provide a direct download link
3. Update the build script automatically

---

## Need Help?

If you get stuck, tell me at which step and I'll help troubleshoot!

**Total Time: ~15 minutes** ⏱️
