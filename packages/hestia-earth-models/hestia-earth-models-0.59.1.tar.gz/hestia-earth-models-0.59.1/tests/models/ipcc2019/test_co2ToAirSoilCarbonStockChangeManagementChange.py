from functools import reduce
import json
from pytest import mark
from unittest.mock import patch

from hestia_earth.schema import MeasurementMethodClassification

from hestia_earth.models.ipcc2019.co2ToAirSoilCarbonStockChangeManagementChange import (
    _calc_soc_stock_change,
    _convert_c_to_co2,
    _get_max_measurement_method,
    _get_min_measurement_method,
    _linear_interpolate_soc_stock,
    _nodes_to_soc_stock,
    MODEL,
    run,
    SocStock,
    TERM_ID
)

from tests.utils import (
    fake_new_emission,
    fixtures_path
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

RUN_SCENARIOS = [
    ("no-overlapping-cycles", 3),
    ("overlapping-cycles", 4),
    ("complex-overlapping-cycles", 5),
    ("missing-measurement-dates", 3),
    ("no-organic-carbon-measurements", 1)  # Closes issue #700
]
"""List of (subfolder: str, num_cycles: int)."""

RUN_PARAMS = reduce(
    lambda params, scenario: params + [(scenario[0], scenario[1], i) for i in range(scenario[1])],
    RUN_SCENARIOS,
    list()
)
"""List of (subfolder: str, num_cycles: int, cycle_index: int)."""

RUN_IDS = [f"{param[0]}, cycle{param[2]}" for param in RUN_PARAMS]


def _load_fixture(path: str):
    with open(path, encoding="utf-8") as f:
        fixture = json.load(f)
    return fixture


def _get_site_path(subfolder: str) -> str:
    return f"{fixtures_folder}/{subfolder}/site.jsonld"


def _get_cycle_path(subfolder: str, index: int) -> str:
    return f"{fixtures_folder}/{subfolder}/cycle{index}.jsonld"


def _get_result_path(subfolder: str, index: int) -> str:
    return f"{fixtures_folder}/{subfolder}/result{index}.jsonld"


def test_calc_soc_stock_change():
    START_SOC_STOCK = SocStock(20000, MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    END_SOC_STOCK = SocStock(21000, MeasurementMethodClassification.TIER_1_MODEL)
    EXPECTED = SocStock(1000, MeasurementMethodClassification.TIER_1_MODEL)

    result = _calc_soc_stock_change(START_SOC_STOCK, END_SOC_STOCK)
    assert result == EXPECTED


def test_convert_c_to_co2():
    KG_C = 1000
    EXPECTED = 3663.836163836164

    assert _convert_c_to_co2(KG_C) == EXPECTED


def test_get_max_measurement_method():
    EXPECTED = MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT
    result = _get_max_measurement_method(
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
    )
    assert result == EXPECTED


def test_get_max_measurement_method_list():
    EXPECTED = MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT
    METHODS = [
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
    ]
    result = _get_max_measurement_method(METHODS)
    assert result == EXPECTED


def test_get_max_measurement_method_no_methods():
    EXPECTED = MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT
    result = _get_max_measurement_method()
    assert result == EXPECTED


def test_get_min_measurement_method():
    EXPECTED = MeasurementMethodClassification.TIER_1_MODEL
    result = _get_min_measurement_method(
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
    )
    assert result == EXPECTED


def test_get_min_measurement_method_list():
    EXPECTED = MeasurementMethodClassification.TIER_1_MODEL
    METHODS = [
        MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT,
        MeasurementMethodClassification.TIER_2_MODEL,
        MeasurementMethodClassification.TIER_1_MODEL
    ]
    result = _get_min_measurement_method(METHODS)
    assert result == EXPECTED


def test_get_min_measurement_method_no_methods():
    EXPECTED = MeasurementMethodClassification.UNSOURCED_ASSUMPTION
    result = _get_min_measurement_method()
    assert result == EXPECTED


def test_linear_interpolate_soc_stock():
    START_YEAR = 2000
    END_YEAR = 2002
    START_SOC_STOCK = SocStock(20000, MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    END_SOC_STOCK = SocStock(22000, MeasurementMethodClassification.ON_SITE_PHYSICAL_MEASUREMENT)
    TARGET_YEAR = 2001
    EXPECTED = SocStock(21000, MeasurementMethodClassification.TIER_1_MODEL)

    result = _linear_interpolate_soc_stock(
        START_YEAR, END_YEAR, START_SOC_STOCK, END_SOC_STOCK, TARGET_YEAR
    )
    assert result == EXPECTED


def test_nodes_to_soc_stock_diff_dates():
    NODES = [
        {
            "value": [1000],
            "dates": ["2020"],
            "methodClassification": "modelled using other measurements"
        },
        {
            "value": [12000],
            "dates": ["2020-12-31"],
            "methodClassification": "tier 1 model"
        }
    ]
    EXPECTED = SocStock(12000, MeasurementMethodClassification.TIER_1_MODEL)

    assert _nodes_to_soc_stock(2020, NODES) == EXPECTED


def test_nodes_to_soc_stock_same_dates():
    NODES = [
        {
            "value": [10000],
            "dates": ["2020-12-31"],
            "methodClassification": "modelled using other measurements"
        },
        {
            "value": [12000],
            "dates": ["2020-12-31"],
            "methodClassification": "tier 1 model"
        },
        {
            "value": [11000],
            "dates": ["2020-06-01"],
            "methodClassification": "on-site physical measurement"
        }
    ]
    EXPECTED = SocStock(10000, MeasurementMethodClassification.MODELLED_USING_OTHER_MEASUREMENTS)

    assert _nodes_to_soc_stock(2020, NODES) == EXPECTED


@mark.parametrize("subfolder, num_cycles, cycle_index", RUN_PARAMS, ids=RUN_IDS)
@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{class_path}.related_cycles")
@patch(f"{class_path}.get_site")
def test_run(_get_site_mock, related_cycles_mock, _new_emission_mock, subfolder, num_cycles, cycle_index):
    """
    Test `run` function for each cycle in each scenario.
    """
    site = _load_fixture(_get_site_path(subfolder))
    cycle = _load_fixture(_get_cycle_path(subfolder, cycle_index))
    expected = _load_fixture(_get_result_path(subfolder, cycle_index))

    cycles = [
        _load_fixture(_get_cycle_path(subfolder, i)) for i in range(num_cycles)
    ]

    _get_site_mock.return_value = site
    related_cycles_mock.return_value = cycles

    result = run(cycle)
    assert result == expected


@patch(f"{class_path}._new_emission", side_effect=fake_new_emission)
@patch(f"{class_path}.related_cycles")
@patch(f"{class_path}.get_site")
def test_run_empty(_get_site_mock, related_cycles_mock, _new_emission_mock):
    """
    Test `run` function for each cycle in each scenario.
    """
    CYCLE = {}
    EXPECTED = []

    _get_site_mock.return_value = {}
    related_cycles_mock.return_value = [CYCLE]

    result = run(CYCLE)
    assert result == EXPECTED
