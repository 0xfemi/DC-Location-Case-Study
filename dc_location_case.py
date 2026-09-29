"""Roboticus Prairie DC location case.

Run with: python3 dc_location_case.py

Freight is estimated using the case's $2/ton-mile rate and the supplied
one-way city distances. The wage rates below are statutory floors, not
recommended warehouse pay. Replace them and enter quoted net lease rates for
a commercial site-selection model. No Midwest forecast or lane distances were
provided, so the expansion result is a break-even threshold, not a forecast.
"""

from __future__ import annotations

from dataclasses import dataclass


# Case data: annual units sold and one-way miles between Prairie cities.
SALES = {
    "Calgary": 16_000,
    "Edmonton": 16_000,
    "Regina": 3_000,
    "Saskatoon": 4_000,
    "Winnipeg": 9_000,
}
DISTANCES = {
    "Calgary": {
        "Calgary": 0,
        "Edmonton": 183,
        "Regina": 475,
        "Saskatoon": 385,
        "Winnipeg": 830,
    },
    "Regina": {
        "Calgary": 475,
        "Edmonton": 488,
        "Regina": 0,
        "Saskatoon": 160,
        "Winnipeg": 355,
    },
    "Winnipeg": {
        "Calgary": 830,
        "Edmonton": 843,
        "Regina": 355,
        "Saskatoon": 515,
        "Winnipeg": 0,
    },
}
PROVINCE = {"Calgary": "Alberta", "Regina": "Saskatchewan", "Winnipeg": "Manitoba"}

# Planning assumptions / editable inputs.
UNIT_WEIGHT_LB = 12
UNIT_LENGTH_IN = 24
UNIT_WIDTH_IN = 12
UNIT_HEIGHT_IN = 12
ANNUAL_UNITS = sum(SALES.values())
TRUCK_RATE_PER_TON_MILE = 2.00
FTE = 3
HOURS_PER_FTE_YEAR = 2_080
LEASED_SQ_FT = 5_000
STORAGE_SQ_FT = 4_000
# General minimum wages used only as a conservative wage floor (CAD/hour).
MINIMUM_WAGE = {"Calgary": 15.00, "Regina": 15.35, "Winnipeg": 16.00}
# Enter quoted annual net rent in CAD/sq.ft. for each candidate. Values are
# deliberately None because the case provides no city-specific lease quotes.
NET_RENT_PER_SQ_FT = {"Calgary": None, "Regina": None, "Winnipeg": None}


@dataclass(frozen=True)
class Result:
    city: str
    weighted_miles_per_unit: float
    ton_miles: float
    freight_cost: float
    labor_floor: float
    known_cost: float


def freight_cost(city: str, sales: dict[str, int] = SALES,
                 distances: dict[str, int] | None = None) -> tuple[float, float]:
    """Return ton-miles and annual one-way freight cost for one DC city."""
    lane_miles = distances if distances is not None else DISTANCES[city]
    ton_miles = sum(
        units * UNIT_WEIGHT_LB / 2_000 * lane_miles[destination]
        for destination, units in sales.items()
    )
    return ton_miles, ton_miles * TRUCK_RATE_PER_TON_MILE


def build_results() -> list[Result]:
    results = []
    for city in DISTANCES:
        ton_miles, freight = freight_cost(city)
        labor = FTE * HOURS_PER_FTE_YEAR * MINIMUM_WAGE[city]
        results.append(Result(
            city=city,
            weighted_miles_per_unit=sum(
                units * DISTANCES[city][destination]
                for destination, units in SALES.items()
            ) / ANNUAL_UNITS,
            ton_miles=ton_miles,
            freight_cost=freight,
            labor_floor=labor,
            known_cost=freight + labor,
        ))
    return sorted(results, key=lambda result: result.known_cost)


def rent_break_even(calculated: list[Result], baseline_city: str) -> None:
    """Show the extra net rent/sq.ft. each alternative can bear vs baseline."""
    baseline = next(row for row in calculated if row.city == baseline_city)
    print(f"\nRent break-even vs. {baseline_city} (before lease quotes):")
    for alternative in calculated:
        if alternative.city == baseline_city:
            continue
        premium = (alternative.known_cost - baseline.known_cost) / LEASED_SQ_FT
        print(
            f"  {baseline_city} can pay up to ${premium:,.2f}/sq.ft./year "
            f"more than {alternative.city} and tie on modeled annual cost."
        )


