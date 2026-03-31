"""
AI-powered flood risk and water scarcity prediction service.
Analyzes weather patterns and provides intelligent water storage recommendations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime, timedelta


class RiskLevel(Enum):
    """Water management risk levels"""
    NORMAL = "normal"
    FLOOD_RISK = "flood_risk"
    WATER_SCARCITY = "scarcity"


@dataclass
class WeatherForecast:
    """Weather forecast data structure"""
    date: str
    rainfall_mm: float
    temperature: float
    humidity: float


@dataclass
class PredictionResult:
    """AI prediction result with recommendations"""
    risk_level: RiskLevel
    confidence: float
    predicted_rainfall_7days: float
    current_tank_level_pct: float
    recommended_action: str
    system_action: str
    alert_message: str
    color_code: str
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'risk_level': self.risk_level.value,
            'confidence': round(self.confidence, 2),
            'predicted_rainfall_7days': round(self.predicted_rainfall_7days, 2),
            'current_tank_level_pct': round(self.current_tank_level_pct, 2),
            'recommended_action': self.recommended_action,
            'system_action': self.system_action,
            'alert_message': self.alert_message,
            'color_code': self.color_code,
        }


class FloodPredictionAI:
    """
    AI engine for predicting flood risk and water scarcity.
    Uses threshold-based logic with weather forecast data.
    """
    
    # Thresholds (configurable)
    FLOOD_THRESHOLD_MM_PER_DAY = 50.0
    SCARCITY_THRESHOLD_MM_PER_DAY = 5.0
    SCARCITY_CONSECUTIVE_DAYS = 3
    
    # Tank management thresholds
    TANK_HIGH_LEVEL = 80.0  # Release water if above this during flood risk
    TANK_LOW_LEVEL = 30.0   # Trigger conservation mode
    
    def __init__(self):
        """Initialize the AI prediction engine"""
        pass
    
    def predict(
        self,
        forecast_data: list[WeatherForecast],
        current_tank_level_pct: float,
        tank_capacity_liters: float
    ) -> PredictionResult:
        """
        Main prediction method - analyzes forecast and returns recommendations.
        
        Args:
            forecast_data: List of weather forecasts for next 7 days
            current_tank_level_pct: Current tank fill level (0-100%)
            tank_capacity_liters: Total tank capacity in liters
            
        Returns:
            PredictionResult with risk assessment and recommendations
        """
        if not forecast_data:
            return self._create_default_result(current_tank_level_pct)
        
        # Calculate total predicted rainfall
        total_rainfall = sum(day.rainfall_mm for day in forecast_data)
        avg_daily_rainfall = total_rainfall / len(forecast_data)
        
        # Detect flood risk
        if self._is_flood_risk(forecast_data):
            return self._create_flood_result(
                total_rainfall, current_tank_level_pct, tank_capacity_liters
            )
        
        # Detect water scarcity
        if self._is_water_scarcity(forecast_data):
            return self._create_scarcity_result(
                total_rainfall, current_tank_level_pct
            )
        
        # Normal conditions
        return self._create_normal_result(
            total_rainfall, current_tank_level_pct
        )
    
    def _is_flood_risk(self, forecast_data: list[WeatherForecast]) -> bool:
        """Check if any day exceeds flood threshold"""
        return any(
            day.rainfall_mm > self.FLOOD_THRESHOLD_MM_PER_DAY 
            for day in forecast_data
        )
    
    def _is_water_scarcity(self, forecast_data: list[WeatherForecast]) -> bool:
        """Check for consecutive days of low rainfall"""
        consecutive_low = 0
        for day in forecast_data:
            if day.rainfall_mm < self.SCARCITY_THRESHOLD_MM_PER_DAY:
                consecutive_low += 1
                if consecutive_low >= self.SCARCITY_CONSECUTIVE_DAYS:
                    return True
            else:
                consecutive_low = 0
        return False
    
    def _create_flood_result(
        self, 
        total_rainfall: float, 
        tank_level: float,
        tank_capacity: float
    ) -> PredictionResult:
        """Generate flood risk prediction result"""
        
        # Determine system action based on tank level
        if tank_level > self.TANK_HIGH_LEVEL:
            system_action = f"Releasing {int((tank_level - 70) * tank_capacity / 100)}L to create storage space"
            recommended_action = "System preparing for heavy rainfall - storage optimized"
        else:
            system_action = "Preparing to capture maximum rainwater"
            recommended_action = "Ensure drainage systems are clear"
        
        alert = f"⚠️ Heavy rain expected ({total_rainfall:.1f}mm in 7 days) - storage optimized"
        
        return PredictionResult(
            risk_level=RiskLevel.FLOOD_RISK,
            confidence=0.85,
            predicted_rainfall_7days=total_rainfall,
            current_tank_level_pct=tank_level,
            recommended_action=recommended_action,
            system_action=system_action,
            alert_message=alert,
            color_code="#ef4444"  # Red
        )
    
    def _create_scarcity_result(
        self, 
        total_rainfall: float, 
        tank_level: float
    ) -> PredictionResult:
        """Generate water scarcity prediction result"""
        
        if tank_level < self.TANK_LOW_LEVEL:
            system_action = "Low usage mode activated - conserving water"
            recommended_action = "Minimize water usage - critical level"
        else:
            system_action = "Storing maximum water - conservation mode"
            recommended_action = "Reduce non-essential water usage"
        
        alert = f"💧 Low rainfall predicted ({total_rainfall:.1f}mm in 7 days) - conserve water"
        
        return PredictionResult(
            risk_level=RiskLevel.WATER_SCARCITY,
            confidence=0.80,
            predicted_rainfall_7days=total_rainfall,
            current_tank_level_pct=tank_level,
            recommended_action=recommended_action,
            system_action=system_action,
            alert_message=alert,
            color_code="#eab308"  # Yellow
        )
    
    def _create_normal_result(
        self, 
        total_rainfall: float, 
        tank_level: float
    ) -> PredictionResult:
        """Generate normal conditions result"""
        
        system_action = "Normal operation - optimal water management"
        recommended_action = "Continue regular water usage"
        alert = f"✓ Normal conditions ({total_rainfall:.1f}mm expected in 7 days)"
        
        return PredictionResult(
            risk_level=RiskLevel.NORMAL,
            confidence=0.75,
            predicted_rainfall_7days=total_rainfall,
            current_tank_level_pct=tank_level,
            recommended_action=recommended_action,
            system_action=system_action,
            alert_message=alert,
            color_code="#22c55e"  # Green
        )
    
    def _create_default_result(self, tank_level: float) -> PredictionResult:
        """Fallback result when no forecast data available"""
        return PredictionResult(
            risk_level=RiskLevel.NORMAL,
            confidence=0.50,
            predicted_rainfall_7days=0.0,
            current_tank_level_pct=tank_level,
            recommended_action="No forecast data available",
            system_action="Monitoring mode",
            alert_message="⚠️ Weather data unavailable - manual monitoring recommended",
            color_code="#6b7280"  # Gray
        )


# Singleton instance
flood_ai = FloodPredictionAI()
