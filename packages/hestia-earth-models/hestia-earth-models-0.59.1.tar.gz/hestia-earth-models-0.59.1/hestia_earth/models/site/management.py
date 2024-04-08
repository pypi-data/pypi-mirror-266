"""
Management node with data gap-filled data from cycles.
"""
from typing import List
from functools import reduce
from hestia_earth.schema import SchemaType, TermTermType
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.model import filter_list_term_type, linked_node
from hestia_earth.utils.tools import flatten

from hestia_earth.models.log import logRequirements, logShouldRun, log_blank_nodes_id
from hestia_earth.models.utils.site import related_cycles
from hestia_earth.models.utils.term import get_lookup_value
from hestia_earth.models.utils.blank_node import get_node_value
from . import MODEL

REQUIREMENTS = {
    "Site": {
        "related": {
            "Cycle": [{
                "@type": "Cycle",
                "startDate": "",
                "endDate": "",
                "products": [
                    {
                        "@type": "Product",
                        "term.termType": ["crop", "forage", "landCover"]
                    }
                ],
                "practices": [
                    {
                        "term.termType": [
                            "waterRegime",
                            "tillage",
                            "cropResidueManagement",
                            "landUseManagement"
                        ],
                        "value": ""
                    }
                ]
            }]
        }
    }
}
RETURNS = {
    "Management": [{
        "@type": "Management",
        "term.termType": [
            "landCover", "waterRegime", "tillage", "cropResidueManagement", "landUseManagement"
        ],
        "value": "",
        "endDate": "",
        "startDate": ""
    }]
}

MODEL_KEY = 'management'
LAND_COVER_KEY = 'landCoverId'


def management(data: dict):
    node = {'@type': SchemaType.MANAGEMENT.value}
    return node | data


def _extract_node_value(node: dict) -> dict:
    return node | {'value': get_node_value(node)}


def _include(value: dict, keys: list): return {k: v for k, v in value.items() if k in keys}


def _include_start_end(cycle: dict, values: list):
    return [(_include(cycle, ['startDate', 'endDate']) | v) for v in values]


def _copy_item_if_exists(source: dict, keys: List[str] = [], dest: dict = {}) -> dict:
    return reduce(lambda p, c: p | ({c: source[c]} if c in source else {}), keys, dest)


def _get_landCover_term_id(product: dict) -> str:
    value = get_lookup_value(product.get('term', {}), LAND_COVER_KEY, model=MODEL, model_key=LAND_COVER_KEY)
    # TODO: what should happen when there are multiple values?
    return value.split(';')[0] if value else None


def _get_items_with_relevant_term_type(cycles: List[dict], item_name: str, relevant_values: list):
    """Get items from the list of cycles with any of the relevant values. Also adds dates if missing."""
    return flatten(
        [
            _include_start_end(
                cycle=cycle,
                values=filter_list_term_type(cycle.get(item_name, []), relevant_values)
            ) for cycle in cycles
        ]
    )


def should_run(site: dict):
    # Only get related cycles once.
    cycles = related_cycles(site.get("@id"))

    products_land_cover = [
        _extract_node_value(
            _include(
                value=product,
                keys=["term", "value", "startDate", "endDate", "properties"]
            )
        ) for product in _get_items_with_relevant_term_type(
            cycles=cycles,
            item_name="products",
            relevant_values=[TermTermType.LANDCOVER]
        )
    ]

    products_crop_forage = _get_items_with_relevant_term_type(
        cycles=cycles,
        item_name="products",
        relevant_values=[TermTermType.CROP, TermTermType.FORAGE]
    )
    products_crop_forage = [
        _copy_item_if_exists(
            source=product,
            keys=["startDate", "endDate", "properties"],
            dest={
                "term": linked_node(download_hestia(_get_landCover_term_id(product))),
                "value": 100
            }
        )
        for product in list(filter(_get_landCover_term_id, products_crop_forage))
    ]

    practices = [
        _extract_node_value(
            _include(
                value=practice,
                keys=["term", "value", "startDate", "endDate"]
            )
        ) for practice in _get_items_with_relevant_term_type(
            cycles=cycles,
            item_name="practices",
            relevant_values=[
                TermTermType.WATERREGIME,
                TermTermType.TILLAGE,
                TermTermType.CROPRESIDUEMANAGEMENT,
                TermTermType.LANDUSEMANAGEMENT
            ]
        )
    ]

    logRequirements(
        site,
        model=MODEL,
        term=None,
        model_key=MODEL_KEY,
        products_crop_forage_ids=log_blank_nodes_id(products_crop_forage),
        products_land_cover_ids=log_blank_nodes_id(products_land_cover),
        practice_ids=log_blank_nodes_id(practices)
    )

    _should_run = any(products_crop_forage + products_land_cover + practices)
    logShouldRun(site, MODEL, None, should_run=_should_run, model_key=MODEL_KEY)
    return _should_run, products_crop_forage + products_land_cover, practices


def run(site: dict):
    _should_run, products, practices = should_run(site)
    return list(map(management, products + practices)) if _should_run else []
