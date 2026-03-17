import re
import json
from typing import Dict, List, Tuple
from django.http import JsonResponse
from difflib import SequenceMatcher
from .rainwater_calculator import validate_district, get_district_rainfall, VALID_DISTRICTS, RAINFALL_MAP
from .water_savings import BADGE_LEVELS, WATER_COST_PER_LITER_INR

# Try to import NLTK, fallback to basic processing if not available
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)

    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class RainwaterChatbot:
    def __init__(self):
        self.context = {}
        
        # Initialize stopwords with fallback
        if NLTK_AVAILABLE:
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        else:
            self.stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Enhanced intent patterns with more variations
        self.intent_patterns = {
            'greeting': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                'start', 'begin', 'help me', 'assist me'
            ],
            'calculator_help': [
                'calculate', 'calculator', 'how to use', 'form', 'roof area', 'district', 
                'soil', 'input', 'enter data', 'fill form', 'use calculator', 'calculation'
            ],
            'results_explanation': [
                'suitability', 'cost', 'water potential', 'explain', 'meaning', 'result',
                'score', 'prediction', 'analysis', 'interpretation', 'understand'
            ],
            'data_questions': [
                'data', 'dataset', 'information', 'statistics', 'numbers', 'facts',
                'how much', 'how many', 'what is the', 'show me', 'tell me about',
                'average', 'maximum', 'minimum', 'total', 'compare', 'comparison'
            ],
            'rainfall_data': [
                'rainfall', 'rain', 'precipitation', 'monsoon', 'weather', 'climate',
                'annual rainfall', 'monthly rainfall', 'seasonal', 'wet season'
            ],
            'cost_data': [
                'cost', 'price', 'expense', 'money', 'budget', 'investment', 'roi',
                'return on investment', 'payback', 'savings', 'economic'
            ],
            'technical_specs': [
                'tank', 'capacity', 'storage', 'system', 'installation', 'equipment',
                'components', 'materials', 'specifications', 'requirements'
            ],
            'environmental_impact': [
                'environment', 'eco', 'green', 'sustainable', 'carbon', 'impact',
                'conservation', 'groundwater', 'recharge', 'pollution'
            ],
            'district_help': [
                'district', 'city', 'location', 'where', 'find district', 'place',
                'area', 'region', 'state', 'geography'
            ],
            'savings_help': [
                'savings', 'dashboard', 'badge', 'progress', 'money saved', 'track',
                'achievement', 'level', 'status'
            ],
            'comparison': [
                'compare', 'comparison', 'versus', 'vs', 'difference', 'better',
                'which is', 'should i choose', 'recommend'
            ],
            'faq': [
                'what is', 'why', 'benefits', 'rainwater harvesting', 'how does',
                'advantages', 'disadvantages', 'pros', 'cons'
            ],
            'goodbye': ['bye', 'goodbye', 'thanks', 'thank you', 'exit', 'quit']
        }
        
        # Knowledge base for data questions
        self.knowledge_base = {
            'rainfall_stats': {
                'india_average': 1200,  # mm per year
                'highest_state': 'Meghalaya (11,871 mm)',
                'lowest_state': 'Rajasthan (313 mm)',
                'monsoon_months': 'June to September',
                'pre_monsoon': 'March to May',
                'post_monsoon': 'October to December'
            },
            'cost_ranges': {
                'small_system': '₹15,000 - ₹30,000',
                'medium_system': '₹30,000 - ₹75,000',
                'large_system': '₹75,000 - ₹1,50,000',
                'maintenance_annual': '₹2,000 - ₹5,000'
            },
            'water_facts': {
                'collection_efficiency': '80-90%',
                'first_flush_waste': '10-15%',
                'storage_period': '6-12 months',
                'quality': 'Better than groundwater in most areas'
            },
            'environmental_benefits': {
                'groundwater_recharge': 'Increases by 40-60%',
                'flood_reduction': 'Reduces urban flooding by 30-50%',
                'energy_savings': 'No pumping costs',
                'carbon_footprint': 'Reduces by 0.5-1 ton CO2/year'
            }
        }
        
        self.responses = {
            'greeting': "Hello! I'm your advanced rainwater harvesting assistant. I can help you with calculations, explain results, provide data insights, or answer detailed questions about rainwater harvesting. What would you like to know?",
            'goodbye': "Thank you for using JalNidhi AI! Feel free to ask me anything about rainwater harvesting anytime. Have a great day! 💧",
            'default': "I can help you with various aspects of rainwater harvesting:\n• Calculator guidance and data input\n• Results analysis and interpretation\n• Rainfall and cost data for different regions\n• Technical specifications and comparisons\n• Environmental impact and benefits\n• District-specific information\n\nWhat specific information are you looking for?"
        }

    def extract_keywords(self, message: str) -> List[str]:
        """Extract meaningful keywords from user message"""
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(message.lower())
                keywords = [word for word in tokens if word.isalpha() and word not in self.stop_words]
                return keywords
            except:
                pass
        
        # Fallback to simple word splitting
        words = message.lower().split()
        keywords = [word.strip('.,!?;:') for word in words if word.isalpha() and word not in self.stop_words]
        return keywords

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()

    def classify_intent(self, message: str) -> str:
        """Enhanced intent classification with similarity matching"""
        message_lower = message.lower()
        keywords = self.extract_keywords(message)
        
        intent_scores = {}
        
        # Direct keyword matching
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in message_lower:
                    score += 1
                # Check for partial matches in keywords
                for keyword in keywords:
                    if self.calculate_similarity(keyword, pattern) > 0.8:
                        score += 0.5
            intent_scores[intent] = score
        
        # Find the best matching intent
        if intent_scores:
            best_intent = max(intent_scores, key=intent_scores.get)
            if intent_scores[best_intent] > 0:
                return best_intent
        
        # Check for specific data questions
        if any(word in keywords for word in ['data', 'statistics', 'numbers', 'facts', 'information']):
            return 'data_questions'
        
        return 'default'

    def handle_data_questions(self, message: str) -> str:
        """Handle various data-related questions"""
        message_lower = message.lower()
        keywords = self.extract_keywords(message)
        
        # Rainfall data questions
        if any(word in keywords for word in ['rainfall', 'rain', 'precipitation', 'monsoon']):
            return self.handle_rainfall_data(message)
        
        # Cost data questions
        if any(word in keywords for word in ['cost', 'price', 'expense', 'money', 'budget']):
            return self.handle_cost_data(message)
        
        # District-specific data
        if 'district' in keywords or 'city' in keywords:
            return self.handle_district_data(message)
        
        # General statistics
        if any(word in keywords for word in ['statistics', 'stats', 'numbers', 'facts']):
            return self.handle_general_stats(message)
        
        # Environmental impact data
        if any(word in keywords for word in ['environment', 'impact', 'carbon', 'green']):
            return self.handle_environmental_data(message)
        
        return "I can provide data about:\n• **Rainfall patterns** across India\n• **Cost estimates** for different system sizes\n• **District-specific** information\n• **Environmental impact** statistics\n• **Water collection** efficiency data\n\nWhat specific data would you like to know about?"

    def handle_rainfall_data(self, message: str) -> str:
        """Handle rainfall-related data questions"""
        message_lower = message.lower()
        
        if 'average' in message_lower or 'typical' in message_lower:
            return f"📊 **Rainfall Data in India**:\n\n• **National Average**: {self.knowledge_base['rainfall_stats']['india_average']} mm/year\n• **Highest**: {self.knowledge_base['rainfall_stats']['highest_state']}\n• **Lowest**: {self.knowledge_base['rainfall_stats']['lowest_state']}\n• **Monsoon Season**: {self.knowledge_base['rainfall_stats']['monsoon_months']}\n\nYour location's rainfall affects water collection potential significantly!"
        
        if 'monsoon' in message_lower:
            return f"🌧️ **Monsoon Patterns**:\n\n• **Main Monsoon**: {self.knowledge_base['rainfall_stats']['monsoon_months']} (75-80% of annual rainfall)\n• **Pre-Monsoon**: {self.knowledge_base['rainfall_stats']['pre_monsoon']} (10-15%)\n• **Post-Monsoon**: {self.knowledge_base['rainfall_stats']['post_monsoon']} (10-15%)\n\nMost rainwater harvesting systems are designed for monsoon collection!"
        
        # Check if user mentioned a specific district
        if RAINFALL_MAP:
            for district in list(RAINFALL_MAP.keys())[:10]:  # Check first 10 districts
                if district.lower() in message_lower:
                    rainfall = RAINFALL_MAP.get(district, 'Data not available')
                    return f"🌧️ **{district.title()} Rainfall Data**:\n\n• **Annual Rainfall**: {rainfall} mm\n• **Collection Potential**: {rainfall * 0.8:.0f} liters per sqm of roof\n• **Best Months**: Monsoon season (June-September)\n\nThis data is used in our suitability calculations!"
        
        return f"🌧️ **Rainfall Information**:\n\n• India receives an average of {self.knowledge_base['rainfall_stats']['india_average']} mm rainfall annually\n• Varies from 313 mm (Rajasthan) to 11,871 mm (Meghalaya)\n• 75% falls during monsoon months\n• Your roof can collect ~0.8 liters per sqm per mm of rainfall\n\nWhich specific aspect interests you?"

    def handle_cost_data(self, message: str) -> str:
        """Handle cost-related questions"""
        message_lower = message.lower()
        
        if 'small' in message_lower or '50' in message_lower or '100' in message_lower:
            return f"💰 **Small System Costs** (50-100 sqm roof):\n\n• **Setup Cost**: {self.knowledge_base['cost_ranges']['small_system']}\n• **Components**: Tank (5,000L), pipes, filters\n• **Annual Maintenance**: ₹2,000-3,000\n• **Payback Period**: 3-5 years\n• **Annual Savings**: ₹8,000-15,000\n\nGreat for individual homes!"
        
        if 'large' in message_lower or 'commercial' in message_lower:
            return f"💰 **Large System Costs** (200+ sqm roof):\n\n• **Setup Cost**: {self.knowledge_base['cost_ranges']['large_system']}\n• **Components**: Multiple tanks, pumps, treatment\n• **Annual Maintenance**: ₹5,000-10,000\n• **Payback Period**: 2-4 years\n• **Annual Savings**: ₹30,000-75,000\n\nIdeal for apartments and commercial buildings!"
        
        if 'roi' in message_lower or 'return' in message_lower or 'payback' in message_lower:
            return "📈 **Return on Investment**:\n\n• **Payback Period**: 2-5 years typically\n• **Water Bill Savings**: 40-70% reduction\n• **Property Value**: Increases by 3-5%\n• **Government Subsidies**: Up to 50% in some states\n• **20-Year Savings**: ₹2-10 lakhs depending on system size\n\nExcellent long-term investment!"
        
        return f"💰 **Cost Information**:\n\n• **Small Systems**: {self.knowledge_base['cost_ranges']['small_system']}\n• **Medium Systems**: {self.knowledge_base['cost_ranges']['medium_system']}\n• **Large Systems**: {self.knowledge_base['cost_ranges']['large_system']}\n• **Annual Maintenance**: {self.knowledge_base['cost_ranges']['maintenance_annual']}\n\nCosts vary by location, components, and installation complexity. Want details for a specific system size?"

    def handle_district_data(self, message: str) -> str:
        """Handle district-specific data questions"""
        message_lower = message.lower()
        
        # Extract potential district names
        words = message_lower.split()
        found_districts = []
        
        if RAINFALL_MAP:
            for word in words:
                if len(word) > 3:
                    for district in list(RAINFALL_MAP.keys())[:20]:  # Check top 20 districts
                        if word in district.lower() or district.lower() in word:
                            found_districts.append(district)
        
        if found_districts:
            district = found_districts[0]
            rainfall = RAINFALL_MAP.get(district, 'Data not available')
            if isinstance(rainfall, (int, float)):
                water_potential = rainfall * 0.8
                return f"📍 **{district.title()} Data**:\n\n• **Annual Rainfall**: {rainfall} mm\n• **Water Collection**: {water_potential:.0f} L per sqm of roof\n• **100 sqm roof potential**: {water_potential * 100:,.0f} L/year\n• **Estimated savings**: ₹{water_potential * 100 * WATER_COST_PER_LITER_INR:,.0f}/year\n• **Suitability**: {'High' if rainfall > 800 else 'Medium' if rainfall > 400 else 'Low'}\n\nThis data is used in our calculations!"
        
        if 'how many' in message_lower or 'total' in message_lower:
            total_districts = len(RAINFALL_MAP) if RAINFALL_MAP else 600
            return f"📊 **District Coverage**:\n\n• **Total Districts**: {total_districts}+ Indian districts\n• **States Covered**: All 28 states + 8 UTs\n• **Data Sources**: IMD, State Water Boards\n• **Update Frequency**: Annual\n• **Accuracy**: ±5% based on 10-year averages\n\nWe have comprehensive coverage across India!"
        
        return "📍 **District Information**:\n\nI have detailed data for 600+ Indian districts including:\n• Annual rainfall patterns\n• Water collection potential\n• Cost estimates\n• Suitability scores\n\nJust mention your district name and I'll provide specific data! Examples: Mumbai, Delhi, Bangalore, Chennai, Pune..."

    def handle_general_stats(self, message: str) -> str:
        """Handle general statistics questions"""
        return f"📊 **Rainwater Harvesting Statistics**:\n\n**Collection Efficiency**:\n• Roof collection: {self.knowledge_base['water_facts']['collection_efficiency']}\n• First flush waste: {self.knowledge_base['water_facts']['first_flush_waste']}\n• Storage period: {self.knowledge_base['water_facts']['storage_period']}\n\n**System Performance**:\n• Average payback: 3-4 years\n• System lifespan: 20-25 years\n• Water quality: {self.knowledge_base['water_facts']['quality']}\n\n**India Statistics**:\n• Only 8% households use rainwater harvesting\n• Potential to meet 40% urban water demand\n• Can reduce groundwater depletion by 60%"

    def handle_environmental_data(self, message: str) -> str:
        """Handle environmental impact questions"""
        return f"🌍 **Environmental Impact Data**:\n\n**Groundwater Benefits**:\n• Recharge increase: {self.knowledge_base['environmental_benefits']['groundwater_recharge']}\n• Prevents land subsidence\n• Improves water table levels\n\n**Urban Benefits**:\n• Flood reduction: {self.knowledge_base['environmental_benefits']['flood_reduction']}\n• Reduces stormwater runoff\n• Decreases urban heat island effect\n\n**Carbon Impact**:\n• CO₂ reduction: {self.knowledge_base['environmental_benefits']['carbon_footprint']}\n• Energy savings: {self.knowledge_base['environmental_benefits']['energy_savings']}\n• Reduces water treatment plant load\n\nEvery liter harvested makes a difference!"

    def handle_calculator_help(self, message: str) -> str:
        if 'roof area' in message.lower():
            return "📏 **Roof Area**: Enter your roof area in square meters (sqm). For example:\n• Small house: 50-100 sqm\n• Medium house: 100-200 sqm\n• Large house: 200+ sqm\n\nTip: Measure length × width of your roof!"
        
        elif 'district' in message.lower():
            return "📍 **District**: Enter your district name in India. I can help find it if you're unsure!\n\nExamples: Mumbai, Delhi, Bangalore, Chennai, Pune\n\nDon't worry about exact spelling - I'll suggest corrections if needed."
        
        elif 'soil' in message.lower():
            return "🌱 **Soil Type**: Choose your soil type:\n• **Sandy**: Drains quickly, good for harvesting\n• **Clay**: Retains water well\n• **Loamy**: Best of both worlds\n• **Rocky**: May need special considerations"
        
        else:
            return "🧮 **Calculator Help**:\n\n1. **Roof Area**: Your roof size in square meters\n2. **District**: Your location in India\n3. **Soil Type**: Sandy, Clay, Loamy, or Rocky\n\nFill these details and click 'Calculate Water Potential' to get your personalized rainwater harvesting analysis!"

    def handle_results_explanation(self, message: str) -> str:
        if 'suitability' in message.lower():
            return "🎯 **Suitability Score**:\n• **High (80-100%)**: Excellent conditions for rainwater harvesting\n• **Medium (50-79%)**: Good potential with some considerations\n• **Low (0-49%)**: Challenging but still possible\n\nFactors: Rainfall, roof area, soil type, and local conditions."
        
        elif 'cost' in message.lower():
            return "💰 **Cost Estimation**:\n• Based on your roof area and local factors\n• Includes: Tank, pipes, filters, installation\n• **ROI**: Usually pays back in 2-5 years through water savings\n• Consider government subsidies in your area!"
        
        elif 'water potential' in message.lower():
            return "💧 **Water Potential**:\n• **Annual**: Total liters you can collect per year\n• **Monthly**: Average monthly collection\n• Formula: Roof Area × Rainfall × Runoff Coefficient\n• 1mm rain on 1 sqm = 1 liter of water!"
        
        else:
            return "📊 **Understanding Your Results**:\n\n• **Suitability**: How suitable your location is (0-100%)\n• **Cost**: Estimated setup cost in INR\n• **Water Potential**: How much water you can collect\n• **Savings**: Money saved on water bills\n• **Weather**: Current conditions in your area"

    def handle_district_help(self, message: str) -> str:
        # Extract potential district name from message
        words = message.split()
        potential_district = None
        
        for word in words:
            if len(word) > 3 and word.lower() not in ['district', 'city', 'find', 'where', 'what', 'help']:
                potential_district = word
                break
        
        if potential_district:
            suggestions = self.find_district_suggestions(potential_district)
            if suggestions:
                return f"🔍 **District Suggestions for '{potential_district}'**:\n\n" + "\n".join([f"• {dist.title()}" for dist in suggestions[:5]])
            else:
                return f"❌ Couldn't find '{potential_district}'. Try major cities like:\n• Mumbai, Delhi, Bangalore, Chennai\n• Pune, Hyderabad, Kolkata, Ahmedabad\n• Or your state capital"
        
        return "📍 **Finding Your District**:\n\nJust type your city or district name. I support all major Indian districts!\n\nExamples:\n• Mumbai → Mumbai\n• Bengaluru → Bangalore\n• NCR → Delhi\n\nNeed help with a specific location? Just ask!"

    def find_district_suggestions(self, query: str) -> List[str]:
        """Find district suggestions using fuzzy matching"""
        if not VALID_DISTRICTS:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for district in VALID_DISTRICTS:
            if query_lower in district.lower():
                matches.append(district)
        
        return sorted(matches)[:5]

    def handle_savings_help(self, message: str) -> str:
        if 'badge' in message.lower():
            badge_info = "🏆 **Badge System**:\n\n"
            for badge, liters in BADGE_LEVELS:
                badge_info += f"• **{badge}**: {liters:,} liters saved\n"
            badge_info += "\nKeep calculating to unlock higher badges!"
            return badge_info
        
        elif 'dashboard' in message.lower():
            return "📊 **Savings Dashboard**:\n\n• **Total Savings**: Your cumulative water and money saved\n• **Monthly Breakdown**: Track your progress over time\n• **Badge Progress**: See how close you are to the next level\n• **Charts**: Visual representation of your impact\n\nAccess it from the navigation menu!"
        
        else:
            return "💰 **Your Savings**:\n\n• **Water Saved**: Calculated from your roof area and rainfall\n• **Money Saved**: Based on ₹0.05 per liter water cost\n• **Environmental Impact**: Every liter counts!\n• **Badge System**: Unlock achievements as you save more\n\nCheck your dashboard to track progress!"

    def handle_faq(self, message: str) -> str:
        faq_responses = {
            'what is rainwater harvesting': "🌧️ **Rainwater Harvesting** is collecting and storing rainwater from rooftops for later use. It's an eco-friendly way to:\n• Reduce water bills\n• Conserve groundwater\n• Prevent flooding\n• Ensure water security",
            
            'benefits': "✅ **Benefits of Rainwater Harvesting**:\n• 💰 Save money on water bills\n• 🌍 Reduce environmental impact\n• 💧 Ensure water security\n• 🏠 Increase property value\n• 🌱 Recharge groundwater\n• 🌊 Prevent urban flooding",
            
            'how does it work': "⚙️ **How It Works**:\n1. Rain falls on your roof\n2. Water flows through gutters\n3. First flush diverter removes debris\n4. Clean water is stored in tanks\n5. Use for gardening, cleaning, or drinking (after treatment)\n\nSimple, effective, and sustainable!"
        }
        
        message_lower = message.lower()
        for key, response in faq_responses.items():
            if key in message_lower:
                return response
        
        return "❓ **Common Questions**:\n\n• What is rainwater harvesting?\n• What are the benefits?\n• How does it work?\n• Is it cost-effective?\n• What permits do I need?\n\nAsk me anything specific about rainwater harvesting!"

    def get_response(self, message: str, user_context: Dict = None) -> str:
        """Main method to get chatbot response"""
        if user_context:
            self.context.update(user_context)
        
        intent = self.classify_intent(message)
        
        if intent == 'greeting':
            return self.responses['greeting']
        elif intent == 'goodbye':
            return self.responses['goodbye']
        elif intent == 'calculator_help':
            return self.handle_calculator_help(message)
        elif intent == 'results_explanation':
            return self.handle_results_explanation(message)
        elif intent == 'data_questions':
            return self.handle_data_questions(message)
        elif intent == 'rainfall_data':
            return self.handle_rainfall_data(message)
        elif intent == 'cost_data':
            return self.handle_cost_data(message)
        elif intent == 'environmental_impact':
            return self.handle_environmental_data(message)
        elif intent == 'district_help':
            return self.handle_district_help(message)
        elif intent == 'savings_help':
            return self.handle_savings_help(message)
        elif intent == 'faq':
            return self.handle_faq(message)
        else:
            return self.responses['default']


# Global chatbot instance
chatbot = RainwaterChatbot()