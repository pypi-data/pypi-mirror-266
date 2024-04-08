from collections.abc import Iterable
from enum import Enum
from functools import reduce
from pydash.objects import merge
from typing import NamedTuple, Optional, Union

from hestia_earth.schema import (
    CycleFunctionalUnit, EmissionMethodTier, MeasurementMethodClassification
)
from hestia_earth.utils.date import diff_in_days
from hestia_earth.utils.tools import flatten, non_empty_list

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import (
    group_nodes_by_year, GroupNodesByYearMode, node_term_match,
)
from hestia_earth.models.utils.constant import Units, get_atomic_conversion
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.measurement import OLDEST_DATE
from hestia_earth.models.utils.site import related_cycles

from .utils import check_consecutive
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "site": {
            "measurements": [
                {
                    "@type": "Measurement",
                    "value": "",
                    "dates": "",
                    "depthUpper": "0",
                    "depthLower": "30",
                    "term.@id": " organicCarbonPerHa"
                }
            ]
        },
        "functionalUnit": "1 ha",
        "endDate": "",
        "optional": {
            "startDate": ""
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "",
        "depth": "30"
    }]
}
TERM_ID = 'co2ToAirSoilCarbonStockChangeManagementChange'

DEPTH_UPPER = 0
DEPTH_LOWER = 30

ORGANIC_CARBON_PER_HA_TERM_ID = 'organicCarbonPerHa'


SocStock = NamedTuple("SocStock", [
    ("value", float),
    ("method", MeasurementMethodClassification)
])
"""
NamedTuple representing either an SOC stock or SOC stock change.

Attributes
----------
value : float
    The value of the SOC stock (kg C ha-1).
method: MeasurementMethodClassification
    The measurement method for the SOC stock.
"""


_InnerKey = Enum("_InnerKey", [
    "SOC_STOCK",
    "SOC_STOCK_CHANGE",
    "SHARE_OF_EMISSIONS"
])
"""
The inner keys of the annualised inventory created by the `_should_run` function.
"""


REQUIRED_INNER_KEYS = [_InnerKey.SHARE_OF_EMISSIONS, _InnerKey.SOC_STOCK_CHANGE]

MEASUREMENT_METHOD_RANKING = [
    MeasurementMethodClassification.UNSOURCED_ASSUMPTION,
    MeasurementMethodClassification.EXPERT_OPINION,
    MeasurementMethodClassification.COUNTRY_LEVEL_STATISTICAL_DATA,
    MeasurementMethodClassification.REGIONAL_STATISTICAL_DATA,
    MeasurementMethodClassification.GEOSPATIAL_DATASET,
    MeasurementMethodClassification.PHYSICAL_MEASUREMENT_ON_NEARBY_SITE,
    MeasurementMethodClassification.TIER_1_MODEL,
    MeasurementMethodClassification.TIER_2_MODEL,
    MeasurementMethodClassification.TIER_3_MODEL,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS,
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT
]
"""
A ranking of `MeasurementMethodClassification`s from weakest to strongest used to determine the `EmissionMethodTier` of
the `co2ToAirSoilCarbonStockChangeManagementChange` output.

The `EmissionMethodTier` should be based on the weakest `MeasurementMethodClassification` between the current SOC and
previous SOC.
"""


def _to_measurement_method_classification(
    method: Union[str, MeasurementMethodClassification]
) -> Optional[MeasurementMethodClassification]:
    """
    Convert the input to a MeasurementMethodClassification object if possible.

    Parameters
    ----------
    method : str | MeasurementMethodClassification
        The measurement method as either a `str` or `MeasurementMethodClassification`.

    Returns
    -------
    MeasurementMethodClassification | None
        The matching `MeasurementMethodClassification` or `None` if invalid string.
    """
    return (
        method if isinstance(method, MeasurementMethodClassification)
        else MeasurementMethodClassification(method) if method in (m.value for m in MeasurementMethodClassification)
        else None
    )


