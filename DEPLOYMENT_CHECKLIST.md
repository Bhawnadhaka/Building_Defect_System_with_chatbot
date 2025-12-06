# ✅ Deployment Files Checklist

## All files created for Render deployment:

### Core Configuration Files
- [x] `Procfile` - Gunicorn startup command
- [x] `runtime.txt` - Python version specification
- [x] `render-build.sh` - Build script for Render
- [x] `requirements.txt` - Updated with gunicorn and headless opencv
- [x] `.gitignore` - Git ignore rules

### Application Files (Already Exist)
- [x] `flask_app.py` - Updated with PORT environment variable
- [x] `templates/index.html`
- [x] `static/css/style.css`
- [x] `static/js/script.js`
- [x] `.env` - Will NOT be pushed to GitHub

### Documentation
- [x] `DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- [x] `DEPLOY_QUICK.md` - Quick 5-step guide

### Files to Handle Separately
- [ ] `best_defect_model.pth` - Upload to Google Drive or use Git LFS

---

## Quick Start Commands

### 1. Initialize Git and Push to GitHub

```powershell
# Initialize repository
git init
git add .
git commit -m "Deploy Building Defect Detection to Render"

# Create repo on github.com/new then:
git remote add origin https://github.com/YOUR_USERNAME/building-defect-detection.git
git branch -M main
git push -u origin main
```

### 2. Update render-build.sh with Model Download

Choose ONE method:

**Method A: Google Drive**
```bash
# Add to render-build.sh before "Build completed"
pip install gdown
gdown "https://drive.google.com/uc?id=YOUR_FILE_ID" -O best_defect_model.pth
```

**Method B: Git LFS**
```powershell
git lfs install
git lfs track "*.pth"
git add .gitattributes best_defect_model.pth
git commit -m "Add model file"
git push
```

### 3. Deploy on Render

1. **Go to**: https://render.com
2. **New Web Service** → Connect GitHub repo
3. **Settings**:
   - Build: `bash render-build.sh`
   - Start: `gunicorn flask_app:app --bind 0.0.0.0:$PORT`
   - Free tier
4. **Environment Variables**:
   ```
   GEMINI_API_KEY=AIzaSyD2ssTYntdiqTxDZjwy3-q4JG3SSxFmMO4
   FLASK_SECRET_KEY=[generate random key]
   FLASK_ENV=production
   ```
5. **Click**: Create Web Service

---

## Files Modified for Deployment

### requirements.txt
✅ Added: gunicorn
✅ Changed: opencv-python → opencv-python-headless
✅ Removed: streamlit (not needed for Flask)

### flask_app.py
✅ Updated: Port from environment variable
✅ Updated: Debug mode based on FLASK_ENV

### All Configuration Files
✅ Created: Procfile, runtime.txt, render-build.sh
✅ Created: .gitignore

---

## What Happens During Deployment

1. **Build Phase** (10-15 min):
   - Install Python 3.11
   - Install all requirements
   - Download model file (if configured)
   - Create directories

2. **Start Phase** (30 sec):
   - Start Gunicorn server
   - Load PyTorch model
   - Initialize Gemini API
   - Start serving on Render URL

3. **Ready** ✅:
   - Your app is live!
   - SSL certificate auto-configured
   - URL: https://your-app-name.onrender.com

---

## Troubleshooting

### Issue: Model file not found
**Solution**: Update render-build.sh with correct download link

### Issue: Out of memory
**Solution**: Free tier has 512MB RAM - should be enough
If not, reduce workers in Procfile to 1

### Issue: Build timeout
**Solution**: Check requirements.txt - remove unnecessary packages

### Issue: Port binding error
**Solution**: Already fixed - using $PORT variable

---

## Next Steps

1. **Push to GitHub** (2 min)
2. **Upload model to Google Drive** (2 min)
3. **Update render-build.sh** (1 min)
4. **Deploy on Render** (3 min)
5. **Wait for build** (10 min)
6. **Test your app** ✅

**Total: ~20 minutes to deployment!**

---

## Your Deployment URL

After deployment, share this with your professor:

```
https://building-defect-ai.onrender.com
```

(Replace with your actual service name)

---

Ready to deploy? Start with Step 1! 🚀
