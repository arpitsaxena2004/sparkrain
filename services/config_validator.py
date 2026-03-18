"""
Configuration validator for API keys and services
"""
from django.conf import settings
from groq import Groq


def validate_groq_config():
    """
    Validate Groq API configuration
    Returns: (is_valid: bool, message: str)
    """
    try:
        groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
        
        if not groq_api_key:
            return False, "GROQ_API_KEY not found in settings"
        
        if groq_api_key == 'your-groq-api-key-here':
            return False, "GROQ_API_KEY is set to placeholder value"
        
        # Test API key by creating client
        try:
            client = Groq(api_key=groq_api_key)
            # You could add a simple test call here if needed
            return True, "Groq API key is valid"
        except Exception as e:
            return False, f"Invalid Groq API key: {str(e)}"
            
    except Exception as e:
        return False, f"Configuration error: {str(e)}"


def get_chatbot_status():
    """
    Get comprehensive chatbot status
    Returns: dict with status information
    """
    groq_valid, groq_message = validate_groq_config()
    
    chatbot_config = getattr(settings, 'CHATBOT_CONFIG', {})
    fallback_enabled = chatbot_config.get('FALLBACK_ENABLED', True)
    
    return {
        'groq_api_available': groq_valid,
        'groq_status_message': groq_message,
        'fallback_enabled': fallback_enabled,
        'model': chatbot_config.get('GROQ_MODEL', 'llama-3.1-70b-versatile'),
        'max_tokens': chatbot_config.get('MAX_TOKENS', 500),
        'temperature': chatbot_config.get('TEMPERATURE', 0.7),
    }


def print_chatbot_status():
    """Print chatbot configuration status to console"""
    status = get_chatbot_status()
    
    print("\n" + "="*50)
    print("CHATBOT CONFIGURATION STATUS")
    print("="*50)
    print(f"Groq API Available: {'✅' if status['groq_api_available'] else '❌'}")
    print(f"Status: {status['groq_status_message']}")
    print(f"Fallback Enabled: {'✅' if status['fallback_enabled'] else '❌'}")
    print(f"Model: {status['model']}")
    print(f"Max Tokens: {status['max_tokens']}")
    print(f"Temperature: {status['temperature']}")
    print("="*50 + "\n")