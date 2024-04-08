"""
The IPCC model for estimating soil organic carbon stock changes in the 0 - 30cm depth interval due to management
changes. This model combines the Tier 1 & Tier 2 methodologies. It first tries to run Tier 2 (only on croplands
remaining croplands). If Tier 2 cannot run, it will try to run Tier 1 (for croplands remaining croplands and for
grasslands remaining grasslands). Source:
[IPCC 2019, Vol. 4, Chapter 10](https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch05_Cropland.pdf).
"""
from enum import Enum
from numpy import exp
from pydash.objects import merge
from statistics import mean
from typing import (
    Any,
    NamedTuple,
    Optional,
    Union
)
from hestia_earth.schema import (
    CycleFunctionalUnit,
    MeasurementMethodClassification,
    SiteSiteType,
    TermTermType,
)
from hestia_earth.utils.model import find_term_match, filter_list_term_type
from hestia_earth.utils.tools import flatten, list_sum, non_empty_list

from hestia_earth.models.log import log_as_table, logRequirements, logShouldRun
from hestia_earth.models.utils.blank_node import (
    cumulative_nodes_match,
    cumulative_nodes_lookup_match,
    cumulative_nodes_term_match,
    get_node_value,
    group_nodes_by_year_and_month,
    group_nodes_by_year,
    GroupNodesByYearMode,
    node_lookup_match,
    node_term_match
)
from hestia_earth.models.utils.cycle import check_cycle_site_ids_identical
from hestia_earth.models.utils.ecoClimateZone import get_ecoClimateZone_lookup_value
from hestia_earth.models.utils.measurement import (
    _new_measurement,
)
from hestia_earth.models.utils.property import get_node_property
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.term import (
    get_cover_crop_property_terms,
    get_crop_residue_incorporated_or_left_on_field_terms,
    get_irrigated_terms,
    get_long_fallow_land_cover_terms,
    get_residue_removed_or_burnt_terms,
    get_upland_rice_crop_terms,
    get_upland_rice_land_cover_terms
)

from .utils import check_consecutive
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "siteType": ["cropland", "permanent pasture", "forest", "other natural vegetation"],
        "measurements": [
            {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"}
        ],
        "optional": {
            "measurements": [
                {"@type": "Measurement", "value": "", "term.termType": ["soilType", "usdaSoilType"]}
            ],
            "management": [
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "cropResidueManagement",
                    "name": ["burnt", "removed"]
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.termType": "landCover"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "landUseManagement"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.termType": "tillage"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.termType": "waterRegime",
                    "name": ["irrigated", "deep water"]
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "animalManureUsed"},
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "inorganicNitrogenFertiliserUsed"
                },
                {
                    "@type": "Management",
                    "value": "",
                    "startDate": "",
                    "endDate": "",
                    "term.@id": "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed"
                },
                {"@type": "Management", "value": "", "startDate": "", "endDate": "", "term.@id": "shortBareFallow"}
            ]
        }
    }
}
LOOKUPS = {
    "crop": "IPCC_LAND_USE_CATEGORY",
    "ecoClimateZone": [
        "IPCC_2019_SOC_REF_KG_C_HECTARE_SAN",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_WET",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_VOL",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_POD",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_HAC",
        "IPCC_2019_SOC_REF_KG_C_HECTARE_LAC",
        "IPCC_2019_LANDUSE_FACTOR_GRASSLAND",
        "IPCC_2019_LANDUSE_FACTOR_PERENNIAL_CROPS",
        "IPCC_2019_LANDUSE_FACTOR_PADDY_RICE_CULTIVATION",
        "IPCC_2019_LANDUSE_FACTOR_ANNUAL_CROPS_WET",
        "IPCC_2019_LANDUSE_FACTOR_ANNUAL_CROPS",
        "IPCC_2019_LANDUSE_FACTOR_SET_ASIDE",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_SEVERELY_DEGRADED",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_IMPROVED_GRASSLAND",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_HIGH_INTENSITY_GRAZING",
        "IPCC_2019_GRASSLAND_MANAGEMENT_FACTOR_NOMINALLY_MANAGED",
        "IPCC_2019_TILLAGE_MANAGEMENT_FACTOR_FULL_TILLAGE",
        "IPCC_2019_TILLAGE_MANAGEMENT_FACTOR_REDUCED_TILLAGE",
        "IPCC_2019_TILLAGE_MANAGEMENT_FACTOR_NO_TILLAGE",
        "IPCC_2019_GRASSLAND_CARBON_INPUT_FACTOR_HIGH",
        "IPCC_2019_GRASSLAND_CARBON_INPUT_FACTOR_MEDIUM",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_HIGH_WITH_MANURE",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_HIGH_WITHOUT_MANURE",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_MEDIUM",
        "IPCC_2019_CROPLAND_CARBON_INPUT_FACTOR_LOW"
    ],
    "landCover": [
        "IPCC_LAND_USE_CATEGORY",
        "LOW_RESIDUE_PRODUCING_CROP",
        "N_FIXING_CROP"
    ],
    "landUseManagement": "PRACTICE_INCREASING_C_INPUT",
    "soilType": "IPCC_SOIL_CATEGORY",
    "tillage": "IPCC_TILLAGE_MANAGEMENT_CATEGORY",
    "usdaSoilType": "IPCC_SOIL_CATEGORY"
}
RETURNS = {
    "Measurement": [{
        "value": "",
        "dates": "",
        "depthUpper": "0",
        "depthLower": "30",
        "methodClassification": ""
    }]
}

TERM_ID = 'organicCarbonPerHa'

# --- SHARED TIER 1 & TIER 2 CONSTANTS ---

MIN_AREA_THRESHOLD = 30  # 30% as per IPCC guidelines
SUPER_MAJORITY_AREA_THRESHOLD = 100 - MIN_AREA_THRESHOLD
MIN_YIELD_THRESHOLD = 1
DEPTH_UPPER = 0
DEPTH_LOWER = 30

# --- TIER 2 CONSTANTS ---

NUMBER_OF_TILLAGES_TERM_ID = "numberOfTillages"
TEMPERATURE_MONTHLY_TERM_ID = "temperatureMonthly"
PRECIPITATION_MONTHLY_TERM_ID = "precipitationMonthly"
PET_MONTHLY_TERM_ID = "potentialEvapotranspirationMonthly"
SAND_CONTENT_TERM_ID = "sandContent"
CARBON_CONTENT_TERM_ID = "carbonContent"
NITROGEN_CONTENT_TERM_ID = "nitrogenContent"
LIGNIN_CONTENT_TERM_ID = "ligninContent"

CROP_RESIDUE_PROPERTY_TERM_IDS = [
    CARBON_CONTENT_TERM_ID,
    NITROGEN_CONTENT_TERM_ID,
    LIGNIN_CONTENT_TERM_ID
]

CARBON_SOURCE_TERM_TYPES = [
    TermTermType.ORGANICFERTILISER.value,
    TermTermType.SOILAMENDMENT.value,
    TermTermType.SEED.value
]

MIN_RUN_IN_PERIOD = 5

DEFAULT_PARAMS = {
    "active_decay_factor": 7.4,
    "slow_decay_factor": 0.209,
    "passive_decay_factor": 0.00689,
    "f_1": 0.378,
    "f_2_full_tillage": 0.455,
    "f_2_reduced_tillage": 0.477,
    "f_2_no_tillage": 0.5,
    "f_2_unknown_tillage": 0.368,
    "f_3": 0.455,
    "f_5": 0.0855,
    "f_6": 0.0504,
    "f_7": 0.42,
    "f_8": 0.45,
    "tillage_factor_full_tillage": 3.036,
    "tillage_factor_reduced_tillage": 2.075,
    "tillage_factor_no_tillage": 1,
    "maximum_temperature": 45,
    "optimum_temperature": 33.69,
    "water_factor_slope": 1.331,
    "default_carbon_content": 0.42,
    "default_nitrogen_content": 0.0085,
    "default_lignin_content": 0.073
}

VALID_SITE_TYPES_TIER_2 = [
    SiteSiteType.CROPLAND.value
]

VALID_FUNCTIONAL_UNITS_TIER_2 = [
    CycleFunctionalUnit._1_HA.value
]

# --- TIER 1 CONSTANTS ---

CLAY_CONTENT_TERM_ID = "clayContent"
LONG_FALLOW_CROP_TERM_ID = "longFallowCrop"
IMPROVED_PASTURE_TERM_ID = "improvedPasture"
SHORT_BARE_FALLOW_TERM_ID = "shortBareFallow"
ANIMAL_MANURE_USED_TERM_ID = "animalManureUsed"
INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID = "inorganicNitrogenFertiliserUsed"
ORGANIC_FERTILISER_USED_TERM_ID = "organicFertiliserOrSoilCarbonIncreasingAmendmentUsed"

CLAY_CONTENT_MAX = 8
SAND_CONTENT_MIN = 70

EQUILIBRIUM_TRANSITION_PERIOD = 20
"""
The number of years required for soil organic carbon to reach equilibrium after
a change in land use, management regime or carbon input regime.
"""

VALID_SITE_TYPES_TIER_1 = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.FOREST.value,
    SiteSiteType.OTHER_NATURAL_VEGETATION.value,
    SiteSiteType.PERMANENT_PASTURE.value,
]

# --- SHARED TIER 1 & TIER 2 FORMAT MEASUREMENT OUTPUT ---


def _measurement(year: int, value: float, method_classification: str) -> dict:
    """
    Build a Hestia `Measurement` node to contain a value calculated by the models.

    Parameters
    ----------
    year : int
        The year that the value is associated with.
    value : float
        The value calculated by either the Tier 1 or Tier 2 model.
    method_classification :str
        The method tier used to calculate the value, either `tier 1 model` or `tier 2 model`.

    Returns
    -------
    dict
        A valid Hestia `Measurement` node, see: https://www.hestia.earth/schema/Measurement.
    """
    measurement = _new_measurement(TERM_ID, MODEL)
    measurement["value"] = [value]
    measurement["dates"] = [f"{year}-12-31"]
    measurement["depthUpper"] = DEPTH_UPPER
    measurement["depthLower"] = DEPTH_LOWER
    measurement["methodClassification"] = method_classification
    return measurement


# --- SHARED TIER 1 & TIER 2 ENUMS ---

class IpccManagementCategory(Enum):
    """
    Enum representing IPCC Management Categories for grasslands and annual croplands.

    See [IPCC (2019) Vol. 4, Ch. 5 and 6](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more
    information.
    """
    SEVERELY_DEGRADED = "severely degraded"
    IMPROVED_GRASSLAND = "improved grassland"
    HIGH_INTENSITY_GRAZING = "high-intensity grazing"
    NOMINALLY_MANAGED = "nominally managed"
    FULL_TILLAGE = "full tillage"
    REDUCED_TILLAGE = "reduced tillage"
    NO_TILLAGE = "no tillage"
    OTHER = "other"


class _InventoryKey(Enum):
    """
    Enum representing the inner keys of the annual inventory is constructed from site and cycle data.
    """
    # Tier 1
    LU_CATEGORY = 'ipcc land use category'
    MG_CATEGORY = 'ipcc management category'
    CI_CATEGORY = 'ipcc carbon input category'
    SHOULD_RUN_TIER_1 = 'should run tier 1'
    # Tier 2
    TEMP_MONTHLY = 'temperature monthly'
    PRECIP_MONTHLY = 'precipitation monthly'
    PET_MONTHLY = 'PET monthly'
    IRRIGATED_MONTHLY = 'irrigated monthly'
    CARBON_INPUT = 'carbon input'
    N_CONTENT = 'nitrogen content'
    LIGNIN_CONTENT = 'lignin content'
    TILLAGE_CATEGORY = 'ipcc tillage category'
    SAND_CONTENT = 'sand content'
    IS_PADDY_RICE = 'is paddy rice'
    SHOULD_RUN_TIER_2 = 'should run tier 2'


REQUIRED_KEYS_TIER_1 = [
    _InventoryKey.LU_CATEGORY,
    _InventoryKey.MG_CATEGORY,
    _InventoryKey.CI_CATEGORY
]


REQUIRED_KEYS_TIER_2 = [
    _InventoryKey.TEMP_MONTHLY,
    _InventoryKey.PRECIP_MONTHLY,
    _InventoryKey.PET_MONTHLY,
    _InventoryKey.CARBON_INPUT,
    _InventoryKey.N_CONTENT,
    _InventoryKey.LIGNIN_CONTENT,
    _InventoryKey.TILLAGE_CATEGORY,
    _InventoryKey.IS_PADDY_RICE
]


# --- TIER 1 ENUMS ---


class IpccSoilCategory(Enum):
    """
    Enum representing IPCC Soil Categories.

    See [IPCC (2019) Vol 4, Ch. 2 and 3](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more
    information.
    """
    ORGANIC_SOILS = "organic soils"
    SANDY_SOILS = "sandy soils"
    WETLAND_SOILS = "wetland soils"
    VOLCANIC_SOILS = "volcanic soils"
    SPODIC_SOILS = "spodic soils"
    HIGH_ACTIVITY_CLAY_SOILS = "high-activity clay soils"
    LOW_ACTIVITY_CLAY_SOILS = "low-activity clay soils"


class IpccLandUseCategory(Enum):
    """
    Enum representing IPCC Land Use Categories.

    See [IPCC (2019) Vol 4](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.
    """
    GRASSLAND = "grassland"
    PERENNIAL_CROPS = "perennial crops"
    PADDY_RICE_CULTIVATION = "paddy rice cultivation"
    ANNUAL_CROPS_WET = "annual crops (wet)"
    ANNUAL_CROPS = "annual crops"
    SET_ASIDE = "set aside"
    FOREST = "forest"
    NATIVE = "native"
    OTHER = "other"


class IpccCarbonInputCategory(Enum):
    """
    Enum representing IPCC Carbon Input Categories for improved grasslands and annual croplands.

    See [IPCC (2019) Vol. 4, Ch. 4, 5 and 6](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more
    information.
    """
    GRASSLAND_HIGH = "grassland high"
    GRASSLAND_MEDIUM = "grassland medium"
    CROPLAND_HIGH_WITH_MANURE = "cropland high (with manure)"
    CROPLAND_HIGH_WITHOUT_MANURE = "cropland high (without manure)"
    CROPLAND_MEDIUM = "cropland medium"
    CROPLAND_LOW = "cropland low"
    OTHER = "other"


# --- TIER 2 NAMED TUPLES FOR CARBON SOURCES AND MODEL RESULTS ---


CarbonSource = NamedTuple(
    "CarbonSource",
    [
        ("mass", float),
        ("carbon_content", float),
        ("nitrogen_content", float),
        ("lignin_content", float),
    ]
)
"""
A single carbon source (e.g. crop residues or organic amendment).

Attributes
-----------
mass : float
    The dry-matter mass of the carbon source, kg ha-1
carbon_content : float
    The carbon content of the carbon source, decimal proportion, kg C (kg d.m.)-1.
nitrogen_content : float
    The nitrogen content of the carbon source, decimal_proportion, kg N (kg d.m.)-1.
lignin_content : float
    The lignin content of the carbon source, decimal_proportion, kg lignin (kg d.m.)-1.
"""


TemperatureFactorResult = NamedTuple(
    "TemperatureFactorResult",
    [
        ("timestamps", list[float]),
        ("annual_temperature_factors", list[float])
    ]
)
"""
A named tuple to hold the result of `_run_annual_temperature_factors`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
annual_temperature_factors : list[float]
    A list of annual temperature factors for each year in the inventory, dimensionless, between `0` and `1`.
"""


WaterFactorResult = NamedTuple(
    "WaterFactorResult",
    [
        ("timestamps", list[float]),
        ("annual_water_factors", list[float])
    ]
)
"""
A named tuple to hold the result of `_run_annual_water_factors`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
annual_water_factors : list[float]
    A list of annual water factors for each year in the inventory, dimensionless, between `0.31935` and `2.25`.
"""


Tier2SocResult = NamedTuple(
    "Tier2SocResult",
    [
        ("timestamps", list[float]),
        ("active_pool_soc_stocks", list[float]),
        ("slow_pool_soc_stocks", list[float]),
        ("passive_pool_soc_stocks", list[float]),
    ]
)
"""
A named tuple to hold the result of `_run_soc_stocks`.

Attributes
----------
timestamps : list[int]
    A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
active_pool_soc_stocks : list[float]
    The active sub-pool SOC stock for each year in the inventory, kg C ha-1.
slow_pool_soc_stocks : list[float]
    The slow sub-pool SOC stock for each year in the inventory, kg C ha-1.
passive_pool_soc_stocks : list[float]
    The passive sub-pool SOC stock for each year in the inventory, kg C ha-1.
"""