def _get_min_measurement_method(
    *methods: Union[MeasurementMethodClassification, Iterable[MeasurementMethodClassification]]
) -> MeasurementMethodClassification:
    """
    Get the minimum ranking measurement method from the provided methods.

    Parameters
    ----------
    *methods : MeasurementMethodClassification | Iterable[MeasurementMethodClassification]
        Measurement methods or iterables of measurement methods.

    Returns
    -------
    MeasurementMethodClassification
        The measurement method with the minimum ranking.
    """

    # flatten methods into a single list, convert any strings into `MeasurementMethodClassification`s
    # and remove invalid methods.
    _methods = non_empty_list(flatten([
        [_to_measurement_method_classification(method) for method in arg] if isinstance(arg, Iterable)
        else [_to_measurement_method_classification(arg)] for arg in methods
    ]))

    return min(
        _methods,
        key=lambda method: MEASUREMENT_METHOD_RANKING.index(method),
        default=list(MEASUREMENT_METHOD_RANKING)[0]
    )


def _get_max_measurement_method(
    *methods: Union[MeasurementMethodClassification, Iterable[MeasurementMethodClassification]]
) -> MeasurementMethodClassification:
    """
    Get the max ranking measurement method from the provided methods.

    Parameters
    ----------
    *methods : MeasurementMethodClassification | Iterable[MeasurementMethodClassification]
        Measurement methods or iterables of measurement methods.

    Returns
    -------
    MeasurementMethodClassification
        The measurement method with the maximum ranking.
    """

    # flatten methods into a single list, convert any strings into `MeasurementMethodClassification`s
    # and remove invalid methods.
    _methods = non_empty_list(flatten([
        [_to_measurement_method_classification(method) for method in arg] if isinstance(arg, Iterable)
        else [_to_measurement_method_classification(arg)] for arg in methods
    ]))

    return max(
        _methods,
        key=lambda method: MEASUREMENT_METHOD_RANKING.index(method),
        default=MEASUREMENT_METHOD_RANKING[-1]
    )


DEFAULT_EMISSION_METHOD_TIER = EmissionMethodTier.TIER_1
MEASUREMENT_METHOD_CLASSIFICATION_TO_EMISSION_METHOD_TIER = {
    MeasurementMethodClassification.TIER_2_MODEL: EmissionMethodTier.TIER_2,
    MeasurementMethodClassification.TIER_3_MODEL: EmissionMethodTier.TIER_3,
    MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS: EmissionMethodTier.MEASURED,
    MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT: EmissionMethodTier.MEASURED,
}
"""
A mapping between `MeasurementMethodClassification`s and `EmissionMethodTier`s. As SOC measurements can be
measured/estimated through a variety of methods, the emission model needs be able to assign an emission tier for each.
Any `MeasurementMethodClassification` not in the mapping should be assigned `DEFAULT_EMISSION_METHOD_TIER`.
"""


def _get_emission_method_tier(
    measurement_method: MeasurementMethodClassification
) -> EmissionMethodTier:
    """
    Get the emission method tier based on the provided measurement method.

    Parameters
    ----------
    measurement_method : MeasurementMethodClassification
        The measurement method classification.

    Returns
    -------
    EmissionMethodTier
        The corresponding emission method tier.
    """
    return MEASUREMENT_METHOD_CLASSIFICATION_TO_EMISSION_METHOD_TIER.get(
        measurement_method, DEFAULT_EMISSION_METHOD_TIER
    )


def _emission(
    value: float, method_tier: EmissionMethodTier
) -> dict:
    """
    Create an emission node based on the provided value and method tier.

    See [Emission schema](https://www.hestia.earth/schema/Emission) for more information.

    Parameters
    ----------
    value : float
        The emission value (kg CO2 ha-1).

    method_tier : EmissionMethodTier
        The emission method tier.

    Returns
    -------
    dict
        The emission dictionary with keys 'depth', 'value', and 'methodTier'.
    """
    emission = _new_emission(TERM_ID, MODEL)
    emission["depth"] = DEPTH_LOWER
    emission["value"] = [value]
    emission["methodTier"] = method_tier.value
    return emission


