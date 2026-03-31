from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import math
import json
from datetime import datetime, timezone
from .utils import predict_suitability, predict_cost
from .models import UserWaterSavings, Vendor, WaterTank, FloodPredictionLog, BorewellEstimation
from services.rainwater_calculator import (
    calculate_water,
    get_district_rainfall,
    validate_district,
    validate_inputs,
)
from services.weather_api import get_weather
from services.water_savings import analyze_savings
from services.gemini_chatbot import chatbot  # Changed from openai_chatbot to gemini_chatbot
from services.flood_prediction import flood_ai
from services.weather_forecast import weather_forecast_service
from services.borewell_estimator import borewell_estimator, RegionType, SoilType


def _get_actor_filter(request):
    if getattr(request, "user", None) is not None and request.user.is_authenticated:
        return {"user": request.user}, ""

    if not request.session.session_key:
        request.session.save()
    return {"session_key": request.session.session_key}, request.session.session_key


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def vendor_list(request):
    vendors = Vendor.objects.all().order_by('-added_date')
    return render(request, "vendors.html", {"vendors": vendors})


def analytics(request):
    return render(request, "analytics.html")


def analytics_download(request):
    now = datetime.now(timezone.utc)
    filename = f"jalnidhi_personal_report_{now.strftime('%Y%m%d_%H%M%S')}Z.csv"

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Get user's calculation data
    actor_filter, _ = _get_actor_filter(request)
    latest = UserWaterSavings.objects.filter(**actor_filter).order_by("-calculation_date").first()
    
    lines = []
    def w(row):
        output = []
        for value in row:
            text = "" if value is None else str(value)
            if any(ch in text for ch in [",", "\"", "\n", "\r"]):
                text = "\"" + text.replace("\"", "\"\"") + "\""
            output.append(text)
        lines.append(",".join(output))

    w(["JalNidhi AI - Personal Water Savings Report"])
    w(["Generated (UTC)", now.isoformat()])
    w([])

    if latest:
        # Calculate analysis data
        analysis = analyze_savings(latest.roof_area, latest.rainfall, latest.runoff_coefficient)
        
        w(["Personal Calculation Summary"])
        w(["Calculation Date", latest.calculation_date.isoformat()])
        w(["Roof Area (sqm)", latest.roof_area])
        w(["Annual Rainfall (mm)", latest.rainfall])
        w(["Runoff Coefficient", latest.runoff_coefficient])
        w([])
        
        w(["Water Savings Results"])
        w(["Annual Water Saved (Liters)", f"{analysis.water_yearly_liters:,.1f}"])
        w(["Monthly Water Saved (Liters)", f"{analysis.water_monthly_liters:,.1f}"])
        w(["Annual Money Saved (INR)", f"{analysis.money_yearly_inr:,.2f}"])
        w(["Monthly Money Saved (INR)", f"{analysis.money_monthly_inr:,.2f}"])
        w(["Current Badge", analysis.badge])
        w(["Progress to Next Badge (%)", f"{analysis.progress_to_next_pct}%"])
        w([])
        
        w(["Environmental Impact"])
        families_supported = max(1, int(analysis.water_yearly_liters / 21600))  # 21,600L per family per month
        w(["Families Supported (1 month)", families_supported])
        w(["CO2 Reduction (kg/year)", f"{analysis.water_yearly_liters * 0.0005:,.1f}"])  # Approx 0.5g CO2 per liter
        w(["Groundwater Recharge (Liters)", f"{analysis.water_yearly_liters * 0.6:,.1f}"])  # 60% recharge rate
        w([])
        
        w(["Monthly Breakdown (Last 6 Months Projection)"])
        w(["Month", "Projected Water Saved (Liters)"])
        month_abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        today = datetime.now(timezone.utc).date()
        base_monthly = float(analysis.water_monthly_liters)
        weights = [0.6, 0.75, 0.9, 1.0, 1.15, 1.3]
        
        for i, weight in enumerate(weights):
            month_delta = i - 5
            month_num = (today.month + month_delta - 1) % 12 + 1
            month_name = month_abbr[month_num - 1]
            projected_water = round(base_monthly * weight, 1)
            w([month_name, f"{projected_water:,.1f}"])
        
    else:
        w(["No Calculation Data Available"])
        w(["Please complete a calculation on the home page first"])
        w(["Visit: Home > Calculator > Fill Details > Calculate"])
        w([])
        w(["Sample Benefits of Rainwater Harvesting"])
        w(["Water Bill Reduction", "40-70%"])
        w(["Groundwater Recharge", "40-60% increase"])
        w(["Flood Reduction", "30-50% in urban areas"])
        w(["Property Value Increase", "3-5%"])
        w(["Payback Period", "2-5 years"])

    response.write("\n".join(lines))
    return response


