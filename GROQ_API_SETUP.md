# Groq API Key Setup Instructions

## Step 1: Get Your Groq API Key

1. Go to [https://console.groq.com/](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (it will look like: `gsk_...`)

## Step 2: Add API Key to Code

1. Open the file: `rainwater_ai/settings.py`
2. Find this line (around line 120):
   ```python
   GROQ_API_KEY = 'your-groq-api-key-here'  # ← PASTE YOUR GROQ API KEY HERE
   ```
3. Replace `'your-groq-api-key-here'` with your actual API key:
   ```python
   GROQ_API_KEY = 'gsk_your_actual_api_key_here'
   ```

## Step 3: Test the Configuration

Run this command to test if everything is working:
```bash
python manage.py test_chatbot
```

You should see:
- ✅ Groq client initialized successfully
- ✅ Chatbot response received
- A sample response from the AI

## Step 4: Start Your Server

```bash
python manage.py runserver
```

The chatbot will now be available on your website with AI-powered responses!

## Troubleshooting

### If you see "⚠️ API key is still set to placeholder":
- Make sure you replaced the placeholder text with your actual API key
- Check that there are no extra spaces or quotes

### If you see "❌ Groq client failed to initialize":
- Verify your API key is correct
- Check your internet connection
- Make sure the `groq` package is installed: `pip install groq`

### If chatbot falls back to simple responses:
- The system will automatically use rule-based responses if the API fails
- This ensures the chatbot always works, even without the API

## Security Note

Since the API key is hardcoded, make sure:
- Don't commit this code to public repositories
- Keep your API key secure
- Consider using environment variables for production deployment

## API Usage

The chatbot uses:
- Model: `llama-3.1-70b-versatile`
- Max tokens: 500 per response
- Temperature: 0.7 (balanced creativity)

This provides intelligent, context-aware responses about rainwater harvesting!