def _linear_interpolate_soc_stock(
    start_year: int,
    end_year: int,
    start_soc_stock: SocStock,
    end_soc_stock: SocStock,
    year: int
) -> SocStock:
    """
    Linearly interpolate the SocStock value for a specific year between two given years.

    The `MeasurementMethodClassification` of any SOC stocks estimated using this method should be `tier 1 model` as the
    method is derived from IPCC (2019) Tier 1 SOC model.

    Parameters
    ----------
    start_year : int
        The start year for interpolation.
    end_year : int
        The end year for interpolation.
    start_soc_stock : SocStock
        The `SocStock` corresponding to the start year.
    end_soc_stock : SocStock
        The `SocStock` corresponding to the end year.
    year : int
        The target year for interpolation.

    Returns
    -------
    SocStock
        The interpolated `SocStock` for the specified year.
    """
    METHOD = MeasurementMethodClassification.TIER_1_MODEL

    time_ratio = (year - start_year) / (end_year - start_year)
    soc_delta = (end_soc_stock.value - start_soc_stock.value) * time_ratio
    value = start_soc_stock.value + soc_delta

    return SocStock(value, METHOD)


def _calc_soc_stock_change(start_soc_stock: SocStock, end_soc_stock: SocStock) -> SocStock:
    """
    Calculate the change in SOC stock change between the current and previous states.

    The method should be the weaker of the two `MeasurementMethodClassification`s.

    Parameters
    ----------
    start_soc_stock : SocStock
        The SOC stock at the start (kg C ha-1).

    end_soc_stock : SocStock
        The SOC stock at the end (kg C ha-1).

    Returns
    -------
    SocStock
        The SOC stock change (kg C ha-1).
    """
    value = end_soc_stock.value - start_soc_stock.value
    method = _get_min_measurement_method(end_soc_stock.method, start_soc_stock.method)

    return SocStock(value, method)


def _convert_c_to_co2(kg_c: float) -> float:
    """
    Convert mass of carbon (C) to carbon dioxide (CO2) using the atomic conversion ratio.

    n.b. `get_atomic_conversion` returns the ratio C:CO2 (~44/12).

    Parameters
    ----------
    kg_c : float
        Mass of carbon (C) to be converted to carbon dioxide (CO2) (kg C).

    Returns
    -------
    float
        Mass of carbon dioxide (CO2) resulting from the conversion (kg CO2).
    """
    return kg_c * get_atomic_conversion(Units.KG_CO2, Units.TO_C)


def _soc_stock_stock_change_to_co2_emission(
    soc_stock_change_value: float,
    share_of_emission: float
) -> float:
    """
    Convert SOC stock change to CO2 emission using the given share of emission.

    Parameters
    ----------
    soc_stock_change_value : float
        The change in SOC stock value.

    share_of_emission : float
        The share of emission associated with the SOC stock change.

    Returns
    -------
    float
        The corresponding CO2 emission resulting from the SOC stock change.
    """
    return -1 * share_of_emission * _convert_c_to_co2(soc_stock_change_value)


def _sorted_merge(*sources: Union[dict, list[dict]]) -> dict:
    """
    Merge dictionaries and return the result as a new dictionary with keys sorted in order to preserve the temporal
    order of inventory years.

    Parameters
    ----------
    *sources : dict | List[dict]
        One or more dictionaries or lists of dictionaries to be merged.

    Returns
    -------
    dict
        A new dictionary containing the merged key-value pairs, with keys sorted.
    """

    _sources = non_empty_list(
        flatten([arg if isinstance(arg, list) else [arg] for arg in sources])
    )

    merged = reduce(merge, _sources, {})
    return dict(sorted(merged.items()))


def _validate_soc_measurement_node(node: dict) -> bool:
    """
    Validate a SOC measurement node against specified criteria.

    Parameters
    ----------
    node : dict
        The SOC [Measurement node](https://www.hestia.earth/schema/Measurement) to be validated.

    Returns
    -------
    bool
        True if the node passes all validation criteria, False otherwise.
    """
    return all([
        node_term_match(node, ORGANIC_CARBON_PER_HA_TERM_ID),
        node.get("depthUpper") == DEPTH_UPPER,
        node.get("depthLower") == DEPTH_LOWER
    ])


