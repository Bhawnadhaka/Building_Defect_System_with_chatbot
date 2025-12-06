# 🚀 Deploying to Render - Complete Guide

## Prerequisites
1. GitHub account
2. Render account (free tier)
3. Your Gemini API key: `AIzaSyD2ssTYntdiqTxDZjwy3-q4JG3SSxFmMO4`

---

## Step 1: Prepare Your Repository

### A. Create a GitHub Repository

1. Go to https://github.com/new
2. Create a new repository:
   - Name: `building-defect-detection`
   - Visibility: Public (required for Render free tier)
   - Don't initialize with README (we already have files)
3. Click "Create repository"

### B. Initialize Git and Push Code

Open PowerShell in your project directory and run:

```powershell
# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Building Defect Detection System"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/building-defect-detection.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Important**: You'll need to upload `best_defect_model.pth` separately or use Git LFS (Large File Storage) since it's large.

---

## Step 2: Set Up Render

### A. Create Render Account

1. Go to https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your GitHub account

### B. Create New Web Service

1. Click "New +" button → "Web Service"
2. Connect your GitHub repository:
   - If not already connected, click "Connect Account"
   - Select your `building-defect-detection` repository
3. Click "Connect"

### C. Configure Web Service

Fill in the following settings:

**Basic Settings:**
- **Name**: `building-defect-ai` (or your preferred name)
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `bash render-build.sh`
- **Start Command**: `gunicorn flask_app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120`

**Instance Type:**
- Select: **Free** (512 MB RAM, shared CPU)

### D. Add Environment Variables

Scroll down to "Environment Variables" section and add:

| Key | Value |
|-----|-------|
| `GEMINI_API_KEY` | `AIzaSyD2ssTYntdiqTxDZjwy3-q4JG3SSxFmMO4` |
| `FLASK_SECRET_KEY` | `your-random-secret-key-change-this` |
| `FLASK_ENV` | `production` |
| `UPLOAD_FOLDER` | `uploads` |
| `MAX_CONTENT_LENGTH` | `16777216` |
| `PYTHON_VERSION` | `3.11.0` |

**To generate a secure secret key:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### E. Deploy

1. Click "Create Web Service" button
2. Wait for deployment (10-15 minutes for first build)
3. Watch the logs for any errors

---

## Step 3: Handle the Model File

Since `best_defect_model.pth` is too large for GitHub (>100MB), you have 3 options:

### Option A: Use Git LFS (Recommended)

```powershell
# Install Git LFS
git lfs install

# Track the model file
git lfs track "*.pth"

# Add and commit
git add .gitattributes
git add best_defect_model.pth
git commit -m "Add model file with Git LFS"
git push
```

### Option B: Upload to Cloud Storage

1. Upload `best_defect_model.pth` to Google Drive/Dropbox
2. Get a direct download link
3. Modify `render-build.sh`:

```bash
# Add after pip install
echo "Downloading model file..."
curl -L "YOUR_DIRECT_DOWNLOAD_LINK" -o best_defect_model.pth
```

### Option C: Use Render Disk Storage

1. Create a Render Disk (free 1GB)
2. Mount it to your service at `/app/models`
3. Upload model via SFTP
4. Update model path in code

---

## Step 4: Verify Deployment

### A. Check Build Logs

Watch for:
- ✅ Dependencies installed
- ✅ Directories created
- ✅ Model loaded successfully
- ✅ Server started

### B. Test Your Application

1. Once deployed, Render provides a URL like: `https://building-defect-ai.onrender.com`
2. Open the URL in your browser
3. Test features:
   - Upload single image
   - Check GradCAM visualization
   - Test chatbot
   - Try batch processing

---

## Step 5: Troubleshooting Common Issues

### Issue 1: Model File Not Found

**Error**: `FileNotFoundError: best_defect_model.pth`

**Solution**: Use one of the model upload options from Step 3

