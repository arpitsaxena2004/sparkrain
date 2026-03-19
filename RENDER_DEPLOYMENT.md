# 🚀 Render Deployment Guide for JalNidhi AI

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Groq API Key**: Get from [console.groq.com](https://console.groq.com)

## 🔧 Step-by-Step Deployment

### 1. **Connect GitHub to Render**

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select your repository: `RoofTop_Rainwater_Harvesting`
5. Click **"Connect"**

### 2. **Configure Web Service Settings**

**Basic Settings:**
- **Name**: `jalnidhi-ai` (or your preferred name)
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn rainwater_ai.wsgi:application`

### 3. **Set Environment Variables**

In Render dashboard, go to **Environment** tab and add:

```
GROQ_API_KEY=your-actual-groq-api-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com,localhost
SECRET_KEY=your-production-secret-key-here
```

**Important**: Replace `your-app-name` with your actual Render app name.

### 4. **Advanced Settings**

**Auto-Deploy**: ✅ Enable (deploys automatically on GitHub push)

**Health Check Path**: `/` (optional)

**Instance Type**: 
- **Free Tier**: Good for demo/testing
- **Starter**: Better performance for production

### 5. **Deploy**

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

## 🔐 Environment Variables Setup

### **Required Variables:**

| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Your Groq API key | `gsk_abc123...` |
| `DEBUG` | Django debug mode | `False` |
| `ALLOWED_HOSTS` | Allowed hostnames | `your-app.onrender.com` |
| `SECRET_KEY` | Django secret key | Generate new one |

### **Optional Variables:**

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL URL | SQLite (not recommended for production) |
| `OPENWEATHER_API_KEY` | Weather API key | Not required |

## 🗄️ Database Configuration (Optional)

### **For Production Database:**

1. **Create PostgreSQL Database** in Render:
   - Go to Dashboard → **"New +"** → **"PostgreSQL"**
   - Name: `jalnidhi-db`
   - Copy the **Internal Database URL**

2. **Add to Environment Variables**:
   ```
   DATABASE_URL=postgresql://user:pass@host:port/dbname
   ```

3. **Update settings.py** (already configured):
   ```python
   import dj_database_url
   DATABASES['default'] = dj_database_url.parse(os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'))
   ```

## 🚨 Troubleshooting

### **Common Issues:**

1. **Build Fails**:
   - Check `requirements.txt` is complete
   - Ensure Python version compatibility

2. **App Crashes**:
   - Check logs in Render dashboard
   - Verify environment variables
   - Ensure `ALLOWED_HOSTS` includes your domain

3. **Static Files Not Loading**:
   - Run: `python manage.py collectstatic` (handled automatically)
   - Check `STATIC_ROOT` and `STATIC_URL` settings

4. **Database Errors**:
   - Run migrations: `python manage.py migrate`
   - Check `DATABASE_URL` format

### **Checking Logs:**

1. Go to Render Dashboard
2. Click on your service
3. Go to **"Logs"** tab
4. Check for errors and debug

## 🔄 Updating Your App

### **Automatic Updates:**
- Push to GitHub `main` branch
- Render auto-deploys (if enabled)

### **Manual Deploy:**
- Go to Render Dashboard
- Click **"Manual Deploy"** → **"Deploy latest commit"**

## 📊 Monitoring

### **Health Checks:**
- Render automatically monitors your app
- Check **"Events"** tab for deployment history
- Monitor **"Metrics"** for performance

### **Custom Domain (Optional):**
1. Go to **"Settings"** → **"Custom Domains"**
2. Add your domain
3. Configure DNS records as shown

## 🔒 Security Best Practices

1. **Never commit API keys** to GitHub
2. **Use strong SECRET_KEY** for production
3. **Set DEBUG=False** in production
4. **Use HTTPS** (Render provides free SSL)
5. **Regular security updates**

## 📞 Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Django Deployment**: [docs.djangoproject.com](https://docs.djangoproject.com/en/stable/howto/deployment/)
- **Issues**: Check GitHub repository issues

---

## 🎉 Your App is Live!

Once deployed, your JalNidhi AI app will be accessible at:
`https://your-app-name.onrender.com`

Features available:
- ✅ Rainwater harvesting calculator
- ✅ AI-powered chatbot (with Groq API)
- ✅ Water savings dashboard
- ✅ Analytics and reporting
- ✅ Mobile-responsive design
- ✅ Beautiful water-themed UI

**Happy Deploying! 🚀💧**