def midwest_break_even(candidate: str, candidate_us_weighted_miles: float,
                       calgary_us_weighted_miles: float,
                       candidate_annual_fixed_premium: float = 0) -> float | None:
    """US units needed to offset candidate's Prairie/fixed-cost disadvantage.

    Distances are demand-weighted one-way miles from the DC to the Midwest
    destinations. Returns None if the candidate is not closer to the US demand.
    """
    prairie_penalty = next(row.known_cost for row in build_results()
                           if row.city == candidate) - next(
                               row.known_cost for row in build_results()
                               if row.city == "Calgary")
    total_penalty = prairie_penalty + candidate_annual_fixed_premium
    miles_saved = calgary_us_weighted_miles - candidate_us_weighted_miles
    if total_penalty <= 0:
        return 0.0
    if miles_saved <= 0:
        return None
    savings_per_unit = (UNIT_WEIGHT_LB / 2_000) * TRUCK_RATE_PER_TON_MILE * miles_saved
    return total_penalty / savings_per_unit


def main() -> None:
    total_weight_lb = ANNUAL_UNITS * UNIT_WEIGHT_LB
    unit_cube_ft3 = (UNIT_LENGTH_IN * UNIT_WIDTH_IN * UNIT_HEIGHT_IN) / 1_728
    annual_volume_ft3 = ANNUAL_UNITS * unit_cube_ft3
    results = build_results()

    print("ROBOTICUS PRAIRIE DC CASE")
    print(f"Annual units: {ANNUAL_UNITS:,}; product value: ${ANNUAL_UNITS * 400:,.0f}")
    print(f"Annual outbound weight: {total_weight_lb:,.0f} lb ({total_weight_lb / 2_000:,.0f} short tons)")
    print(f"Box cube: {unit_cube_ft3:.2f} ft^3/unit; annual throughput cube: {annual_volume_ft3:,.0f} ft^3")
    print(f"Warehouse: {STORAGE_SQ_FT:,} storage sq.ft. + {LEASED_SQ_FT - STORAGE_SQ_FT:,} other sq.ft.")
    print("\nPrairie outbound cost (one-way ton-miles; excludes inbound/import and handling):")
    print(f"{'DC':<10} {'Weighted mi/unit':>17} {'Ton-miles':>14} {'Freight':>14} {'Labor floor':>14} {'Known total':>14}")
    for row in results:
        print(
            f"{row.city:<10} {row.weighted_miles_per_unit:>17,.1f} "
            f"{row.ton_miles:>14,.0f} ${row.freight_cost:>13,.0f} "
            f"${row.labor_floor:>13,.0f} ${row.known_cost:>13,.0f}"
        )

    rent_break_even(results, "Calgary")
    print("\nMidwest expansion threshold:")
    print("  Enter quoted demand-weighted one-way miles and annual US unit forecast.")
    print("  At equal wages/rents, each US mile Calgary is farther away costs $0.012/unit.")
    for candidate in ("Regina", "Winnipeg"):
        candidate_result = next(row for row in results if row.city == candidate)
        calgary_result = next(row for row in results if row.city == "Calgary")
        penalty = candidate_result.known_cost - calgary_result.known_cost
        print(f"  {candidate} begins ${penalty:,.0f}/year behind Calgary before rent differentials.")
        for mileage_advantage in (250, 500, 750):
            threshold = midwest_break_even(
                candidate,
                candidate_us_weighted_miles=0,
                calgary_us_weighted_miles=mileage_advantage,
            )
            print(
                f"    If {candidate} is {mileage_advantage} weighted miles closer "
                f"to US customers: {threshold:,.0f} US units/year to tie."
            )
        print("  Use midwest_break_even(candidate, candidate_miles, calgary_miles) to test a forecast.")

    print("\nImportant exclusions: inbound ocean/rail/truck, customs and brokerage, "
          "fuel/tolls, shipment consolidation, inventory carrying cost, taxes/CAM, "
          "wage premiums/payroll burden, service-time targets, and returns.")


if __name__ == "__main__":
    main()


# Sources to replace assumptions and document the analysis:
# - Case handout: forecast, product specs, city distances, $2/ton-mile.
# - Statistics Canada, 2021 Census: https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/index-eng.cfm
# - Alberta Employment Standards minimum wage: https://www.alberta.ca/minimum-wage
# - Manitoba Employment Standards minimum wage: https://www.gov.mb.ca/labour/standards/doc,minimum-wage,factsheet.html
# - Saskatchewan Employment Standards minimum wage: https://www.saskatchewan.ca/business/employment-standards
# - CBRE, Canada Industrial Figures Q4 2025 (national benchmark; obtain local quotes): https://www.cbre.ca/insights/figures/canada-industrial-figures-q4-2025
# - CentrePort Canada, inland port capabilities: https://centreportcanada.ca/about-centreport/
# - CBSA, guide to importing commercial goods: https://www.cbsa-asfc.gc.ca/import/guide-eng.html
