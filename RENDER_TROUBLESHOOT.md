# 🔍 Render Deployment Troubleshooting

## Current Error: ModuleNotFoundError: No module named 'apps'

### Latest Fixes Applied:

1. ✅ Simplified `INSTALLED_APPS` back to `'core'`
2. ✅ Updated `wsgi.py` to add project to Python path
3. ✅ Simplified `Procfile` to basic gunicorn command
4. ✅ Enhanced `build.sh` with detailed logging
5. ✅ Created all `__init__.py` files

### 🚀 Deploy These Changes:

```bash
git add .
git commit -m "Fix: Enhanced debugging and simplified configuration"
git push origin main
```

### 📋 Check Render Build Logs For:

The enhanced build script will now show:
1. Python version being used
2. Django installation verification
3. Project structure
4. Core app existence
5. Settings import test
6. Detailed collectstatic output
7. Detailed migration output

### 🔍 Debugging Steps:

#### Step 1: Verify Environment Variables on Render

Make sure these are set in Render dashboard:
```
PYTHON_VERSION=3.11.0
DEBUG=False
SECRET_KEY=<your-secret-key>
DATABASE_URL=<internal-database-url>
```

#### Step 2: Check Build Command

In Render dashboard, verify:
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn rainwater_ai.wsgi:application`

#### Step 3: Check Runtime

Verify `runtime.txt` exists with:
```
python-3.11.0
```

#### Step 4: Clear Build Cache

In Render dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"

### 🐛 Common Causes of This Error:

1. **Missing __init__.py files** ✅ Fixed
2. **Incorrect PYTHONPATH** ✅ Fixed in wsgi.py
3. **App not in correct location** - Check if `core/` directory exists
4. **Circular imports** - Check service files
5. **Old cached build** - Clear cache and redeploy

### 📝 Alternative: Check if it's a Different 'apps' Module

The error might be from a different source. Let me check:

#### Check if error mentions specific file:

Look in Render logs for the full traceback. It should show:
```
File "/path/to/file.py", line X, in <module>
    from apps import something
ModuleNotFoundError: No module named 'apps'
```

This will tell us which file is causing the issue.

### 🔧 If Error Persists:

#### Option 1: Use Different Start Command

Try this in Render:
```
gunicorn --pythonpath /opt/render/project/src rainwater_ai.wsgi:application
```

#### Option 2: Create a Custom Startup Script

Create `start.sh`:
```bash
#!/bin/bash
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH
exec gunicorn rainwater_ai.wsgi:application
```

Then use as start command: `./start.sh`

#### Option 3: Check for Hidden Dependencies

Some packages might have 'apps' as a dependency. Check:
```bash
pip list | grep apps
```

### 📊 What to Share for Further Help:

If error continues, please share:
1. **Full error traceback** from Render logs
2. **Build log output** (especially the new detailed sections)
3. **Which line/file** is mentioned in the error
4. **Environment variables** (without sensitive values)

### 🎯 Most Likely Solution:

Based on the error, try these in order:

1. **Clear build cache** and redeploy
2. **Check if all files are committed** to Git:
   ```bash
   git status
   git add .
   git commit -m "Ensure all files committed"
   git push
   ```

3. **Verify directory structure** on Render:
   - The enhanced build.sh will show this
   - Look for `core/` directory in logs

4. **Check Python path** in Render shell:
   ```python
   import sys
   print(sys.path)
   ```

### 🆘 Emergency Fallback:

If nothing works, try deploying with minimal configuration:

1. Comment out all services imports in views.py temporarily
2. Use only basic Django features
3. Deploy and verify it works
4. Gradually add back features

### 📞 Get More Info:

Run this in Render Shell (after deployment attempt):
```bash
python manage.py shell
```

Then:
```python
import sys
print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nInstalled apps:")
from django.conf import settings
for app in settings.INSTALLED_APPS:
    print(f"  {app}")

print("\nTrying to import core:")
import core
print(f"  Core location: {core.__file__}")
```

This will help identify the exact issue.

---

## 🎯 Next Action:

1. Push the latest changes
2. Watch the detailed build logs
3. Share the specific error line if it persists
4. We'll fix it based on the exact error location

The enhanced logging will help us pinpoint the exact issue! 🔍