def _nodes_to_soc_stock(year: int, nodes: list[dict]) -> SocStock:
    """
    Reduces all the the SOC measurement nodes in an inventory year into a single value and measurement method.

    Any nodes with missing or invalid `dates` field will already have been filtered out at this point, so we can assume
    `node.value` and `node.dates` will have equal number of elements. See test case `missing-measurement-dates`.

    Parameters
    ----------
    year : int
        The target year for calculating the SOC stock.

    nodes : List[dict]
        List of [Measurement nodes](https://www.hestia.earth/schema/Measurement) containing SOC data.

    Returns
    -------
    SocStock
        The calculated SOC stock for the specified year.
    """
    target_date = f"{year}-12-31T23:59:59"

    values = flatten([measurement.get("value", []) for measurement in nodes])
    dates = flatten([measurement.get("dates", []) for measurement in nodes])
    methods = flatten([
        [measurement.get("methodClassification") for _ in measurement.get("value", [])]
        for measurement in nodes
    ])

    closest_date = min(
        dates,
        key=lambda date: abs(diff_in_days(date if date else OLDEST_DATE, target_date)),
    )

    closest_method = _get_max_measurement_method(
        method for method, date in zip(methods, dates) if date == closest_date
    )

    value = next(
        (value for value, method in zip(values, methods) if method == closest_method.value), 0
    )

    return SocStock(value, closest_method)


def _group_soc_stocks(site: dict) -> dict:
    """
    Group valid `organicCarbonPerHa` measurement nodes by year (based on node "dates" field) and reduce them to a
    single `SocStock` for each year.

    Parameters
    ----------
    site : dict
        A [Site node](https://www.hestia.earth/schema/Cycle).

    Returns
    -------
    dict
        A dictionary where each key represents a year and its corresponding value is a dictionary containing SOC stock
        information under the inner key specified by _InnerKey.SOC_STOCK.
    """
    INNER_KEY = _InnerKey.SOC_STOCK

    grouped_soc_measurements = group_nodes_by_year(
        (node for node in site.get("measurements", []) if _validate_soc_measurement_node(node)),
        mode=GroupNodesByYearMode.DATES
    )

    return {
        year: {
            INNER_KEY: (
                _nodes_to_soc_stock(year, nodes)
            )
        } for year, nodes in grouped_soc_measurements.items()
    }


def _interpolate_grouped_soc_stocks(grouped_soc_stocks: dict) -> dict:
    """
    Interpolate SOC stocks for years between grouped SOC stock data.

    This function iterates over the provided grouped SOC stock data and performs linear interpolation for years between
    existing data points. The result is a dictionary with SOC stock information for all years, including those without
    initially available data.

    Parameters
    ----------
    grouped_soc_stocks : dict
        Dictionary containing grouped SOC stock data with years as keys.

    Returns
    -------
    dict
        A dictionary with interpolated SOC stock data for missing years.
    """

    INNER_KEY = _InnerKey.SOC_STOCK

    def group_interpolate(data: dict, i: int):
        current_year = list(grouped_soc_stocks.keys())[i]
        prev_year = list(grouped_soc_stocks.keys())[i-1]

        current_soc_stock = grouped_soc_stocks[current_year][INNER_KEY]
        prev_soc_stock = grouped_soc_stocks[prev_year][INNER_KEY]

        return data | {
            inner_year: {
                INNER_KEY: _linear_interpolate_soc_stock(
                    prev_year, current_year, prev_soc_stock, current_soc_stock, inner_year
                )
            } for inner_year in range(prev_year+1, current_year)
        }

    return reduce(group_interpolate, range(1, len(grouped_soc_stocks)), dict())


def _get_grouped_soc_stocks(site: dict) -> dict:
    """
    Get grouped and interpolated SOC stocks for a site.

    This function combines grouping and interpolation of SOC stocks for a given site, providing a comprehensive
    dictionary with SOC stock information for all years.

    Parameters
    ----------
    site : dict
        The site dictionary containing SOC measurements.

    Returns
    -------
    dict
        A dictionary with grouped and interpolated SOC stock data for all years.
    """
    grouped_soc_stocks = _group_soc_stocks(site)
    grouped_interpolated_soc_stocks = _interpolate_grouped_soc_stocks(grouped_soc_stocks)
    return _sorted_merge(grouped_soc_stocks, grouped_interpolated_soc_stocks)


