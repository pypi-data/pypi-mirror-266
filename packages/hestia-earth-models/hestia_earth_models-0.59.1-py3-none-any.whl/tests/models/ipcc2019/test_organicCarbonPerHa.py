from unittest.mock import patch
import json
from numpy.testing import assert_almost_equal
from pytest import mark
import random

from tests.utils import (
    fixtures_path,
    fake_new_measurement,
)
from hestia_earth.models.ipcc2019.organicCarbonPerHa import (
    _assign_ipcc_carbon_input_category,
    _assign_ipcc_land_use_category,
    _assign_ipcc_management_category,
    _assign_ipcc_soil_category,
    _calc_temperature_factor,
    _calc_tier_1_soc_stocks,
    _calc_water_factor,
    _check_cropland_low_category,
    _check_cropland_medium_category,
    _get_carbon_input_kwargs,
    _iterate_soc_equilibriums,
    IpccCarbonInputCategory,
    IpccLandUseCategory,
    IpccManagementCategory,
    IpccSoilCategory,
    MODEL,
    run,
    TERM_ID
)

class_path = f"hestia_earth.models.{MODEL}.{TERM_ID}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{TERM_ID}"

COVER_CROP_PROPERTY_TERM_IDS = [
    "catchCrop",
    "coverCrop",
    "groundCover",
    "longFallowCrop",
    "shortFallowCrop"
]

CROP_RESIDUE_INCORP_TERM_IDS = [
    "aboveGroundCropResidueIncorporated",
    "aboveGroundCropResidueLeftOnField",
    "belowGroundCropResidue",
    "discardedCropIncorporated",
    "discardedCropLeftOnField"
]

IRRIGATED_TERM_IDS = [
    "rainfedDeepWater",
    "rainfedDeepWaterWaterDepth100Cm",
    "rainfedDeepWaterWaterDepth50100Cm",
    "irrigatedTypeUnspecified",
    "irrigatedCenterPivotIrrigation",
    "irrigatedContinuouslyFlooded",
    "irrigatedDripIrrigation",
    "irrigatedFurrowIrrigation",
    "irrigatedLateralMoveIrrigation",
    "irrigatedLocalizedIrrigation",
    "irrigatedManualIrrigation",
    "irrigatedSurfaceIrrigationMultipleDrainagePeriods",
    "irrigatedSurfaceIrrigationSingleDrainagePeriod",
    "irrigatedSprinklerIrrigation",
    "irrigatedSubIrrigation",
    "irrigatedSurfaceIrrigationDrainageRegimeUnspecified"
]

LONG_FALLOW_LAND_COVER_TERM_IDS = [
    "longFallow",
    "longBareFallow"
]

RESIDUE_REMOVED_OR_BURNT_TERM_IDS = [
    "residueBurnt",
    "residueRemoved"
]

UPLAND_RICE_LAND_COVER_TERM_IDS = [
    "ricePlantUpland"
]

UPLAND_RICE_CROP_TERM_IDS = [
    "riceGrainInHuskUpland"
]


# --- TIER 1 & TIER 2 TESTS ---


# subfolder, load_cycles
RUN_SUBFOLDERS = [
    ("tier-1-and-2/cropland", True),
    ("tier-2/with-generalised-monthly-measurements", True),  # Closes issue 600
    ("tier-2/with-incomplete-climate-data", True),  # Closes issue 599
    ("tier-2/with-initial-soc", True),
    ("tier-2/with-multi-year-cycles", True),
    ("tier-2/without-any-measurements", True),  # Closes issue 594
    ("tier-2/without-initial-soc", True),
    ("tier-2/with-irrigation", True),
    ("tier-2/with-irrigation-dates", True),
    ("tier-2/with-paddy-rice", True),
    ("tier-2/with-irrigated-upland-rice", True),
    ("tier-1/cropland-depth-as-float", False),
    ("tier-1/cropland-with-measured-soc", False),
    ("tier-1/cropland-without-measured-soc", False),
    ("tier-1/permanent-pasture", False),
    ("tier-1/should-not-run", False),
    ("tier-1/without-management-with-measured-soc", False)
]