# --- TIER 1 NAMED TUPLES FOR STOCK CHANGE FACTORS AND MODEL RESULTS ---


StockChangeFactors = NamedTuple("StockChangeFactors", [
    ("land_use_factor", float),
    ("management_factor", float),
    ("carbon_input_factor", float)
])
"""
A named tuple to hold the 3 stock change factors retrieved by the model for each year in the inventory.

Attributes
----------
land_use_factor : float
    The stock change factor for mineral soil organic C land-use systems or sub-systems for a particular land-use,
    dimensionless.
management_factor : float
    The stock change factor for mineral soil organic C for management regime, dimensionless.
carbon_input_factor : float
    The stock change factor for mineral soil organic C for the input of organic amendments, dimensionless.
"""


# --- SHARED TIER 1 & TIER 2 MAPPING DICTS ---


IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE = {
    IpccManagementCategory.FULL_TILLAGE: "Full tillage",
    IpccManagementCategory.REDUCED_TILLAGE: "Reduced tillage",
    IpccManagementCategory.NO_TILLAGE: "No tillage"
}
"""
A dictionary mapping IPCC management categories to corresponding tillage lookup values in the
`"IPCC_TILLAGE_MANAGEMENT_CATEGORY" column`.
"""


# --- TIER 1 MAPPING DICTS ---


IPCC_CATEGORY_TO_ECO_CLIMATE_ZONE_LOOKUP_COLUMN = {
    # IpccSoilCategory
    IpccSoilCategory.SANDY_SOILS: LOOKUPS["ecoClimateZone"][0],
    IpccSoilCategory.WETLAND_SOILS: LOOKUPS["ecoClimateZone"][1],
    IpccSoilCategory.VOLCANIC_SOILS: LOOKUPS["ecoClimateZone"][2],
    IpccSoilCategory.SPODIC_SOILS: LOOKUPS["ecoClimateZone"][3],
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: LOOKUPS["ecoClimateZone"][4],
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: LOOKUPS["ecoClimateZone"][5],
    # IpccLandUseCategory
    IpccLandUseCategory.GRASSLAND: LOOKUPS["ecoClimateZone"][6],
    IpccLandUseCategory.PERENNIAL_CROPS: LOOKUPS["ecoClimateZone"][7],
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: LOOKUPS["ecoClimateZone"][8],
    IpccLandUseCategory.ANNUAL_CROPS_WET: LOOKUPS["ecoClimateZone"][9],
    IpccLandUseCategory.ANNUAL_CROPS: LOOKUPS["ecoClimateZone"][10],
    IpccLandUseCategory.SET_ASIDE: LOOKUPS["ecoClimateZone"][11],
    # IpccManagementCategory
    IpccManagementCategory.SEVERELY_DEGRADED: LOOKUPS["ecoClimateZone"][12],
    IpccManagementCategory.IMPROVED_GRASSLAND: LOOKUPS["ecoClimateZone"][13],
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: LOOKUPS["ecoClimateZone"][14],
    IpccManagementCategory.NOMINALLY_MANAGED: LOOKUPS["ecoClimateZone"][15],
    IpccManagementCategory.FULL_TILLAGE: LOOKUPS["ecoClimateZone"][16],
    IpccManagementCategory.REDUCED_TILLAGE: LOOKUPS["ecoClimateZone"][17],
    IpccManagementCategory.NO_TILLAGE: LOOKUPS["ecoClimateZone"][18],
    # IpccCarbonInputCategory
    IpccCarbonInputCategory.GRASSLAND_HIGH: LOOKUPS["ecoClimateZone"][19],
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: LOOKUPS["ecoClimateZone"][20],
    IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE: LOOKUPS["ecoClimateZone"][21],
    IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE: LOOKUPS["ecoClimateZone"][22],
    IpccCarbonInputCategory.CROPLAND_MEDIUM: LOOKUPS["ecoClimateZone"][23],
    IpccCarbonInputCategory.CROPLAND_LOW: LOOKUPS["ecoClimateZone"][24]
}
"""
A dictionary mapping IPCC category enums to their corresponding eco-climate zone lookup columns.
"""


def _get_eco_climate_zone_lookup_column(
    ipcc_category: Union[
        IpccSoilCategory,
        IpccLandUseCategory,
        IpccManagementCategory,
        IpccCarbonInputCategory
    ]
) -> Optional[str]:
    """
    Retrieve the corresponding eco-climate zone lookup column for the given IPCC category.

    Parameters
    ----------
    ipcc_category : IpccSoilCategory | IpccLandUseCategory | IpccManagementCategory | IpccCarbonInputCategory
        The IPCC category for which the eco-climate zone lookup column is needed.

    Returns
    -------
    str | None
        The eco-climate zone lookup column associated with the provided
        IPCC category, or None if no mapping is found.
    """
    return IPCC_CATEGORY_TO_ECO_CLIMATE_ZONE_LOOKUP_COLUMN.get(ipcc_category, None)


IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE = {
    IpccSoilCategory.ORGANIC_SOILS: "Organic soils",
    IpccSoilCategory.SANDY_SOILS: "Sandy soils",
    IpccSoilCategory.WETLAND_SOILS: "Wetland soils",
    IpccSoilCategory.VOLCANIC_SOILS: "Volcanic soils",
    IpccSoilCategory.SPODIC_SOILS: "Spodic soils",
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: "High-activity clay soils",
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: "Low-activity clay soils",
}
"""
A dictionary mapping IPCC soil categories to corresponding soil type and USDA soil type lookup values in the
`"IPCC_SOIL_CATEGORY"` column.
"""

IPCC_LAND_USE_CATEGORY_TO_SITE_TYPE = {
    IpccLandUseCategory.GRASSLAND: SiteSiteType.PERMANENT_PASTURE.value,
    IpccLandUseCategory.PERENNIAL_CROPS: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.ANNUAL_CROPS_WET: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.ANNUAL_CROPS: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.SET_ASIDE: SiteSiteType.CROPLAND.value,
    IpccLandUseCategory.FOREST: SiteSiteType.FOREST.value,
    IpccLandUseCategory.NATIVE: SiteSiteType.OTHER_NATURAL_VEGETATION.value
}
"""
A dictionary mapping IPCC land use categories to corresponding site types.
"""

IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE = {
    IpccLandUseCategory.PERENNIAL_CROPS: "Perennial crops",
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: "Paddy rice cultivation",
    IpccLandUseCategory.ANNUAL_CROPS_WET: "Annual crops",
    IpccLandUseCategory.ANNUAL_CROPS: "Annual crops"
}
"""
A dictionary mapping IPCC land use categories to corresponding land cover lookup values in the
`"IPCC_LAND_USE_CATEGORY"` column.
"""

IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID = {
    IpccManagementCategory.SEVERELY_DEGRADED: "severelyDegradedPasture",
    IpccManagementCategory.IMPROVED_GRASSLAND: "improvedPasture",
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: "highIntensityGrazingPasture",
    IpccManagementCategory.NOMINALLY_MANAGED: "nominallyManagedPasture",
    IpccManagementCategory.OTHER: "nativePasture"
}
"""
A dictionary mapping IPCC management categories to corresponding grassland management term IDs from the land cover
glossary.
"""


# --- TIER 2 FUNCTIONS: ASSIGN TILLAGE CATEGORY TO CYCLES ---


def _check_zero_tillages(practices: list[dict]) -> bool:
    """
    Checks whether a list of `Practice`s nodes describe 0 total tillages, or not.

    Parameters
    ----------
    practices : list[dict]
        A list of Hestia `Practice` nodes, see: https://www.hestia.earth/schema/Practice.

    Returns
    -------
    bool
        Whether or not 0 tillages counted.
    """
    practice = find_term_match(practices, NUMBER_OF_TILLAGES_TERM_ID)
    nTillages = list_sum(practice.get("value", []))
    return nTillages <= 0


def _check_cycle_tillage_management_category(
    cycle: dict,
    key: IpccManagementCategory
) -> bool:
    """
    Checks whether a Hesita `Cycle` node meets the requirements of a specific tillage `IpccManagementCategory`.

    Parameters
    ----------
    cycle : dict
        A Hestia `Cycle` node, see: https://www.hestia.earth/schema/Cycle.
    key : IpccManagementCategory
        The `IpccManagementCategory` to match.

    Returns
    -------
    bool
        Whether or not the cycle meets the requirements for the category.
    """
    LOOKUP = LOOKUPS["tillage"]
    target_lookup_values = IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE.get(key, None)

    practices = cycle.get("practices", [])
    tillage_nodes = filter_list_term_type(
        practices, [TermTermType.TILLAGE]
    )

    return cumulative_nodes_lookup_match(
        tillage_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    ) and (
        key is not IpccManagementCategory.NO_TILLAGE
        or _check_zero_tillages(tillage_nodes)
    )


TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.FULL_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    ),
    IpccManagementCategory.REDUCED_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    ),
    IpccManagementCategory.NO_TILLAGE: (
        lambda cycles, key: any(
            _check_cycle_tillage_management_category(cycle, key) for cycle in cycles
        )
    )
}


def _assign_tier_2_ipcc_tillage_management_category(
    cycles: list[dict],
    default: IpccManagementCategory = IpccManagementCategory.OTHER
) -> IpccManagementCategory:
    """
    Assigns a tillage `IpccManagementCategory` to a list of Hestia `Cycle`s.

    Parameters
    ----------
    cycles : list[dict])
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
        IpccManagementCategory: The assigned tillage `IpccManagementCategory`.
    """
    return next(
        (
            key for key in TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE
            if TIER_2_TILLAGE_MANAGEMENT_CATEGORY_DECISION_TREE[key](cycles, key)
        ),
        default
    ) if len(cycles) > 0 else default


# --- TIER 2 FUNCTIONS: ANNUAL TEMPERATURE FACTOR FROM MONTHLY TEMPERATURE DATA ---


def _calc_temperature_factor(
    average_temperature: float,
    maximum_temperature: float = 45.0,
    optimum_temperature: float = 33.69,
) -> float:
    """
    Equation 5.0E, part 2. Calculate the temperature effect on decomposition in mineral soils for a single month using
    the Steady-State Method.

    If `average_temperature >= maximum_temperature` the function should always return 0.

    Parameters
    ----------
    average_temperature : float
        The average air temperature of a given month, degrees C.
    maximum_temperature : float
        The maximum air temperature for decomposition, degrees C, default value: `45.0`.
    optimum_temperature : float
        The optimum air temperature for decomposition, degrees C, default value: `33.69`.

    Returns
    -------
    float
        The air temperature effect on decomposition for a given month, dimensionless, between `0` and `1`.
    """
    prelim = (maximum_temperature - average_temperature) / (
        maximum_temperature - optimum_temperature
    )
    return 0 if average_temperature >= maximum_temperature else (
        pow(prelim, 0.2) * exp((0.2 / 2.63) * (1 - pow(prelim, 2.63)))
    )


def _calc_annual_temperature_factor(
    average_temperature_monthly: list[float],
    maximum_temperature: float = 45.0,
    optimum_temperature: float = 33.69,
) -> Union[float, None]:
    """
    Equation 5.0E, part 1. Calculate the average annual temperature effect on decomposition in mineral soils using the
    Steady-State Method.

    Parameters
    ----------
    average_temperature_monthly : list[float]
        A list of monthly average air temperatures in degrees C, must have a length of 12.

    Returns
    -------
    float | None
        Average annual temperature factor, dimensionless, between `0` and `1`, or `None` if the input list is empty.
    """
    return mean(
        list(
            _calc_temperature_factor(t, maximum_temperature, optimum_temperature)
            for t in average_temperature_monthly
        )
    ) if average_temperature_monthly else None


# --- TIER 2 FUNCTIONS: ANNUAL WATER FACTOR FROM MONTHLY PRECIPITATION, PET AND IRRIGATION DATA ---


def _calc_water_factor(
    precipitation: float,
    pet: float,
    is_irrigated: bool = False,
    water_factor_slope: float = 1.331,
) -> float:
    """
    Equation 5.0F, part 2. Calculate the water effect on decomposition in mineral soils for a single month using the
    Steady-State Method.

    If `is_irrigated == True` the function should always return `0.775`.

    Parameters
    ----------
    precipitation : float
        The sum total precipitation of a given month, mm.
    pet : float
        The sum total potential evapotranspiration in a given month, mm.
    is_irrigated : bool
        Whether or not irrigation has been used in a given month.
    water_factor_slope : float
        The slope for mappet term to estimate water factor, dimensionless, default value: `1.331`.

    Returns
    -------
    float
        The water effect on decomposition for a given month, dimensionless, between `0.2129` and `1.5`.
    """
    mappet = min(1.25, precipitation / pet)
    return 0.775 if is_irrigated else 0.2129 + (water_factor_slope * (mappet)) - (0.2413 * pow(mappet, 2))


def _calc_annual_water_factor(
    precipitation_monthly: list[float],
    pet_monthly: list[float],
    is_irrigated_monthly: Union[list[bool], None] = None,
    water_factor_slope: float = 1.331,
) -> Union[float, None]:
    """
    Equation 5.0F, part 1. Calculate the average annual water effect on decomposition in mineral soils using the
    Steady-State Method multiplied by a coefficient of `1.5`.

    Parameters
    ----------
    precipitation_monthly : list[float]
        A list of monthly sum total precipitation values in mm, must have a length of 12.
    pet_monthly : list[float])
        A list of monthly sum total potential evapotranspiration values in mm, must have a length of 12.
    is_irrigated_monthly : list[boolean] | None)
        A list of true/false values that describe whether irrigation has been used in each calendar month, must have a
        length of 12. If `None` is provided, a list of 12 `False` values is used.
    water_factor_slope : float
        The slope for mappet term to estimate water factor, dimensionless, default value: `1.331`.

    Returns
    -------
    float | None
        Average annual water factor multiplied by `1.5`, dimensionless, between `0.31935` and `2.25`,
        or `None` if any of the input lists are empty.
    """
    is_irrigated_monthly = (
        [False] * 12 if is_irrigated_monthly is None else is_irrigated_monthly
    )
    zipped = zip(precipitation_monthly, pet_monthly, is_irrigated_monthly)
    return 1.5 * mean(list(
        _calc_water_factor(precipitation, pet, is_irrigated, water_factor_slope)
        for precipitation, pet, is_irrigated in zipped
    )) if all([precipitation_monthly, pet_monthly]) else None


# --- TIER 2 FUNCTIONS: ANNUAL TOTAL ORGANIC C INPUT TO SOIL, N CONTENT AND LIGNIN CONTENT FROM CARBON SOURCES ---


def _calc_total_organic_carbon_input(
    carbon_sources: list[CarbonSource], default_carbon_content=0.42
) -> float:
    """
    Equation 5.0H part 1. Calculate the total organic carbon to a site from all carbon sources (above-ground and
    below-ground crop residues, organic amendments, etc.).

    Parameters
    ----------
    carbon_sources : list[CarbonSource])
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`.
    default_carbon_content : float
        The default carbon content of a carbon source, decimal proportion, kg C (kg d.m.)-1.

    Returns
    -------
    float
        The total mass of organic carbon inputted into the site, kg C ha-1.
    """
    return sum(c.mass * (c.carbon_content if c.carbon_content else default_carbon_content) for c in carbon_sources)


def _calc_average_nitrogen_content_of_organic_carbon_sources(
    carbon_sources: list[CarbonSource], default_nitrogen_content=0.0085
) -> float:
    """
    Calculate the average nitrogen content of the carbon inputs through a weighted mean.

    Parameters
    ----------
    carbon_sources : list[CarbonSource]
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`
    default_nitrogen_content : float
        The default nitrogen content of a carbon source, decimal proportion, kg N (kg d.m.)-1.

    Returns
    -------
    float
        The average nitrogen content of the carbon sources, decimal_proportion, kg N (kg d.m.)-1.
    """
    total_weight = sum(c.mass for c in carbon_sources)
    weighted_values = [
        c.mass * (c.nitrogen_content if c.nitrogen_content else default_nitrogen_content) for c in carbon_sources
    ]
    return sum(weighted_values) / total_weight if total_weight > 0 else default_nitrogen_content


