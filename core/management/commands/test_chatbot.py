"""
Django management command to test chatbot functionality
Usage: python manage.py test_chatbot
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from services.openai_chatbot import chatbot


class Command(BaseCommand):
    help = 'Test chatbot configuration and functionality'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🤖 Testing Chatbot Configuration...\n'))
        
        # Check API key configuration
        api_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if not api_key:
            self.stdout.write(self.style.ERROR('❌ OPENAI_API_KEY not found in settings'))
            return
        
        if api_key == 'your-openai-api-key-here':
            self.stdout.write(self.style.WARNING('⚠️  API key is still set to placeholder'))
            self.stdout.write(self.style.WARNING('   Please update OPENAI_API_KEY in rainwater_ai/settings.py'))
            return
        
        # Test chatbot initialization
        if chatbot.client:
            self.stdout.write(self.style.SUCCESS('✅ OpenAI client initialized successfully'))
        else:
            self.stdout.write(self.style.ERROR('❌ OpenAI client failed to initialize'))
            return
        
        # Test a simple query
        self.stdout.write('\n🧪 Testing chatbot response...')
        try:
            test_message = "Hello, what is rainwater harvesting?"
            response = chatbot.get_response(test_message)
            
            if response:
                self.stdout.write(self.style.SUCCESS('✅ Chatbot response received'))
                self.stdout.write(f'\n📝 Test Query: "{test_message}"')
                self.stdout.write(f'🤖 Response: {response[:100]}...\n')
            else:
                self.stdout.write(self.style.ERROR('❌ No response from chatbot'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error testing chatbot: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Chatbot test completed!'))