def _calc_grouped_soc_stock_changes(grouped_soc_stocks: dict) -> dict:
    """
    Calculate SOC stock changes between grouped SOC stock data for consecutive years.

    Parameters
    ----------
    grouped_soc_stocks : dict
        Dictionary containing grouped SOC stock data with years as keys.

    Returns
    -------
    dict
        A dictionary with calculated SOC stock changes for consecutive years.
    """
    INNER_KEY = _InnerKey.SOC_STOCK_CHANGE

    def group_changes(data: dict, i: int):
        current_year = list(grouped_soc_stocks.keys())[i]
        prev_year = list(grouped_soc_stocks.keys())[i-1]

        current_soc_stock = grouped_soc_stocks[current_year][_InnerKey.SOC_STOCK]
        prev_soc_stock = grouped_soc_stocks[prev_year][_InnerKey.SOC_STOCK]

        return data | {
            current_year: {
                INNER_KEY: _calc_soc_stock_change(prev_soc_stock, current_soc_stock)
            }
        }

    return reduce(group_changes, range(1, len(grouped_soc_stocks)), dict())


def _calc_sum_cycle_occupancy(cycles: list[dict]) -> float:
    """
    Calculate the sum of cycle occupancies based on the `fraction_of_group_duration` field added by the
    `group_nodes_by_year` function.

    If a cycle does not have the "fraction_of_group_duration" key, it is treated as zero occupancy for that year.

    Parameters
    ----------
    cycles : List[dict]
        List of cycles, where each cycle dictionary should contain a "fraction_of_group_duration" key.

    Returns
    -------
    float
        The sum of cycle occupancies based on the fraction of the year.
    """
    return sum(cycle.get("fraction_of_group_duration", 0) for cycle in cycles)


def _calc_grouped_share_of_emissions(cycles: list[dict]) -> dict:
    """
    Calculate grouped share of emissions for cycles based on the amount they contribute the the overall land management
    of an inventory year.

    This function groups cycles by year, then calculates the share of emissions for each cycle based on the
    "fraction_of_group_duration" value. The share of emissions is normalized by the sum of cycle occupancies for the
    entire dataset to ensure the values represent a valid share.

    Parameters
    ----------
    cycles : List[dict]
        List of [Cycle nodes](https://www.hestia.earth/schema/Cycle), where each cycle dictionary should contain a
        "fraction_of_group_duration" key added by the `group_nodes_by_year` function.

    Returns
    -------
    dict
        A dictionary with grouped share of emissions for each cycle based on the fraction of the year.
    """
    INNER_KEY = _InnerKey.SHARE_OF_EMISSIONS
    grouped_cycles = group_nodes_by_year(cycles)
    return {
        year: {
            INNER_KEY: {
                cycle["@id"]: cycle.get("fraction_of_group_duration", 0) / _calc_sum_cycle_occupancy(cycles)
                for cycle in cycles
            }
        } for year, cycles in grouped_cycles.items()
    }


def _run(cycle_id: str, grouped_data: dict) -> list[dict]:
    """
    Calculate emissions for a specific cycle using grouped SOC stock change and share of emissions data.

    The emission method tier based on the minimum measurement method tier among the SOC stock change data in the
    grouped data.

    Parameters
    ----------
    cycle_id : str
        The "@id" field of the [Cycle node](https://www.hestia.earth/schema/Cycle).

    grouped_data : dict
        A dictionary containing grouped SOC stock change and share of emissions data.

    Returns
    -------
    list[dict]
        A list containing emission data calculated for the specified cycle.
    """

    value = sum(
        _soc_stock_stock_change_to_co2_emission(
            group[_InnerKey.SOC_STOCK_CHANGE].value,
            group[_InnerKey.SHARE_OF_EMISSIONS].get(cycle_id, 1)
        ) for group in grouped_data.values()
    )

    method_tier = _get_emission_method_tier(
        _get_min_measurement_method(
            group[_InnerKey.SOC_STOCK_CHANGE].method for group in grouped_data.values()
        )
    )

    return [_emission(value, method_tier)]


