"""
AI-powered Borewell Depth Estimation Service
Estimates optimal borewell depth using proxy factors without real groundwater data
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class RegionType(Enum):
    """Region classification"""
    URBAN = "urban"
    RURAL = "rural"
    SEMI_URBAN = "semi_urban"


class SoilType(Enum):
    """Soil type classification"""
    LOAMY = "loamy"
    CLAY = "clay"
    SANDY = "sandy"
    ROCKY = "rocky"


@dataclass
class BorewellEstimate:
    """Borewell depth estimation result"""
    min_depth_feet: int
    max_depth_feet: int
    recommended_depth_feet: int
    confidence_level: float  # 0.0 to 1.0
    water_availability: str  # "High", "Moderate", "Low"
    estimated_yield_lph: int  # Liters per hour
    reasoning: str
    cost_estimate_inr: Tuple[int, int]  # (min, max)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'min_depth_feet': self.min_depth_feet,
            'max_depth_feet': self.max_depth_feet,
            'recommended_depth_feet': self.recommended_depth_feet,
            'confidence_level': round(self.confidence_level, 2),
            'water_availability': self.water_availability,
            'estimated_yield_lph': self.estimated_yield_lph,
            'reasoning': self.reasoning,
            'cost_estimate_min': self.cost_estimate_inr[0],
            'cost_estimate_max': self.cost_estimate_inr[1],
        }


class BorewellDepthEstimator:
    """
    AI-based borewell depth estimator using proxy factors
    """
    
    # Base depth ranges by region type (in feet)
    BASE_DEPTHS = {
        RegionType.URBAN: (80, 200),
        RegionType.SEMI_URBAN: (100, 250),
        RegionType.RURAL: (120, 300),
    }
    
    # Soil type multipliers
    SOIL_MULTIPLIERS = {
        SoilType.LOAMY: 1.0,      # Best water retention
        SoilType.CLAY: 1.1,       # Moderate retention, deeper needed
        SoilType.SANDY: 1.3,      # Poor retention, much deeper
        SoilType.ROCKY: 1.4,      # Hardest to drill, deepest
    }
    
    # Rainfall impact factors (mm/year)
    RAINFALL_THRESHOLDS = {
        'very_high': 2000,  # >2000mm - shallow borewell sufficient
        'high': 1200,       # 1200-2000mm - moderate depth
        'moderate': 600,    # 600-1200mm - standard depth
        'low': 300,         # 300-600mm - deeper needed
        'very_low': 0,      # <300mm - very deep required
    }
    
    # Cost per foot (INR) - varies by region
    COST_PER_FOOT = {
        RegionType.URBAN: (300, 500),
        RegionType.SEMI_URBAN: (250, 400),
        RegionType.RURAL: (200, 350),
    }
    
    def __init__(self):
        """Initialize the estimator"""
        pass
    
    def estimate_depth(
        self,
        location: str,
        annual_rainfall_mm: float,
        region_type: RegionType = RegionType.SEMI_URBAN,
        soil_type: SoilType = SoilType.LOAMY,
        population_density: Optional[int] = None
    ) -> BorewellEstimate:
        """
        Estimate optimal borewell depth using AI logic
        
        Args:
            location: City or region name
            annual_rainfall_mm: Annual rainfall in millimeters
            region_type: Urban, Semi-urban, or Rural
            soil_type: Type of soil
            population_density: Optional population density (people/sq km)
            
        Returns:
            BorewellEstimate with depth range and confidence
        """
        
        # Step 1: Get base depth range for region
        base_min, base_max = self.BASE_DEPTHS[region_type]
        
        # Step 2: Apply rainfall adjustment
        rainfall_factor = self._calculate_rainfall_factor(annual_rainfall_mm)
        
        # Step 3: Apply soil type multiplier
        soil_multiplier = self.SOIL_MULTIPLIERS[soil_type]
        
        # Step 4: Apply population density adjustment (if available)
        density_factor = self._calculate_density_factor(population_density, region_type)
        
        # Step 5: Calculate adjusted depths
        adjusted_min = int(base_min * rainfall_factor * soil_multiplier * density_factor)
        adjusted_max = int(base_max * rainfall_factor * soil_multiplier * density_factor)
        
        # Step 6: Calculate recommended depth (sweet spot)
        recommended = int((adjusted_min + adjusted_max) / 2)
        
        # Step 7: Ensure reasonable bounds
        adjusted_min = max(50, min(adjusted_min, 500))
        adjusted_max = max(100, min(adjusted_max, 600))
        recommended = max(adjusted_min, min(recommended, adjusted_max))
        
        # Step 8: Calculate confidence level
        confidence = self._calculate_confidence(
            annual_rainfall_mm, region_type, soil_type, population_density
        )
        
        # Step 9: Estimate water availability
        water_availability = self._estimate_water_availability(
            annual_rainfall_mm, soil_type, recommended
        )
        
        # Step 10: Estimate yield
        estimated_yield = self._estimate_yield(
            annual_rainfall_mm, soil_type, recommended
        )
        
        # Step 11: Generate reasoning
        reasoning = self._generate_reasoning(
            location, annual_rainfall_mm, region_type, soil_type,
            adjusted_min, adjusted_max, recommended
        )
        
        # Step 12: Calculate cost estimate
        cost_min, cost_max = self.COST_PER_FOOT[region_type]
        cost_estimate = (
            recommended * cost_min,
            recommended * cost_max
        )
        
        return BorewellEstimate(
            min_depth_feet=adjusted_min,
            max_depth_feet=adjusted_max,
            recommended_depth_feet=recommended,
            confidence_level=confidence,
            water_availability=water_availability,
            estimated_yield_lph=estimated_yield,
            reasoning=reasoning,
            cost_estimate_inr=cost_estimate
        )
    
    def _calculate_rainfall_factor(self, rainfall_mm: float) -> float:
        """Calculate depth adjustment factor based on rainfall"""
        if rainfall_mm >= self.RAINFALL_THRESHOLDS['very_high']:
            return 0.7  # Less depth needed with high rainfall
        elif rainfall_mm >= self.RAINFALL_THRESHOLDS['high']:
            return 0.85
        elif rainfall_mm >= self.RAINFALL_THRESHOLDS['moderate']:
            return 1.0  # Standard depth
        elif rainfall_mm >= self.RAINFALL_THRESHOLDS['low']:
            return 1.2  # More depth needed
        else:
            return 1.5  # Much more depth needed in low rainfall areas
    
    def _calculate_density_factor(
        self, 
        population_density: Optional[int],
        region_type: RegionType
    ) -> float:
        """Calculate adjustment based on population density"""
        if population_density is None:
            return 1.0
        
        # High density = more water extraction = deeper borewell needed
        if population_density > 10000:  # Very high density
            return 1.2
        elif population_density > 5000:  # High density
            return 1.1
        elif population_density > 1000:  # Moderate density
            return 1.0
        else:  # Low density
            return 0.9
    
    def _calculate_confidence(
        self,
        rainfall_mm: float,
        region_type: RegionType,
        soil_type: SoilType,
        population_density: Optional[int]
    ) -> float:
        """Calculate confidence level of the estimate"""
        confidence = 0.7  # Base confidence
        
        # Higher confidence with more typical values
        if 600 <= rainfall_mm <= 2000:
            confidence += 0.1
        
        # Higher confidence with common soil types
        if soil_type in [SoilType.LOAMY, SoilType.CLAY]:
            confidence += 0.05
        
        # Higher confidence if we have population data
        if population_density is not None:
            confidence += 0.05
        
        # Urban areas have more predictable patterns
        if region_type == RegionType.URBAN:
            confidence += 0.05
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def _estimate_water_availability(
        self,
        rainfall_mm: float,
        soil_type: SoilType,
        depth_feet: int
    ) -> str:
        """Estimate water availability at the recommended depth"""
        # High rainfall + good soil + adequate depth = high availability
        score = 0
        
        if rainfall_mm > 1200:
            score += 3
        elif rainfall_mm > 600:
            score += 2
        else:
            score += 1
        
        if soil_type in [SoilType.LOAMY, SoilType.CLAY]:
            score += 2
        else:
            score += 1
        
        if depth_feet >= 150:
            score += 2
        elif depth_feet >= 100:
            score += 1
        
        if score >= 6:
            return "High"
        elif score >= 4:
            return "Moderate"
        else:
            return "Low"
    
    def _estimate_yield(
        self,
        rainfall_mm: float,
        soil_type: SoilType,
        depth_feet: int
    ) -> int:
        """Estimate water yield in liters per hour"""
        # Base yield
        base_yield = 500
        
        # Rainfall impact
        if rainfall_mm > 1500:
            base_yield *= 2.0
        elif rainfall_mm > 1000:
            base_yield *= 1.5
        elif rainfall_mm > 600:
            base_yield *= 1.2
        elif rainfall_mm < 300:
            base_yield *= 0.6
        
        # Soil impact
        if soil_type == SoilType.LOAMY:
            base_yield *= 1.3
        elif soil_type == SoilType.CLAY:
            base_yield *= 1.1
        elif soil_type == SoilType.SANDY:
            base_yield *= 0.8
        elif soil_type == SoilType.ROCKY:
            base_yield *= 0.7
        
        # Depth impact (deeper = more yield, but diminishing returns)
        if depth_feet > 200:
            base_yield *= 1.3
        elif depth_feet > 150:
            base_yield *= 1.2
        elif depth_feet > 100:
            base_yield *= 1.1
        
        return int(base_yield)
    
    def _generate_reasoning(
        self,
        location: str,
        rainfall_mm: float,
        region_type: RegionType,
        soil_type: SoilType,
        min_depth: int,
        max_depth: int,
        recommended: int
    ) -> str:
        """Generate human-readable reasoning for the estimate"""
        reasons = []
        
        # Location context
        reasons.append(f"For {location} ({region_type.value} area)")
        
        # Rainfall analysis
        if rainfall_mm > 1500:
            reasons.append(f"High annual rainfall ({rainfall_mm:.0f}mm) allows for shallower borewell")
        elif rainfall_mm > 800:
            reasons.append(f"Moderate rainfall ({rainfall_mm:.0f}mm) requires standard depth")
        else:
            reasons.append(f"Low rainfall ({rainfall_mm:.0f}mm) requires deeper borewell for reliable water")
        
        # Soil analysis
        if soil_type == SoilType.LOAMY:
            reasons.append("Loamy soil has good water retention")
        elif soil_type == SoilType.SANDY:
            reasons.append("Sandy soil requires deeper drilling due to poor water retention")
        elif soil_type == SoilType.ROCKY:
            reasons.append("Rocky terrain requires deeper drilling and may increase costs")
        
        # Recommendation
        reasons.append(f"Recommended depth: {recommended} feet (range: {min_depth}-{max_depth} feet)")
        
        return ". ".join(reasons) + "."


# Singleton instance
borewell_estimator = BorewellDepthEstimator()
