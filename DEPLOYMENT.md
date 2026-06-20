# Deployment Guide - Expense Manager

## Deploy to Render (Free Tier)

### Step-by-Step Instructions:

1. **Go to Render.com**
   - Visit https://render.com
   - Sign up (free account)

2. **Connect GitHub**
   - Click "New +" → "Web Service"
   - Select "Deploy an existing project from a Git repository"
   - Connect your GitHub account if prompted
   - Select `poonamlearning1602-arch/Expense_Manager` repository
   - Click "Connect"

3. **Configure Deployment**
   - **Name**: `expense-manager` (or your choice)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Region**: Choose closest to you
   - **Instance Type**: Free
   - Click "Create Web Service"

4. **Wait for Deployment**
   - Deployment takes 2-5 minutes
   - You'll see a live URL like: `https://expense-manager-xxxx.onrender.com`

5. **Database Setup**
   - The SQLite database will be created automatically on first run
   - Data persists in Render's ephemeral storage for the session

### Access Your App

Once deployed, your live URL will be:
```
https://expense-manager-xxxx.onrender.com
```

### Features Available

✅ Dashboard with financial overview
✅ Add/Edit/Delete expenses
✅ Add income tracking
✅ Budget management with visual progress
✅ Spending analytics with charts
✅ CSV export/import
✅ Category management
✅ Monthly trends analysis
✅ Recurring expense support

### Notes

- **Free Tier Limits**: Your app will spin down after 15 minutes of inactivity (will wake up when accessed)
- **Database**: SQLite stores data locally (persists during active sessions)
- **Data**: For production, consider upgrading to a paid tier or using a managed database
- **Scaling**: For production use, upgrade to Render's paid tiers

### Troubleshooting

If deployment fails:
1. Check the build logs in Render dashboard
2. Ensure all files are pushed to GitHub
3. Verify requirements.txt has all dependencies
4. Check that Procfile exists and is correct

### Local Testing Before Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Access at http://localhost:5000
```

## Alternative Deployments

- **Heroku**: Previously free, now paid tier only
- **Railway**: Free $5/month credit
- **Replit**: Free tier available
- **PythonAnywhere**: Free tier available
- **AWS Free Tier**: 12 months free

## Support

For issues:
1. Check Render documentation: https://render.com/docs
2. Review Flask documentation: https://flask.palletsprojects.com
3. GitHub Issues: Describe the problem and steps to reproduce