def get_site(cycle: dict) -> dict:
    return cycle.get("site", {})


def _should_run(cycle: dict) -> tuple:
    """
    Determine if calculations should run for a given cycle based on SOC stock and emissions data.

    This function assesses whether calculations should run for a given cycle by checking the availability of SOC stock
    data and cycle nodes. It retrieves SOC stock data and for the site linked to the cycle, calculates SOC stock
    changes and share of emissions, and merges the data into a grouped format. The function checks for the presence of
    necessary keys in the grouped data and ensures that the years are consecutive before determining if calculations
    should run.

    Parameters
    ----------
    cycle : dict
        The cycle dictionary for which the calculations will be evaluated.

    Returns
    -------
    tuple
        A tuple containing a boolean indicating whether calculations should run,
        the cycle identifier, and grouped SOC stock and emissions data.
    """
    cycle_id = cycle.get("@id")
    site = get_site(cycle)
    cycles = related_cycles(site.get("@id"))

    grouped_soc_stocks = _get_grouped_soc_stocks(site)
    grouped_soc_stock_changes = _calc_grouped_soc_stock_changes(grouped_soc_stocks)
    grouped_share_of_emissions = _calc_grouped_share_of_emissions(cycles)

    def _should_run_group(year: int, group: dict) -> bool:
        is_data_complete = all(key in group.keys() for key in REQUIRED_INNER_KEYS)
        is_relevant_for_cycle = cycle_id in group.get(_InnerKey.SHARE_OF_EMISSIONS, {}).keys()
        return is_data_complete and is_relevant_for_cycle

    inventory = _sorted_merge(grouped_soc_stocks, grouped_soc_stock_changes, grouped_share_of_emissions)
    valid_years = [year for year, group in inventory.items() if _should_run_group(year, group)]

    num_organic_carbon_per_ha_measurements = len(
        [node for node in site.get('measurements', []) if _validate_soc_measurement_node(node)]
    )
    has_organic_carbon_per_ha_measurements = num_organic_carbon_per_ha_measurements > 1
    has_functional_unit_1_ha = all(
        cycle.get('functionalUnit') == CycleFunctionalUnit._1_HA.value for cycle in cycles
    )
    has_valid_inventory = len(valid_years) > 0 and check_consecutive(valid_years)

    logRequirements(
        cycle, model=MODEL, term=TERM_ID,
        has_organic_carbon_per_ha_measurements=has_organic_carbon_per_ha_measurements,
        has_functional_unit_1_ha=has_functional_unit_1_ha,
        has_valid_inventory=has_valid_inventory,
        inventory=log_as_table(
            {
                "year": year,
                "should-run": year in valid_years,
                "soc-stock": (
                    group.get(_InnerKey.SOC_STOCK).value if group.get(_InnerKey.SOC_STOCK)
                    else None
                ),
                "soc-stock-method": (
                    group.get(_InnerKey.SOC_STOCK).method.value if group.get(_InnerKey.SOC_STOCK)
                    else None
                ),
                "soc-stock-change": (
                    group.get(_InnerKey.SOC_STOCK_CHANGE).value if group.get(_InnerKey.SOC_STOCK_CHANGE)
                    else None
                ),
                "soc-stock-change-method": (
                    group.get(_InnerKey.SOC_STOCK_CHANGE).method.value if group.get(_InnerKey.SOC_STOCK_CHANGE)
                    else None
                ),
                "share-of-emission": group.get(_InnerKey.SHARE_OF_EMISSIONS, {}).get(cycle_id, 0)
            } for year, group in inventory.items()
        )
    )

    should_run = has_functional_unit_1_ha and has_valid_inventory
    logShouldRun(cycle, MODEL, TERM_ID, should_run)

    return should_run, cycle_id, {year: group for year, group in inventory.items() if year in valid_years}


def run(cycle: dict) -> list[dict]:
    should_run, *args = _should_run(cycle)

    return _run(*args) if should_run else []
