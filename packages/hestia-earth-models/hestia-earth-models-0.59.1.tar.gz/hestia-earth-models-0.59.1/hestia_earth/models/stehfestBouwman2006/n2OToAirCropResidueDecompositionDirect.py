from hestia_earth.schema import EmissionMethodTier

from hestia_earth.models.utils.cycle import get_crop_residue_decomposition_N_total
from hestia_earth.models.utils.emission import _new_emission
from .n2OToAirSoilFlux import _should_run, _get_value
from . import MODEL

REQUIREMENTS = {
    "Cycle": {
        "completeness.cropResidue": "True",
        "products": [{
            "@type": "Product",
            "value": "",
            "term.termType": "cropResidue",
            "properties": [{"@type": "Property", "value": "", "term.@id": "nitrogenContent"}]
        }],
        "site": {
            "@type": "Site",
            "measurements": [
                {"@type": "Measurement", "value": "", "term.@id": "totalNitrogenPerKgSoil"},
                {"@type": "Measurement", "value": "", "term.@id": "organicCarbonPerKgSoil"},
                {"@type": "Measurement", "value": "", "term.@id": "ecoClimateZone"},
                {"@type": "Measurement", "value": "", "term.@id": "clayContent"},
                {"@type": "Measurement", "value": "", "term.@id": "sandContent"},
                {"@type": "Measurement", "value": "", "term.@id": "soilPh"}
            ]
        }
    }
}
RETURNS = {
    "Emission": [{
        "value": "",
        "methodTier": "tier 2"
    }]
}
LOOKUPS = {
    "cropResidue": "decomposesOnField",
    "crop": "cropGroupingStehfestBouwman",
    "ecoClimateZone": "STEHFEST_BOUWMAN_2006_N2O-N_FACTOR"
}
TERM_ID = 'n2OToAirCropResidueDecompositionDirect'
TIER = EmissionMethodTier.TIER_2.value


def _emission(value: float):
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = TIER
    return emission


def _run(cycle: dict, content_list_of_items: list, N_total: float):
    n2OToAirSoilFlux = _get_value(cycle, content_list_of_items, N_total, TERM_ID)
    N_crop_residue = get_crop_residue_decomposition_N_total(cycle)
    value = N_crop_residue / N_total * n2OToAirSoilFlux if all([
        N_crop_residue, N_total
    ]) else 0
    return [_emission(value)]


def run(cycle: dict):
    should_run, N_total, content_list_of_items = _should_run(cycle, TERM_ID, TIER)
    return _run(cycle, content_list_of_items, N_total) if should_run else []