@mark.parametrize(
    "subfolder, load_cycles",
    RUN_SUBFOLDERS,
    ids=[params[0] for params in RUN_SUBFOLDERS]
)
@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_long_fallow_land_cover_terms", return_value=LONG_FALLOW_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_upland_rice_crop_terms", return_value=UPLAND_RICE_CROP_TERM_IDS)
@patch(f"{class_path}.related_cycles")
def test_run(
    mock_related_cycles,
    _mock_get_upland_rice_crop_terms,
    _mock_get_upland_rice_land_cover_terms,
    _mock_get_residue_removed_or_burnt_terms,
    _mock_get_long_fallow_land_cover_terms,
    _mock_get_irrigated_terms,
    _mock_get_crop_residue_incorporated_or_left_on_field_terms,
    _mock_get_cover_crop_property_terms,
    _mock_new_measurement,
    subfolder,
    load_cycles
):
    folder = f"{fixtures_folder}/{subfolder}"

    def load_cycles_from_file():
        with open(f"{folder}/cycles.jsonld", encoding='utf-8') as f:
            return json.load(f)

    mock_related_cycles.return_value = load_cycles_from_file() if load_cycles else []

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected


@patch(f"{class_path}._new_measurement", side_effect=fake_new_measurement)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_long_fallow_land_cover_terms", return_value=LONG_FALLOW_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
@patch(f"{class_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_upland_rice_crop_terms", return_value=UPLAND_RICE_CROP_TERM_IDS)
@patch(f"{class_path}.related_cycles", return_value=[])
def test_run_no_data(*args):
    SITE = {}
    EXPECTED = []
    result = run(SITE)
    assert result == EXPECTED


# --- TIER 2 TESTS: SUB-MODELS ---


def test_calc_temperature_factor():
    NUM_RANDOM = 9999
    MIN_T, MAX_T = -60, 60
    MIN_FAC, MAX_FAC = 0, 1

    temperatures = [random.uniform(MIN_T, MAX_T) for _ in range(0, NUM_RANDOM)]
    results = [
        _calc_temperature_factor(t) for t in temperatures
    ]

    assert all(MIN_FAC <= result <= MAX_FAC for result in results)


def test_calc_water_factor():
    NUM_RANDOM = 9999
    MIN, MAX = 0, 9999
    MIN_FAC, MAX_FAC = 0.2129, 1.5
    IRR_FAC = 0.775

    precipitations = [random.uniform(MIN, MAX) for _ in range(0, NUM_RANDOM)]
    pets = [random.uniform(MIN, MAX) for _ in range(0, NUM_RANDOM)]

    results = [
        _calc_water_factor(pre, pet) for pre, pet in zip(precipitations, pets)
    ]
    irr_results = [
        _calc_water_factor(pre, pet, is_irrigated=True) for pre, pet in zip(precipitations, pets)
    ]

    assert all(MIN_FAC <= result <= MAX_FAC for result in results)
    assert all(result == IRR_FAC for result in irr_results)
    assert _calc_water_factor(1, 1) == _calc_water_factor(1000, 1000)


# --- IPCC SOIL CATEGORY TESTS ---