def _calc_average_lignin_content_of_organic_carbon_sources(
    carbon_sources: list[dict[str, float]], default_lignin_content=0.073
) -> float:
    """
    Calculate the average lignin content of the carbon inputs through a weighted mean.

    Parameters
    ----------
    carbon_sources : list[CarbonSource]
        A list of carbon sources as named tuples with the format
        `(mass: float, carbon_content: float, nitrogen_content: float, lignin_content: float)`
    default_lignin_content : float
        The default lignin content of a carbon source, decimal proportion, kg lignin (kg d.m.)-1.

    Returns
    -------
    float
        The average lignin content of the carbon sources, decimal_proportion, kg lignin (kg d.m.)-1.
    """
    total_weight = sum(c.mass for c in carbon_sources)
    weighted_values = [
        c.mass * (c.lignin_content if c.lignin_content else default_lignin_content) for c in carbon_sources
    ]
    return sum(weighted_values) / total_weight if total_weight > 0 else default_lignin_content


# --- TIER 2 FUNCTIONS: ACTIVE SUB-POOL SOC STOCK ---


def _calc_beta(
    carbon_input: float,
    lignin_content: float = 0.073,
    nitrogen_content: float = 0.0083,
) -> float:
    """
    Equation 5.0G, part 2. Calculate the C input to the metabolic dead organic matter C component, kg C ha-1.

    See table 5.5b for default values for lignin content and nitrogen content.

    Parameters
    ----------
    carbon_input : float
        Total carbon input to the soil during an inventory year, kg C ha-1.
    lignin_content : float
        The average lignin content of carbon input sources, decimal proportion, default value: `0.073`.
    nitrogen_content : float
        The average nitrogen content of carbon sources, decimal proportion, default value: `0.0083`.

    Returns
    -------
    float
        The C input to the metabolic dead organic matter C component, kg C ha-1.
    """
    return carbon_input * (0.85 - 0.018 * (lignin_content / nitrogen_content))


def _get_f_2(
    tillage_management_category: IpccManagementCategory = IpccManagementCategory.OTHER,
    f_2_full_tillage: float = 0.455,
    f_2_reduced_tillage: float = 0.477,
    f_2_no_tillage: float = 0.5,
    f_2_unknown_tillage: float = 0.368,
) -> float:
    """
    Get the value of `f_2` (the stabilisation efficiencies for structural decay products entering the active pool)
    based on the tillage `IpccManagementCategory`.

    If tillage regime is unknown, `IpccManagementCategory.OTHER` should be assumed.

    Parameters
    ----------
    tillage_management_category : (IpccManagementCategory)
        The tillage category of the inventory year, default value: `IpccManagementCategory.OTHER`.
    f_2_full_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool under full tillage,
        decimal proportion, default value: `0.455`.
    f_2_reduced_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool under reduced tillage,
        decimal proportion, default value: `0.477`.
    f_2_no_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool under no tillage,
        decimal proportion, default value: `0.5`.
    f_2_unknown_tillage : float
        The stabilisation efficiencies for structural decay products entering the active pool if tillage is not known,
        decimal proportion, default value: `0.368`.

    Returns
    -------
        float: The stabilisation efficiencies for structural decay products entering the active pool,
        decimal proportion.
    """
    ipcc_tillage_management_category_to_f_2s = {
        IpccManagementCategory.FULL_TILLAGE: f_2_full_tillage,
        IpccManagementCategory.REDUCED_TILLAGE: f_2_reduced_tillage,
        IpccManagementCategory.NO_TILLAGE: f_2_no_tillage,
        IpccManagementCategory.OTHER: f_2_unknown_tillage
    }
    default = f_2_unknown_tillage

    return ipcc_tillage_management_category_to_f_2s.get(tillage_management_category, default)


def _calc_f_4(sand_content: float = 0.33, f_5: float = 0.0855) -> float:
    """
    Equation 5.0C, part 4. Calculate the value of the stabilisation efficiencies for active pool decay products
    entering the slow pool based on the sand content of the soil.

    Parameters
    ----------
    sand_content : float)
        The sand content of the soil, decimal proportion, default value: `0.33`.
    f_5 : float
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal_proportion,
        default value: `0.0855`.

    Returns
    -------
    float
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    """
    return 1 - f_5 - (0.17 + 0.68 * sand_content)


def _calc_alpha(
    carbon_input: float,
    f_2: float,
    f_4: float,
    lignin_content: float = 0.073,
    nitrogen_content: float = 0.0083,
    f_1: float = 0.378,
    f_3: float = 0.455,
    f_5: float = 0.0855,
    f_6: float = 0.0504,
    f_7: float = 0.42,
    f_8: float = 0.45,
) -> float:
    """
    Equation 5.0G, part 1. Calculate the C input to the active soil carbon sub-pool, kg C ha-1.

    See table 5.5b for default values for lignin content and nitrogen content.

    Parameters
    ----------
    carbon_input : float
        Total carbon input to the soil during an inventory year, kg C ha-1.
    f_2 : float
        The stabilisation efficiencies for structural decay products entering the active pool, decimal proportion.
    f_4 : float
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    lignin_content : float
        The average lignin content of carbon input sources, decimal proportion, default value: `0.073`.
    nitrogen_content : float
        The average nitrogen content of carbon input sources, decimal proportion, default value: `0.0083`.
    sand_content : float
        The sand content of the soil, decimal proportion, default value: `0.33`.
    f_1 : float
        The stabilisation efficiencies for metabolic decay products entering the active pool, decimal proportion,
        default value: `0.378`.
    f_3 : float
        The stabilisation efficiencies for structural decay products entering the slow pool, decimal proportion,
        default value: `0.455`.
    f_5 : float
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal proportion,
        default value: `0.0855`.
    f_6 : float
        The stabilisation efficiencies for slow pool decay products entering the passive pool, decimal proportion,
        default value: `0.0504`.
    f_7 : float
        The stabilisation efficiencies for slow pool decay products entering the active pool, decimal proportion,
        default value: `0.42`.
    f_8 : float
        The stabilisation efficiencies for passive pool decay products entering the active pool, decimal proportion,
        default value: `0.45`.

    Returns
    -------
    float
        The C input to the active soil carbon sub-pool, kg C ha-1.
    """
    beta = _calc_beta(
        carbon_input, lignin_content=lignin_content, nitrogen_content=nitrogen_content
    )

    x = beta * f_1
    y = (carbon_input * (1 - lignin_content) - beta) * f_2
    z = (carbon_input * lignin_content) * f_3 * (f_7 + (f_6 * f_8))
    d = 1 - (f_4 * f_7) - (f_5 * f_8) - (f_4 * f_6 * f_8)
    return (x + y + z) / d


def _get_tillage_factor(
    tillage_management_category: IpccManagementCategory = IpccManagementCategory.FULL_TILLAGE,
    tillage_factor_full_tillage: float = 3.036,
    tillage_factor_reduced_tillage: float = 2.075,
    tillage_factor_no_tillage: float = 1,
) -> float:
    """
    Calculate the tillage disturbance modifier on decay rate for active and slow sub-pools based on the tillage
    `IpccManagementCategory`.

    If tillage regime is unknown, `FULL_TILLAGE` should be assumed.

    Parameters
    ----------
    tillage_factor_full_tillage : float)
        The tillage disturbance modifier for decay rates under full tillage, dimensionless, default value: `3.036`.
    tillage_factor_reduced_tillage : float
        Tillage disturbance modifier for decay rates under reduced tillage, dimensionless, default value: `2.075`.
    tillage_factor_no_tillage : float
        Tillage disturbance modifier for decay rates under no tillage, dimensionless, default value: `1`.

    Returns
    -------
    float
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    """
    ipcc_tillage_management_category_to_tillage_factors = {
        IpccManagementCategory.FULL_TILLAGE: tillage_factor_full_tillage,
        IpccManagementCategory.REDUCED_TILLAGE: tillage_factor_reduced_tillage,
        IpccManagementCategory.NO_TILLAGE: tillage_factor_no_tillage,
    }
    default = tillage_factor_full_tillage

    return ipcc_tillage_management_category_to_tillage_factors.get(
        tillage_management_category, default
    )


def _calc_active_pool_decay_rate(
    annual_temperature_factor: float,
    annual_water_factor: float,
    tillage_factor: float,
    sand_content: float = 0.33,
    active_decay_factor: float = 7.4,
) -> float:
    """
    Equation 5.0B, part 3. Calculate the decay rate for the active SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    annual_temperature_factor : float
        Average annual temperature factor, dimensionless, between `0` and `1`.
    annual_water_factor : float
        Average annual water factor, dimensionless, between `0.31935` and `2.25`.
    tillage_factor : float
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    sand_content : float
        sand_content (float): The sand content of the soil, decimal proportion, default value: `0.33`.
    active_decay_factor : float
        decay rate constant under optimal conditions for decomposition of the active SOC subpool, year-1, default value:
        `7.4`.

    Returns
    -------
    float
        The decay rate for active SOC sub-pool, year-1.
    """
    sand_factor = 0.25 + (0.75 * sand_content)
    return (
        annual_temperature_factor
        * annual_water_factor
        * tillage_factor
        * sand_factor
        * active_decay_factor
    )


def _calc_active_pool_steady_state(
    alpha: float, active_pool_decay_rate: float
) -> float:
    """
    Equation 5.0B part 2. Calculate the steady state active sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    alpha : float
        The C input to the active soil carbon sub-pool, kg C ha-1.
    active_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.

    Returns
    -------
    float
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1
    """
    return alpha / active_pool_decay_rate


# --- TIER 2 FUNCTIONS: SLOW SUB-POOL SOC STOCK ---


def _calc_slow_pool_decay_rate(
    annual_temperature_factor: float,
    annual_water_factor: float,
    tillage_factor: float,
    slow_decay_factor: float = 0.209,
) -> float:
    """
    Equation 5.0C, part 3. Calculate the decay rate for the slow SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    annual_temperature_factor : float
        Average annual temperature factor, dimensionless, between `0` and `1`.
    annual_water_factor : float
        Average annual water factor, dimensionless, between `0.31935` and `2.25`.
    tillage_factor : float
        The tillage disturbance modifier on decay rate for active and slow sub-pools, dimensionless.
    slow_decay_factor : float)
        The decay rate constant under optimal conditions for decomposition of the slow SOC subpool, year-1,
        default value: `0.209`.

    Returns
    -------
    float
        The decay rate for slow SOC sub-pool, year-1.
    """
    return (
        annual_temperature_factor
        * annual_water_factor
        * tillage_factor
        * slow_decay_factor
    )


def _calc_slow_pool_steady_state(
    carbon_input: float,
    f_4: float,
    active_pool_steady_state: float,
    active_pool_decay_rate: float,
    slow_pool_decay_rate: float,
    lignin_content: float = 0.073,
    f_3: float = 0.455,
) -> float:
    """
    Equation 5.0C, part 2. Calculate the steady state slow sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    carbon_input : float
        Total carbon input to the soil during an inventory year, kg C ha-1.
    f_4 : float
        The stabilisation efficiencies for active pool decay products entering the slow pool, decimal proportion.
    active_pool_steady_state : float
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1
    active_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.
    slow_pool_decay_rate : float
        Decay rate for slow SOC sub-pool, year-1.
    lignin_content : float
        The average lignin content of carbon input sources, decimal proportion, default value: `0.073`.
    f_3 : float
        The stabilisation efficiencies for structural decay products entering the slow pool, decimal proportion,
        default value: `0.455`.

    Returns
    -------
    float
        The steady state slow sub-pool SOC stock given conditions in year y, kg C ha-1
    """
    x = carbon_input * lignin_content * f_3
    y = active_pool_steady_state * active_pool_decay_rate * f_4
    return (x + y) / slow_pool_decay_rate


# --- TIER 2 FUNCTIONS: PASSIVE SUB-POOL SOC STOCK ---


def _calc_passive_pool_decay_rate(
    annual_temperature_factor: float,
    annual_water_factor: float,
    passive_decay_factor: float = 0.00689,
) -> float:
    """
    Equation 5.0D, part 3. Calculate the decay rate for the passive SOC sub-pool given conditions in an inventory year.

    Parameters
    ----------
    annual_temperature_factor : float
        Average annual temperature factor, dimensionless, between `0` and `1`.
    annual_water_factor : float
        Average annual water factor, dimensionless, between `0.31935` and `2.25`.
    passive_decay_factor : float
        decay rate constant under optimal conditions for decomposition of the passive SOC subpool, year-1,
        default value: `0.00689`.

    Returns
    -------
    float
        The decay rate for passive SOC sub-pool, year-1.
    """
    return annual_temperature_factor * annual_water_factor * passive_decay_factor


def _calc_passive_pool_steady_state(
    active_pool_steady_state: float,
    slow_pool_steady_state: float,
    active_pool_decay_rate: float,
    slow_pool_decay_rate: float,
    passive_pool_decay_rate: float,
    f_5: float = 0.0855,
    f_6: float = 0.0504,
) -> float:
    """
    Equation 5.0D, part 2. Calculate the steady state passive sub-pool SOC stock given conditions in an inventory year.

    Parameters
    ----------
    active_pool_steady_state : float
        The steady state active sub-pool SOC stock given conditions in year y, kg C ha-1.
    slow_pool_steady_state : float
        The steady state slow sub-pool SOC stock given conditions in year y, kg C ha-1.
    active_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.
    slow_pool_decay_rate : float
        Decay rate for slow SOC sub-pool, year-1.
    passive_pool_decay_rate : float
        Decay rate for passive SOC sub-pool, year-1.
    f_5 : float
        The stabilisation efficiencies for active pool decay products entering the passive pool, decimal proportion,
        default value: `0.0855`.
    f_6 : float
        The stabilisation efficiencies for slow pool decay products entering the passive pool, decimal proportion,
        default value: `0.0504`.

    Returns
    -------
    float
        The steady state passive sub-pool SOC stock given conditions in year y, kg C ha-1.
    """
    x = active_pool_steady_state * active_pool_decay_rate * f_5
    y = slow_pool_steady_state * slow_pool_decay_rate * f_6
    return (x + y) / passive_pool_decay_rate


# --- TIER 2 FUNCTIONS:  GENERIC SUB-POOL SOC STOCK ---


def _calc_sub_pool_soc_stock(
    sub_pool_steady_state: (float),
    previous_sub_pool_soc_stock: (float),
    sub_pool_decay_rate: (float),
    timestep: int = 1,
) -> float:
    """
    Generalised from equations 5.0B, 5.0C and 5.0D, part 1. Calculate the sub-pool SOC stock in year y, kg C ha-1.

    If `sub_pool_decay_rate > 1` then set its value to `1` for this calculation.

    Parameters
    ----------
    sub_pool_steady_state : float
        The steady state sub-pool SOC stock given conditions in year y, kg C ha-1.
    previous_sub_pool_soc_stock : float
        The sub-pool SOC stock in year y-timestep (by default one year ago), kg C ha-1.
    sub_pool_decay_rate : float
        Decay rate for active SOC sub-pool, year-1.
    timestep : int
        The number of years between current and previous inventory year.

    Returns
    -------
    float
        The sub-pool SOC stock in year y, kg C ha-1.
    """
    sub_pool_decay_rate = min(1, sub_pool_decay_rate)
    return (
        previous_sub_pool_soc_stock
        + (sub_pool_steady_state - previous_sub_pool_soc_stock)
        * timestep
        * sub_pool_decay_rate
    )


# --- TIER 2 FUNCTIONS: SOC STOCK CHANGE ---


def _calc_tier_2_soc_stock(
    active_pool_soc_stock: float,
    slow_pool_soc_stock: float,
    passive_pool_soc_stock: float,
) -> float:
    """
    Equation 5.0A, part 3. Calculate the total SOC stock for a site by summing its active, slow and passive SOC stock
    sub-pools. This is the value we need for our `organicCarbonPerHa` measurement.

    Parameters
    ----------
    actve_pool_soc_stock : float
        The active sub-pool SOC stock in year y, kg C ha-1.
    slow_pool_soc_stock : float
        The slow sub-pool SOC stock in year y, kg C ha-1.
    passive_pool_soc_stock : float
        The passive sub-pool SOC stock in year y, kg C ha-1.

    Returns
    -------
    float
        The SOC stock of a site in year y, kg C ha-1.
    """
    return active_pool_soc_stock + slow_pool_soc_stock + passive_pool_soc_stock


