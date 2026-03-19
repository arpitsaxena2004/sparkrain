# OpenAI API Key Setup Instructions

## Step 1: Get Your OpenAI API Key

1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section (Dashboard -> API Keys)
4. Create a new secret API key
5. Copy the API key (it will look like: `sk-proj-...`)

## Step 2: Add API Key to Code

1. In your project root folder `d:\Projects\RoofTop_Rainwater_Harvesting-main\`, open or create a file named `.env`.
2. Add the following line to the file, replacing `your_actual_key_here` with the copied key:
   ```env
   OPENAI_API_KEY=sk-proj-your_actual_key_here
   ```

## Step 3: Test the Configuration

Run this command to test if everything is working:
```bash
python manage.py test_chatbot
```

You should see:
- ✅ OpenAI client initialized successfully
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

### If you see "❌ OpenAI client failed to initialize" or API errors:
- Verify your API key is correct
- Ensure you have a funded billing account on OpenAI ($5 minimum credit usually required)
- Check your internet connection
- Make sure the `openai` package is installed: `pip install openai`

### If chatbot falls back to simple responses:
- The system will automatically use rule-based responses if the API fails
- This ensures the chatbot always works, even without the API

## Security Note

- Don't commit this code (`.env` file) to public repositories
- Keep your API key secure
- Use environment variables for production deployment (like Render)

## API Usage

The chatbot uses:
- Model: `gpt-4o-mini`
- Max tokens: 500 per response
- Temperature: 0.7 (balanced creativity)

This provides intelligent, context-aware responses about rainwater harvesting!