# 📋 Render Deployment Checklist

Quick checklist to deploy JalNidhi Water Guard to Render.

## Pre-Deployment ✅

- [x] All code committed to Git
- [x] `requirements.txt` updated
- [x] `build.sh` created
- [x] `Procfile` exists
- [x] `settings.py` configured for production
- [x] `.gitignore` excludes sensitive files
- [ ] Code pushed to GitHub

## Render Setup 🚀

### 1. Create Accounts
- [ ] Render account created
- [ ] GitHub connected to Render

### 2. Create Database
- [ ] PostgreSQL database created on Render
- [ ] Database name: `jalnidhi-db`
- [ ] Internal Database URL copied

### 3. Create Web Service
- [ ] Web service created
- [ ] Repository connected
- [ ] Build command: `./build.sh`
- [ ] Start command: `gunicorn rainwater_ai.wsgi:application`

### 4. Environment Variables Set
- [ ] `PYTHON_VERSION=3.11.0`
- [ ] `DEBUG=False`
- [ ] `SECRET_KEY=<your-secret-key>`
- [ ] `DATABASE_URL=<internal-database-url>`
- [ ] `OPENWEATHER_API_KEY=<your-key>`
- [ ] `GEMINI_API_KEY=<your-key>`
- [ ] `GROQ_API_KEY=<your-key>` (optional)

### 5. Deploy
- [ ] Service deployed successfully
- [ ] Build logs show no errors
- [ ] Application status: "Live"

## Post-Deployment Testing 🧪

### Test Pages
- [ ] Home page loads: `/`
- [ ] Dashboard works: `/dashboard/`
- [ ] Water Guard MVP: `/mvp/`
- [ ] Live Demo: `/animation/`
- [ ] Analytics: `/analytics/`
- [ ] Vendors: `/vendors/`
- [ ] About: `/about/`

### Test Features
- [ ] Static files loading (CSS, images)
- [ ] Chatbot working
- [ ] Voice assistant working
- [ ] AI predictions working
- [ ] Borewell estimator working
- [ ] Weather forecast working
- [ ] Forms submitting correctly

### Test APIs
- [ ] Chatbot API: `/api/chatbot/`
- [ ] Flood prediction: `/api/flood/predict/`
- [ ] Borewell estimation: `/api/borewell/estimate/`
- [ ] District rainfall: `/api/district/rainfall/`

## Security Check 🔒

- [ ] DEBUG=False in production
- [ ] SECRET_KEY is strong and unique
- [ ] HTTPS enabled (automatic on Render)
- [ ] No API keys in code
- [ ] `.env` file not in repository
- [ ] ALLOWED_HOSTS configured

## Performance Check ⚡

- [ ] Static files compressed (WhiteNoise)
- [ ] Database migrations applied
- [ ] No console errors in browser
- [ ] Pages load within 3 seconds
- [ ] Mobile responsive

## Optional Enhancements 🎯

- [ ] Custom domain configured
- [ ] Monitoring set up
- [ ] Error tracking (Sentry)
- [ ] Backup strategy
- [ ] Admin user created

## Common Issues & Solutions 🔧

### Build Fails
- Check build logs
- Verify `requirements.txt`
- Ensure `build.sh` has correct permissions

### App Crashes
- Check application logs
- Verify DATABASE_URL
- Check SECRET_KEY is set

### Static Files Missing
- Run `collectstatic` in build
- Check WhiteNoise configuration
- Clear build cache and redeploy

### Database Errors
- Use Internal Database URL
- Check PostgreSQL is running
- Verify migrations ran

## Quick Commands 💻

### Local Testing
```bash
python manage.py runserver
python manage.py collectstatic
python manage.py migrate
```

### Git Commands
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

### Render Shell (via dashboard)
```bash
python manage.py createsuperuser
python manage.py migrate
python manage.py collectstatic
```

## Support Resources 📚

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Full Guide: See `RENDER_DEPLOYMENT_GUIDE.md`

## Deployment Status

**Date:** _____________
**Status:** ⬜ Not Started | ⬜ In Progress | ⬜ Completed
**URL:** _____________________________________________
**Notes:** ___________________________________________

---

✅ **Ready to Deploy!** Follow the steps in `RENDER_DEPLOYMENT_GUIDE.md`
