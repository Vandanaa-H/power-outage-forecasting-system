# 🌐 Render Web Service Setup Guide

## Step-by-Step Render Deployment

### 📋 Prerequisites
- ✅ GitHub account with your code repository
- ✅ Free Render account at [render.com](https://render.com)

### 🚀 Method 1: Blueprint Deployment (Recommended)

#### Step 1: Prepare Your Repository
1. **Commit all files** to GitHub:
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

#### Step 2: Deploy via Blueprint
1. **Sign up/Login** to [render.com](https://render.com)
2. **Connect GitHub**: 
   - Click "New" → "Blueprint"
   - Connect your GitHub account
   - Select repository: `power-outage-forecasting-system`
3. **Auto-Deploy**: Render reads `render.yaml` and creates both services automatically

### 🔧 Method 2: Manual Service Creation

#### Backend Service Setup

1. **Create Web Service**:
   - Dashboard → "New" → "Web Service"
   - Connect GitHub repository
   - Select `power-outage-forecasting-system`

2. **Configure Backend**:
   ```
   Name: power-outage-api
   Environment: Python 3
   Build Command: pip install -r requirements-minimal.txt
   Start Command: uvicorn backend_simple:app --host 0.0.0.0 --port $PORT
   ```

3. **Environment Variables**:
   ```
   PYTHON_VERSION = 3.11.0
   ```

#### Frontend Service Setup

1. **Create Static Site**:
   - Dashboard → "New" → "Static Site"
   - Connect same GitHub repository

2. **Configure Frontend**:
   ```
   Name: power-outage-frontend
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/build
   ```

3. **Environment Variables**:
   ```
   REACT_APP_API_URL = https://power-outage-api.onrender.com
   ```

### ⚙️ Detailed Configuration

#### Backend Configuration
```yaml
# Service Settings
Name: power-outage-api
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (leave empty)

# Build & Deploy
Build Command: pip install -r requirements-minimal.txt
Start Command: uvicorn backend_simple:app --host 0.0.0.0 --port $PORT

# Advanced Settings
Auto-Deploy: Yes
Health Check Path: /health (if you have one)
```

#### Frontend Configuration
```yaml
# Service Settings
Name: power-outage-frontend
Environment: Static Site
Region: Oregon (US West)
Branch: main
Root Directory: frontend

# Build & Deploy
Build Command: npm install && npm run build
Publish Directory: build
```

### 🔍 Troubleshooting Common Issues

#### Backend Issues

**Build Fails - Heavy Dependencies:**
```bash
# Solution: Use minimal requirements
mv requirements.txt requirements-full.txt
mv requirements-minimal.txt requirements.txt
git commit -am "Use minimal requirements"
git push
```

**Port Error:**
- ✅ **Correct**: `uvicorn backend_simple:app --host 0.0.0.0 --port $PORT`
- ❌ **Wrong**: `uvicorn backend_simple:app --port 8002`

**CORS Error:**
- Ensure backend allows Render domains (already configured)

#### Frontend Issues

**Build Fails:**
```bash
# Check if these exist in frontend/
package.json
src/index.js
public/index.html
```

**API Connection Issues:**
- Ensure `REACT_APP_API_URL` points to backend service
- Backend must be deployed first

### 📊 Monitoring Your Services

#### Check Service Status
1. **Dashboard**: See all services at a glance
2. **Logs**: Click service → "Logs" tab
3. **Metrics**: Monitor CPU, memory usage
4. **Events**: See deployment history

#### Service URLs
After deployment:
- **Backend**: `https://power-outage-api.onrender.com`
- **Frontend**: `https://power-outage-frontend.onrender.com`
- **API Docs**: `https://power-outage-api.onrender.com/docs`

### 🚨 Free Tier Limitations

**What's Included:**
- ✅ 750 hours/month total
- ✅ 512MB RAM per service
- ✅ SSL certificates
- ✅ Custom domains
- ✅ GitHub auto-deploy

**Limitations:**
- ⚠️ Services sleep after 15 minutes of inactivity
- ⚠️ 30-second cold start when waking up
- ⚠️ Shared resources (slower performance)

### 💡 Tips for Success

1. **Start Simple**: Use `requirements-minimal.txt` first
2. **Deploy Backend First**: Frontend needs backend URL
3. **Test Locally**: Ensure everything works before deploying
4. **Monitor Logs**: Check for errors during deployment
5. **Use HTTPS**: Always use secure URLs in production

### 🔄 Updating Your App

**Automatic Updates:**
```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main
# Render auto-deploys from GitHub
```

**Manual Deploy:**
- Service Dashboard → "Manual Deploy" → "Deploy Latest Commit"

### 📱 Alternative Commands

**If using full requirements.txt:**
```bash
# Build Command (heavier)
pip install -r requirements.txt

# Or install specific packages only
pip install fastapi uvicorn pandas numpy scikit-learn
```

**For frontend debugging:**
```bash
# Build Command with verbose output
npm install && npm run build --verbose
```

### 🎯 Next Steps After Deployment

1. **Test Your App**: Visit the frontend URL
2. **Check API**: Visit `/docs` endpoint for API documentation
3. **Monitor Usage**: Keep an eye on your 750-hour limit
4. **Share**: Send the live URL to users!

---

**🎉 Your power outage forecasting system is now live on the web!**

**Need help?** Check Render's documentation or their Discord community.