def savings_dashboard(request):
    actor_filter, _ = _get_actor_filter(request)
    latest = UserWaterSavings.objects.filter(**actor_filter).order_by("-calculation_date").first()

    analysis = None
    if latest is not None:
        analysis = analyze_savings(latest.roof_area, latest.rainfall, latest.runoff_coefficient)

    totals = None
    families_supported = None
    chart = None

    if analysis is not None:
        water_yearly_raw = int(round(float(analysis.water_yearly_liters)))
        money_monthly_raw = float(analysis.money_monthly_inr)
        money_yearly_raw = float(analysis.money_yearly_inr)

        totals = {
            "water_yearly_liters_raw": water_yearly_raw,
            "water_yearly_liters_display": f"{water_yearly_raw:,}",
            "money_monthly_inr_display": f"{money_monthly_raw:,.0f}",
            "money_yearly_inr_display": f"{money_yearly_raw:,.0f}",
        }

        family_monthly_liters = 21_600
        if water_yearly_raw <= 0:
            families_supported = 0
        else:
            families_supported = max(1, int(math.floor(water_yearly_raw / float(family_monthly_liters))))

        month_abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        today = datetime.now(timezone.utc).date()

        def _shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
            month = month + delta
            year = year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            return year, month

        month_labels = []
        for delta in range(-5, 1):
            _, m = _shift_month(today.year, today.month, delta)
            month_labels.append(month_abbr[m - 1])

        base_monthly = float(analysis.water_monthly_liters)
        weights = [0.6, 0.75, 0.9, 1.0, 1.15, 1.3]
        monthly_water = [round(base_monthly * w, 1) for w in weights]

        chart = {
            "month_labels": month_labels,
            "monthly_water": monthly_water,
            "breakdown": [75, 25],
        }

    return render(request, "savings_dashboard.html", {
        "latest": latest,
        "analysis": analysis,
        "totals": totals,
        "families_supported": families_supported,
        "chart": chart,
    })


def savings_latest_api(request):
    actor_filter, _ = _get_actor_filter(request)
    latest = UserWaterSavings.objects.filter(**actor_filter).order_by("-calculation_date").first()
    if latest is None:
        return JsonResponse({"ok": False, "error": "No savings found yet."}, status=404)

    analysis = analyze_savings(latest.roof_area, latest.rainfall, latest.runoff_coefficient)

    return JsonResponse({
        "ok": True,
        "data": {
            "roof_area": latest.roof_area,
            "rainfall": latest.rainfall,
            "runoff_coefficient": latest.runoff_coefficient,
            "water_yearly_liters": analysis.water_yearly_liters,
            "water_monthly_liters": analysis.water_monthly_liters,
            "money_yearly_inr": analysis.money_yearly_inr,
            "money_monthly_inr": analysis.money_monthly_inr,
            "badge": analysis.badge,
            "current_badge_goal_liters": analysis.current_badge_goal_liters,
            "next_badge": analysis.next_badge,
            "next_badge_goal_liters": analysis.next_badge_goal_liters,
            "progress_to_next_pct": analysis.progress_to_next_pct,
            "calculation_date": latest.calculation_date.isoformat(),
        }
    })


