# Guerrero's Electric Invoice Generator - Railway Deployment

## Quick Deploy to Railway

### 1. Prepare Your Files

1. Create a new folder on your computer
2. Copy all the Python files into it
3. Add your `BASE_INVOICE.pdf` template

### 2. Create GitHub Repository
```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/yourusername/invoice-generator.git
git push -u origin main
```

### 3. Deploy to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your invoice-generator repo
6. Railway will auto-detect it's a Python app and deploy!

### 4. Set Environment Variables

In Railway dashboard:
1. Click on your project
2. Go to "Variables" tab
3. Add these variables:
```
EMAIL_ADDRESS = your-email@gmail.com
EMAIL_PASSWORD = your-gmail-app-password
RECIPIENT_EMAIL = your-email@gmail.com
```

**Important:** For Gmail, you need an "App Password":
- Go to Google Account settings
- Security → 2-Step Verification → App passwords
- Generate a new app password
- Use that password (not your regular Gmail password)

### 5. Get Your Webhook URL

After deployment:
1. Railway gives you a URL like: `https://your-app.up.railway.app`
2. Your webhook will be: `https://your-app.up.railway.app/webhook/sms`

### 6. Set Up Twilio

1. Sign up at [twilio.com](https://twilio.com)
2. Get a phone number ($1-2/month)
3. In Phone Numbers → Active Numbers → Click your number
4. Under "Messaging", set webhook URL to:
```
   https://your-app.up.railway.app/webhook/sms
```
5. Save!

### 7. Test It!

Text your Twilio number with:
```
Customer: John Smith
Address: 123 Main St, Dallas, TX 75001
Job: Electrical
Invoice: 999

Line items:
- Test item - $100

Total: $100
```

You should get:
- SMS response confirming generation
- Email with PDF attached

## Testing Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file with your credentials
cp .env.example .env
# Edit .env with your actual credentials

# Run locally
python app.py

# Test with curl
curl -X POST http://localhost:5000/webhook/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Customer: Test\nInvoice: 999\nTotal: $100"}'
```

## Troubleshooting

### No email received?
- Check spam folder
- Verify Gmail app password is correct
- Check Railway logs for errors

### PDF not filling correctly?
- Make sure BASE_INVOICE.pdf has form fields
- Check Railway logs to see which fields were found

### SMS not working?
- Verify Twilio webhook URL is correct
- Check it ends with `/webhook/sms`
- Check Railway logs