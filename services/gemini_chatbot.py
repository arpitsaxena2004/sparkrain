"""
Google Gemini AI Chatbot for Rainwater Harvesting
Replaces OpenAI with Google's Gemini API
"""

import os
import json
from typing import Dict, Optional
from django.conf import settings

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  WARNING: google-generativeai package not installed")
    print("   Install with: pip install google-generativeai")


class GeminiRainwaterChatbot:
    def __init__(self):
        """Initialize Gemini chatbot"""
        self.gemini_api_key = os.environ.get('GEMINI_API_KEY', '')
        
        # Check if API key is configured
        if not self.gemini_api_key:
            self.gemini_api_key = None
            print("⚠️  WARNING: Gemini API key not configured")
            print("   Add GEMINI_API_KEY to your .env file")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
            print("   Currently using fallback responses instead of AI")
        
        self.model = None
        if self.gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                print("✅ Gemini AI initialized successfully!")
            except Exception as e:
                print(f"❌ Error initializing Gemini: {e}")
                self.model = None
        
        # System prompt
        self.system_prompt = """You are JalNidhi AI, an expert assistant for rainwater harvesting in India. You help users with:

CORE EXPERTISE:
- Rainwater harvesting calculations and system design
- Cost estimation and ROI analysis
- District-specific rainfall data and suitability
- Environmental benefits and water conservation
- Technical specifications for tanks, filters, pumps
- Government policies and subsidies
- Installation and maintenance guidance

AVAILABLE DATA:
- Rainfall data for 600+ Indian districts
- Cost ranges: Small systems (₹15,000-30,000), Medium (₹30,000-75,000), Large (₹75,000-1,50,000)
- Water collection formula: Roof Area × Rainfall × 0.8 (runoff coefficient)
- Badge system: Beginner Saver (10,000L) to Earth Champion (200,000L)
- Water cost: ₹0.05 per liter
- Collection efficiency: 80-90%
- Payback period: 2-5 years typically

RESPONSE STYLE:
- Be helpful, knowledgeable, and encouraging
- Use emojis appropriately (💧🌧️🏠💰🌍)
- Provide specific, actionable advice
- Include relevant data and calculations when possible
- Keep responses concise but comprehensive (max 300 words)
- Always relate answers back to rainwater harvesting benefits

IMPORTANT:
- If asked about specific districts, mention that you have rainfall data
- For cost questions, provide ranges and factors affecting cost
- For technical questions, give practical specifications
- Always emphasize environmental and economic benefits
- Encourage users to use the calculator for personalized results

Answer all questions related to rainwater harvesting, water conservation, environmental sustainability, and related topics. If asked about unrelated topics, politely redirect to rainwater harvesting."""

    def get_context_data(self, user_context: Dict = None) -> str:
        """Prepare context data for the AI"""
        context_info = []
        
        if user_context and user_context.get('has_calculations'):
            context_info.append(f"User's latest calculation:")
            context_info.append(f"- Badge: {user_context.get('latest_badge', 'N/A')}")
            context_info.append(f"- Water saved: {user_context.get('water_saved', 0):,.0f} L/year")
            context_info.append(f"- Money saved: ₹{user_context.get('money_saved', 0):,.0f}/year")
        
        return "\n".join(context_info) if context_info else "No user calculation data available."

    def get_gemini_response(self, message: str, user_context: Dict = None) -> Optional[str]:
        """Get response from Gemini API"""
        if not self.model:
            return None
        
        try:
            context_data = self.get_context_data(user_context)
            
            # Combine system prompt, context, and user message
            full_prompt = f"""{self.system_prompt}

Current user context:
{context_data}

User question: {message}

Provide a helpful, concise response (max 300 words):"""
            
            # Generate response
            response = self.model.generate_content(full_prompt)
            
            # Extract text from response
            if response and response.text:
                return response.text.strip()
            else:
                return None
            
        except Exception as e:
            print(f"Gemini API error: {e}")
            return None

    def get_fallback_response(self, message: str) -> str:
        """Enhanced fallback responses when Gemini API is not available"""
        message_lower = message.lower()
        
        # Import rainfall data for better responses
        try:
            from .rainwater_calculator import RAINFALL_MAP
        except:
            RAINFALL_MAP = {}
        
        # Check for specific district mentions
        district_mentioned = None
        if RAINFALL_MAP:
            for district in list(RAINFALL_MAP.keys())[:50]:
                if district.lower() in message_lower:
                    district_mentioned = district
                    break
        
        # Keyword-based responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start']):
            return "Hello! 👋 I'm JalNidhi AI, your rainwater harvesting assistant. I can help you with calculations, costs, technical specs, and environmental benefits. What would you like to know? 💧"
        
        elif any(word in message_lower for word in ['cost', 'price', 'money', 'expensive']):
            return "💰 **Rainwater Harvesting Costs**:\n\n• Small systems (50-100 sqm): ₹15,000-30,000\n• Medium systems (100-200 sqm): ₹30,000-75,000\n• Large systems (200+ sqm): ₹75,000-1,50,000\n\nPayback period is typically 2-5 years. Use our calculator for personalized estimates!"
        
        elif any(word in message_lower for word in ['rainfall', 'rain', 'data', 'weather']) or district_mentioned:
            if district_mentioned and RAINFALL_MAP:
                rainfall = RAINFALL_MAP.get(district_mentioned, 'Data not available')
                if isinstance(rainfall, (int, float)):
                    water_potential = rainfall * 0.8
                    return f"🌧️ **{district_mentioned.title()} Rainfall Data**:\n\n• Annual Rainfall: {rainfall} mm\n• Water Collection Potential: {water_potential:.0f} L per sqm\n• For 100 sqm roof: {water_potential * 100:,.0f} L/year\n• Estimated Value: ₹{water_potential * 100 * 0.05:,.0f}/year"
            return "🌧️ I have rainfall data for 600+ Indian districts! Which city are you interested in? Try: Mumbai, Delhi, Bangalore, Chennai, Pune, Hyderabad..."
        
        elif any(word in message_lower for word in ['benefit', 'advantage', 'why', 'good']):
            return "🌍 **Benefits of Rainwater Harvesting**:\n\n• 💰 Reduce water bills by 40-70%\n• 🌱 Recharge groundwater by 40-60%\n• 🌊 Reduce urban flooding by 30-50%\n• 🏠 Increase property value by 3-5%\n• ♻️ Reduce carbon footprint\n\nIt's a win-win for your wallet and the environment!"
        
        elif any(word in message_lower for word in ['calculate', 'calculator', 'how to use']):
            return "🧮 **Using the Calculator**:\n\n1. Enter your roof area in square meters\n2. Select your district (auto-fills rainfall)\n3. Choose your soil type\n4. Click 'Calculate Water Potential'\n\nYou'll get personalized suitability scores, cost estimates, and water savings!"
        
        elif any(word in message_lower for word in ['tank', 'storage', 'capacity', 'size']):
            return "🏺 **Tank Specifications**:\n\n• Capacity: 1,000L per 25 sqm roof minimum\n• Materials: Plastic (10-15 years), Concrete (25+ years), Fiberglass (20+ years)\n• Sizing: Roof Area × Annual Rainfall × 0.8 ÷ 12 months\n\nFor 100 sqm roof with 1000mm rainfall: ~6,600L capacity needed."
        
        elif any(word in message_lower for word in ['water level', 'current', 'status', 'tank level']):
            return "💧 To check your water level, use the Water Guard dashboard. It shows real-time tank status, predictions, and recommendations. Would you like to know about water management features?"
        
        elif any(word in message_lower for word in ['conserve', 'save', 'scarcity', 'drought']):
            return "💧 **Water Conservation Tips**:\n\n• Fix leaks immediately\n• Use water-efficient fixtures\n• Harvest rainwater for non-potable uses\n• Reuse greywater for gardens\n• Monitor usage with Water Guard\n\nOur AI system can predict scarcity and activate conservation mode automatically!"
        
        elif any(word in message_lower for word in ['flood', 'overflow', 'heavy rain']):
            return "🌊 **Flood Prevention**:\n\n• Water Guard AI detects flood risk when rainfall >50mm/day\n• System recommends releasing water if tank >80% full\n• Prevents overflow and property damage\n• Automated alerts and actions\n\nCheck the Water Guard MVP for real-time predictions!"
        
        elif any(word in message_lower for word in ['thanks', 'thank you', 'bye', 'goodbye']):
            return "Thank you for using JalNidhi AI! 🙏 Remember, every drop counts in water conservation. Feel free to ask me anything about rainwater harvesting anytime! 💧🌍"
        
        else:
            return "I'm here to help with rainwater harvesting! I can assist with:\n\n• 🧮 Calculator guidance\n• 💰 Cost estimates\n• 🌧️ Rainfall data for 600+ districts\n• 🔧 Technical specifications\n• 🌍 Environmental benefits\n• 💧 Water Guard predictions\n\n**Note**: For best AI responses, add GEMINI_API_KEY to .env file\n\nWhat would you like to know?"

    def get_response(self, message: str, user_context: Dict = None) -> str:
        """Main method to get chatbot response"""
        # Try Gemini API first
        gemini_response = self.get_gemini_response(message, user_context)
        
        if gemini_response:
            return gemini_response
        
        # Fallback to rule-based responses
        return self.get_fallback_response(message)


# Global chatbot instance
chatbot = GeminiRainwaterChatbot()