def calculate(request):
    if request.method == "POST":

        # ── 1. Get raw inputs ──────────────────────────────────────────
        city = request.POST.get("city", "").strip()
        soil = request.POST.get("soil", "").strip()
        name = request.POST.get("name", "").strip()

        # ── 2. Validate city FIRST — stop everything if invalid ────────
        if not city:
            return render(request, "home.html", {
                "error": "Please enter a district name.",
                "prev_name": name,
            })

        is_valid, suggestion = validate_district(city)

        if not is_valid:
            error_msg = (
                f'"{city}" not found. Did you mean "{suggestion.title()}"?'
                if suggestion else
                f'"{city}" is not a recognised district in our dataset. Please enter a valid Indian district.'
            )
            return render(request, "home.html", {
                "error": error_msg,
                "prev_city": city,
                "prev_name": name,
            })

        # ✅ Auto-fetch rainfall from dataset instead of user input
        rainfall = get_district_rainfall(city)
        if rainfall is None:
            return render(request, "home.html", {
                "error": f"Rainfall data not available for {city.title()}.",
                "prev_city": city,
                "prev_name": name,
            })
        rainfall = round(float(rainfall), 1)

        # ── 3. Validate numeric inputs ─────────────────────────────────
        try:
            area     = float(request.POST.get("area", 0))
            tank     = float(request.POST.get("tank", 0))
        except (ValueError, TypeError):
            return render(request, "home.html", {
                "error": "Rooftop area and tank capacity must be valid numbers.",
                "prev_city": city,
                "prev_name": name,
            })

        numeric_error = validate_inputs(area, tank)
        if numeric_error:
            return render(request, "home.html", {
                "error": numeric_error,
                "prev_city": city,
                "prev_name": name,
            })

        # ── 4. Validate soil type ──────────────────────────────────────
        valid_soils = ["Loamy", "Clay", "Sandy", "Rocky"]
        if soil not in valid_soils:
            return render(request, "home.html", {
                "error": f'Invalid soil type. Choose from: {", ".join(valid_soils)}',
                "prev_city": city,
                "prev_name": name,
            })

        # The suitability model was trained with a "soil_suitability" label
        # (High/Moderate/Low). The UI collects soil type, so map it to a signal.
        soil_type_to_signal = {
            "Loamy": "High",
            "Sandy": "Moderate",
            "Clay": "Low",
            "Rocky": "Low",
        }
        soil_signal = soil_type_to_signal.get(soil, "Moderate")

        # ── 5. Get weather — city already validated, safe to call ──────
        weather = get_weather(city)
        if weather is None:
            # Valid district but OpenWeatherMap can't match spelling — safe defaults
            weather = {"temp": "--", "humidity": "--", "rain": 0, "city_found": False}

        # ── 6. Run ML models — wrapped in try/except for safety ────────
        try:
            suitability = predict_suitability(10, 5, rainfall, soil_signal)
            cost        = predict_cost(suitability, area, rainfall, tank, 0.8)
        except RuntimeError as e:
            return render(request, "home.html", {
                "error": str(e),
                "prev_city": city,
                "prev_name": name,
            })
        except ValueError as e:
            return render(request, "home.html", {
                "error": f"Model error: {str(e)}",
                "prev_city": city,
                "prev_name": name,
            })
        except Exception:
            return render(request, "home.html", {
                "error": "Something went wrong running the prediction. Please try again.",
                "prev_city": city,
                "prev_name": name,
            })

        runoff_coefficient = 0.8
        water = calculate_water(area, rainfall, runoff=runoff_coefficient)

        savings = analyze_savings(area, rainfall, runoff_coefficient)
        actor_filter, session_key = _get_actor_filter(request)
        user = actor_filter.get("user")
        UserWaterSavings.objects.create(
            user=user if user is not None else None,
            session_key=session_key,
            roof_area=area,
            rainfall=rainfall,
            runoff_coefficient=runoff_coefficient,
            water_saved=savings.water_yearly_liters,
            money_saved=savings.money_yearly_inr,
            badge=savings.badge,
        )

        context = {
            "city"        : city.title(),
            "name"        : name,
            "suitability" : suitability,
            "cost"        : cost,
            "water"       : water,
            "savings"     : savings,
            "weather"     : weather,
            "area"        : area,
            "rainfall"    : rainfall,
            "tank"        : tank,
        }
        return render(request, "result.html", context)

    return render(request, "home.html")