# subfolder, expected
SOIL_CATEGORY_PARAMS = [
    ("fractional", IpccSoilCategory.WETLAND_SOILS),
    ("no-measurements", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS),
    ("sandy-override", IpccSoilCategory.SANDY_SOILS),
    ("soilType/hac", IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS),
    ("soilType/lac", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS),
    ("soilType/org", IpccSoilCategory.ORGANIC_SOILS),
    ("soilType/pod", IpccSoilCategory.SPODIC_SOILS),
    ("soilType/san", IpccSoilCategory.SANDY_SOILS),
    ("soilType/vol", IpccSoilCategory.VOLCANIC_SOILS),
    ("soilType/wet", IpccSoilCategory.WETLAND_SOILS),
    ("usdaSoilType/hac", IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS),
    ("usdaSoilType/lac", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS),
    ("usdaSoilType/org", IpccSoilCategory.ORGANIC_SOILS),
    ("usdaSoilType/pod", IpccSoilCategory.SPODIC_SOILS),
    ("usdaSoilType/san", IpccSoilCategory.SANDY_SOILS),
    ("usdaSoilType/vol", IpccSoilCategory.VOLCANIC_SOILS),
    ("usdaSoilType/wet", IpccSoilCategory.WETLAND_SOILS)
]


@mark.parametrize(
    "subfolder, expected",
    SOIL_CATEGORY_PARAMS,
    ids=[params[0] for params in SOIL_CATEGORY_PARAMS]
)
def test_assign_ipcc_soil_category(subfolder, expected):
    folder = f"{fixtures_folder}/IpccSoilCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_soil_category(site.get("measurements", []))
    assert result == expected


# --- IPCC LAND USE CATEGORY TESTS ---


# subfolder, soil_category, expected
LAND_USE_CATEGORY_PARAMS = [
    ("annual-crops", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.ANNUAL_CROPS),
    ("annual-crops-wet", IpccSoilCategory.WETLAND_SOILS, IpccLandUseCategory.ANNUAL_CROPS_WET),
    ("forest", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.FOREST),
    ("fractional", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PERENNIAL_CROPS),
    ("grassland", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.GRASSLAND),
    ("irrigated-upland-rice", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PADDY_RICE_CULTIVATION),
    ("native", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.NATIVE),
    ("other", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.OTHER),
    ("paddy-rice-cultivation", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PADDY_RICE_CULTIVATION),
    ("perennial-crops", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.PERENNIAL_CROPS),
    ("set-aside", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.SET_ASIDE),
    ("set-aside-override", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.SET_ASIDE),
    ("upland-rice", IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS, IpccLandUseCategory.ANNUAL_CROPS),
]


@mark.parametrize(
    "subfolder, soil_category, expected",
    LAND_USE_CATEGORY_PARAMS,
    ids=[params[0] for params in LAND_USE_CATEGORY_PARAMS]
)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_long_fallow_land_cover_terms", return_value=LONG_FALLOW_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_upland_rice_land_cover_terms", return_value=UPLAND_RICE_LAND_COVER_TERM_IDS)
def test_assign_ipcc_land_use_category(
    _mock_get_upland_rice_land_cover_terms,
    _mock_get_long_fallow_land_cover_terms,
    _mock_get_irrigated_terms,
    subfolder,
    soil_category,
    expected
):
    folder = f"{fixtures_folder}/IpccLandUseCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_land_use_category(site.get("siteType"), site.get("management", []), soil_category)
    assert result == expected


# --- IPCC MANAGEMENT CATEGORY TESTS ---


# subfolder, land_use_category, expected
MANAGEMENT_CATEGORY_PARAMS = [
    ("fractional-annual-crops", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.REDUCED_TILLAGE),
    ("fractional-annual-crops-wet", IpccLandUseCategory.ANNUAL_CROPS_WET, IpccManagementCategory.REDUCED_TILLAGE),
    ("fractional-grassland", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.IMPROVED_GRASSLAND),
    ("full-tillage", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.FULL_TILLAGE),
    ("high-intensity-grazing", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.HIGH_INTENSITY_GRAZING),
    ("improved-grassland", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.IMPROVED_GRASSLAND),
    ("no-management/annual-crops", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.FULL_TILLAGE),
    ("no-management/annual-crops-wet", IpccLandUseCategory.ANNUAL_CROPS_WET, IpccManagementCategory.FULL_TILLAGE),
    ("no-management/grassland", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.NOMINALLY_MANAGED),
    ("no-tillage", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.NO_TILLAGE),
    ("nominally-managed", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.NOMINALLY_MANAGED),
    ("other", IpccLandUseCategory.OTHER, IpccManagementCategory.OTHER),
    ("reduced-tillage", IpccLandUseCategory.ANNUAL_CROPS, IpccManagementCategory.REDUCED_TILLAGE),
    ("severely-degraded", IpccLandUseCategory.GRASSLAND, IpccManagementCategory.SEVERELY_DEGRADED),
]


