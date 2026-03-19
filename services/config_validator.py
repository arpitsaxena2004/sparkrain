"""
Configuration validator for API keys and services
"""
from django.conf import settings
from openai import OpenAI


def validate_openai_config():
    """
    Validate OpenAI API configuration
    Returns: (is_valid: bool, message: str)
    """
    try:
        openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if not openai_api_key:
            return False, "OPENAI_API_KEY not found in settings"
        
        if openai_api_key == 'your-openai-api-key-here':
            return False, "OPENAI_API_KEY is set to placeholder value"
        
        # Test API key by creating client
        try:
            client = OpenAI(api_key=openai_api_key)
            # You could add a simple test call here if needed
            return True, "OpenAI API key is valid"
        except Exception as e:
            return False, f"Invalid OpenAI API key: {str(e)}"
            
    except Exception as e:
        return False, f"Configuration error: {str(e)}"


def get_chatbot_status():
    """
    Get comprehensive chatbot status
    Returns: dict with status information
    """
    openai_valid, openai_message = validate_openai_config()
    
    chatbot_config = getattr(settings, 'CHATBOT_CONFIG', {})
    fallback_enabled = chatbot_config.get('FALLBACK_ENABLED', True)
    
    return {
        'openai_api_available': openai_valid,
        'openai_status_message': openai_message,
        'fallback_enabled': fallback_enabled,
        'model': chatbot_config.get('OPENAI_MODEL', 'gpt-4o-mini'),
        'max_tokens': chatbot_config.get('MAX_TOKENS', 500),
        'temperature': chatbot_config.get('TEMPERATURE', 0.7),
    }


def print_chatbot_status():
    """Print chatbot configuration status to console"""
    status = get_chatbot_status()
    
    print("\n" + "="*50)
    print("CHATBOT CONFIGURATION STATUS")
    print("="*50)
    print(f"OpenAI API Available: {'✅' if status['openai_api_available'] else '❌'}")
    print(f"Status: {status['openai_status_message']}")
    print(f"Fallback Enabled: {'✅' if status['fallback_enabled'] else '❌'}")
    print(f"Model: {status['model']}")
    print(f"Max Tokens: {status['max_tokens']}")
    print(f"Temperature: {status['temperature']}")
    print("="*50 + "\n")