# --- TIER 2 SUB-MODEL: RUN ACTIVE, SLOW AND PASSIVE SOC STOCKS ---


def timeseries_to_inventory(timeseries_data: list[float], run_in_period: int):
    """
    Convert annual data to inventory data by averaging the values for the run-in period.

    Parameters
    ----------
    timeseries_data : list[float]
        The timeseries data to be reformatted.
    run_in_period : int
        The length of the run-in in years.

    Returns
    -------
    list[float]
        The inventory formatted data, where value 0 is the average of the run-in values.
    """
    return [mean(timeseries_data[0:run_in_period])] + timeseries_data[run_in_period:]


def _run_soc_stocks(
    timestamps: list[int],
    annual_temperature_factors: list[float],
    annual_water_factors: list[float],
    annual_organic_carbon_inputs: list[float],
    annual_n_contents: list[float],
    annual_lignin_contents: list[float],
    annual_tillage_categories: Union[list[IpccManagementCategory], None] = None,
    sand_content: float = 0.33,
    run_in_period: int = 5,
    params: Union[dict[str, float], None] = None,
) -> Tier2SocResult:
    """
    Run the IPCC Tier 2 SOC model with precomputed `annual_temperature_factors`, `annual_water_factors`,
    `annual_organic_carbon_inputs`, `annual_n_contents`, `annual_lignin_contents`.

    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
    annual_temperature_factors : list[float]
        A list of temperature factors for each year in the inventory, dimensionless (see Equation 5.0E).
    annual_water_factors : list[float]
        A list of water factors for each year in the inventory, dimensionless (see Equation 5.0F).
    annual_organic_carbon_inputs : list[float]
        A list of organic carbon inputs to the soil for each year in the inventory, kg C ha-1 year-1 (see Equation
        5.0H).
    annual_n_contents : list[float]
        A list of the average nitrogen contents of the organic carbon sources for each year in the inventory, decimal
        proportion.
    annual_lignin_contents : list[float]
        A list of the average lignin contents of the organic carbon sources for each year in the inventory, decimal
        proportion.
    annual_tillage_categories : list[IpccManagementCategory] | None
        A list of the site"s `IpccManagementCategory`s for each year in the inventory.
    sand_content : float
        The sand content of the site, decimal proportion, default value: `0.33`.
    run_in_period : int
        The length of the run-in period in years, must be greater than or equal to 1, default value: `5`.
    params : dict[str: float] | None
        Overrides for the model parameters. If `None` only default parameters will be used.

    Returns
    -------
    Tier2SocResult
        Returns an annual inventory of organicCarbonPerHa data in the format
        `(timestamps: list[int], organicCarbonPerHa_values: list[float], active_pool_soc_stocks: list[float],
        slow_pool_soc_stocks: list[float], passive_pool_soc_stocks: list[float])`
    """

    # --- MERGE ANY USER-SET PARAMETERS WITH THE IPCC DEFAULTS ---

    params = DEFAULT_PARAMS | (params or {})

    # --- GET F4 ---

    f_4 = _calc_f_4(sand_content, f_5=params.get("f_5"))

    # --- GET ANNUAL DATA ---

    annual_f_2s = [
        _get_f_2(
            till,
            f_2_full_tillage=params.get("f_2_full_tillage"),
            f_2_reduced_tillage=params.get("f_2_reduced_tillage"),
            f_2_no_tillage=params.get("f_2_no_tillage"),
            f_2_unknown_tillage=params.get("f_2_unknown_tillage"),
        )
        for till in annual_tillage_categories
    ]

    annual_tillage_factors = [
        _get_tillage_factor(
            till,
            tillage_factor_full_tillage=params.get("tillage_factor_full_tillage"),
            tillage_factor_reduced_tillage=params.get("tillage_factor_reduced_tillage"),
            tillage_factor_no_tillage=params.get("tillage_factor_no_tillage"),
        )
        for till in annual_tillage_categories
    ]

    # --- SPLIT ANNUAL DATA INTO RUN-IN AND INVENTORY PERIODS ---

    inventory_temperature_factors = timeseries_to_inventory(annual_temperature_factors, run_in_period)
    inventory_water_factors = timeseries_to_inventory(annual_water_factors, run_in_period)
    inventory_carbon_inputs = timeseries_to_inventory(annual_organic_carbon_inputs, run_in_period)
    inventory_n_contents = timeseries_to_inventory(annual_n_contents, run_in_period)
    inventory_lignin_contents = timeseries_to_inventory(annual_lignin_contents, run_in_period)
    inventory_f_2s = timeseries_to_inventory(annual_f_2s, run_in_period)
    inventory_tillage_factors = timeseries_to_inventory(annual_tillage_factors, run_in_period)

    # The last year of the run-in should be the first year of the inventory
    inventory_timestamps = timestamps[run_in_period - 1:]

    # --- CALCULATE THE ACTIVE ACTIVE POOL STEADY STATES ---

    inventory_alphas = [
        _calc_alpha(
            carbon_input,
            f_2,
            f_4,
            lignin_content,
            nitrogen_content,
            f_1=params.get("f_1"),
            f_3=params.get("f_3"),
            f_5=params.get("f_5"),
            f_6=params.get("f_6"),
            f_7=params.get("f_7"),
            f_8=params.get("f_8"),
        )
        for carbon_input, f_2, lignin_content, nitrogen_content in zip(
            inventory_carbon_inputs,
            inventory_f_2s,
            inventory_lignin_contents,
            inventory_n_contents,
        )
    ]

    inventory_active_pool_decay_rates = [
        _calc_active_pool_decay_rate(
            temp_fac,
            water_fac,
            till_fac,
            sand_content,
            active_decay_factor=params.get("active_decay_factor"),
        )
        for temp_fac, water_fac, till_fac in zip(
            inventory_temperature_factors,
            inventory_water_factors,
            inventory_tillage_factors,
        )
    ]

    inventory_active_pool_steady_states = [
        _calc_active_pool_steady_state(alpha, active_decay_rate)
        for alpha, active_decay_rate in zip(
            inventory_alphas, inventory_active_pool_decay_rates
        )
    ]

    # --- CALCULATE THE SLOW POOL STEADY STATES ---

    inventory_slow_pool_decay_rates = [
        _calc_slow_pool_decay_rate(
            temp_fac, water_fac, till_fac, slow_decay_factor=params.get("slow_decay_factor")
        )
        for temp_fac, water_fac, till_fac in zip(
            inventory_temperature_factors,
            inventory_water_factors,
            inventory_tillage_factors,
        )
    ]

    inventory_slow_pool_steady_states = [
        _calc_slow_pool_steady_state(
            carbon_input,
            f_4,
            active_steady_state,
            active_decay_rate,
            slow_decay_rate,
            lignin_content,
            f_3=params.get("f_3"),
        )
        for carbon_input, active_steady_state, active_decay_rate, slow_decay_rate, lignin_content in zip(
            inventory_carbon_inputs,
            inventory_active_pool_steady_states,
            inventory_active_pool_decay_rates,
            inventory_slow_pool_decay_rates,
            inventory_lignin_contents,
        )
    ]

    # --- CALCULATE THE PASSIVE POOL STEADY STATES ---

    inventory_passive_pool_decay_rates = [
        _calc_passive_pool_decay_rate(
            temp_fac, water_fac, passive_decay_factor=params.get("passive_decay_factor")
        )
        for temp_fac, water_fac in zip(
            inventory_temperature_factors, inventory_water_factors
        )
    ]

    inventory_passive_pool_steady_states = [
        _calc_passive_pool_steady_state(
            active_steady_state,
            slow_steady_state,
            active_decay_rate,
            slow_decay_rate,
            passive_decay_rate,
            f_5=params.get("f_5"),
            f_6=params.get("f_6"),
        )
        for active_steady_state, slow_steady_state, active_decay_rate, slow_decay_rate, passive_decay_rate in zip(
            inventory_active_pool_steady_states,
            inventory_slow_pool_steady_states,
            inventory_active_pool_decay_rates,
            inventory_slow_pool_decay_rates,
            inventory_passive_pool_decay_rates,
        )
    ]

    # --- CALCULATE THE ACTIVE, SLOW AND PASSIVE SOC STOCKS ---

    inventory_active_pool_soc_stocks = inventory_active_pool_steady_states[:1]
    inventory_slow_pool_soc_stocks = inventory_slow_pool_steady_states[:1]
    inventory_passive_pool_soc_stocks = inventory_passive_pool_steady_states[:1]

    for index in range(1, len(inventory_timestamps), 1):
        inventory_active_pool_soc_stocks.insert(
            index,
            _calc_sub_pool_soc_stock(
                inventory_active_pool_steady_states[index],
                inventory_active_pool_soc_stocks[index - 1],
                inventory_active_pool_decay_rates[index],
            ),
        )
        inventory_slow_pool_soc_stocks.insert(
            index,
            _calc_sub_pool_soc_stock(
                inventory_slow_pool_steady_states[index],
                inventory_slow_pool_soc_stocks[index - 1],
                inventory_slow_pool_decay_rates[index],
            ),
        )
        inventory_passive_pool_soc_stocks.insert(
            index,
            _calc_sub_pool_soc_stock(
                inventory_passive_pool_steady_states[index],
                inventory_passive_pool_soc_stocks[index - 1],
                inventory_passive_pool_decay_rates[index],
            ),
        )

    # --- RETURN THE RESULT ---

    return Tier2SocResult(
        timestamps=inventory_timestamps,
        active_pool_soc_stocks=inventory_active_pool_soc_stocks,
        slow_pool_soc_stocks=inventory_slow_pool_soc_stocks,
        passive_pool_soc_stocks=inventory_passive_pool_soc_stocks,
    )


# --- TIER 2 SUB-MODEL: ANNUAL TEMPERATURE FACTORS ---


def _check_12_months(inner_dict: dict, keys: set[Any]):
    """
    Checks whether an inner dict has 12 months of data for each of the required inner keys.

    Parameters
    ----------
    inner_dict : dict
        A dictionary representing one year in a timeseries for the Tier 2 model.
    keys : set[Any]
        The required inner keys.

    Returns
    -------
    bool
        Whether or not the inner dict satisfies the conditions.
    """
    return all(
        len(inner_dict.get(key, [])) == 12 for key in keys
    )


# --- SUB-MODEL ANNUAL TEMPERATURE FACTORS ---


def _run_annual_temperature_factors(
    timestamps: list[int],
    temperatures: list[list[float]],
    maximum_temperature: float = 45.0,
    optimum_temperature: float = 33.69,
):
    """
    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996]`) for each year in the inventory.
    temperatures : list[list[float]])
        A list of monthly average temperatures for each year in the inventory
        (e.g. `[[10,10,10,20,25,15,15,10,10,10,5,5]]`).
    maximum_temperature : float
        The maximum air temperature for decomposition, degrees C, default value: `45.0`.
    optimum_temperature : float
        The optimum air temperature for decomposition, degrees C, default value: `33.69`.

    Returns
    -------
    TemperatureFactorResult
        An inventory of annual temperature factor data as a named tuple with the format
        `(timestamps: list[int], annual_temperature_factors: list[float])`.
    """
    return TemperatureFactorResult(
        timestamps=timestamps,
        annual_temperature_factors=[
            _calc_annual_temperature_factor(
                monthly_temperatures, maximum_temperature, optimum_temperature
            )
            for monthly_temperatures in temperatures
        ],
    )


# --- TIER 2 SUB-MODEL: ANNUAL WATER FACTORS ---


def _run_annual_water_factors(
    timestamps: list[int],
    precipitations: list[list[float]],
    pets: list[list[float]],
    is_irrigateds: Union[list[list[bool]], None] = None,
    water_factor_slope: float = 1.331,
):
    """
    Parameters
    ----------
    timestamps : list[int]
        A list of integer timestamps (e.g. `[1995, 1996...]`) for each year in the inventory.
    precipitations : list[list[float]]
        A list of monthly sum precipitations for each year in the inventory
        (e.g. `[[10,10,10,20,25,15,15,10,10,10,5,5]]`).
    pets list[list[float]]
        A list of monthly sum potential evapotransiprations for each year in the inventory.
    is_irrigateds list[list[bool]] | None
        A list of monthly booleans that describe whether irrigation is used in a particular calendar month for each
        year in the inventory.
    water_factor_slope : float
        The slope for mappet term to estimate water factor, dimensionless, default value: `1.331`.

    Returns
    -------
    WaterFactorResult
        An inventory of annual water factor data as a named tuple with the format
        `(timestamps: list[int], annual_water_factors: list[float])`.
    """
    is_irrigateds = [None] * len(timestamps) if is_irrigateds is None else is_irrigateds
    return WaterFactorResult(
        timestamps=timestamps,
        annual_water_factors=[
            _calc_annual_water_factor(
                monthly_precipitations,
                monthly_pets,
                monthly_is_irrigateds,
                water_factor_slope,
            )
            for monthly_precipitations, monthly_pets, monthly_is_irrigateds in zip(
                precipitations, pets, is_irrigateds
            )
        ],
    )


# --- TIER 2 SUB-MODEL: ANNUAL ORGANIC CARBON INPUTS ---


def _iterate_carbon_source(node: dict) -> Union[CarbonSource, None]:
    """
    Validates whether a node is a valid carbon source and returns
    a `CarbonSource` named tuple if yes.

    Parameters
    ----------
    node : dict
        A Hestia `Product` or `Input` node, see: https://www.hestia.earth/schema/Product
        or https://www.hestia.earth/schema/Input.

    Returns
    -------
    CarbonSource | None
        A `CarbonSource` named tuple if the node is a carbon source with the required properties, else `None`.
    """
    term = node.get("term", {})
    mass = list_sum(node.get("value", []))
    carbon_content, nitrogen_content, lignin_content = (
        get_node_property(node, term_id, False).get("value", 0)/100 for term_id in CROP_RESIDUE_PROPERTY_TERM_IDS
    )

    should_run = all([
        any([
            term.get("@id", None) in get_crop_residue_incorporated_or_left_on_field_terms(),
            term.get("termType") in CARBON_SOURCE_TERM_TYPES
        ]),
        mass > 0,
        0 < carbon_content <= 1,
        0 < nitrogen_content <= 1,
        0 < lignin_content <= 1
    ])

    return (
        CarbonSource(
            mass, carbon_content, nitrogen_content, lignin_content
        ) if should_run else None
    )


def _get_carbon_sources_from_cycles(cycles: dict) -> list[CarbonSource]:
    """
    Retrieves and formats all of the valid carbon sources from a list of cycles.

    Carbon sources can be either a Hestia `Product` node (e.g. crop residue) or `Input` node (e.g. organic amendment).

    Parameters
    ----------
    cycles : list[dict]
        A list of Hestia `Cycle` nodes, see: https://www.hestia.earth/schema/Cycle.

    Returns
    -------
    list[CarbonSource]
        A formatted list of `CarbonSource`s for the inputted `Cycle`s.
    """
    inputs_and_products = non_empty_list(flatten(
        [cycle.get("inputs", []) + cycle.get("products", []) for cycle in cycles]
    ))

    return non_empty_list([_iterate_carbon_source(node) for node in inputs_and_products])


# --- TIER 2 SOC MODEL ---


