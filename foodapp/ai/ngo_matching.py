from .food_priority import calculate_food_priority

def find_best_ngos(donation, ngos):
    """
    Find suitable NGOs for a food donation.
    """

    results = []

    for ngo in ngos:

        score = 0

        # 1. City matching
        if donation.city.lower() == ngo.city.lower():
            score += 50

        # 2. Active NGO
        if ngo.status == "Active":
            score += 20

        # 3. Food urgency
        priority = calculate_food_priority(
            donation.expiry_time
        )

        if priority == "HIGH":
            score += 30
        elif priority == "MEDIUM":
            score += 20
        else:
            score += 10

        results.append({
            "ngo": ngo,
            "score": score,
            "priority": priority
        })

    # Highest score first
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:3]