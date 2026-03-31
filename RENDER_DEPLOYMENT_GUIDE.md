# 🚀 Deploy JalNidhi Water Guard to Render

Complete step-by-step guide to deploy your Django application to Render.

## Prerequisites

✅ GitHub account
✅ Render account (free tier available at https://render.com)
✅ Your code pushed to GitHub repository

## Step 1: Prepare Your Repository

Your repository is already configured with:
- ✅ `requirements.txt` - All Python dependencies
- ✅ `build.sh` - Build script for Render
- ✅ `Procfile` - Process configuration
- ✅ Updated `settings.py` - Production-ready settings
- ✅ `.gitignore` - Excludes sensitive files

### Push Latest Changes to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

## Step 2: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

## Step 3: Create PostgreSQL Database

1. From Render Dashboard, click "New +"
2. Select "PostgreSQL"
3. Configure:
   - **Name:** `jalnidhi-db` (or your preferred name)
   - **Database:** `jalnidhi`
   - **User:** (auto-generated)
   - **Region:** Choose closest to your users
   - **Plan:** Free
4. Click "Create Database"
5. **IMPORTANT:** Copy the "Internal Database URL" - you'll need this!

## Step 4: Create Web Service

1. From Render Dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure the service:

### Basic Settings:
- **Name:** `jalnidhi-water-guard` (or your preferred name)
- **Region:** Same as your database
- **Branch:** `main`
- **Root Directory:** (leave empty)
- **Runtime:** `Python 3`
- **Build Command:** `./build.sh`
- **Start Command:** `gunicorn rainwater_ai.wsgi:application`

### Advanced Settings:

#### Environment Variables (Click "Add Environment Variable"):

Add these one by one:

```
PYTHON_VERSION=3.11.0
DEBUG=False
SECRET_KEY=your-super-secret-key-here-change-this-to-random-string
DATABASE_URL=<paste-your-internal-database-url-here>
OPENWEATHER_API_KEY=<your-openweather-api-key>
GEMINI_API_KEY=<your-gemini-api-key>
GROQ_API_KEY=<your-groq-api-key-if-you-have>
```

**Important Notes:**
- Generate a strong SECRET_KEY (use: https://djecrety.ir/)
- DATABASE_URL should be the Internal Database URL from Step 3
- Add your actual API keys

### Plan:
- Select "Free" plan

5. Click "Create Web Service"

## Step 5: Wait for Deployment

Render will now:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Run `build.sh` (collectstatic & migrate)
4. Start your application with gunicorn

This takes 5-10 minutes for the first deployment.

Watch the logs in real-time to see progress.

## Step 6: Verify Deployment

Once deployed, you'll see:
- ✅ "Live" status with a green indicator
- Your app URL: `https://jalnidhi-water-guard.onrender.com`

Click the URL to visit your live application!

## Step 7: Test Your Application

Visit these pages to ensure everything works:
- Home: `https://your-app.onrender.com/`
- Dashboard: `https://your-app.onrender.com/dashboard/`
- Water Guard MVP: `https://your-app.onrender.com/mvp/`
- Live Demo: `https://your-app.onrender.com/animation/`
- Analytics: `https://your-app.onrender.com/analytics/`

## Troubleshooting

### Issue: Build Failed

**Check:**
- Build logs for specific error
- Ensure all dependencies in `requirements.txt`
- Verify `build.sh` has execute permissions

**Fix:**
```bash
chmod +x build.sh
git add build.sh
git commit -m "Fix build.sh permissions"
git push
```

### Issue: Application Crashes

**Check:**
- Application logs in Render dashboard
- DATABASE_URL is correctly set
- SECRET_KEY is set

**Common fixes:**
- Ensure `gunicorn` is in `requirements.txt` ✅
- Check `ALLOWED_HOSTS` includes `.onrender.com` ✅
- Verify environment variables are set correctly

### Issue: Static Files Not Loading

**Check:**
- `STATIC_ROOT` is set correctly ✅
- `whitenoise` is in `requirements.txt` ✅
- `collectstatic` ran successfully in build logs

**Fix:**
- Redeploy: Click "Manual Deploy" → "Clear build cache & deploy"

### Issue: Database Connection Error

**Check:**
- DATABASE_URL environment variable is set
- PostgreSQL database is running
- Internal Database URL (not External)

### Issue: 502 Bad Gateway

**Causes:**
- Application failed to start
- Port binding issue
- Gunicorn configuration

**Fix:**
- Check application logs
- Ensure start command is: `gunicorn rainwater_ai.wsgi:application`

## Free Tier Limitations

Render Free Tier includes:
- ✅ 750 hours/month (enough for 1 app running 24/7)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start takes 30-60 seconds

**Note:** First request after inactivity will be slow (cold start).

## Updating Your Application

After making changes:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically detect the push and redeploy!

## Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Update DNS records as instructed
5. Wait for SSL certificate (automatic)

## Monitoring

### View Logs:
- Click on your service
- Go to "Logs" tab
- Real-time application logs

### Metrics:
- CPU usage
- Memory usage
- Request count
- Response times

## Environment Variables Management

To update environment variables:
1. Go to service settings
2. Click "Environment"
3. Add/Edit/Delete variables
4. Click "Save Changes"
5. Service will automatically redeploy

## Backup Database

### Manual Backup:
1. Go to your PostgreSQL database
2. Click "Backups" tab
3. Click "Create Backup"

### Automatic Backups:
- Free tier: No automatic backups
- Paid tier: Daily automatic backups

## Cost Optimization

Free tier is sufficient for:
- Development
- Testing
- Small projects
- Portfolio demos

Upgrade to paid tier for:
- Production applications
- No cold starts
- More resources
- Automatic backups

## Security Checklist

Before going live:
- ✅ DEBUG=False in production
- ✅ Strong SECRET_KEY
- ✅ HTTPS enabled (automatic on Render)
- ✅ Environment variables for sensitive data
- ✅ ALLOWED_HOSTS configured
- ✅ CSRF protection enabled
- ✅ SQL injection protection (Django ORM)

## Performance Tips

1. **Enable Caching:**
   - Add Redis for session storage
   - Cache database queries

2. **Optimize Static Files:**
   - Already using WhiteNoise ✅
   - Consider CDN for large files

3. **Database Optimization:**
   - Add indexes to frequently queried fields
   - Use select_related() and prefetch_related()

4. **Monitor Performance:**
   - Use Render metrics
   - Add application monitoring (Sentry, New Relic)

## Support

### Render Documentation:
- https://render.com/docs

### Django Deployment:
- https://docs.djangoproject.com/en/stable/howto/deployment/

### Community:
- Render Community Forum
- Django Forum
- Stack Overflow

## Quick Reference

### Important URLs:
- Render Dashboard: https://dashboard.render.com
- Your App: https://your-app-name.onrender.com
- Database: Internal URL from Render

### Important Commands:
```bash
# Local testing
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Create superuser (on Render shell)
python manage.py createsuperuser
```

### Render Shell Access:
1. Go to your service
2. Click "Shell" tab
3. Run Django management commands

## Success Checklist

- ✅ Code pushed to GitHub
- ✅ PostgreSQL database created
- ✅ Web service created
- ✅ Environment variables set
- ✅ Build successful
- ✅ Application running
- ✅ All pages accessible
- ✅ Static files loading
- ✅ Database connected
- ✅ API keys working

## Next Steps

After successful deployment:
1. Create admin user via Render shell
2. Test all features thoroughly
3. Set up monitoring
4. Configure custom domain (optional)
5. Share your live app! 🎉

---

## Your Deployment URLs

Once deployed, your app will be available at:
- **Main App:** `https://jalnidhi-water-guard.onrender.com`
- **Admin Panel:** `https://jalnidhi-water-guard.onrender.com/admin/`

**Note:** Replace `jalnidhi-water-guard` with your actual service name.

---

## Need Help?

If you encounter issues:
1. Check Render logs first
2. Review this guide
3. Check Render documentation
4. Ask in Render community forum

Good luck with your deployment! 🚀💧