def _run_tier_2(
    inventory: dict[int: dict[_InventoryKey: any]],
    *,
    run_in_period: int = 5,
    run_with_irrigation: bool = True,
    sand_content: float = 0.33,
    params: Union[dict[str, float], None] = None,
    **_
) -> list[dict]:
    """
    Run the IPCC Tier 2 SOC model on a time series of annual data about a site and the mangagement activities taking
    place on it. To avoid any errors, the `inventory` parameter must be pre-validated by the `should_run` function.

    The inventory should be in the following shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN_TIER_2: bool,
            _InventoryKey.TEMP_MONTHLY: list[float],
            _InventoryKey.PRECIP_MONTHLY: list[float],
            _InventoryKey.PET_MONTHLY: list[float],
            _InventoryKey.IRRIGATED_MONTHLY: list[bool]
            _InventoryKey.CARBON_INPUT: float,
            _InventoryKey.N_CONTENT: float,
            _InventoryKey.TILLAGE_CATEGORY: IpccManagementCategory,
            _InventoryKey.SAND_CONTENT: float
        },
        ...
    }
    ```

    TODO: interpolate between `sandContent` measurements for different years of the inventory

    Parameters
    ----------
    inventory : dict
        The inventory built by the `_should_run` function.
    run_in_period : int, optional
        The length of the run-in period in years, must be greater than or equal to 1, default value: `5`.
    run_with_irrigation : bool, optional
        `True` if the model should run while taking into account irrigation, `False` if not.
    params : dict | None, optional
        Overrides for the model parameters. If `None` only default parameters will be used.

    Returns
    -------
    list[dict]
        A list of Hestia `Measurement` nodes containing the calculated SOC stocks and additional relevant data.
    """
    valid_inventory = {
        year: group for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN_TIER_2)
    }

    timestamps = [year for year in valid_inventory.keys()]

    annual_temperature_monthlys = [group[_InventoryKey.TEMP_MONTHLY] for group in valid_inventory.values()]
    annual_precipitation_monthlys = [group[_InventoryKey.PRECIP_MONTHLY] for group in valid_inventory.values()]
    annual_pet_monthlys = [group[_InventoryKey.PET_MONTHLY] for group in valid_inventory.values()]

    annual_carbon_inputs = [group[_InventoryKey.CARBON_INPUT] for group in valid_inventory.values()]
    annual_n_contents = [group[_InventoryKey.N_CONTENT] for group in valid_inventory.values()]
    annual_lignin_contents = [group[_InventoryKey.LIGNIN_CONTENT] for group in valid_inventory.values()]
    annual_tillage_categories = [group[_InventoryKey.TILLAGE_CATEGORY] for group in valid_inventory.values()]
    annual_irrigated_monthly = (
        [group[_InventoryKey.IRRIGATED_MONTHLY] for group in valid_inventory.values()] if run_with_irrigation else None
    )

    sand_content = next(
        group[_InventoryKey.SAND_CONTENT]/100 for group in valid_inventory.values()
        if _InventoryKey.SAND_CONTENT in group
    )

    # --- MERGE ANY USER-SET PARAMETERS WITH THE IPCC DEFAULTS ---

    params = DEFAULT_PARAMS | (params or {})

    # --- COMPUTE FACTORS AND CARBON INPUTS ---

    _, annual_temperature_factors = _run_annual_temperature_factors(
        timestamps,
        annual_temperature_monthlys,
        maximum_temperature=params.get("maximum_temperature"),
        optimum_temperature=params.get("optimum_temperature")
    )

    _, annual_water_factors = _run_annual_water_factors(
        timestamps,
        annual_precipitation_monthlys,
        annual_pet_monthlys,
        annual_irrigated_monthly,
        water_factor_slope=params.get("water_factor_slope")
    )

    # --- RUN THE MODEL ---

    result = _run_soc_stocks(
        timestamps=timestamps,
        annual_temperature_factors=annual_temperature_factors,
        annual_water_factors=annual_water_factors,
        annual_organic_carbon_inputs=annual_carbon_inputs,
        annual_n_contents=annual_n_contents,
        annual_lignin_contents=annual_lignin_contents,
        annual_tillage_categories=annual_tillage_categories,
        sand_content=sand_content,
        run_in_period=run_in_period,
        params=params
    )

    values = [
        _calc_tier_2_soc_stock(
            active,
            slow,
            passive
        ) for active, slow, passive in zip(
            result.active_pool_soc_stocks,
            result.slow_pool_soc_stocks,
            result.passive_pool_soc_stocks
        )
    ]

    # --- RETURN MEASUREMENT NODES ---

    return [
        _measurement(
            year,
            value,
            MeasurementMethodClassification.TIER_2_MODEL.value
        ) for year, value in zip(
            result.timestamps,
            values
        )
    ]


# --- TIER 1 FUNCTIONS ---


def _retrieve_soc_ref(
    eco_climate_zone: int,
    ipcc_soil_category: IpccSoilCategory
) -> float:
    """
    Retrieve the soil organic carbon (SOC) reference value for a given combination of eco-climate zone
    and IPCC soil category.

    See [IPCC (2019) Vol. 4, Ch. 2, Table 2.3](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html)
    for more information.

    Parameters
    ----------
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    ipcc_soil_category : IpccSoilCategory
        The IPCC soil category of the site.

    Returns
    -------
    float
        The reference condition soil organic carbon (SOC) stock in the 0-30cm depth interval, kg C ha-1.
    """
    col_name = _get_eco_climate_zone_lookup_column(ipcc_soil_category)
    return get_ecoClimateZone_lookup_value(eco_climate_zone, col_name)


def _retrieve_soc_stock_factors(
    eco_climate_zone: int,
    ipcc_land_use_category: IpccLandUseCategory,
    ipcc_management_category: IpccManagementCategory,
    ipcc_carbon_input_category: IpccCarbonInputCategory
) -> StockChangeFactors:
    """
    Retrieve the stock change factors for soil organic carbon (SOC) based on a given combination of land use,
    management and carbon input.

    Parameters
    ----------
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    ipcc_land_use_category : IpccLandUseCategory
        The IPCC land use category for the inventory year.
    ipcc_management_category : IpccManagementCategory
        The IPCC land use category for the inventory year.
    ipcc_carbon_input_category : IpccCarbonInputCategory
        The IPCC land use category for the inventory year.

    Returns
    -------
    StockChangeFactors
        A named tuple containing the retrieved stock change factors for SOC.
    """
    DEFAULT_FACTOR = 1

    EXCLUDED_LAND_USE_CATEGORIES = {
        IpccLandUseCategory.FOREST,
        IpccLandUseCategory.NATIVE,
        IpccLandUseCategory.OTHER
    }

    EXCLUDED_MANAGEMENT_CATEGORIES = {
        IpccManagementCategory.OTHER
    }

    EXCLUDED_CARBON_INPUT_CATEGORIES = {
        IpccCarbonInputCategory.OTHER
    }

    def get_factor(category, exclude_set):
        return (
            DEFAULT_FACTOR if category in exclude_set
            else get_ecoClimateZone_lookup_value(
                eco_climate_zone, _get_eco_climate_zone_lookup_column(category)
            )
        )

    land_use_factor = get_factor(ipcc_land_use_category, EXCLUDED_LAND_USE_CATEGORIES)
    management_factor = get_factor(ipcc_management_category, EXCLUDED_MANAGEMENT_CATEGORIES)
    carbon_input_factor = get_factor(ipcc_carbon_input_category, EXCLUDED_CARBON_INPUT_CATEGORIES)

    return StockChangeFactors(land_use_factor, management_factor, carbon_input_factor)


def _calc_soc_equilibrium(
    soc_ref: float,
    land_use_factor: float,
    management_factor: float,
    carbon_input_factor: float
) -> float:
    """
    Calculate the soil organic carbon (SOC) equilibrium based on reference SOC and factors.

    In the tier 1 model, SOC equilibriums are considered to be reached after 20 years of consistant land use,
    management and carbon input.

    Parameters
    ----------
    soc_ref : float
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.
    land_use_factor : float
        The stock change factor for mineral soil organic C land-use systems or sub-systems
        for a particular land-use, dimensionless.
    management_factor : float
        The stock change factor for mineral soil organic C for management regime, dimensionless.
    carbon_input_factor : float
        The stock change factor for mineral soil organic C for the input of organic amendments, dimensionless.

    Returns
    -------
    float
        The calculated SOC equilibrium, kg C ha-1.
    """
    return soc_ref * land_use_factor * management_factor * carbon_input_factor


def _calc_regime_start_index(
    current_index: int, soc_equilibriums: list[float], default: Optional[int] = None
) -> Optional[int]:
    """
    Calculate the start index of the SOC regime based on the current index and equilibriums.

    Parameters
    ----------
    current_index : int
        The current index in the SOC equilibriums list.
    soc_equilibriums : list[float]
        List of SOC equilibriums.
    default : Any | None
        Default value to return if no suitable start index is found, by default `None`.

    Returns
    -------
    int | None
        The calculated start index for the SOC regime.
    """

    def calc_forward_index(sliced_reverse_index: int) -> int:
        """
        Calculate the forward index based on a sliced reverse index.
        """
        return current_index - sliced_reverse_index - 1

    current_soc_equilibrium = soc_equilibriums[current_index]
    sliced_reversed_soc_equilibriums = reversed(soc_equilibriums[0:current_index])

    return next(
        (
            calc_forward_index(sliced_reverse_index) for sliced_reverse_index, prev_equilibrium
            in enumerate(sliced_reversed_soc_equilibriums)
            if not prev_equilibrium == current_soc_equilibrium
        ),
        default
    )


def _iterate_soc_equilibriums(
    timestamps: list[int], soc_equilibriums: list[float]
) -> tuple[list[int], list[float]]:
    """
    Iterate over SOC equilibriums, inserting timestamps and soc_equilibriums for any missing years where SOC would have
    reached equilibrium.

    Parameters
    ----------
    timestamps : list[int]
        List of timestamps for each year in the inventory.
    soc_equilibriums : list[float]
        List of SOC equilibriums for each year in the inventory.

    Returns
    -------
    tuple[list[int], list[float]]
        Updated `timestamps` and `soc_equilibriums`.
    """
    iterated_timestamps = list(timestamps)
    iterated_soc_equilibriums = list(soc_equilibriums)

    def calc_equilibrium_reached_timestamp(index: int) -> int:
        """
        Calculate the timestamp when SOC equilibrium is reached based on the current index.
        """
        regime_start_index = _calc_regime_start_index(index, soc_equilibriums)
        regime_start_timestamp = (
            timestamps[regime_start_index] if regime_start_index is not None
            else timestamps[0] - EQUILIBRIUM_TRANSITION_PERIOD
        )
        return regime_start_timestamp + EQUILIBRIUM_TRANSITION_PERIOD

    def is_missing_equilibrium_year(
        timestamp: int, equilibrium_reached_timestamp: int
    ) -> bool:
        """
        Check if the given timestamp is after equilibrium and the equilibrium year is missing.
        """
        return (
            timestamp > equilibrium_reached_timestamp
            and equilibrium_reached_timestamp not in iterated_timestamps
        )

    for index, (timestamp, soc_equilibrium) in enumerate(zip(timestamps, soc_equilibriums)):
        equilibrium_reached_timestamp = calc_equilibrium_reached_timestamp(index)

        if is_missing_equilibrium_year(timestamp, equilibrium_reached_timestamp):
            iterated_timestamps.insert(index, equilibrium_reached_timestamp)
            iterated_soc_equilibriums.insert(index, soc_equilibrium)

    return iterated_timestamps, iterated_soc_equilibriums


def _run_soc_equilibriums(
    timestamps: list[int],
    ipcc_land_use_categories: list[IpccLandUseCategory],
    ipcc_management_categories: list[IpccManagementCategory],
    ipcc_carbon_input_categories: list[IpccCarbonInputCategory],
    eco_climate_zone: int,
    soc_ref: float
) -> tuple[list[int], list[float]]:
    """
    Run the soil organic carbon (SOC) equilibriums calculation for each year in the inventory.

    Missing years where SOC equilibrium would be reached are inserted to allow for annual SOC change to be calculated
    correctly.

    Parameters
    ----------
    timestamps : list[int]
        A list of timestamps for each year in the inventory.
    ipcc_land_use_categories : list[IpccLandUseCategory]
        A list of IPCC land use categories for each year in the inventory.
    ipcc_management_categories : list[IpccManagementCategory]
        A list of IPCC management categories for each year in the inventory.
    ipcc_carbon_input_categories : list[IpccCarbonInputCategory]
        A list of IPCC carbon input categories for each year in the inventory.
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    soc_ref : float
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.

    Returns
    -------
    tuple[list[int], list[float]]
        `timestamps` and `soc_equilibriums` for each year in the inventory, including any missing years where SOC
        equilibrium would have been reached.
    """

    # Calculate SOC equilibriums for each year
    soc_equilibriums = [
        _calc_soc_equilibrium(
            soc_ref,
            *_retrieve_soc_stock_factors(
                eco_climate_zone,
                land_use_category,
                management_category,
                carbon_input_category
            )
        ) for land_use_category, management_category, carbon_input_category in zip(
            ipcc_land_use_categories,
            ipcc_management_categories,
            ipcc_carbon_input_categories
        )
    ]

    # Insert missing years where SOC equilibrium would have been reached
    iterated_timestamps, iterated_soc_equilibriums = (
        _iterate_soc_equilibriums(timestamps, soc_equilibriums)
    )

    return iterated_timestamps, iterated_soc_equilibriums


def _calc_tier_1_soc_stocks(
    timestamps: list[int],
    soc_equilibriums: list[float],
) -> list[float]:
    """
    Calculate soil organic carbon (SOC) stocks (kg C ha-1) in the 0-30cm depth interval for each year in the inventory.

    Parameters
    ----------
    timestamps : list[int]
        A list of timestamps for each year in the inventory.
    soc_equilibriums : list[float]
        A list of SOC equilibriums for each year in the inventory.

    Returns
    -------
    list[float]
        SOC stocks for each year in the inventory.
    """
    soc_stocks = [soc_equilibriums[0]]

    for index in range(1, len(soc_equilibriums)):

        timestamp = timestamps[index]
        soc_equilibrium = soc_equilibriums[index]

        regime_start_index = _calc_regime_start_index(index, soc_equilibriums)

        regime_start_timestamp = (
            timestamps[regime_start_index]
            if regime_start_index is not None
            else timestamps[0] - EQUILIBRIUM_TRANSITION_PERIOD
        )

        regime_start_soc_stock = soc_stocks[regime_start_index or 0]

        regime_duration = timestamp - regime_start_timestamp

        time_ratio = min(regime_duration / EQUILIBRIUM_TRANSITION_PERIOD, 1)
        soc_delta = (soc_equilibrium - regime_start_soc_stock) * time_ratio

        soc_stocks.append(regime_start_soc_stock + soc_delta)

    return soc_stocks


# --- GET THE ECO-CLIMATE ZONE FROM THE MEASUREMENTS ---


def _get_eco_climate_zone(measurements: list[dict]) -> Optional[int]:
    """
    Get the eco-climate zone value from a list of measurements.

    Parameters
    ----------
    measurements : list[dict]
        A list of measurement nodes.

    Returns
    -------
    int | None
        The eco-climate zone value if found, otherwise None.
    """
    eco_climate_zone = find_term_match(measurements, "ecoClimateZone")
    return get_node_value(eco_climate_zone) or None


# --- ASSIGN IPCC SOIL CATEGORY TO SITE ---


