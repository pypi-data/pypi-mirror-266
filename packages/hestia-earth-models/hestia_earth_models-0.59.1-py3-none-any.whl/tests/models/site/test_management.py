import json
from unittest.mock import patch
from hestia_earth.schema import TermTermType

from hestia_earth.models.site.management import MODEL, MODEL_KEY, run, should_run
from tests.utils import fixtures_path

CLASS_PATH = f"hestia_earth.models.{MODEL}.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/{MODEL_KEY}"

TERM_BY_ID = {
    'genericCropPlant': {'@type': 'Term', '@id': 'genericCropPlant', 'termType': TermTermType.LANDCOVER.value}
}


@patch(f"{CLASS_PATH}.download_hestia", side_effect=lambda id, *args: TERM_BY_ID[id])
@patch(f"{CLASS_PATH}.related_cycles")
def test_should_run(mock_related_cycles, *args):
    # no cycles => do not run
    mock_related_cycles.return_value = []
    _should_run, *args = should_run({})
    assert _should_run is False

    # no products => do not run
    mock_related_cycles.return_value = [{"products": []}]
    _should_run, *args = should_run({})
    assert _should_run is False

    # with irrelevant termType => do not run
    mock_related_cycles.return_value = [
        {
            "products": [
                {"term": {"termType": TermTermType.BUILDING.value}},
                {"term": {"termType": TermTermType.EXCRETA.value}}
            ],
            "startDate": "2021",
            "endDate": "2022"
        }
    ]
    _should_run, *args = should_run({})
    assert _should_run is False

    # products and practices but no relevant terms/termTypes => do not run
    mock_related_cycles.return_value = [
        {
            "practices": [
                {"term": {"@id": "soilAssociationOrganicStandard"}},
                {"term": {"@id": "noTillage"}}
            ],
            "products": [
                {"term": {"termType": TermTermType.BUILDING.value}},
                {"term": {"termType": TermTermType.EXCRETA.value}}
            ]
        }
    ]
    _should_run, *args = should_run({})
    assert _should_run is False

    # # practices with relevant termType => run
    mock_related_cycles.return_value = [
        {
            "practices": [
                {"term": {"termType": TermTermType.WATERREGIME.value}},
                {"term": {"termType": TermTermType.MACHINERY.value}}
            ],
            "startDate": "2021",
            "endDate": "2022"
        }
    ]
    _should_run, *args = should_run({})
    assert _should_run is True

    # with relevant product => run
    mock_related_cycles.return_value = [
        {
            "products": [
                {
                    "term": {
                        "termType": TermTermType.CROP.value,
                        "@id": "genericCropProduct"
                    },
                    "value": [51],
                    "startDate": "2001",
                    "endDate": "2002",
                    "properties": {"test": "properties"}
                }
            ],
            "startDate": "2021",
            "endDate": "2022"
        }
    ]
    _should_run, *args = should_run({})
    assert _should_run is True
    assert args[0] == [{
        'term': TERM_BY_ID['genericCropPlant'],
        'value': 100,
        'endDate': '2002',
        'startDate': '2001',
        'properties': {'test': 'properties'}
    }]


@patch(f"{CLASS_PATH}.download_hestia", side_effect=lambda id, *args: TERM_BY_ID[id])
@patch(f"{CLASS_PATH}.related_cycles")
def test_run(mock_related_cycles, *args):
    with open(f"{fixtures_folder}/cycles.jsonld", encoding='utf-8') as f:
        cycles = json.load(f)
    mock_related_cycles.return_value = cycles

    with open(f"{fixtures_folder}/site.jsonld", encoding='utf-8') as f:
        site = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    result = run(site)
    assert result == expected
