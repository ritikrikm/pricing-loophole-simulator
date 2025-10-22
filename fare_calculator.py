import math

# --- Developer Constants & Parameters ---

# Note: All monetary values are pre-promotional discount for clearer analysis.
# We are aiming to model:
# Route A (Original, Fast, Toll) ~ $106.96
# Route B (Midpoint, Slower, No Toll) ~ $40.29

# Base Rates for demonstration
RATE_PER_MINUTE = 0.80  # Higher rate due to assumed complexity/premium service
RATE_PER_KM = 1.20
PEAK_HOUR_BASE_SURGE_FLOOR = 1.20 # The minimum surge multiplier allowed during peak times (The Fix)

def calculate_base_fare(time_minutes: float, distance_km: float) -> float:
    """Calculates the time/distance component of the fare."""
    return (time_minutes * RATE_PER_MINUTE) + (distance_km * RATE_PER_KM)

def apply_surge_and_toll(
    base_cost: float,
    toll_fee: float,
    surge_multiplier: float,
    is_peak_hour: bool = True,
    mitigate_loophole: bool = False
) -> float:
    """
    Applies the surge and toll fee to the base cost. This is where the
    algorithmic "mistake" (and the fix) occurs.
    """
    total_cost_before_surge = base_cost + toll_fee
    final_multiplier = surge_multiplier

    # --- THE MITIGATION STRATEGY (The Developer Fix) ---
    if mitigate_loophole and is_peak_hour and toll_fee == 0:
        # Loophole: During peak hours, non-toll routes might be under-surged
        # due to the system's over-reliance on the toll route for speed.
        # FIX: Implement a 'Surge Floor' to ensure all peak-hour trips meet a
        # minimum required pricing level based on market demand, even if the
        # specific route is non-premium (no toll).
        if final_multiplier < PEAK_HOUR_BASE_SURGE_FLOOR:
            print(f"    [FIX] Surge Multiplier raised from {final_multiplier:.2f}x to {PEAK_HOUR_BASE_SURGE_FLOOR:.2f}x (Surge Floor applied)")
            final_multiplier = PEAK_HOUR_BASE_SURGE_FLOOR
    # -----------------------------------------------------

    final_fare = total_cost_before_surge * final_multiplier
    return round(final_fare, 2)


# --- Scenario Data Modeling the User's Real-World Trip ---

# 1. Original Trip (Mississauga to Midtown - Direct)
# The algorithm chose the fastest route, which included the 407 ETR toll.
ROUTE_A_DATA = {
    "name": "Route A (Fastest, Toll Route)",
    "time_min": 45.0,        # Faster (Original arrival 5:41 AM)
    "distance_km": 60.0,
    "toll": 8.13,            # Explicit toll fee
    "surge_M": 1.70,         # High surge due to speed/premium route/peak time
}

# 2. Midpoint Trip (Mississauga -> Eglinton -> Midtown)
# The midpoint forced the algorithm onto a non-toll route (401/QEW).
ROUTE_B_DATA = {
    "name": "Route B (Slower, Non-Toll Route)",
    "time_min": 57.0,        # Slower (+12 mins, arrival 5:53 AM)
    "distance_km": 65.0,     # Slightly longer distance
    "toll": 0.00,            # Toll is avoided
    "surge_M": 0.75,         # Loophole: This low surge is the mistake for peak hours
}

# --- Demo Execution ---

def run_demo(mitigate=False):
    print("\n" + "="*50)
    print(f"FARE CALCULATION DEMO (Mitigation Active: {mitigate})")
    print("="*50)

    routes = [ROUTE_A_DATA, ROUTE_B_DATA]
    fares = {}

    for route in routes:
        base_cost = calculate_base_fare(route["time_min"], route["distance_km"])

        final_fare = apply_surge_and_toll(
            base_cost=base_cost,
            toll_fee=route["toll"],
            surge_multiplier=route["surge_M"],
            mitigate_loophole=mitigate
        )

        fares[route["name"]] = final_fare

        print(f"\n--- {route['name']} ---")
        print(f"  Base Cost (T+D): ${base_cost:.2f}")
        print(f"  Toll Fee:        ${route['toll']:.2f}")
        print(f"  Surge Applied:   {route['surge_M']:.2f}x")
        print(f"  FINAL PRE-PROMO FARE: ${final_fare:.2f}")


    # Summary of the problem / solution
    fare_A = fares[ROUTE_A_DATA["name"]]
    fare_B = fares[ROUTE_B_DATA["name"]]
    fare_difference = fare_A - fare_B

    print("\n" + "-"*50)
    print("DEMO SUMMARY (Pre-Promo Prices):")
    print(f"Route A (Direct/Toll): ${fare_A:.2f}")
    print(f"Route B (Midpoint/No-Toll): ${fare_B:.2f}")
    print(f"Difference: ${fare_difference:.2f}")

    if fare_difference > 60 and not mitigate:
        print("\n*** The Algorithmic Loophole is active: Difference is too extreme! ***")
    elif mitigate and fare_B > 45: # Check if the fix raised the price significantly
        print(f"\n*** Mitigation SUCCESSFUL: Route B's price is now consistent with peak demand. ***")
    else:
        print("\n*** Price difference is reasonable. ***")

if __name__ == "__main__":
    # 1. Demonstrate the Algorithmic Mistake (The Loophole)
    run_demo(mitigate=False)

    # 2. Demonstrate the Fix (Applying the Surge Floor)
    run_demo(mitigate=True)