def _check_soil_category(
    *,
    key: IpccSoilCategory,
    soil_types: list[dict],
    usda_soil_types: list[dict],
    **_
) -> bool:
    """
    Check if the soil category matches the given key.

    Parameters
    ----------
    key : IpccSoilCategory
        The IPCC soil category to check.
    soil_types : list[dict]
        List of soil type measurement nodes.
    usda_soil_types : list[dict]
        List of USDA soil type measurement nodes

    Returns
    -------
    bool
        `True` if the soil category matches, `False` otherwise.
    """
    SOIL_TYPE_LOOKUP = LOOKUPS["soilType"]
    USDA_SOIL_TYPE_LOOKUP = LOOKUPS["usdaSoilType"]

    target_lookup_values = IPCC_SOIL_CATEGORY_TO_SOIL_TYPE_LOOKUP_VALUE.get(key, None)

    is_soil_type_match = cumulative_nodes_lookup_match(
        soil_types,
        lookup=SOIL_TYPE_LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    is_usda_soil_type_match = cumulative_nodes_lookup_match(
        usda_soil_types,
        lookup=USDA_SOIL_TYPE_LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    return is_soil_type_match or is_usda_soil_type_match


def _check_sandy_soil_category(
    *,
    key: IpccSoilCategory,
    soil_types: list[dict],
    usda_soil_types: list[dict],
    has_sandy_soil: bool,
    **_
) -> bool:
    """
    Check if the soils are sandy.

    This function is special case of `_check_soil_category`.

    Parameters
    ----------
    key : IpccSoilCategory
        The IPCC soil category to check.
    soil_types : list[dict]
        List of soil type measurement nodes.
    usda_soil_types : list[dict]
        List of USDA soil type measurement nodes
    has_sandy_soil : bool
        True if the soils are sandy, False otherwise.

    Returns
    -------
    bool
        `True` if the soil category matches, `False` otherwise.
    """
    return _check_soil_category(key=key, soil_types=soil_types, usda_soil_types=usda_soil_types) or has_sandy_soil


SOIL_CATEGORY_DECISION_TREE = {
    IpccSoilCategory.ORGANIC_SOILS: _check_soil_category,
    IpccSoilCategory.SANDY_SOILS: _check_sandy_soil_category,
    IpccSoilCategory.WETLAND_SOILS: _check_soil_category,
    IpccSoilCategory.VOLCANIC_SOILS: _check_soil_category,
    IpccSoilCategory.SPODIC_SOILS: _check_soil_category,
    IpccSoilCategory.HIGH_ACTIVITY_CLAY_SOILS: _check_soil_category,
    IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS: _check_soil_category
}
"""
A decision tree mapping IPCC soil categories to corresponding check functions.

Key: IpccSoilCategory
Value: Corresponding function for checking the match of the given soil category based on soil types.
"""


def _assign_ipcc_soil_category(
    measurements: list[dict],
    default: IpccSoilCategory = IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS
) -> IpccSoilCategory:
    """
    Assign an IPCC soil category based on a site"s measurement nodes.

    Parameters
    ----------
    measurements : list[dict]
        List of measurement nodes.
    default : IpccSoilCategory, optional
        The default soil category if none matches, by default IpccSoilCategory.LOW_ACTIVITY_CLAY_SOILS.

    Returns
    -------
    IpccSoilCategory
        The assigned IPCC soil category.
    """
    soil_types = filter_list_term_type(measurements, TermTermType.SOILTYPE)
    usda_soil_types = filter_list_term_type(measurements, TermTermType.USDASOILTYPE)

    clay_content = get_node_value(find_term_match(measurements, CLAY_CONTENT_TERM_ID))
    sand_content = get_node_value(find_term_match(measurements, SAND_CONTENT_TERM_ID))

    has_sandy_soil = clay_content < CLAY_CONTENT_MAX and sand_content > SAND_CONTENT_MIN

    return next(
        (
            key for key in SOIL_CATEGORY_DECISION_TREE
            if SOIL_CATEGORY_DECISION_TREE[key](
                key=key,
                soil_types=soil_types,
                usda_soil_types=usda_soil_types,
                has_sandy_soil=has_sandy_soil
            )
        ),
        default
    ) if len(soil_types) > 0 or len(usda_soil_types) > 0 else default


# --- ASSIGN IPCC LAND USE CATEGORY ---


def _has_irrigation(water_regime_nodes: list[dict]) -> bool:
    """
    Check if irrigation is present in the water regime nodes.

    Parameters
    ----------
    water_regime_nodes : List[dict]
        List of water regime nodes to be checked.

    Returns
    -------
    bool
        `True` if irrigation is present, `False` otherwise.
    """
    return cumulative_nodes_term_match(
        water_regime_nodes,
        target_term_ids=get_irrigated_terms(),
        cumulative_threshold=MIN_AREA_THRESHOLD
    )


def _has_long_fallow(land_cover_nodes: list[dict]) -> bool:
    """
    Check if long fallow terms is present in the land cover nodes.

    n.b., a super majority of the site area must be under long fallow for it to be classified as set aside.

    Parameters
    ----------
    land_cover_nodes : List[dict]
        List of land cover nodes to be checked.

    Returns
    -------
    bool
        `True` if long fallow is present, `False` otherwise.
    """
    return cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=get_long_fallow_land_cover_terms(),
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD
    ) or cumulative_nodes_match(
        lambda node: get_node_property(node, LONG_FALLOW_CROP_TERM_ID, False).get("value", 0),
        land_cover_nodes,
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD
    )


def _has_upland_rice(land_cover_nodes: list[dict]) -> bool:
    """
    Check if upland rice is present in the land cover nodes.

    Parameters
    ----------
    land_cover_nodes : List[dict]
        List of land cover nodes to be checked.

    Returns
    -------
    bool
        `True` if upland rice is present, `False` otherwise.
    """
    return cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=get_upland_rice_land_cover_terms(),
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD
    )


IPCC_LAND_USE_CATEGORY_TO_VALIDATION_KWARGS = {
    IpccLandUseCategory.SET_ASIDE: {"has_long_fallow"},
    IpccLandUseCategory.ANNUAL_CROPS_WET: {"has_wetland_soils"}
}
"""
Keyword arguments that need to be checked for specific `IpccLandUseCategory`s.
"""


def _check_ipcc_land_use_category(*, key: IpccLandUseCategory, site_type: str, **kwargs) -> bool:
    """
    Check if the site type matches the target site type for the given key.

    Parameters
    ----------
    key : IpccLandUseCategory
        The IPCC land use category to check.
    site_type : str
        The site type to check.

    Keyword Args
    ------------
    has_long_fallow : bool
        Indicates whether long fallow is present on more than 30% of the site.
    has_wetland_soils : bool
        Indicates whether wetland soils are present to more than 30% of the site.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.

    """
    target_site_type = IPCC_LAND_USE_CATEGORY_TO_SITE_TYPE.get(key, None)
    validation_kwargs = IPCC_LAND_USE_CATEGORY_TO_VALIDATION_KWARGS.get(key, set())
    valid_kwargs = all(v for k, v in kwargs.items() if k in validation_kwargs)
    return site_type == target_site_type and valid_kwargs


def _check_cropland_land_use_category(
    *, key: IpccLandUseCategory, site_type: str, land_cover_nodes: list[dict], **kwargs
) -> bool:
    """
    Check if the site type and land cover nodes match the target conditions for a cropland IpccLandUseCategory.

    This function is special case of `_check_ipcc_land_use_category`.

    Parameters
    ----------
    key : IpccLandUseCategory
        The IPCC land use category to check.
    site_type : str
        The site type to check.

    Keyword Args
    ------------
    has_long_fallow : bool
        Indicates whether long fallow is present on more than 30% of the site.
    has_wetland_soils : bool
        Indicates whether wetland soils are present to more than 30% of the site.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    LOOKUP = LOOKUPS["landCover"][0]
    target_lookup_values = IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE.get(key, None)
    valid_lookup = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )
    return _check_ipcc_land_use_category(key=key, site_type=site_type, **kwargs) and valid_lookup


def _check_paddy_rice_cultivation_land_use_category(
    *, key: IpccLandUseCategory, site_type: str, has_irrigated_upland_rice: bool, **kwargs
) -> bool:
    """
    Check if the site type and land cover nodes match the target conditions for a cropland IpccLandUseCategory.

    This function is special case of `_check_cropland_land_use_category`.

    Parameters
    ----------
    key : IpccLandUseCategory
        The IPCC land use category to check.
    site_type : str
        The site type to check.

    Keyword Args
    ------------
    has_irrigated_upland_rice : bool
        Indicates whether irrigated upland rice is present on more than 30% of the site.
    has_long_fallow : bool
        Indicates whether long fallow is present on more than 30% of the site.
    has_wetland_soils : bool
        Indicates whether wetland soils are present to more than 30% of the site.

    Returns
    -------
    bool
        `True` if the conditions match the specified land use category, `False` otherwise.
    """
    return _check_cropland_land_use_category(key=key, site_type=site_type, **kwargs) or has_irrigated_upland_rice


LAND_USE_CATEGORY_DECISION_TREE = {
    IpccLandUseCategory.GRASSLAND: _check_ipcc_land_use_category,
    IpccLandUseCategory.SET_ASIDE: _check_ipcc_land_use_category,
    IpccLandUseCategory.PERENNIAL_CROPS: _check_cropland_land_use_category,
    IpccLandUseCategory.PADDY_RICE_CULTIVATION: _check_paddy_rice_cultivation_land_use_category,
    IpccLandUseCategory.ANNUAL_CROPS_WET: _check_cropland_land_use_category,
    IpccLandUseCategory.ANNUAL_CROPS: _check_cropland_land_use_category,
    IpccLandUseCategory.FOREST: _check_ipcc_land_use_category,
    IpccLandUseCategory.NATIVE: _check_ipcc_land_use_category,
    IpccLandUseCategory.OTHER: _check_ipcc_land_use_category
}
"""
A decision tree mapping IPCC soil categories to corresponding check functions.

Key: IpccLandUseCategory
Value: Corresponding function for checking the match of the given land use category based on site type
and land cover nodes.
"""


def _assign_ipcc_land_use_category(
    site_type: str, management_nodes: list[dict], ipcc_soil_category: IpccSoilCategory
) -> IpccLandUseCategory:
    """
    Assigns IPCC land use category based on site type, management nodes, and soil category.

    Parameters
    ----------
    site_type : str
        The type of the site.
    management_nodes : list[dict]
        List of management nodes.
    ipcc_soil_category : IpccSoilCategory
        The site"s assigned IPCC soil category.

    Returns
    -------
    IpccLandUseCategory
        Assigned IPCC land use category.
    """
    DECISION_TREE = LAND_USE_CATEGORY_DECISION_TREE
    DEFAULT = IpccLandUseCategory.OTHER

    land_cover_nodes = filter_list_term_type(management_nodes, [TermTermType.LANDCOVER])
    water_regime_nodes = filter_list_term_type(management_nodes, [TermTermType.WATERREGIME])

    has_irrigation = _has_irrigation(water_regime_nodes)
    has_upland_rice = _has_upland_rice(land_cover_nodes)
    has_irrigated_upland_rice = has_upland_rice and has_irrigation
    has_long_fallow = _has_long_fallow(land_cover_nodes)
    has_wetland_soils = ipcc_soil_category is IpccSoilCategory.WETLAND_SOILS

    should_run = bool(site_type)

    return next(
        (
            key for key in DECISION_TREE
            if DECISION_TREE[key](
                key=key,
                site_type=site_type,
                land_cover_nodes=land_cover_nodes,
                has_long_fallow=has_long_fallow,
                has_irrigated_upland_rice=has_irrigated_upland_rice,
                has_wetland_soils=has_wetland_soils
            )
        ),
        DEFAULT
    ) if should_run else DEFAULT


# --- ASSIGN IPCC MANAGEMENT CATEGORY ---


def _check_grassland_ipcc_management_category(
    *, key: IpccManagementCategory, land_cover_nodes: list[dict], **_
) -> bool:
    """
    Check if the land cover nodes match the target conditions for a grassland IpccManagementCategory.

    Parameters
    ----------
    key : IpccManagementCategory
        The IPCC management category to check.
    land_cover_nodes : List[dict]
        List of land cover nodes to be checked.

    Returns
    -------
    bool
        `True` if the conditions match the specified management category, `False` otherwise.
    """
    target_term_id = IPCC_MANAGEMENT_CATEGORY_TO_GRASSLAND_MANAGEMENT_TERM_ID.get(key, None)
    return cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=target_term_id,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )


def _check_tillage_ipcc_management_category(
    *, key: IpccManagementCategory, tillage_nodes: list[dict], **_
) -> bool:
    """
    Check if the tillage nodes match the target conditions for a tillage IpccManagementCategory.

    Parameters
    ----------
    key : IpccManagementCategory
        The IPCC management category to check.
    tillage_nodes : List[dict]
        List of tillage nodes to be checked.

    Returns
    -------
    bool
        `True` if the conditions match the specified management category, `False` otherwise.
    """
    LOOKUP = LOOKUPS["tillage"]
    target_lookup_values = IPCC_MANAGEMENT_CATEGORY_TO_TILLAGE_MANAGEMENT_LOOKUP_VALUE.get(key, None)
    return cumulative_nodes_lookup_match(
        tillage_nodes,
        lookup=LOOKUP,
        target_lookup_values=target_lookup_values,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )


GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.SEVERELY_DEGRADED: _check_grassland_ipcc_management_category,
    IpccManagementCategory.IMPROVED_GRASSLAND: _check_grassland_ipcc_management_category,
    IpccManagementCategory.HIGH_INTENSITY_GRAZING: _check_grassland_ipcc_management_category,
    IpccManagementCategory.NOMINALLY_MANAGED: _check_grassland_ipcc_management_category,
    IpccManagementCategory.OTHER: _check_grassland_ipcc_management_category
}
"""
Decision tree mapping IPCC management categories to corresponding check functions for grassland.

Key: IpccManagementCategory
Value: Corresponding function for checking the match of the given management category based on land cover nodes.
"""

TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE = {
    IpccManagementCategory.FULL_TILLAGE: _check_tillage_ipcc_management_category,
    IpccManagementCategory.REDUCED_TILLAGE: _check_tillage_ipcc_management_category,
    IpccManagementCategory.NO_TILLAGE: _check_tillage_ipcc_management_category
}
"""
Decision tree mapping IPCC management categories to corresponding check functions for tillage.

Key: IpccManagementCategory
Value: Corresponding function for checking the match of the given management category based on tillage nodes.
"""

IPCC_LAND_USE_CATEGORY_TO_DECISION_TREE = {
    IpccLandUseCategory.GRASSLAND: GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE,
    IpccLandUseCategory.ANNUAL_CROPS_WET: TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE,
    IpccLandUseCategory.ANNUAL_CROPS: TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE
}
"""
Decision tree mapping IPCC land use categories to corresponding decision trees for management categories.

Key: IpccLandUseCategory
Value: Corresponding decision tree for IPCC management categories based on land use categories.
"""

IPCC_LAND_USE_CATEGORY_TO_DEFAULT_IPCC_MANAGEMENT_CATEGORY = {
    IpccLandUseCategory.GRASSLAND: IpccManagementCategory.NOMINALLY_MANAGED,
    IpccLandUseCategory.ANNUAL_CROPS_WET: IpccManagementCategory.FULL_TILLAGE,
    IpccLandUseCategory.ANNUAL_CROPS: IpccManagementCategory.FULL_TILLAGE
}
"""
Mapping of default IPCC management categories for each IPCC land use category.

Key: IpccLandUseCategory
Value: Default IPCC management category for the given land use category.
"""


def _assign_ipcc_management_category(
    management_nodes: list[dict], ipcc_land_use_category: IpccLandUseCategory
) -> IpccManagementCategory:
    """
    Assign an IPCC Management Category based on the given management nodes and IPCC Land Use Category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes.
    ipcc_land_use_category : IpccLandUseCategory
        The IPCC Land Use Category.

    Returns
    -------
    IpccManagementCategory
        The assigned IPCC Management Category.
    """
    decision_tree = IPCC_LAND_USE_CATEGORY_TO_DECISION_TREE.get(ipcc_land_use_category, {})
    default = IPCC_LAND_USE_CATEGORY_TO_DEFAULT_IPCC_MANAGEMENT_CATEGORY.get(
        ipcc_land_use_category, IpccManagementCategory.OTHER
    )

    land_cover_nodes = filter_list_term_type(management_nodes, [TermTermType.LANDCOVER])
    tillage_nodes = filter_list_term_type(management_nodes, [TermTermType.TILLAGE])

    should_run = any([
        decision_tree == GRASSLAND_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE and len(land_cover_nodes) > 0,
        decision_tree == TILLAGE_IPCC_MANAGEMENT_CATEGORY_DECISION_TREE and len(tillage_nodes) > 0
    ])

    return next(
        (
            key for key in decision_tree
            if decision_tree[key](
                key=key,
                land_cover_nodes=land_cover_nodes,
                tillage_nodes=tillage_nodes,
            )
        ),
        default
    ) if should_run else default


# --- ASSIGN IPCC CARBON INPUT CATEGORY ---


GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_TO_MIN_NUM_IMPROVEMENTS = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: 2,
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: 1
}
"""
A mapping from IPCC Grassland Carbon Input Categories to the minimum number of improvements required.

