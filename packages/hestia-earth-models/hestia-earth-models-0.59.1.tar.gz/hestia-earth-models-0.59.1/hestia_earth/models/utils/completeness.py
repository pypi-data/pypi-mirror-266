from typing import Union
from hestia_earth.schema import TermTermType
from hestia_earth.utils.api import download_hestia


def _get_term_type_completeness(cycle: dict, term: Union[str, dict]):
    term = download_hestia(term) if isinstance(term, str) else term
    term_type = term.get('termType') if term else None
    return cycle.get('completeness', {}).get(term_type, False)


def _is_term_type_complete(cycle: dict, term: Union[str, dict, TermTermType]):
    term_type = (
        term if term in cycle.get('completeness', {}) else None
    ) if isinstance(term, str) else None if isinstance(term, dict) else term.value
    completeness = _get_term_type_completeness(cycle, term) if term_type is None else (
        cycle.get('completeness', {}).get(term_type, False)
    )
    return completeness is True


def _is_term_type_incomplete(cycle: dict, term: Union[str, dict, TermTermType]):
    term_type = (
        term if term in cycle.get('completeness', {}) else None
    ) if isinstance(term, str) else None if isinstance(term, dict) else term.value
    completeness = _get_term_type_completeness(cycle, term) if term_type is None else (
        cycle.get('completeness', {}).get(term_type, False)
    )
    return completeness is False