### Issue 2: Out of Memory

**Error**: `Killed` or `OOMKilled`

**Solution**: 
- Reduce workers in Procfile to 1
- Optimize model loading
- Consider upgrading to paid tier ($7/month)

### Issue 3: Timeout During Build

**Error**: Build takes >15 minutes

**Solution**:
- Simplify requirements.txt
- Use pre-built wheels
- Split build into stages

### Issue 4: OpenCV Errors

**Error**: `libGL.so.1: cannot open shared object file`

**Solution**: We already switched to `opencv-python-headless` in requirements.txt

### Issue 5: Port Binding Error

**Error**: `Port 5000 is already in use`

**Solution**: We updated flask_app.py to use `$PORT` environment variable

---

## Step 6: Optimize for Free Tier

### A. Prevent Sleep (Optional)

Render free tier sleeps after 15 minutes of inactivity. To keep it awake:

1. Use a service like UptimeRobot (free)
2. Ping your URL every 14 minutes
3. Note: This may violate Render's free tier terms

### B. Reduce Cold Start Time

1. Minimize dependencies
2. Use lightweight libraries
3. Lazy-load heavy models

### C. Monitor Usage

Free tier includes:
- ✅ 750 hours/month
- ✅ 100 GB bandwidth
- ✅ 512 MB RAM
- ❌ Sleeps after 15 min inactivity

---

## Step 7: Post-Deployment Configuration

### A. Update CORS (if needed)

If you plan to access the API from other domains:

```python
from flask_cors import CORS

CORS(app, origins=['https://yourdomain.com'])
```

### B. Set Up Custom Domain (Optional)

1. Go to Render Dashboard → Your Service → Settings
2. Scroll to "Custom Domains"
3. Add your domain
4. Update DNS records

### C. Enable HTTPS

Render provides free SSL certificates automatically!

---

## Step 8: Monitoring and Maintenance

### A. Check Logs

```
Render Dashboard → Your Service → Logs
```

### B. Restart Service

```
Render Dashboard → Your Service → Manual Deploy → Deploy latest commit
```

### C. Update Environment Variables

```
Render Dashboard → Your Service → Environment → Edit
```

---

## Complete Deployment Checklist

- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Created Render account
- [ ] Connected GitHub to Render
- [ ] Created Web Service
- [ ] Added environment variables
- [ ] Handled model file (Git LFS/Cloud/Disk)
- [ ] Deployed successfully
- [ ] Tested all features
- [ ] Checked logs for errors
- [ ] Verified GradCAM works
- [ ] Tested chatbot
- [ ] Saved deployment URL

---

## Your Deployment URL

After successful deployment, your app will be available at:

```
https://building-defect-ai.onrender.com
```

(Replace with your actual service name)

---

## Quick Commands Reference

### Git Commands
```powershell
git add .
git commit -m "Update message"
git push
```

### Redeploy on Render
```
Dashboard → Manual Deploy → Deploy latest commit
```

### View Logs
```
Dashboard → Logs (real-time)
```

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **Git LFS**: https://git-lfs.github.com/
- **Flask Deployment**: https://flask.palletsprojects.com/en/3.0.x/deploying/

---

## Cost Breakdown (Free Tier)

| Resource | Free Tier | Your Usage |
|----------|-----------|------------|
| RAM | 512 MB | ~400 MB (model + app) |
| CPU | Shared | Sufficient |
| Bandwidth | 100 GB/month | ~10 GB/month |
| Build Time | Unlimited | ~10 min/build |
| Uptime | 750 hrs/month | 24/7 possible |

**Estimated Monthly Cost: $0** ✅

---

## Next Steps

1. Follow Step 1 to push code to GitHub
2. Follow Step 2 to deploy on Render
3. Follow Step 3 to handle model file
4. Test your live application!

**Good luck with your deployment! 🚀**

If you encounter issues, check the troubleshooting section or Render logs.