Key: IpccCarbonInputCategory
Value: Minimum number of improvements required for the corresponding Grassland Carbon Input Category.
"""


def _check_grassland_ipcc_carbon_input_category(
    *, key: IpccCarbonInputCategory, num_grassland_improvements: int, **_,
) -> bool:
    """
    Checks if the given carbon input arguments satisfy the conditions for a specific
    Grassland IPCC Carbon Input Category.

    Parameters
    ----------
    key : IpccCarbonInputCategory
        The grassland IPCC Carbon Input Category to check.
    num_grassland_improvements : int
        The number of grassland improvements.

    Returns
    -------
    bool
        `True` if the conditions for the specified category are met; otherwise, `False`.
    """
    return num_grassland_improvements >= GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_TO_MIN_NUM_IMPROVEMENTS[key]


def _check_cropland_high_with_manure_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Optional[int]:
    """
    Checks the Cropland High with Manure IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | none
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            has_animal_manure_used
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_high_without_manure_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_cover_crop: bool,
    has_irrigation: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_organic_fertiliser_or_soil_amendment_used: bool,
    has_practice_increasing_c_input: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Optional[int]:
    """
    Checks the Cropland High without Manure IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            any([
                has_irrigation,
                has_practice_increasing_c_input,
                has_cover_crop,
                has_organic_fertiliser_or_soil_amendment_used
            ]),
            not has_animal_manure_used
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_medium_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_cover_crop: bool,
    has_irrigation: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_organic_fertiliser_or_soil_amendment_used: bool,
    has_practice_increasing_c_input: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Optional[int]:
    """
    Checks the Cropland Medium IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            has_residue_removed_or_burnt,
            has_animal_manure_used
        ]),
        2: all([
            not has_residue_removed_or_burnt,
            any([
                has_low_residue_producing_crops,
                has_bare_fallow
            ]),
            any([
                has_irrigation,
                has_practice_increasing_c_input,
                has_cover_crop,
                has_organic_fertiliser_or_soil_amendment_used,
            ])
        ]),
        3: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            not has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            any([
                has_irrigation,
                has_practice_increasing_c_input,
                has_cover_crop,
                has_organic_fertiliser_or_soil_amendment_used
            ])
        ]),
        4: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            not has_irrigation,
            not has_organic_fertiliser_or_soil_amendment_used,
            not has_practice_increasing_c_input,
            not has_cover_crop
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _check_cropland_low_category(
    *,
    has_animal_manure_used: bool,
    has_bare_fallow: bool,
    has_cover_crop: bool,
    has_irrigation: bool,
    has_low_residue_producing_crops: bool,
    has_n_fixing_crop_or_inorganic_n_fertiliser_used: bool,
    has_organic_fertiliser_or_soil_amendment_used: bool,
    has_practice_increasing_c_input: bool,
    has_residue_removed_or_burnt: bool,
    **_
) -> Optional[int]:
    """
    Checks the Cropland Low IPCC Carbon Input Category based on the given carbon input arguments.

    Parameters
    ----------
    has_animal_manure_used : bool
        Indicates whether animal manure is used on more than 30% of the site.
    has_bare_fallow : bool
        Indicates whether bare fallow is present on more than 30% of the site.
    has_cover_crop : bool
        Indicates whether cover crops are present on more than 30% of the site.
    has_irrigation : bool
        Indicates whether irrigation is applied to more than 30% of the site.
    has_low_residue_producing_crops : bool
        Indicates whether low residue-producing crops are present on more than 70% of the site.
    has_n_fixing_crop_or_inorganic_n_fertiliser_used : bool
        Indicates whether a nitrogen-fixing crop or inorganic nitrogen fertiliser is used on more than 30% of the site.
    has_organic_fertiliser_or_soil_amendment_used : bool
        Indicates whether organic fertiliser or soil amendments are used on more than 30% of the site.
    has_practice_increasing_c_input : bool
        Indicates whether practices increasing carbon input are present on more than 30% of the site.
    has_residue_removed_or_burnt : bool
        Indicates whether residues are removed or burnt on more than 30% of the site.

    Returns
    -------
    int | None
        The category key if conditions are met; otherwise, `None`.
    """
    conditions = {
        1: all([
            has_residue_removed_or_burnt,
            not has_animal_manure_used
        ]),
        2: all([
            not has_residue_removed_or_burnt,
            any([
                has_low_residue_producing_crops,
                has_bare_fallow
            ]),
            not has_irrigation,
            not has_practice_increasing_c_input,
            not has_cover_crop,
            not has_organic_fertiliser_or_soil_amendment_used
        ]),
        3: all([
            not has_residue_removed_or_burnt,
            not has_low_residue_producing_crops,
            not has_bare_fallow,
            not has_n_fixing_crop_or_inorganic_n_fertiliser_used,
            not has_irrigation,
            not has_organic_fertiliser_or_soil_amendment_used,
            not has_practice_increasing_c_input,
            not has_cover_crop
        ])
    }

    return next(
        (key for key, condition in conditions.items() if condition), None
    )


def _get_carbon_input_kwargs(
    management_nodes: list[dict]
) -> dict:
    """
    Creates CarbonInputArgs based on the provided list of management nodes.

    Parameters
    ----------
    management_nodes : list[dict]
        The list of management nodes.

    Returns
    -------
    dict
        The carbon input keyword arguments.
    """

    PRACTICE_INCREASING_C_INPUT_LOOKUP = LOOKUPS["landUseManagement"]
    LOW_RESIDUE_PRODUCING_CROP_LOOKUP = LOOKUPS["landCover"][1]
    N_FIXING_CROP_LOOKUP = LOOKUPS["landCover"][2]

    # To prevent double counting already explicitly checked practices.
    EXCLUDED_PRACTICE_TERM_IDS = {
        IMPROVED_PASTURE_TERM_ID,
        ANIMAL_MANURE_USED_TERM_ID,
        INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID,
        ORGANIC_FERTILISER_USED_TERM_ID
    }

    crop_residue_management_nodes = filter_list_term_type(management_nodes, [TermTermType.CROPRESIDUEMANAGEMENT])
    land_cover_nodes = filter_list_term_type(management_nodes, [TermTermType.LANDCOVER])
    land_use_management_nodes = filter_list_term_type(management_nodes, [TermTermType.LANDUSEMANAGEMENT])
    water_regime_nodes = filter_list_term_type(management_nodes, [TermTermType.WATERREGIME])

    has_animal_manure_used = any(
        get_node_value(node) for node in land_use_management_nodes if node_term_match(node, ANIMAL_MANURE_USED_TERM_ID)
    )

    has_bare_fallow = cumulative_nodes_term_match(
        land_cover_nodes,
        target_term_ids=SHORT_BARE_FALLOW_TERM_ID,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_cover_crop = cumulative_nodes_match(
        lambda node: any(
            get_node_property(node, term_id, False).get("value", False) for term_id in get_cover_crop_property_terms()
        ),
        land_cover_nodes,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_inorganic_n_fertiliser_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, INORGANIC_NITROGEN_FERTILISER_USED_TERM_ID)
    )

    has_irrigation = _has_irrigation(water_regime_nodes)

    # SUPER_MAJORITY_AREA_THRESHOLD
    has_low_residue_producing_crops = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=LOW_RESIDUE_PRODUCING_CROP_LOOKUP,
        target_lookup_values=True,
        cumulative_threshold=SUPER_MAJORITY_AREA_THRESHOLD
    )

    has_n_fixing_crop = cumulative_nodes_lookup_match(
        land_cover_nodes,
        lookup=N_FIXING_CROP_LOOKUP,
        target_lookup_values=True,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_n_fixing_crop_or_inorganic_n_fertiliser_used = has_n_fixing_crop or has_inorganic_n_fertiliser_used

    has_organic_fertiliser_or_soil_amendment_used = any(
        get_node_value(node) for node in land_use_management_nodes
        if node_term_match(node, ORGANIC_FERTILISER_USED_TERM_ID)
    )

    has_practice_increasing_c_input = cumulative_nodes_match(
        lambda node: (
            node_lookup_match(node, PRACTICE_INCREASING_C_INPUT_LOOKUP, True)
            and not node_term_match(node, EXCLUDED_PRACTICE_TERM_IDS)
        ),
        land_use_management_nodes,
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    has_residue_removed_or_burnt = cumulative_nodes_term_match(
        crop_residue_management_nodes,
        target_term_ids=get_residue_removed_or_burnt_terms(),
        cumulative_threshold=MIN_AREA_THRESHOLD
    )

    num_grassland_improvements = [
        has_irrigation,
        has_practice_increasing_c_input,
        has_n_fixing_crop_or_inorganic_n_fertiliser_used,
        has_organic_fertiliser_or_soil_amendment_used
    ].count(True)

    return {
        "has_animal_manure_used": has_animal_manure_used,
        "has_bare_fallow": has_bare_fallow,
        "has_cover_crop": has_cover_crop,
        "has_irrigation": has_irrigation,
        "has_low_residue_producing_crops": has_low_residue_producing_crops,
        "has_n_fixing_crop_or_inorganic_n_fertiliser_used": has_n_fixing_crop_or_inorganic_n_fertiliser_used,
        "has_organic_fertiliser_or_soil_amendment_used": has_organic_fertiliser_or_soil_amendment_used,
        "has_practice_increasing_c_input": has_practice_increasing_c_input,
        "has_residue_removed_or_burnt": has_residue_removed_or_burnt,
        "num_grassland_improvements": num_grassland_improvements
    }


GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE = {
    IpccCarbonInputCategory.GRASSLAND_HIGH: _check_grassland_ipcc_carbon_input_category,
    IpccCarbonInputCategory.GRASSLAND_MEDIUM: _check_grassland_ipcc_carbon_input_category
}
"""
A decision tree for assigning IPCC Carbon Input Categories to Grassland based on the number of improvements.

Key: IpccCarbonInputCategory
Value: Corresponding function to check if the given conditions are met for the category.
"""

CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE = {
    IpccCarbonInputCategory.CROPLAND_HIGH_WITH_MANURE: _check_cropland_high_with_manure_category,
    IpccCarbonInputCategory.CROPLAND_HIGH_WITHOUT_MANURE: _check_cropland_high_without_manure_category,
    IpccCarbonInputCategory.CROPLAND_MEDIUM: _check_cropland_medium_category,
    IpccCarbonInputCategory.CROPLAND_LOW: _check_cropland_low_category
}
"""
A decision tree for assigning IPCC Carbon Input Categories to Cropland based on specific conditions.

Key: IpccCarbonInputCategory
Value: Corresponding function to check if the given conditions are met for the category.
"""

DECISION_TREE_FROM_IPCC_MANAGEMENT_CATEGORY = {
    IpccManagementCategory.IMPROVED_GRASSLAND: GRASSLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.FULL_TILLAGE: CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.REDUCED_TILLAGE: CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE,
    IpccManagementCategory.NO_TILLAGE: CROPLAND_IPCC_CARBON_INPUT_CATEGORY_DECISION_TREE
}
"""
A decision tree mapping IPCC Management Categories to respective Carbon Input Category decision trees.

Key: IpccManagementCategory
Value: Decision tree for Carbon Input Categories corresponding to the management category.
"""

DEFAULT_CARBON_INPUT_CATEGORY = {
    IpccManagementCategory.IMPROVED_GRASSLAND: IpccCarbonInputCategory.GRASSLAND_MEDIUM,
    IpccManagementCategory.FULL_TILLAGE: IpccCarbonInputCategory.CROPLAND_LOW,
    IpccManagementCategory.REDUCED_TILLAGE: IpccCarbonInputCategory.CROPLAND_LOW,
    IpccManagementCategory.NO_TILLAGE: IpccCarbonInputCategory.CROPLAND_LOW
}
"""
A mapping from IPCC Management Categories to default Carbon Input Categories.

Key: IpccManagementCategory
Value: Default Carbon Input Category for the corresponding Management Category.
"""


def _assign_ipcc_carbon_input_category(
    management_nodes: list[dict],
    ipcc_management_category: IpccManagementCategory
) -> IpccCarbonInputCategory:
    """
    Assigns an IPCC Carbon Input Category based on the provided management nodes and IPCC Management Category.

    Parameters
    ----------
    management_nodes : list[dict]
        List of management nodes containing information about land management practices.
    ipcc_management_category : IpccManagementCategory
        IPCC Management Category for which the Carbon Input Category needs to be assigned.

    Returns
    -------
    IpccCarbonInputCategory
        Assigned IPCC Carbon Input Category.
    """
    decision_tree = DECISION_TREE_FROM_IPCC_MANAGEMENT_CATEGORY.get(ipcc_management_category, {})
    default = DEFAULT_CARBON_INPUT_CATEGORY.get(ipcc_management_category, IpccCarbonInputCategory.OTHER)

    should_run = len(management_nodes) > 0

    return next(
        (key for key in decision_tree if decision_tree[key](
            key=key,
            **_get_carbon_input_kwargs(management_nodes)
        )),
        default
    ) if should_run else default


# --- TIER 1 SOC MODEL ---


def _run_tier_1(
    inventory: dict,
    *,
    eco_climate_zone: int,
    soc_ref: float,
    **_
) -> list[dict]:
    """
    Run the IPCC (2019) Tier 1 methodology for calculating SOC stocks (in kg C ha-1) for each year in the inventory
    and wrap each of the calculated values in Hestia measurement nodes. To avoid any errors, the `inventory` parameter
    must be pre-validated by the `should_run` function.

    See [IPCC (2019) Vol. 4, Ch. 2](https://www.ipcc-nggip.iges.or.jp/public/2019rf/vol4.html) for more information.

    The inventory should be in the following shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN_TIER_1: bool,
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory
        },
        ...
    }
    ```

    Parameters
    ----------
    inventory : dict
        The inventory built by the `_should_run` function.
    eco_climate_zone : int
        The eco-climate zone identifier for the site corresponding to a row in the
        [ecoClimateZone](https://gitlab.com/hestia-earth/hestia-glossary/-/blob/develop/Measurements/ecoClimateZone-lookup.csv)
        lookup table.
    ipcc_soil_category : IpccSoilCategory
        The reference condition SOC stock in the 0-30cm depth interval, kg C ha-1.

    Returns
    -------
    list[dict]
        A list of Hestia `Measurement` nodes containing the calculated SOC stocks and additional relevant data.
    """

    valid_inventory = {
        year: group for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN_TIER_1)
    }

    timestamps = [year for year in valid_inventory.keys()]
    ipcc_land_use_categories = [group[_InventoryKey.LU_CATEGORY] for group in valid_inventory.values()]
    ipcc_management_categories = [group[_InventoryKey.MG_CATEGORY] for group in valid_inventory.values()]
    ipcc_carbon_input_categories = [group[_InventoryKey.CI_CATEGORY] for group in valid_inventory.values()]

    iterated_timestamps, iterated_soc_equilibriums = _run_soc_equilibriums(
        timestamps,
        ipcc_land_use_categories,
        ipcc_management_categories,
        ipcc_carbon_input_categories,
        eco_climate_zone,
        soc_ref
    )

    soc_stocks = _calc_tier_1_soc_stocks(iterated_timestamps, iterated_soc_equilibriums)

    return [
        _measurement(
            year,
            soc_stock,
            MeasurementMethodClassification.TIER_1_MODEL.value
        ) for year, soc_stock in zip(
            iterated_timestamps,
            soc_stocks
        )
    ]


# --- SHOULD RUN ---


def _should_run(site: dict) -> tuple[bool, dict]:
    """
    Extract data from site & related cycles, pre-process data and determine whether there is sufficient data to run the
    tier 1 and/or tier 2 model.

    The inventory dict should be in the following shape:
    ```
    {
        year (int): {
            _InventoryKey.SHOULD_RUN_TIER_2: bool,
            _InventoryKey.TEMP_MONTHLY: list[float],
            _InventoryKey.PRECIP_MONTHLY: list[float],
            _InventoryKey.PET_MONTHLY: list[float],
            _InventoryKey.IRRIGATED_MONTHLY: list[bool]
            _InventoryKey.CARBON_INPUT: float,
            _InventoryKey.N_CONTENT: float,
            _InventoryKey.TILLAGE_CATEGORY: IpccManagementCategory,
            _InventoryKey.SAND_CONTENT: float,
            _InventoryKey.SHOULD_RUN_TIER_1: bool,
            _InventoryKey.LU_CATEGORY: IpccLandUseCategory,
            _InventoryKey.MG_CATEGORY: IpccManagementCategory,
            _InventoryKey.CI_CATEGORY: IpccCarbonInputCategory
        },
        ...
    }
    ```

    The kwargs dict should be in the following shape:
    ```
    {
        "run_with_irrigation": bool,
        "eco_climate_zone": int,
        "ipcc_soil_category": IpccSoilCategory,
        "soc_ref": float
    }
    ```
    """
    site_type = site.get("siteType", "")
    management_nodes = site.get("management", [])
    measurement_nodes = site.get("measurements", [])
    cycles = related_cycles(site.get("@id"))

    has_management = len(management_nodes) > 0
    has_measurements = len(measurement_nodes) > 0
    has_related_cycles = len(cycles) > 0
    has_functional_unit_1_ha = all(cycle.get("functionalUnit") in VALID_FUNCTIONAL_UNITS_TIER_2 for cycle in cycles)

    should_build_inventory_tier_1 = all([
        site_type in VALID_SITE_TYPES_TIER_1,
        has_management,
        has_measurements
    ])

    should_build_inventory_tier_2 = all([
        site_type in VALID_SITE_TYPES_TIER_2,
        has_related_cycles,
        check_cycle_site_ids_identical(cycles),
        has_functional_unit_1_ha
    ])

    inventory_tier_1, kwargs_tier_1 = (
        _build_inventory_tier_1(site_type, management_nodes, measurement_nodes)
        if should_build_inventory_tier_1 else ({}, {})
    )

    inventory_tier_2, kwargs_tier_2 = (
        _build_inventory_tier_2(cycles, measurement_nodes)
        if should_build_inventory_tier_2 else ({}, {})
    )

    inventory = dict(sorted(merge(inventory_tier_1, inventory_tier_2).items()))
    kwargs = kwargs_tier_1 | kwargs_tier_2

    should_run_tier_1 = _should_run_tier_1(inventory, **kwargs) if should_build_inventory_tier_1 else False
    should_run_tier_2 = _should_run_tier_2(inventory, **kwargs) if should_build_inventory_tier_2 else False

    logRequirements(
        site, model=MODEL, term=TERM_ID,
        should_build_inventory_tier_1=should_build_inventory_tier_1,
        should_build_inventory_tier_2=should_build_inventory_tier_2,
        should_run_tier_1=should_run_tier_1,
        should_run_tier_2=should_run_tier_2,
        site_type=site_type,
        has_management=has_management,
        has_measurements=has_measurements,
        has_related_cycles=has_related_cycles,
        is_unit_hectare=has_functional_unit_1_ha,
        **kwargs,
        inventory=_log_inventory(inventory)
    )

    should_run = should_run_tier_1 or should_run_tier_2
    logShouldRun(site, MODEL, TERM_ID, should_run)

    return should_run_tier_1, should_run_tier_2, inventory, kwargs


def _should_run_tier_1(
    inventory: dict,
    *,
    eco_climate_zone: int = None,
    soc_ref: float = None,
    **_
) -> bool:
    """
    Determines whether there is sufficient data in the inventory and keyword args to run the tier 1 model.
    """
    return all([
        eco_climate_zone and eco_climate_zone > 0,
        soc_ref and soc_ref > 0,
        any(year for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN_TIER_1))
    ])


