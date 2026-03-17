from __future__ import annotations

from dataclasses import dataclass


WATER_COST_PER_LITER_INR = 0.05

BADGE_LEVELS = [
    ("Beginner Saver", 10_000),
    ("Water Protector", 25_000),
    ("Rain Hero", 50_000),
    ("Water Guardian", 100_000),
    ("Earth Champion", 200_000),
]


@dataclass(frozen=True)
class SavingsAnalysis:
    water_yearly_liters: float
    water_monthly_liters: float
    money_yearly_inr: float
    money_monthly_inr: float
    badge: str
    current_badge_goal_liters: int
    next_badge: str | None
    next_badge_goal_liters: int | None
    progress_to_next_pct: float


def calculate_water_collected_liters(roof_area_sqm: float, rainfall_mm: float, runoff_coefficient: float) -> float:
    """
    With rainfall in mm and roof area in m^2:
    1 mm over 1 m^2 equals ~1 liter, so area * rainfall gives liters.
    """
    return float(roof_area_sqm) * float(rainfall_mm) * float(runoff_coefficient)


def determine_badge(water_saved_liters: float):
    water_saved_liters = float(water_saved_liters)

    current_badge = BADGE_LEVELS[0][0]
    current_goal = 0
    next_badge = BADGE_LEVELS[0][0]
    next_goal = BADGE_LEVELS[0][1]

    for badge_name, goal in BADGE_LEVELS:
        if water_saved_liters >= goal:
            current_badge = badge_name
            current_goal = goal
        else:
            next_badge = badge_name
            next_goal = goal
            break
    else:
        next_badge = None
        next_goal = None

    if next_goal is None:
        progress_pct = 100.0
    else:
        progress_pct = max(0.0, min(100.0, (water_saved_liters / float(next_goal)) * 100.0))

    return current_badge, current_goal, next_badge, next_goal, round(progress_pct, 1)


def analyze_savings(roof_area_sqm: float, rainfall_mm: float, runoff_coefficient: float = 0.8) -> SavingsAnalysis:
    water_yearly = calculate_water_collected_liters(roof_area_sqm, rainfall_mm, runoff_coefficient)
    water_yearly = round(water_yearly, 1)
    water_monthly = round(water_yearly / 12.0, 1)

    money_yearly = round(water_yearly * WATER_COST_PER_LITER_INR, 2)
    money_monthly = round(money_yearly / 12.0, 2)

    badge, current_goal, next_badge, next_goal, progress_pct = determine_badge(water_yearly)

    return SavingsAnalysis(
        water_yearly_liters=water_yearly,
        water_monthly_liters=water_monthly,
        money_yearly_inr=money_yearly,
        money_monthly_inr=money_monthly,
        badge=badge,
        current_badge_goal_liters=current_goal,
        next_badge=next_badge,
        next_badge_goal_liters=next_goal,
        progress_to_next_pct=progress_pct,
    )

