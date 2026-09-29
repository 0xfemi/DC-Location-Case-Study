# DC Location Case Study

Python analysis of the Roboticus distribution-centre location case. The model uses the case handout's unit forecasts, product weight, city-to-city mileage, and $2/ton-mile truckload assumption.

## Recommendation

For Prairie-only sales, choose Calgary, subject to a local warehouse quote. Calgary and Edmonton account for 32,000 of the forecast 48,000 units, so Calgary has the lowest forecast-weighted outbound distance and truck cost.

| DC city | Sales-weighted miles/unit | Outbound freight/year | Freight + three-FTE wage floor |
| --- | ---: | ---: | ---: |
| Calgary | 278.4 | $160,356 | $253,956 |
| Regina | 400.9 | $230,916 | $326,700 |
| Winnipeg | 622.8 | $358,716 | $458,556 |

The wage estimate applies general statutory minimum wage rates to 3 FTE at 2,080 hours each. It is a floor, not a realistic hiring budget. Lease rates are deliberately left as inputs because the case gives no city-specific quotes. Calgary can bear about $14.55/sq.ft./year more rent than Regina, or $40.92 more than Winnipeg, and tie on modeled freight plus wage-floor cost for 5,000 sq. ft.

These results are one-way outbound costs only. The model does not include inbound transport from Taiwan, customs/brokerage, fuel/tolls, labor burden or wage premiums, inventory carrying cost, building operating costs, returns, or service-level effects.

## Inland Port and Midwest

An inland-port site should be selected only if its actual inbound/intermodal, customs, handling, or other operating savings exceed any added rent and drayage. CentrePort Canada in Winnipeg advertises access to three Class I railways, trucking, and air cargo, but that does not offset Winnipeg's Prairie outbound penalty without a broader network or inbound-cost benefit.

The case supplies no Midwest demand forecast or route distances, so the script reports break-even scenarios rather than picking a new location. For example, if Regina were 500 demand-weighted one-way miles closer to Midwest customers than Calgary, it would need about 12,124 U.S. units/year to offset its current modeled disadvantage, before rent differences. Winnipeg would need about 34,100 units under the same mileage assumption.

## Run

Requires Python 3.10+; no third-party packages are used.

```sh
python3 dc_location_case.py
```

Edit `NET_RENT_PER_SQ_FT` and the assumptions near the top of `dc_location_case.py` to evaluate site quotes. Use `midwest_break_even()` with route-weighted one-way mileage from each candidate and a realistic annual U.S. demand forecast.

## Sources

- Case handout: city sales forecast, unit specs, distances, and assumed truckload rate.
- [Statistics Canada, 2021 Census](https://www12.statcan.gc.ca/census-recensement/2021/dp-pd/index-eng.cfm): population context.
- [Alberta Employment Standards, minimum wage](https://www.alberta.ca/minimum-wage).
- [Manitoba Employment Standards, minimum wage](https://www.gov.mb.ca/labour/standards/doc,minimum-wage,factsheet.html).
- [Saskatchewan Employment Standards](https://www.saskatchewan.ca/business/employment-standards): verify the applicable current wage rate when setting up a local cost model.
- [CBRE, Canada Industrial Figures Q4 2025](https://www.cbre.ca/insights/figures/canada-industrial-figures-q4-2025): national market context; obtain city-level quotes for a decision.
- [CentrePort Canada, inland port capabilities](https://centreportcanada.ca/about-centreport/).
- [Canada Border Services Agency, importing commercial goods](https://www.cbsa-asfc.gc.ca/import/guide-eng.html): import-process requirements and cost categories.