def _should_run_tier_2(
    inventory: dict,
    **_
) -> bool:
    """
    Determines whether there is sufficient data in the inventory and keyword args to run the tier 2 model.
    """
    valid_years = [year for year, group in inventory.items() if group.get(_InventoryKey.SHOULD_RUN_TIER_2)]
    return all([
        len(valid_years) >= MIN_RUN_IN_PERIOD,
        check_consecutive(valid_years),
        any(inventory.get(year).get(_InventoryKey.SAND_CONTENT) for year in valid_years)
    ])


# --- LOGGING ---


def _log_inventory(inventory: dict) -> str:
    """
    Format the inventory data as a table for logging.
    """
    log_table = log_as_table(
        {
            "year": year,
            "should-run-tier-1": group.get(_InventoryKey.SHOULD_RUN_TIER_1, False),
            "should-run-tier-2": group.get(_InventoryKey.SHOULD_RUN_TIER_2, False),
            "ipcc-land-use-category": (
                group.get(_InventoryKey.LU_CATEGORY).value if group.get(_InventoryKey.LU_CATEGORY) else None
            ),
            "ipcc-management-category": (
                group.get(_InventoryKey.MG_CATEGORY).value if group.get(_InventoryKey.MG_CATEGORY) else None
            ),
            "ipcc-carbon-input-category": (
                group.get(_InventoryKey.CI_CATEGORY).value if group.get(_InventoryKey.CI_CATEGORY) else None
            ),
            "temperature-monthly": (
                " ".join(f"{val:.1f}" for val in group.get(_InventoryKey.TEMP_MONTHLY, []))
                if group.get(_InventoryKey.TEMP_MONTHLY) else None
            ),
            "precipitation-monthly": (
                " ".join(f"{val:.1f}" for val in group.get(_InventoryKey.PRECIP_MONTHLY, []))
                if group.get(_InventoryKey.PRECIP_MONTHLY) else None
            ),
            "pet-monthly": (
                " ".join(f"{val:.1f}" for val in group.get(_InventoryKey.PET_MONTHLY, []))
                if group.get(_InventoryKey.PET_MONTHLY) else None
            ),
            "irrigated-monthly": (
                " ".join(str(val) for val in group.get(_InventoryKey.IRRIGATED_MONTHLY, []))
                if group.get(_InventoryKey.PET_MONTHLY) else None
            ),
            "sand-content": group.get(_InventoryKey.SAND_CONTENT, None),
            "carbon-input": group.get(_InventoryKey.CARBON_INPUT, None),
            "n-content": group.get(_InventoryKey.N_CONTENT, None),
            "lignin-content": group.get(_InventoryKey.LIGNIN_CONTENT, None),
            "ipcc-tillage-category": (
                group.get(_InventoryKey.TILLAGE_CATEGORY).value if group.get(_InventoryKey.TILLAGE_CATEGORY) else None
            ),
            "is-paddy-rice": group.get(_InventoryKey.IS_PADDY_RICE, None),
        } for year, group in inventory.items()
    )

    return log_table or None


# --- TIER 2 BUILD INVENTORY ---


def _build_inventory_tier_2(
    cycles: list[dict], measurement_nodes: list[dict]
) -> tuple[dict, dict]:
    """
    Builds an annual inventory of data and a dictionary of keyword arguments for the tier 2 model.

    TODO: implement long-term average climate data and annual climate data as back ups for monthly data
    """
    grouped_cycles = group_nodes_by_year(cycles)
    grouped_measurements = group_nodes_by_year(measurement_nodes, mode=GroupNodesByYearMode.DATES)

    grouped_climate_data = _get_grouped_climate_measurements(grouped_measurements)
    grouped_irrigated_monthly = _get_grouped_irrigated_monthly(grouped_cycles)
    grouped_sand_content_measurements = _get_grouped_sand_content_measurements(grouped_measurements)
    grouped_carbon_input_data = _get_grouped_carbon_input_data(grouped_cycles)
    grouped_tillage_categories = _get_grouped_tillage_categories(grouped_cycles)
    grouped_is_paddy_rice = _get_grouped_is_paddy_rice(grouped_cycles)

    grouped_data = merge(
        grouped_climate_data,
        grouped_irrigated_monthly,
        grouped_sand_content_measurements,
        grouped_carbon_input_data,
        grouped_tillage_categories,
        grouped_is_paddy_rice
    )

    grouped_should_run = {
        year: {_InventoryKey.SHOULD_RUN_TIER_2: _should_run_inventory_year_tier_2(group)}
        for year, group in grouped_data.items()
    }

    inventory = merge(grouped_data, grouped_should_run)
    kwargs = {
        "run_with_irrigation": True
    }

    return inventory, kwargs


def _should_run_inventory_year_tier_2(group: dict) -> bool:
    """
    Determines whether there is sufficient data in an inventory year to run the tier 2 model.

    1. Check that the cycle is not for paddy rice.
    2. Check if monthly data has a value for each calendar month.
    3. Check if all required keys are present.

    Parameters
    ----------
    group : dict
        Dictionary containing information for a specific inventory year.

    Returns
    -------
    bool
        True if the inventory year is valid, False otherwise.
    """
    monthly_data_complete = _check_12_months(
        group,
        {
            _InventoryKey.TEMP_MONTHLY,
            _InventoryKey.PRECIP_MONTHLY,
            _InventoryKey.PET_MONTHLY,
            _InventoryKey.IRRIGATED_MONTHLY
        }
    )

    return all([
        not group.get(_InventoryKey.IS_PADDY_RICE),
        monthly_data_complete,
        all(key in group.keys() for key in REQUIRED_KEYS_TIER_2),
    ])


def _get_grouped_climate_measurements(grouped_measurements: dict) -> dict:
    return {
        year: {
            _InventoryKey.TEMP_MONTHLY: find_term_match(measurements, TEMPERATURE_MONTHLY_TERM_ID, {}).get("value", []),
            _InventoryKey.PRECIP_MONTHLY: (
                find_term_match(measurements, PRECIPITATION_MONTHLY_TERM_ID, {}).get("value", [])
            ),
            _InventoryKey.PET_MONTHLY: find_term_match(measurements, PET_MONTHLY_TERM_ID, {}).get("value", [])
        } for year, measurements in grouped_measurements.items()
    }


def _get_grouped_irrigated_monthly(grouped_cycles: dict) -> dict:
    return {
        year: {
            _InventoryKey.IRRIGATED_MONTHLY: _get_irrigated_monthly(year, cycles)
        } for year, cycles in grouped_cycles.items()
    }


def _get_irrigated_monthly(year: int, cycles: list[dict]) -> list[bool]:
    # Get practice nodes and add "startDate" and "endDate" from cycle if missing.
    irrigation_nodes = non_empty_list(flatten([
        [
            {
                "startDate": cycle.get("startDate"),
                "endDate": cycle.get("endDate"),
                **node
            } for node in cycle.get("practices", [])
        ] for cycle in cycles
    ]))

    grouped_nodes = group_nodes_by_year_and_month(irrigation_nodes)

    # For each month (1 - 12) check if irrigation is present.
    return [
        cumulative_nodes_term_match(
            grouped_nodes.get(year, {}).get(month, []),
            target_term_ids=get_irrigated_terms(),
            cumulative_threshold=MIN_AREA_THRESHOLD
        ) for month in range(1, 13)
    ]


def _get_grouped_sand_content_measurements(grouped_measurements: dict) -> dict:
    grouped_sand_content_measurements = {
        year: find_term_match(
            [m for m in measurements if m.get("depthUpper") == DEPTH_UPPER and m.get("depthLower") == DEPTH_LOWER],
            SAND_CONTENT_TERM_ID,
            {}
        ) for year, measurements in grouped_measurements.items()
    }

    return {
        year: {_InventoryKey.SAND_CONTENT: get_node_value(measurement)}
        for year, measurement in grouped_sand_content_measurements.items() if measurement
    }


def _get_grouped_carbon_input_data(grouped_cycles: dict) -> dict:
    grouped_carbon_sources = {
        year: _get_carbon_sources_from_cycles(cycle)
        for year, cycle in grouped_cycles.items()
    }

    return {
        year: {
            _InventoryKey.CARBON_INPUT: _calc_total_organic_carbon_input(carbon_sources),
            _InventoryKey.N_CONTENT: _calc_average_nitrogen_content_of_organic_carbon_sources(carbon_sources),
            _InventoryKey.LIGNIN_CONTENT: _calc_average_lignin_content_of_organic_carbon_sources(carbon_sources)
        } for year, carbon_sources in grouped_carbon_sources.items()
    }


def _get_grouped_tillage_categories(grouped_cycles):
    return {
        year: {
            _InventoryKey.TILLAGE_CATEGORY: _assign_tier_2_ipcc_tillage_management_category(cycles)
        } for year, cycles in grouped_cycles.items()
    }


def _get_grouped_is_paddy_rice(grouped_cycles: dict) -> dict:
    return {
        year: {
            _InventoryKey.IS_PADDY_RICE: _check_is_paddy_rice(cycles)
        } for year, cycles in grouped_cycles.items()
    }


def _check_is_paddy_rice(cycles: list[dict]) -> bool:
    LOOKUP = LOOKUPS["crop"]
    TARGET_LOOKUP_VALUES = IPCC_LAND_USE_CATEGORY_TO_LAND_COVER_LOOKUP_VALUE.get(
        IpccLandUseCategory.PADDY_RICE_CULTIVATION, None
    )

    has_paddy_rice_products = any(cumulative_nodes_lookup_match(
        filter_list_term_type(
            cycle.get("products", []) + cycle.get("practices", []),
            [TermTermType.CROP, TermTermType.FORAGE, TermTermType.LANDCOVER]
        ),
        lookup=LOOKUP,
        target_lookup_values=TARGET_LOOKUP_VALUES,
        cumulative_threshold=MIN_YIELD_THRESHOLD,
        default_node_value=MIN_YIELD_THRESHOLD
    ) for cycle in cycles)

    has_upland_rice_products = any(cumulative_nodes_term_match(
        filter_list_term_type(
            cycle.get("products", []) + cycle.get("practices", []),
            [TermTermType.CROP, TermTermType.FORAGE, TermTermType.LANDCOVER]
        ),
        target_term_ids=get_upland_rice_crop_terms() + get_upland_rice_land_cover_terms(),
        cumulative_threshold=MIN_YIELD_THRESHOLD,
        default_node_value=MIN_YIELD_THRESHOLD
    ) for cycle in cycles)

    has_irrigation = any(
        _has_irrigation(filter_list_term_type(cycle.get("practices", []), [TermTermType.WATERREGIME]))
        for cycle in cycles
    )

    return has_paddy_rice_products or (has_upland_rice_products and has_irrigation)


# --- TIER 1 BUILD INVENTORY ---


def _build_inventory_tier_1(
    site_type: str, management_nodes: list[dict], measurement_nodes: list[dict]
) -> tuple[dict, dict]:
    """
    Builds an annual inventory of data and a dictionary of keyword arguments for the tier 2 model.
    """
    eco_climate_zone = _get_eco_climate_zone(measurement_nodes)
    ipcc_soil_category = _assign_ipcc_soil_category(measurement_nodes)
    soc_ref = _retrieve_soc_ref(eco_climate_zone, ipcc_soil_category)

    grouped_management = group_nodes_by_year(management_nodes)

    grouped_land_use_categories = {
        year: {
            _InventoryKey.LU_CATEGORY: _assign_ipcc_land_use_category(
                site_type,
                nodes,
                ipcc_soil_category
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_management_categories = {
        year: {
            _InventoryKey.MG_CATEGORY: _assign_ipcc_management_category(
                nodes,
                grouped_land_use_categories[year][_InventoryKey.LU_CATEGORY]
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_carbon_input_categories = {
        year: {
            _InventoryKey.CI_CATEGORY: _assign_ipcc_carbon_input_category(
                nodes,
                grouped_management_categories[year][_InventoryKey.MG_CATEGORY]
            )
        } for year, nodes in grouped_management.items()
    }

    grouped_data = merge(
        grouped_land_use_categories,
        grouped_management_categories,
        grouped_carbon_input_categories
    )

    grouped_should_run = {
        year: {_InventoryKey.SHOULD_RUN_TIER_1: _should_run_inventory_year_tier_1(group)}
        for year, group in grouped_data.items()
    }

    inventory = merge(grouped_data, grouped_should_run)
    kwargs = {
        "eco_climate_zone": eco_climate_zone,
        "ipcc_soil_category": ipcc_soil_category,
        "soc_ref": soc_ref,
    }

    return inventory, kwargs


def _should_run_inventory_year_tier_1(group: dict) -> bool:
    """
    Determines whether there is sufficient data in an inventory year to run the tier 1 model.

    1. Check if the land use category is not "OTHER"
    2. Check if all required keys are present.

    Parameters
    ----------
    group : dict
        Dictionary containing information for a specific inventory year.

    Returns
    -------
    bool
        True if the inventory year is valid, False otherwise.
    """
    return all([
        group.get(_InventoryKey.LU_CATEGORY) != IpccLandUseCategory.OTHER,
        all(key in group.keys() for key in REQUIRED_KEYS_TIER_1),
    ])


# --- RUN ---


def run(site: dict) -> list[dict]:
    """
    Check which Tiers of IPCC SOC model to run, run it and return the formatted output.

    Parameters
    ----------
    site : dict
        A Hestia `Site` node, see: https://www.hestia.earth/schema/Site.

    Returns
    -------
    list[dict]
        A list of Hestia `Measurement` nodes containing the calculated SOC stocks and additional relevant data.
    """
    should_run_tier_1, should_run_tier_2, inventory, kwargs = _should_run(site)
    return (
        _run_tier_2(inventory, **kwargs) if should_run_tier_2
        else _run_tier_1(inventory, **kwargs) if should_run_tier_1
        else []
    )