@csrf_exempt
def chatbot_api(request):
    """API endpoint for chatbot interactions"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Get user context for personalized responses
        user_context = {}
        try:
            actor_filter, _ = _get_actor_filter(request)
            latest_savings = UserWaterSavings.objects.filter(**actor_filter).order_by("-calculation_date").first()
            
            if latest_savings:
                analysis = analyze_savings(latest_savings.roof_area, latest_savings.rainfall, latest_savings.runoff_coefficient)
                user_context = {
                    'has_calculations': True,
                    'latest_badge': analysis.badge,
                    'water_saved': analysis.water_yearly_liters,
                    'money_saved': analysis.money_yearly_inr,
                }
            else:
                user_context = {'has_calculations': False}
        except Exception as e:
            # If there's an error getting user context, continue with empty context
            user_context = {'has_calculations': False}
        
        # Get chatbot response
        try:
            response = chatbot.get_response(message, user_context)
        except Exception as e:
            # Fallback response if chatbot fails
            response = "I'm sorry, I encountered an error processing your message. Please try asking your question in a different way."
        
        return JsonResponse({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)



def flood_dashboard(request):
    """Main dashboard for flood prediction and water management"""
    actor_filter, _ = _get_actor_filter(request)
    
    # Get or create default tank
    tank = WaterTank.objects.filter(**actor_filter).first()
    
    # Get latest prediction if exists
    latest_prediction = None
    if tank:
        latest_prediction = FloodPredictionLog.objects.filter(tank=tank).first()
    
    return render(request, 'flood_dashboard.html', {
        'tank': tank,
        'latest_prediction': latest_prediction,
    })


def water_guard_mvp(request):
    """Complete MVP dashboard with simulation controls and voice assistant"""
    actor_filter, _ = _get_actor_filter(request)
    
    # Get or create default tank
    tank = WaterTank.objects.filter(**actor_filter).first()
    
    # Get latest prediction if exists
    latest_prediction = None
    if tank:
        latest_prediction = FloodPredictionLog.objects.filter(tank=tank).first()
    
    return render(request, 'water_guard_mvp.html', {
        'tank': tank,
        'latest_prediction': latest_prediction,
    })


@csrf_exempt
def flood_prediction_api(request):
    """API endpoint for AI flood prediction"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            city = data.get('city', '').strip()
            tank_capacity = float(data.get('tank_capacity', 5000))
            current_level = float(data.get('current_level', 2500))
            scenario = data.get('scenario', 'normal')  # Simulation scenario
            
            if not city:
                return JsonResponse({'error': 'City is required'}, status=400)
            
            # Get or create tank
            actor_filter, session_key = _get_actor_filter(request)
            user = actor_filter.get('user')
            
            tank, created = WaterTank.objects.get_or_create(
                **actor_filter,
                defaults={
                    'name': f'{city.title()} Tank',
                    'capacity_liters': tank_capacity,
                    'current_level_liters': current_level,
                    'location': city,
                }
            )
            
            if not created:
                tank.capacity_liters = tank_capacity
                tank.current_level_liters = current_level
                tank.location = city
                tank.save()
            
            # Get forecast based on scenario
            if scenario in ['heavy_rain', 'drought', 'normal']:
                # Use simulated forecast for demo
                forecast = weather_forecast_service.get_simulated_forecast(scenario)
            else:
                # Use real API forecast
                forecast = weather_forecast_service.get_7day_forecast(city)
            
            # Run AI prediction
            prediction = flood_ai.predict(
                forecast_data=forecast,
                current_tank_level_pct=tank.level_percentage,
                tank_capacity_liters=tank.capacity_liters
            )
            
            # Log prediction
            FloodPredictionLog.objects.create(
                tank=tank,
                risk_level=prediction.risk_level.value,
                confidence=prediction.confidence,
                predicted_rainfall_7days=prediction.predicted_rainfall_7days,
                tank_level_pct=prediction.current_tank_level_pct,
                recommended_action=prediction.recommended_action,
                system_action=prediction.system_action,
                alert_message=prediction.alert_message,
            )
            
            # Prepare forecast data for response
            forecast_list = [
                {
                    'date': f.date,
                    'rainfall_mm': f.rainfall_mm,
                    'temperature': f.temperature,
                    'humidity': f.humidity,
                }
                for f in forecast
            ]
            
            return JsonResponse({
                'success': True,
                'prediction': prediction.to_dict(),
                'tank': {
                    'name': tank.name,
                    'capacity': tank.capacity_liters,
                    'current_level': tank.current_level_liters,
                    'level_percentage': round(tank.level_percentage, 2),
                },
                'forecast': forecast_list,
                'scenario': scenario,
            })
            
        except ValueError as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    elif request.method == 'GET':
        # Get latest prediction
        actor_filter, _ = _get_actor_filter(request)
        tank = WaterTank.objects.filter(**actor_filter).first()
        
        if not tank:
            return JsonResponse({'error': 'No tank found'}, status=404)
        
        latest_prediction = FloodPredictionLog.objects.filter(tank=tank).first()
        
        if not latest_prediction:
            return JsonResponse({'error': 'No predictions yet'}, status=404)
        
        return JsonResponse({
            'success': True,
            'prediction': {
                'risk_level': latest_prediction.risk_level,
                'confidence': latest_prediction.confidence,
                'predicted_rainfall_7days': latest_prediction.predicted_rainfall_7days,
                'tank_level_pct': latest_prediction.tank_level_pct,
                'recommended_action': latest_prediction.recommended_action,
                'system_action': latest_prediction.system_action,
                'alert_message': latest_prediction.alert_message,
                'prediction_time': latest_prediction.prediction_time.isoformat(),
            },
            'tank': {
                'name': tank.name,
                'capacity': tank.capacity_liters,
                'current_level': tank.current_level_liters,
                'level_percentage': round(tank.level_percentage, 2),
            },
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def update_tank_level(request):
    """API endpoint to update tank water level"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        current_level = float(data.get('current_level', 0))
        
        actor_filter, _ = _get_actor_filter(request)
        tank = WaterTank.objects.filter(**actor_filter).first()
        
        if not tank:
            return JsonResponse({'error': 'No tank found'}, status=404)
        
        tank.current_level_liters = current_level
        tank.save()
        
        return JsonResponse({
            'success': True,
            'tank': {
                'current_level': tank.current_level_liters,
                'level_percentage': round(tank.level_percentage, 2),
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def prediction_history(request):
    """View prediction history"""
    actor_filter, _ = _get_actor_filter(request)
    tank = WaterTank.objects.filter(**actor_filter).first()
    
    predictions = []
    if tank:
        predictions = FloodPredictionLog.objects.filter(tank=tank)[:20]
    
    return render(request, 'prediction_history.html', {
        'tank': tank,
        'predictions': predictions,
    })



@csrf_exempt
def borewell_estimation_api(request):
    """API endpoint for borewell depth estimation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            location = data.get('location', '').strip()
            annual_rainfall = float(data.get('annual_rainfall', 0))
            region_type_str = data.get('region_type', 'semi_urban')
            soil_type_str = data.get('soil_type', 'loamy')
            
            if not location:
                return JsonResponse({'error': 'Location is required'}, status=400)
            
            if annual_rainfall <= 0:
                return JsonResponse({'error': 'Valid rainfall data is required'}, status=400)
            
            # Convert string to enum
            try:
                region_type = RegionType(region_type_str)
            except ValueError:
                region_type = RegionType.SEMI_URBAN
            
            try:
                soil_type = SoilType(soil_type_str)
            except ValueError:
                soil_type = SoilType.LOAMY
            
            # Run estimation
            estimate = borewell_estimator.estimate_depth(
                location=location,
                annual_rainfall_mm=annual_rainfall,
                region_type=region_type,
                soil_type=soil_type
            )
            
            # Save to database
            actor_filter, session_key = _get_actor_filter(request)
            user = actor_filter.get('user')
            
            BorewellEstimation.objects.create(
                user=user if user is not None else None,
                session_key=session_key,
                location=location,
                annual_rainfall_mm=annual_rainfall,
                region_type=region_type.value,
                soil_type=soil_type.value,
                min_depth_feet=estimate.min_depth_feet,
                max_depth_feet=estimate.max_depth_feet,
                recommended_depth_feet=estimate.recommended_depth_feet,
                confidence_level=estimate.confidence_level,
                water_availability=estimate.water_availability,
                estimated_yield_lph=estimate.estimated_yield_lph,
                reasoning=estimate.reasoning,
                cost_estimate_min=estimate.cost_estimate_inr[0],
                cost_estimate_max=estimate.cost_estimate_inr[1],
            )
            
            return JsonResponse({
                'success': True,
                'estimation': estimate.to_dict(),
            })
            
        except ValueError as e:
            return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    elif request.method == 'GET':
        # Get latest estimation
        actor_filter, _ = _get_actor_filter(request)
        latest = BorewellEstimation.objects.filter(**actor_filter).first()
        
        if not latest:
            return JsonResponse({'error': 'No estimations yet'}, status=404)
        
        return JsonResponse({
            'success': True,
            'estimation': {
                'location': latest.location,
                'annual_rainfall_mm': latest.annual_rainfall_mm,
                'region_type': latest.region_type,
                'soil_type': latest.soil_type,
                'min_depth_feet': latest.min_depth_feet,
                'max_depth_feet': latest.max_depth_feet,
                'recommended_depth_feet': latest.recommended_depth_feet,
                'confidence_level': latest.confidence_level,
                'water_availability': latest.water_availability,
                'estimated_yield_lph': latest.estimated_yield_lph,
                'reasoning': latest.reasoning,
                'cost_estimate_min': latest.cost_estimate_min,
                'cost_estimate_max': latest.cost_estimate_max,
                'estimation_time': latest.estimation_time.isoformat(),
            }
        })
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def borewell_history(request):
    """View borewell estimation history"""
    actor_filter, _ = _get_actor_filter(request)
    estimations = BorewellEstimation.objects.filter(**actor_filter)[:20]
    
    return render(request, 'borewell_history.html', {
        'estimations': estimations,
    })



def get_district_rainfall_api(request):
    """API endpoint to get rainfall data for a district"""
    district = request.GET.get('district', '').strip()
    
    if not district:
        return JsonResponse({'error': 'District name required'}, status=400)
    
    # Validate and get rainfall
    is_valid, suggestion = validate_district(district)
    
    if is_valid:
        rainfall = get_district_rainfall(district)
        if rainfall is not None:
            return JsonResponse({
                'success': True,
                'district': district.title(),
                'rainfall': float(rainfall),
                'valid': True
            })
    
    # If not valid, try suggestion
    if suggestion:
        rainfall = get_district_rainfall(suggestion)
        if rainfall is not None:
            return JsonResponse({
                'success': True,
                'district': suggestion.title(),
                'rainfall': float(rainfall),
                'valid': True,
                'corrected': True,
                'original': district
            })
    
    return JsonResponse({
        'success': False,
        'valid': False,
        'message': f'District "{district}" not found in database',
        'suggestion': suggestion if suggestion else None
    })


def get_all_districts_api(request):
    """API endpoint to get list of all districts"""
    from services.rainwater_calculator import VALID_DISTRICTS
    
    # Get search query if provided
    query = request.GET.get('q', '').strip().lower()
    
    if query:
        # Filter districts matching query
        matching = [d for d in VALID_DISTRICTS if query in d.lower()]
        districts = matching[:50]  # Limit to 50 results
    else:
        # Return first 100 districts
        districts = list(VALID_DISTRICTS)[:100]
    
    return JsonResponse({
        'success': True,
        'districts': [d.title() for d in districts],
        'total': len(VALID_DISTRICTS)
    })
