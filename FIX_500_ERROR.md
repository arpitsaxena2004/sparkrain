# 🔧 Fix 500 Error on Render

## Problem: `/mvp/` returns 500 Internal Server Error

### Most Likely Causes:

1. **ML Model Files Missing** - The `ml_models/` directory files aren't on Render
2. **Service Import Errors** - Services trying to load files that don't exist
3. **Database Issues** - Missing migrations or connection problems
4. **Static Files** - Missing static assets

### 🚀 Quick Fixes:

#### Fix 1: Check Render Logs

In Render Dashboard:
1. Go to your service
2. Click "Logs" tab
3. Look for the actual error message
4. Share the error traceback

#### Fix 2: Ensure ML Models are Committed

```bash
# Check if ml_models are in git
git ls-files ml_models/

# If not, add them
git add ml_models/
git commit -m "Add ML model files"
git push
```

#### Fix 3: Make ML Models Optional

The services should handle missing models gracefully. Check if these files exist:
- `ml_models/rainfall_map.pkl`
- `ml_models/suitability_model.pkl`
- `ml_models/cost_model.pkl`
- `ml_models/encoder.pkl`
- `ml_models/scaler.pkl`

#### Fix 4: Check Environment Variables

Ensure these are set in Render:
```
DEBUG=False
SECRET_KEY=<your-key>
DATABASE_URL=<postgres-url>
ALLOWED_HOSTS=.onrender.com
```

#### Fix 5: Run Migrations

The database might be missing tables. In Render Shell:
```bash
python manage.py migrate
```

### 🔍 Debug Steps:

#### Step 1: Enable DEBUG Temporarily

In Render environment variables, change:
```
DEBUG=True
```

This will show the actual error page. **Remember to set it back to False after debugging!**

#### Step 2: Check Specific Page

Try accessing other pages:
- `/` - Home page
- `/dashboard/` - Dashboard
- `/about/` - About page

If these work but `/mvp/` doesn't, the issue is specific to that view.

#### Step 3: Check Static Files

Look in browser console (F12) for:
- 404 errors on CSS/JS files
- Failed resource loads

### 📋 Common 500 Error Solutions:

#### Solution 1: Missing ML Models

If ML models are the issue, you have two options:

**Option A: Upload models to Render**
```bash
# Ensure models are in git
git add ml_models/*.pkl
git commit -m "Add ML model files"
git push
```

**Option B: Make models optional** (recommended for MVP)

The code should already handle this, but verify services have try/except blocks.

#### Solution 2: Database Not Migrated

```bash
# In Render Shell
python manage.py migrate
python manage.py collectstatic --no-input
```

#### Solution 3: Missing Environment Variable

Add to Render:
```
DJANGO_SETTINGS_MODULE=rainwater_ai.settings
```

### 🎯 Most Likely Fix:

Based on the error, try this:

1. **Check Render Logs** for the exact error
2. **Temporarily set DEBUG=True** to see error details
3. **Ensure migrations ran** during build
4. **Check if ML model files exist** on Render

### 📊 What to Share:

To help debug, please share:

1. **Full error from Render logs:**
   ```
   [Date Time] "GET /mvp/ HTTP/1.1" 500
   [Error traceback here]
   ```

2. **Build log output:**
   - Did migrations run successfully?
   - Were static files collected?
   - Any warnings or errors?

3. **Environment variables** (without sensitive values):
   - Is DEBUG set?
   - Is DATABASE_URL set?
   - Is SECRET_KEY set?

### 🆘 Emergency Workaround:

If you need the site working immediately, temporarily disable the problematic features:

1. Comment out ML model imports in services
2. Return simple responses instead of complex calculations
3. Deploy and verify basic functionality works
4. Gradually add features back

### 📞 Get Detailed Error:

Run this in Render Shell:
```python
python manage.py shell

# Then:
from django.test import Client
client = Client()
response = client.get('/mvp/')
print(response.status_code)
print(response.content)
```

This will show the actual error message.

---

## Next Steps:

1. Check Render logs for exact error
2. Share the error traceback
3. We'll fix the specific issue

The 500 error means something is failing server-side. The logs will tell us exactly what! 🔍
