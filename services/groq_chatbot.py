import os
import json
from typing import Dict, List, Optional
from groq import Groq
from django.conf import settings
from .rainwater_calculator import RAINFALL_MAP, VALID_DISTRICTS
from .water_savings import BADGE_LEVELS, WATER_COST_PER_LITER_INR


class GroqRainwaterChatbot:
    def __init__(self):
        # Initialize Groq client using hardcoded API key from Django settings
        self.groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
        self.chatbot_config = getattr(settings, 'CHATBOT_CONFIG', {})
        
        # Check if API key is properly configured
        if not self.groq_api_key or self.groq_api_key == 'your-groq-api-key-here':
            self.groq_api_key = None
            print("⚠️  WARNING: Please replace 'your-groq-api-key-here' with your actual Groq API key in settings.py")
            print("   Location: rainwater_ai/settings.py - Line with GROQ_API_KEY")
            print("   Currently using fallback responses instead of AI")
            print("   Get your API key from: https://console.groq.com/")
            print("   For better responses, add your API key and restart the server")
        
        self.client = None
        if self.groq_api_key:
            try:
                self.client = Groq(api_key=self.groq_api_key)
                print("✅ Groq client initialized successfully!")
            except Exception as e:
                print(f"❌ Error initializing Groq client: {e}")
                print("   Please check if your API key is valid")
                self.client = None
        
        # System prompt with comprehensive knowledge about rainwater harvesting
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
- Keep responses concise but comprehensive
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
        
        # Add some sample district data
        if RAINFALL_MAP:
            sample_districts = list(RAINFALL_MAP.items())[:5]
            context_info.append("\nSample district rainfall data:")
            for district, rainfall in sample_districts:
                context_info.append(f"- {district.title()}: {rainfall} mm/year")
        
        return "\n".join(context_info) if context_info else "No user calculation data available."

    def get_groq_response(self, message: str, user_context: Dict = None) -> Optional[str]:
        """Get response from Groq API"""
        if not self.client:
            return None
        
        try:
            context_data = self.get_context_data(user_context)
            
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "system", "content": f"Current user context:\n{context_data}"},
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model="llama-3.1-70b-versatile",  # Fast and capable model
                messages=messages,
                max_tokens=500,  # Keep responses concise
                temperature=0.7,  # Balanced creativity and consistency
                top_p=0.9,
                stream=False
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return None

    def get_fallback_response(self, message: str) -> str:
        """Enhanced fallback responses when Groq API is not available"""
        message_lower = message.lower()
        
        # Import rainfall data for better responses
        from .rainwater_calculator import RAINFALL_MAP, VALID_DISTRICTS
        
        # Check for specific district mentions
        district_mentioned = None
        if RAINFALL_MAP:
            for district in list(RAINFALL_MAP.keys())[:50]:  # Check top 50 districts
                if district.lower() in message_lower:
                    district_mentioned = district
                    break
        
        # Simple keyword-based responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm JalNidhi AI, your rainwater harvesting assistant. I can help you with calculations, costs, technical specs, and environmental benefits. What would you like to know? 💧"
        
        elif any(word in message_lower for word in ['cost', 'price', 'money']):
            return "💰 **Rainwater Harvesting Costs**:\n\n• Small systems (50-100 sqm): ₹15,000-30,000\n• Medium systems (100-200 sqm): ₹30,000-75,000\n• Large systems (200+ sqm): ₹75,000-1,50,000\n\nPayback period is typically 2-5 years. Use our calculator for personalized estimates!"
        
        elif any(word in message_lower for word in ['rainfall', 'rain', 'data']) or district_mentioned:
            if district_mentioned and RAINFALL_MAP:
                rainfall = RAINFALL_MAP.get(district_mentioned, 'Data not available')
                if isinstance(rainfall, (int, float)):
                    water_potential = rainfall * 0.8
                    return f"🌧️ **{district_mentioned.title()} Rainfall Data**:\n\n• **Annual Rainfall**: {rainfall} mm\n• **Water Collection Potential**: {water_potential:.0f} L per sqm of roof\n• **For 100 sqm roof**: {water_potential * 100:,.0f} L/year\n• **Estimated Value**: ₹{water_potential * 100 * 0.05:,.0f}/year\n\nThis data is used in our suitability calculations!"
                else:
                    return f"🌧️ **{district_mentioned.title()}**: Rainfall data not available in our database.\n\nI have data for 600+ Indian districts. Try major cities like Mumbai, Delhi, Bangalore, Chennai, Pune, Hyderabad, etc."
            else:
                return "🌧️ **Rainfall Information**:\n\nI have rainfall data for 600+ Indian districts! India's average rainfall is 1,200mm/year, varying from 313mm (Rajasthan) to 11,871mm (Meghalaya).\n\nYour roof can collect ~0.8 liters per sqm per mm of rainfall. Which district are you interested in? Try: Mumbai, Delhi, Bangalore, Chennai, Pune..."
        
        elif any(word in message_lower for word in ['benefit', 'advantage', 'why']):
            return "🌍 **Benefits of Rainwater Harvesting**:\n\n• 💰 Reduce water bills by 40-70%\n• 🌱 Recharge groundwater by 40-60%\n• 🌊 Reduce urban flooding by 30-50%\n• 🏠 Increase property value by 3-5%\n• ♻️ Reduce carbon footprint by 0.5-1 ton CO₂/year\n\nIt's a win-win for your wallet and the environment!"
        
        elif any(word in message_lower for word in ['calculate', 'calculator', 'how']):
            return "🧮 **Using the Calculator**:\n\n1. Enter your roof area in square meters\n2. Select your district (I'll auto-fill rainfall data)\n3. Choose your soil type\n4. Click 'Calculate Water Potential'\n\nYou'll get personalized suitability scores, cost estimates, and water collection potential!"
        
        elif any(word in message_lower for word in ['tank', 'storage', 'capacity']):
            return "🏺 **Tank Specifications**:\n\n• **Capacity**: 1,000L per 25 sqm roof area minimum\n• **Materials**: Plastic (10-15 years), Concrete (25+ years), Fiberglass (20+ years)\n• **Sizing**: Roof Area × Annual Rainfall × 0.8 ÷ 12 months\n\nFor a 100 sqm roof with 1000mm rainfall, you'd need ~6,600L capacity."
        
        elif any(word in message_lower for word in ['thanks', 'thank you', 'bye']):
            return "Thank you for using JalNidhi AI! Remember, every drop counts in water conservation. Feel free to ask me anything about rainwater harvesting anytime! 💧🌍"
        
        else:
            return "I'm here to help with rainwater harvesting questions! I can assist with:\n\n• 🧮 Calculator guidance\n• 💰 Cost estimates\n• 🌧️ Rainfall data for 600+ districts\n• 🔧 Technical specifications\n• 🌍 Environmental benefits\n• 📊 System comparisons\n\n**Note**: For best AI responses, please add your Groq API key in settings.py\n\nWhat would you like to know?"

    def get_response(self, message: str, user_context: Dict = None) -> str:
        """Main method to get chatbot response"""
        # Try Groq API first
        groq_response = self.get_groq_response(message, user_context)
        
        if groq_response:
            return groq_response
        
        # Fallback to rule-based responses
        return self.get_fallback_response(message)


# Global chatbot instance
groq_chatbot = GroqRainwaterChatbot()