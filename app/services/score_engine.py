def compute_score(log):
    """
    Rule-based health score calculator.
    Returns an integer score from 0 to 100.

    Weights:
      Sleep hours: 20, Stress: 15, Steps: 15, Water: 10,
      Screen time: 10, Meal timing: 10, Calories: 10,
      Mood: 5, Exercise: 3, Outdoor: 2
    """
    score = 0

    # 1. Sleep hours (max 20 points)
    sh = log.sleep_hours or 0
    if sh >= 8:
        score += 20
    elif sh >= 7:
        score += 16
    elif sh >= 6:
        score += 12
    elif sh >= 5:
        score += 8
    elif sh >= 4:
        score += 4
    # else 0

    # 2. Stress level (max 15 points) — lower is better
    stress = log.stress_level or 5
    if stress <= 2:
        score += 15
    elif stress <= 4:
        score += 12
    elif stress <= 5:
        score += 9
    elif stress <= 7:
        score += 6
    elif stress <= 8:
        score += 3
    # else 0 (9-10)

    # 3. Steps (max 15 points)
    steps = log.steps or 0
    if steps >= 10000:
        score += 15
    elif steps >= 7500:
        score += 12
    elif steps >= 5000:
        score += 9
    elif steps >= 3000:
        score += 6
    elif steps >= 1000:
        score += 3
    # else 0

    # 4. Water intake (max 10 points)
    water = log.water_ml or 0
    if water >= 2500:
        score += 10
    elif water >= 2000:
        score += 8
    elif water >= 1500:
        score += 6
    elif water >= 1000:
        score += 4
    elif water >= 500:
        score += 2
    # else 0

    # 5. Screen time (max 10 points) — lower is better
    screen = log.screen_time_hours or 0
    if screen <= 2:
        score += 10
    elif screen <= 4:
        score += 8
    elif screen <= 6:
        score += 6
    elif screen <= 8:
        score += 4
    elif screen <= 10:
        score += 2
    # else 0

    # 6. Meal timing regularity (max 10 points)
    meals_logged = 0
    if log.breakfast_time:
        meals_logged += 1
    if log.lunch_time:
        meals_logged += 1
    if log.dinner_time:
        meals_logged += 1

    meal_timing_ok = 0
    if log.breakfast_time:
        bh = int(log.breakfast_time.split(':')[0])
        if 6 <= bh <= 10:
            meal_timing_ok += 1
    if log.lunch_time:
        lh = int(log.lunch_time.split(':')[0])
        if 11 <= lh <= 14:
            meal_timing_ok += 1
    if log.dinner_time:
        dh = int(log.dinner_time.split(':')[0])
        if 18 <= dh <= 21:
            meal_timing_ok += 1

    if meals_logged == 3 and meal_timing_ok == 3:
        score += 10
    elif meals_logged >= 2 and meal_timing_ok >= 2:
        score += 7
    elif meals_logged >= 1 and meal_timing_ok >= 1:
        score += 4
    elif meals_logged >= 1:
        score += 2
    # else 0

    # 7. Calories (max 10 points)
    cal = log.calories or 0
    if 1800 <= cal <= 2500:
        score += 10
    elif 1500 <= cal < 1800 or 2500 < cal <= 3000:
        score += 7
    elif 1200 <= cal < 1500 or 3000 < cal <= 3500:
        score += 4
    elif 800 <= cal < 1200 or 3500 < cal <= 4500:
        score += 2
    # else 0

    # 8. Mood (max 5 points) — higher is better
    mood = log.mood or 5
    if mood >= 8:
        score += 5
    elif mood >= 6:
        score += 4
    elif mood >= 5:
        score += 3
    elif mood >= 3:
        score += 2
    elif mood >= 2:
        score += 1
    # else 0

    # 9. Exercise minutes (max 3 points)
    exercise = log.exercise_minutes or 0
    if exercise >= 45:
        score += 3
    elif exercise >= 30:
        score += 2
    elif exercise >= 15:
        score += 1
    # else 0

    # 10. Outdoor minutes (max 2 points)
    outdoor = log.outdoor_minutes or 0
    if outdoor >= 60:
        score += 2
    elif outdoor >= 30:
        score += 1
    # else 0

    return max(0, min(100, score))