@mark.parametrize(
    "subfolder, land_use_category, expected",
    MANAGEMENT_CATEGORY_PARAMS,
    ids=[params[0] for params in MANAGEMENT_CATEGORY_PARAMS]
)
def test_assign_ipcc_management_category(subfolder, land_use_category, expected):
    folder = f"{fixtures_folder}/IpccManagementCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_management_category(site.get("management", []), land_use_category)
    assert result == expected


# --- IPCC CARBON INPUT CATEGORY TESTS ---


@mark.parametrize("key", [1, 2, 3, 4], ids=lambda key: f"scenario-{key}")
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_long_fallow_land_cover_terms", return_value=LONG_FALLOW_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_check_cropland_medium_category(
    _mock_get_residue_removed_or_burnt_terms,
    _mock_get_long_fallow_land_cover_terms,
    _mock_get_irrigated_terms,
    _mock_get_crop_residue_incorporated_or_left_on_field_terms,
    _mock_get_cover_crop_property_terms,
    key
):
    """
    Tests each set of cropland medium conditions against a list of nodes that such satisfy it. The function returns the
    key of the matching condition set, which should match the suffix of the fixtures subfolder.
    """
    folder = f"{fixtures_folder}/IpccCarbonInputCategory/cropland-medium/scenario-{key}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _check_cropland_medium_category(**_get_carbon_input_kwargs(site.get("management", [])))
    assert result == key


@mark.parametrize("key", [1, 2, 3], ids=lambda key: f"scenario-{key}")
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_long_fallow_land_cover_terms", return_value=LONG_FALLOW_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_check_cropland_low_category(
    _mock_get_residue_removed_or_burnt_terms,
    _mock_get_long_fallow_land_cover_terms,
    _mock_get_irrigated_terms,
    _mock_get_crop_residue_incorporated_or_left_on_field_terms,
    _mock_get_cover_crop_property_terms,
    key
):
    """
    Tests each set of cropland low conditions against a list of nodes that such satisfy it. The function returns the
    key of the matching condition set, which should match the suffix of the fixtures subfolder.
    """
    folder = f"{fixtures_folder}/IpccCarbonInputCategory/cropland-low/scenario-{key}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _check_cropland_low_category(**_get_carbon_input_kwargs(site.get("management", [])))
    assert result == key


