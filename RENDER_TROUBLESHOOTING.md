# 🔧 Manual Web Service Setup for Render

## ⚠️ Build Error Solutions

### **Step 1: Deploy Backend (Web Service)**

1. **Create Web Service**:
   - Go to [render.com](https://render.com) → Dashboard
   - Click "New" → "Web Service"
   - Connect GitHub repository: `power-outage-forecasting-system`

2. **Configure Backend**:
   ```
   Name: power-outage-api
   Environment: Python 3
   Build Command: pip install --upgrade pip && pip install fastapi uvicorn pydantic requests python-dotenv
   Start Command: uvicorn backend_simple:app --host 0.0.0.0 --port $PORT
   ```

3. **Advanced Settings**:
   ```
   Auto-Deploy: Yes
   Environment Variables: (none needed for basic setup)
   ```

### **Step 2: Deploy Frontend (Static Site)**

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
   *(Replace with your actual backend URL after step 1)*

## 🚨 Common Build Errors & Fixes

### **Backend Build Errors**

**Error: "Requirements file not found"**
```bash
# Solution: Use inline dependencies
Build Command: pip install fastapi uvicorn pydantic requests python-dotenv
```

**Error: "Package conflicts"**
```bash
# Solution: Upgrade pip first
Build Command: pip install --upgrade pip && pip install fastapi uvicorn pydantic
```

**Error: "Python version issues"**
```bash
# Solution: Specify Python version
Environment Variables:
PYTHON_VERSION = 3.11.0
```

### **Frontend Build Errors**

**Error: "package.json not found"**
```bash
# Solution: Specify frontend directory
Build Command: cd frontend && npm install && npm run build
Publish Directory: frontend/build
```

**Error: "npm install fails"**
```bash
# Solution: Use npm ci for faster, reliable installs
Build Command: cd frontend && npm ci && npm run build
```

**Error: "Build exceeds time limit"**
```bash
# Solution: Skip optional dependencies
Build Command: cd frontend && npm install --only=production && npm run build
```

## 🎯 Simplified Deployment Commands

### **Ultra-Minimal Backend**
If you're still getting build errors:

```bash
# Build Command (copy-paste this):
pip install fastapi==0.103.0 uvicorn==0.23.2 pydantic==2.3.0

# Start Command:
uvicorn backend_simple:app --host 0.0.0.0 --port $PORT
```

### **Frontend with Error Handling**
```bash
# Build Command (copy-paste this):
cd frontend && npm install --legacy-peer-deps && npm run build

# Publish Directory:
frontend/build
```

## 📱 Alternative: Individual Service Setup

If Blueprint fails, deploy services separately:

### **1. Backend Only First**
- Deploy as Web Service
- Get the URL (e.g., `https://your-api.onrender.com`)
- Test it works: visit `https://your-api.onrender.com/docs`

### **2. Frontend Second**  
- Deploy as Static Site
- Use backend URL in `REACT_APP_API_URL`

## 🔍 Debugging Build Issues

### **Check Build Logs**
1. Go to service in Render dashboard
2. Click "Logs" tab
3. Look for specific error messages
4. Common issues:
   - Missing files
   - Package conflicts
   - Memory limits
   - Timeout errors

### **Test Locally First**
Before deploying, test locally:

```bash
# Backend test:
pip install fastapi uvicorn
uvicorn backend_simple:app --reload

# Frontend test:
cd frontend
npm install
npm run build
```

## ✅ Success Checklist

- [ ] Backend deploys without errors
- [ ] Backend URL responds (visit `/docs` endpoint)
- [ ] Frontend builds successfully  
- [ ] Frontend environment variable set correctly
- [ ] Both services show "Live" status in dashboard

---

**Still having issues?** Try the ultra-minimal commands above or contact me with the specific error message!