# subfolder, management_category, expected
CARBON_INPUT_CATEGORY_PARAMS = [
    (
        "cropland-high-with-manure",
        IpccManagementCategory.FULL_TILLAGE,
        IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE
    ),
    (
        "cropland-high-without-manure",
        IpccManagementCategory.FULL_TILLAGE,
        IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE
    ),
    ("cropland-low/scenario-1", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_LOW),
    ("cropland-low/scenario-2", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_LOW),
    ("cropland-low/scenario-3", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_LOW),
    ("cropland-medium/scenario-1", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("cropland-medium/scenario-2", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("cropland-medium/scenario-3", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("cropland-medium/scenario-4", IpccManagementCategory.FULL_TILLAGE, IpccCarbonInputCategory.CROPLAND_MEDIUM),
    ("grassland-high", IpccManagementCategory.IMPROVED_GRASSLAND, IpccCarbonInputCategory.GRASSLAND_HIGH),
    (
        "grassland-medium/0-improvements",
        IpccManagementCategory.IMPROVED_GRASSLAND,
        IpccCarbonInputCategory.GRASSLAND_MEDIUM
    ),
    (
        "grassland-medium/1-improvements",
        IpccManagementCategory.IMPROVED_GRASSLAND,
        IpccCarbonInputCategory.GRASSLAND_MEDIUM
    )
]


@mark.parametrize(
    "subfolder, management_category, expected",
    CARBON_INPUT_CATEGORY_PARAMS,
    ids=[params[0] for params in CARBON_INPUT_CATEGORY_PARAMS]
)
@patch(f"{class_path}.get_cover_crop_property_terms", return_value=COVER_CROP_PROPERTY_TERM_IDS)
@patch(f"{class_path}.get_crop_residue_incorporated_or_left_on_field_terms", return_value=CROP_RESIDUE_INCORP_TERM_IDS)
@patch(f"{class_path}.get_irrigated_terms", return_value=IRRIGATED_TERM_IDS)
@patch(f"{class_path}.get_long_fallow_land_cover_terms", return_value=LONG_FALLOW_LAND_COVER_TERM_IDS)
@patch(f"{class_path}.get_residue_removed_or_burnt_terms", return_value=RESIDUE_REMOVED_OR_BURNT_TERM_IDS)
def test_assign_ipcc_carbon_input_category(
    _mock_get_residue_removed_or_burnt_terms,
    _mock_get_long_fallow_land_cover_terms,
    _mock_get_irrigated_terms,
    _mock_get_crop_residue_incorporated_or_left_on_field_terms,
    _mock_get_cover_crop_property_terms,
    subfolder,
    management_category,
    expected
):
    folder = f"{fixtures_folder}/IpccCarbonInputCategory/{subfolder}"

    with open(f"{folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    result = _assign_ipcc_carbon_input_category(site.get("management", []), management_category)
    assert result == expected


# --- TIER 1 TESTS ---


@mark.parametrize(
    "soc_equilibriums, expected",
    [
        (
            [77.000, 70.840, 70.840, 70.840, 70.840, 70.840, 70.840],
            [77.000, 75.460, 73.920, 72.380, 70.840, 70.840, 70.840]
        ),
        (
            [77.000, 70.840, 70.840, 70.840, 80.850, 80.850, 80.850],
            [77.000, 75.460, 73.920, 72.380, 74.498, 76.615, 78.733]
        ),
        (
            [80.850, 70.840, 70.840, 70.840, 70.840, 80.850, 80.850],
            [80.850, 78.348, 75.845, 73.343, 70.840, 73.343, 75.845]
        ),
        (
            [80.850, 80.850, 77.000, 77.000, 77.000, 77.000, 77.000],
            [80.850, 80.850, 79.888, 78.925, 77.963, 77.000, 77.000]
        ),
        (
            [70.840, 70.840, 70.840, 70.840, 80.850, 80.850, 80.850],
            [70.840, 70.840, 70.840, 70.840, 73.343, 75.845, 78.348]
        ),
        (
            [70.840, 70.840, 80.850, 80.850, 80.850, 70.840, 80.850],
            [70.840, 70.840, 73.343, 75.845, 78.348, 76.471, 77.565]
        ),
    ],
    ids=["land-unit-1", "land-unit-2", "land-unit-3", "land-unit-4", "land-unit-5", "land-unit-6"]
)
def test_run_tier_1_soc_stocks(soc_equilibriums, expected):
    """
    Test the interpolation between SOC equilibriums using test data provided in IPCC (2019).
    """
    TIMESTAMPS = [1990, 1995, 2000, 2005, 2010, 2015, 2020]
    result = _calc_tier_1_soc_stocks(
        TIMESTAMPS, soc_equilibriums
    )
    assert_almost_equal(result, expected, decimal=3)


def test_iterate_soc_equilibriums():
    TIMESTAMPS = [1990, 2020]
    SOC_EQUILIBRIUMS = [20000, 40000]

    EXPECTED = (
        [1990, 2010, 2020],
        [20000, 40000, 40000]
    )

    result = _iterate_soc_equilibriums(TIMESTAMPS, SOC_EQUILIBRIUMS)
    assert result == EXPECTED
