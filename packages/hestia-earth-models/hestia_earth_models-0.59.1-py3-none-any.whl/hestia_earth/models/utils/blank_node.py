from calendar import monthrange
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime
from dateutil.relativedelta import relativedelta
from enum import Enum
from functools import reduce
from statistics import mode, mean
from typing import (
    Any,
    List,
    Callable,
    NamedTuple,
    Optional,
    Union
)
from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.tools import (
    flatten,
    list_sum,
    safe_parse_date,
    safe_parse_float,
    non_empty_list
)

from ..log import debugValues, log_as_table
from . import is_from_model, _filter_list_term_unit
from .constant import Units
from .property import get_node_property, get_node_property_value
from .lookup import (
    is_model_siteType_allowed,
    is_siteType_allowed,
    is_product_id_allowed, is_product_termType_allowed,
    is_input_id_allowed, is_input_termType_allowed
)
from .term import get_lookup_value


def group_by_keys(group_keys: list = ['term']):
    def run(group: dict, input: dict):
        group_key = '-'.join(non_empty_list(map(lambda v: input.get(v, {}).get('@id'), group_keys)))
        group[group_key] = group.get(group_key, []) + [input]
        return group
    return run


def _module_term_id(term_id: str, module): return getattr(module, 'TERM_ID', term_id).split(',')[0]


def _run_model_required(model: str, term: dict, data: dict):
    siteType_allowed = is_model_siteType_allowed(model, term, data)

    run_required = all([siteType_allowed])
    debugValues(data, model=model, term=term.get('@id'),
                run_required=run_required,
                siteType_allowed=siteType_allowed)
    return run_required


def _run_required(model: str, term: dict, data: dict):
    siteType_allowed = is_siteType_allowed(data, term)
    product_id_allowed = is_product_id_allowed(data, term)
    product_termType_allowed = is_product_termType_allowed(data, term)
    input_id_allowed = is_input_id_allowed(data, term)
    input_termType_allowed = is_input_termType_allowed(data, term)

    run_required = all([
        siteType_allowed, product_id_allowed, product_termType_allowed, input_id_allowed, input_termType_allowed
    ])
    # model is only used for logs here, skip logs if model not provided
    if model:
        debugValues(data, model=model, term=term.get('@id'),
                    siteType_allowed=siteType_allowed,
                    product_id_allowed=product_id_allowed,
                    product_termType_allowed=product_termType_allowed,
                    input_id_allowed=input_id_allowed,
                    input_termType_allowed=input_termType_allowed)
        # logging this for the model would cause issues parsing statuses
        if model != 'emissionNotRelevant':
            debugValues(data, model=model, term=term.get('@id'), run_required=run_required)
    return run_required


def is_run_required(model: str, term_id: str, node: dict):
    """
    Determines whether the term for the model should run or not, based on lookup values.

    Parameters
    ----------
    model : str
        The `@id` of the model. Example: `pooreNemecek2018`.
    term_id : str
        The `@id` of the `Term` or the full JSON-LD of the Term. Example: `sandContent`.
    node : dict
        The node on which the model is applied. Logging purpose ony.

    Returns
    -------
    bool
        True if the model is required to run.
    """
    term = download_hestia(term_id)
    return (
        (_run_model_required(model, term, node) if model else True) and _run_required(model, term, node)
    ) if term else True


def run_if_required(model: str, term_id: str, data: dict, module):
    return getattr(module, 'run')(data) if is_run_required(model, _module_term_id(term_id, module), data) else []


def find_terms_value(nodes: list, term_id: str, default: Union[int, None] = 0):
    """
    Returns the sum of all blank nodes in the list which match the `Term` with the given `@id`.

    Parameters
    ----------
    values : list
        The list in which to search for. Example: `cycle['nodes']`.
    term_id : str
        The `@id` of the `Term`. Example: `sandContent`

    Returns
    -------
    float
        The total `value` as a number.
    """
    return list_sum(get_total_value(filter(lambda node: node.get('term', {}).get('@id') == term_id, nodes)), default)


def has_gap_filled_by_ids(nodes: list, term_ids: List[str]):
    nodes = [n for n in nodes if n.get('term', {}).get('@id') in term_ids]
    return any([is_from_model(n) for n in nodes])


def has_original_by_ids(nodes: list, term_ids: List[str]):
    nodes = [n for n in nodes if n.get('term', {}).get('@id') in term_ids]
    return any([not is_from_model(n) for n in nodes])


def get_total_value(nodes: list):
    """
    Get the total `value` of a list of Blank Nodes.
    This method does not take into account the `units` and possible conversions.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    return list(map(lambda node: list_sum(node.get('value', []), None), nodes))


def _value_as(term_id: str, convert_to_property=True):
    def get_value(node: dict):
        property = get_node_property(node, term_id)
        # ignore node value if property is not found
        factor = safe_parse_float(property.get('value', 0))
        value = list_sum(node.get('value', []))
        ratio = factor / 100 if property.get('term', {}).get('units', '') == '%' else factor
        return 0 if ratio == 0 else (value * ratio if convert_to_property else value / ratio)
    return get_value


def get_total_value_converted(nodes: list, conversion_property, convert_to_property=True):
    """
    Get the total `value` of a list of Blank Nodes converted using a property of each Blank Node.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.
    conversion_property : str|List[str]
        Property (or multiple properties) used for the conversion. Example: `nitrogenContent`.
        See https://hestia.earth/glossary?termType=property for a list of `Property`.
    convert_to_property : bool
        By default, property is multiplied on value to get result. Set `False` to divide instead.

    Returns
    -------
    list
        The total `value` as a list of numbers.
    """
    def convert_multiple(node: dict):
        value = 0
        for prop in conversion_property:
            value = _value_as(prop, convert_to_property)(node)
            node['value'] = [value]
        return value

    return [
        _value_as(conversion_property, convert_to_property)(node) if isinstance(conversion_property, str) else
        convert_multiple(node) for node in nodes
    ]


def get_total_value_converted_with_min_ratio(
    model: str, term: str, node: dict = {},
    blank_nodes: list = [],
    prop_id: str = 'energyContentHigherHeatingValue',
    min_ratio: float = 0.8
):
    values = [
        (
            blank_node.get('term', {}).get('@id'),
            list_sum(blank_node.get('value', [])),
            get_node_property_value(model, blank_node, prop_id)
        ) for blank_node in blank_nodes
    ]
    value_logs = log_as_table([{
        'id': term_id,
        'value': value,
        prop_id: prop_value
    } for term_id, value, prop_value in values])

    total_value = list_sum([value for term_id, value, prop_value in values])
    total_value_with_property = list_sum([value for term_id, value, prop_value in values if prop_value])
    total_value_ratio = total_value_with_property / total_value if total_value > 0 else 0

    debugValues(node, model=model, term=term, property_id=prop_id,
                total_value=total_value,
                total_value_with_property=total_value_with_property,
                total_value_ratio=total_value_ratio,
                min_value_ratio=min_ratio,
                conversion_details=value_logs)

    return list_sum([
        value * prop_value for term_id, value, prop_value in values if all([value, prop_value])
    ]) * total_value / total_value_with_property if total_value_ratio >= min_ratio else None


def get_N_total(nodes: list) -> list:
    """
    Get the total nitrogen content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg N` will be used.
    2. Every blank node specified in `kg` or `kg dry matter` will be multiplied by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, [Units.KG, Units.KG_DRY_MATTER])
    return get_total_value(kg_N_nodes) + get_total_value_converted(kg_nodes, 'nitrogenContent')


def get_KG_total(nodes: list) -> list:
    """
    Get the total kg mass of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every blank node in `kg` will be used.
    2. Every blank node specified in `kg N` will be divided by the `nitrogenContent` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The nitrogen values as a list of numbers.
    """
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_nodes) + get_total_value_converted(kg_N_nodes, 'nitrogenContent', False)


def get_P2O5_total(nodes: list) -> list:
    """
    Get the total phosphate content of a list of Blank Node.

    The result contains the values of the following nodes:
    1. Every organic fertiliser specified in `kg P2O5` will be used.
    1. Every organic fertiliser specified in `kg N` will be multiplied by the `phosphateContentAsP2O5` property.
    2. Every organic fertiliser specified in `kg` will be multiplied by the `phosphateContentAsP2O5` property.

    Parameters
    ----------
    nodes : list
        A list of Blank Node.

    Returns
    -------
    list
        The phosphate values as a list of numbers.
    """
    kg_P_nodes = _filter_list_term_unit(nodes, Units.KG_P2O5)
    kg_N_nodes = _filter_list_term_unit(nodes, Units.KG_N)
    kg_nodes = _filter_list_term_unit(nodes, Units.KG)
    return get_total_value(kg_P_nodes) + get_total_value_converted(kg_N_nodes + kg_nodes, 'phosphateContentAsP2O5')


def convert_to_nitrogen(node: dict, model: str, term_id: str, blank_nodes: list, **log_args):
    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'nitrogenContent', default=None, **log_args)
        return value or get_node_property_value(model, input, 'crudeProteinContent', default=0, **log_args) / 6.25

    values = [(i, prop_value(i)) for i in blank_nodes]
    missing_nitrogen_property = [i.get('term', {}).get('@id') for i, p_value in values if not p_value]

    debugValues(node, model=model, term=term_id,
                missing_nitrogen_property=';'.join(set(missing_nitrogen_property)),
                **log_args)

    return list_sum([
        list_sum(i.get('value', [])) * p_value for i, p_value in values if p_value is not None
    ]) if len(missing_nitrogen_property) == 0 else None


def convert_to_carbon(node: dict, model: str, term_id: str, blank_nodes: list, **log_args):
    def prop_value(input: dict):
        value = get_node_property_value(model, input, 'carbonContent', default=None, **log_args)
        return value or \
            get_node_property_value(model, input, 'energyContentHigherHeatingValue', default=0, **log_args) * 0.021

    values = [(i, prop_value(i)) for i in blank_nodes]
    missing_carbon_property = [i.get('term', {}).get('@id') for i, p_value in values if not p_value]

    debugValues(node, model=model, term=term_id,
                missing_carbon_property=';'.join(missing_carbon_property),
                **log_args)

    return list_sum([
        list_sum(i.get('value', [])) * p_value for i, p_value in values if p_value is not None
    ]) if len(missing_carbon_property) == 0 else None


class ArrayTreatment(Enum):
    """
    Enum representing different treatments for arrays of values.
    """
    MEAN = 'mean'
    MODE = 'mode'
    SUM = 'sum'
    FIRST = 'first'
    LAST = 'last'


def _should_run_array_treatment(value):
    return isinstance(value, Iterable) and len(value) > 0


DEFAULT_ARRAY_TREATMENT = ArrayTreatment.MEAN
ARRAY_TREATMENT_TO_REDUCER = {
    ArrayTreatment.MEAN: lambda value: mean(value) if _should_run_array_treatment(value) else 0,
    ArrayTreatment.MODE: lambda value: mode(value) if _should_run_array_treatment(value) else 0,
    ArrayTreatment.SUM: lambda value: sum(value) if _should_run_array_treatment(value) else 0,
    ArrayTreatment.FIRST: lambda value: value[0] if _should_run_array_treatment(value) else 0,
    ArrayTreatment.LAST: lambda value: value[-1] if _should_run_array_treatment(value) else 0
}
"""
A dictionary mapping ArrayTreatment enums to corresponding reducer functions.
"""


def _retrieve_array_treatment(
    node: dict,
    is_larger_unit: bool = False,
    default: ArrayTreatment = ArrayTreatment.FIRST
) -> ArrayTreatment:
    """
    Retrieves the array treatment for a given node.

    Array treatments are used to reduce an array's list of values into
    a single value. The array treatment is retrieved from a lookup on
    the node's term.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    is_larger_unit : bool, optional
        Flag indicating whether to use the larger unit lookup, by default `False`.
    default : ArrayTreatment, optional
        Default value to return if the lookup fails, by default `ArrayTreatment.FIRST`.

    Returns
    -------
    ArrayTreatment
        The retrieved array treatment.

    """
    ARRAY_TREATMENT_LOOKUPS = [
        'arrayTreatmentLargerUnitOfTime',
        'arrayTreatment'
    ]
    lookup = ARRAY_TREATMENT_LOOKUPS[0] if is_larger_unit else ARRAY_TREATMENT_LOOKUPS[1]

    term = node.get('term', {})
    lookup_value = get_lookup_value(term, lookup, skip_debug=True)

    return next(
        (treatment for treatment in ArrayTreatment if treatment.value == lookup_value),
        default
    )


def get_node_value(
    node: dict,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
    default: Any = 0
) -> Union[float, bool]:
    """
    Get the value from the dictionary representing the node,
    applying optional array treatment if the value is a list.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    is_larger_unit : bool, optional
        A flag indicating whether the unit of time is larger, by default `False`.
    array_treatment : ArrayTreatment, optional
        An optional override for the treatment to be applied to an array value, if `None` the array treatment in the
        node's term's lookup is used (which defaults to `FIRST` if no array treatment is specified), by default `None`.

    Returns
    -------
    float | bool
        The extracted value from the node.

    """
    value = node.get("value", 0)

    reducer = ARRAY_TREATMENT_TO_REDUCER[(
        array_treatment or _retrieve_array_treatment(node, is_larger_unit=is_larger_unit)
    )] if isinstance(value, list) and len(value) > 0 else None

    return reducer(value) if reducer else value if isinstance(value, bool) else value or default


def _convert_to_set(
    variable: Union[Iterable[Any], Any]
) -> set:
    """
    Description of function

    Parameters
    ----------
    variable : Iterable[Any] | Any
        The input variable, which can be either an iterable or a single element.

    Returns
    -------
    set
        A set containing the elements of the input variable.
    """
    is_iterable = isinstance(variable, Iterable) and not isinstance(variable, (str, bytes))
    return set(variable) if is_iterable else {variable}


def node_term_match(
    node: dict,
    target_term_ids: Union[str, set[str]]
) -> bool:
    """
    Check if the term ID of the given node matches any of the target term IDs.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    target_term_ids : str | set[str]
        A single term ID or an set of term IDs to check against.

    Returns
    -------
    bool
        `True` if the term ID of the node matches any of the target
        term IDs, `False` otherwise.

    """
    target_term_ids = _convert_to_set(target_term_ids)
    return node.get('term', {}).get('@id', None) in target_term_ids


def node_lookup_match(
    node: dict,
    lookup: str,
    target_lookup_values: Union[str, set[str]]
) -> bool:
    """
    Check if the lookup value in the node's term matches any of the
    target lookup values.

    Parameters
    ----------
    node : dict
        The dictionary representing the node.
    lookup : str
        The lookup key.
    target_lookup_values : str | set[str]
        A single target lookup value or a set of target lookup values
        to check against.

    Returns
    -------
    bool
        `True` if there is a match, `False` otherwise.
    """
    target_lookup_values = _convert_to_set(target_lookup_values)
    return get_lookup_value(node.get('term', {}), lookup) in target_lookup_values


def cumulative_nodes_match(
    function: Callable[[dict], bool],
    nodes: list[dict],
    *,
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes that satisfy the provided
    function exceed the threshold.

    Parameters
    ----------
    function : Callable[[dict], bool]
        A function to determine whether a node should be included in
        the calculation.
    nodes : list[dict]
        The list of nodes to be considered.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the
        function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by
        default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit
        of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False`
        otherwise.

    """
    values = [
        get_node_value(
            node, is_larger_unit, array_treatment
        ) or default_node_value for node in nodes if function(node)
    ]

    return list_sum(non_empty_list(flatten(values))) > cumulative_threshold


def cumulative_nodes_term_match(
    nodes: list[dict],
    *,
    target_term_ids: Union[str, set[str]],
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes with matching term IDs
    exceed the threshold.

    Parameters
    ----------
    nodes : list[dict]
        The list of nodes to be considered.
    target_term_ids : str | set[str]
        The term ID or a set of term IDs to match.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False` otherwise.
    """
    target_term_ids = _convert_to_set(target_term_ids)

    def match_function(node: dict) -> bool:
        return node_term_match(node, target_term_ids)

    return cumulative_nodes_match(
        match_function,
        nodes,
        cumulative_threshold=cumulative_threshold,
        default_node_value=default_node_value,
        is_larger_unit=is_larger_unit,
        array_treatment=array_treatment
    )


def cumulative_nodes_lookup_match(
    nodes: list[dict],
    *,
    lookup: str,
    target_lookup_values: Union[str, set[str]],
    cumulative_threshold: float,
    default_node_value: float = 0,
    is_larger_unit: bool = False,
    array_treatment: Optional[ArrayTreatment] = None,
) -> bool:
    """
    Check if the cumulative values of nodes with matching lookup values exceed the threshold.

    Parameters
    ----------
    nodes : list[dict]
        The list of nodes to be considered.
    lookup : str
        The lookup key to match against in the nodes.
    target_lookup_values : str | set[str]
        The lookup value or a set of lookup values to match.
    cumulative_threshold : float
        The threshold that the cumulative values must exceed for the
        function to return `True`.
    default_node_value : float, optional
        The default value for nodes without a specified value, by
        default `0`.
    is_larger_unit : bool, optional
        A flag indicating whether the node values are in a larger unit
        of time, by default `False`.
    array_treatment : ArrayTreatment | None, optional
        The treatment to apply to arrays of values, by default `None`.

    Returns
    -------
    bool
        `True` if the cumulative values exceed the threshold, `False`
        otherwise.
    """
    target_lookup_values = _convert_to_set(target_lookup_values)

    def match_function(node: dict) -> bool:
        return node_lookup_match(node, lookup, target_lookup_values)

    return cumulative_nodes_match(
        match_function,
        nodes,
        cumulative_threshold=cumulative_threshold,
        default_node_value=default_node_value,
        is_larger_unit=is_larger_unit,
        array_treatment=array_treatment
    )


# --- Blank Node date utils ---


class DatestrFormat(Enum):
    """
    Enum representing ISO date formats permitted by Hestia.

    See: https://en.wikipedia.org/wiki/ISO_8601
    """
    YEAR = r"%Y"
    YEAR_MONTH = r"%Y-%m"
    YEAR_MONTH_DAY = r"%Y-%m-%d"
    YEAR_MONTH_DAY_HOUR_MINUTE_SECOND = r"%Y-%m-%dT%H:%M:%S"
    MONTH = r"--%m"
    MONTH_DAY = r"--%m-%d"


DATESTR_FORMAT_TO_EXPECTED_LENGTH = {
    DatestrFormat.YEAR: len("2001"),
    DatestrFormat.YEAR_MONTH: len("2001-01"),
    DatestrFormat.YEAR_MONTH_DAY: len("2001-01-01"),
    DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND: len("2001-01-01T00:00:00"),
    DatestrFormat.MONTH: len("--01"),
    DatestrFormat.MONTH_DAY: len("--01-01")
}


DatestrGapfillMode = Enum("DatestrGapfillMode", [
    "START",
    "END"
])
"""
Enum representing modes of gapfilling incomplete datestrings.
"""


DatetimeRange = NamedTuple(
    "DatetimeRange",
    [
        ("start", datetime),
        ("end", datetime)
    ]
)
"""
A named tuple for storing a datetime range.

Attributes
----------
start : datetime
    The start of the datetime range.
end : datetime
    The end of the datetime range.
"""


def _check_datestr_format(datestr: str, format: DatestrFormat) -> bool:
    """
    Use `datetime.strptime` to determine if a datestr is in a particular ISO format.
    """
    try:
        expected_length = DATESTR_FORMAT_TO_EXPECTED_LENGTH.get(format, 0)
        format_str = format.value
        parsed_datetime = datetime.strptime(datestr, format_str)
        return bool(parsed_datetime) and len(datestr) == expected_length
    except ValueError:
        return False


def _get_datestr_format(datestr: str, default: Optional[Any] = None) -> Union[DatestrFormat, Any, None]:
    """
    Check a datestr against each ISO format permitted by the Hestia schema and
    return the matching format.
    """
    return next(
        (date_format for date_format in DatestrFormat if _check_datestr_format(str(datestr), date_format)),
        default
    )


def _gapfill_datestr_start(datestr: str, *_) -> str:
    """
    Gapfill an incomplete datestr with the earliest possible date and time.

    Datestr will snap to the start of the year/month/day as appropriate.
    """
    return datestr + "YYYY-01-01T00:00:00"[len(datestr):]


def _gapfill_datestr_end(datestr: str, format: DatestrFormat) -> str:
    """
    Gapfill an incomplete datestr with the latest possible date and time.

    Datestr will snap to the end of the year/month/day as appropriate.
    """
    datetime = safe_parse_date(datestr)
    num_days_in_month = (
        monthrange(datetime.year, datetime.month)[1]
        if datetime and format == DatestrFormat.YEAR_MONTH
        else 31
    )
    completion_str = f"YYYY-12-{num_days_in_month}T23:59:59"
    return datestr + completion_str[len(datestr):]


DATESTR_GAPFILL_MODE_TO_GAPFILL_FUNCTION = {
    DatestrGapfillMode.START: _gapfill_datestr_start,
    DatestrGapfillMode.END: _gapfill_datestr_end
}


def _gapfill_datestr(datestr: str, mode: DatestrGapfillMode = DatestrGapfillMode.START) -> str:
    """
    Gapfill incomplete datestrs and returns them in the format `YYYY-MM-DDTHH:MM_SS`.
    """
    VALID_DATE_FORMATS = {
        DatestrFormat.YEAR, DatestrFormat.YEAR_MONTH, DatestrFormat.YEAR_MONTH_DAY
    }
    _datestr = str(datestr)
    format = _get_datestr_format(_datestr)
    should_run = format in VALID_DATE_FORMATS
    return DATESTR_GAPFILL_MODE_TO_GAPFILL_FUNCTION[mode](_datestr, format) if should_run else _datestr


def _datetime_within_range(datetime: datetime, range: DatetimeRange) -> bool:
    """
    Determine whether or not a `datetime` falls within a `DatetimeRange`.
    """
    return range.start <= datetime <= range.end


def _datetime_range_duration(range: DatetimeRange, add_second=False) -> float:
    """
    Determine the length of a `DatetimeRange` in seconds.

    Option to `add_second` to account for 1 second between 23:59:59 and 00:00:00)
    """
    return (range.end - range.start).total_seconds() + int(add_second)


def _calc_datetime_range_intersection_duration(
    range_a: DatetimeRange, range_b: DatetimeRange, add_second=False
) -> float:
    """
    Determine the length of a `DatetimeRange` in seconds.

    Option to `add_second` to account for 1 second between 23:59:59 and 00:00:00)
    """
    latest_start = max(range_a.start, range_b.start)
    earliest_end = min(range_a.end, range_b.end)

    intersection_range = DatetimeRange(
        start=latest_start,
        end=earliest_end
    )

    duration = _datetime_range_duration(intersection_range)

    # if less than 0 the ranges do not intersect, so return 0.
    return (
        _datetime_range_duration(intersection_range) + int(add_second)
        if duration > 0 else 0
    )


# --- Group nodes by year ---


VALID_DATE_FORMATS_GROUP_NODES_BY_YEAR = {
    DatestrFormat.YEAR,
    DatestrFormat.YEAR_MONTH,
    DatestrFormat.YEAR_MONTH_DAY,
    DatestrFormat.YEAR_MONTH_DAY_HOUR_MINUTE_SECOND
}


GroupNodesByYearMode = Enum("GroupNodesByYearMode", [
    "START_AND_END_DATE",
    "DATES"
])
"""
Enum representing modes of grouping nodes by year.

Members
-------
START_AND_END_DATE
    Use the `startDate` and `endDate` fields of the node.
DATES
    Use the `dates` field of the node.
"""


def _should_run_node_by_end_date(node: dict) -> bool:
    """
    Validate nodes for `group_nodes_by_year` using the "startDate" and "endDate" fields.
    """
    return _get_datestr_format(node.get("endDate")) in VALID_DATE_FORMATS_GROUP_NODES_BY_YEAR


def _should_run_node_by_dates(node: dict) -> bool:
    """
    Validate nodes for `group_nodes_by_year` using the "dates" field.
    """
    value = node.get("value")
    dates = node.get("dates")
    return (
        value and dates and len(dates) > 0 and len(value) == len(dates)
        and all(_get_datestr_format(datestr) in VALID_DATE_FORMATS_GROUP_NODES_BY_YEAR for datestr in node.get("dates"))
    )


GROUP_NODES_BY_YEAR_MODE_TO_SHOULD_RUN_NODE_FUNCTION = {
    GroupNodesByYearMode.START_AND_END_DATE: _should_run_node_by_end_date,
    GroupNodesByYearMode.DATES: _should_run_node_by_dates
}


def _get_node_datetime_range_from_start_and_end_date(
    node: dict, default_node_duration: int = 1
) -> Union[DatetimeRange, None]:
    """
    Get the datetime range from a node's "startDate" and "endDate" fields.

    If "startDate" field is not available, a start date is calculated using the end date
    and `default_node_duration`.
    """
    end = safe_parse_date(_gapfill_datestr(node.get("endDate"), DatestrGapfillMode.END))
    start = (
        safe_parse_date(_gapfill_datestr(node.get("startDate"), DatestrGapfillMode.START))
        or end - relativedelta(years=default_node_duration, seconds=-1) if end else None
    )

    valid = isinstance(start, datetime) and isinstance(end, datetime)
    return DatetimeRange(start, end) if valid else None


def _get_node_datetime_range_from_dates(
    node: dict, **_
) -> Union[DatetimeRange, None]:
    """
    Get the datetime range from a node's "dates" field.
    """
    dates = node.get("dates")
    end = max(
        non_empty_list(
            safe_parse_date(_gapfill_datestr(datestr, DatestrGapfillMode.END)) for datestr in dates
        ), default=None
    )
    start = min(
        non_empty_list(
            safe_parse_date(_gapfill_datestr(datestr, DatestrGapfillMode.START)) for datestr in dates
        ), default=None
    )

    valid = isinstance(start, datetime) and isinstance(end, datetime)
    return DatetimeRange(start, end) if valid else None


GROUP_NODES_BY_YEAR_MODE_TO_GET_DATETIME_RANGE_FUNCTION = {
    GroupNodesByYearMode.START_AND_END_DATE: _get_node_datetime_range_from_start_and_end_date,
    GroupNodesByYearMode.DATES: _get_node_datetime_range_from_dates
}


def _build_time_fraction_dict(
    group_datetime_range: DatetimeRange,
    node_datetime_range: DatetimeRange
) -> dict:
    """
    Build a dictionary containing fractions of the year and node duration based on datetime ranges.

    This function calculates the duration of the group or year, the duration of the node, and the intersection
    duration between the two. It then computes the fractions of the year and node duration represented by the
    intersection. The results are returned in a dictionary.

    Parameters
    ----------
    group_datetime_range : DatetimeRange
        The datetime range representing the entire group or year.
    node_datetime_range : DatetimeRange
        The datetime range representing the node.

    Returns
    -------
    dict
        A dictionary containing "fraction_of_group_duration" and "fraction_of_node_duration".
    """
    group_duration = _datetime_range_duration(group_datetime_range, add_second=True)
    node_duration = _datetime_range_duration(node_datetime_range, add_second=True)

    intersection_duration = _calc_datetime_range_intersection_duration(
        node_datetime_range, group_datetime_range, add_second=True
    )

    fraction_of_group_duration = intersection_duration / group_duration
    fraction_of_node_duration = intersection_duration / node_duration

    return {
        "fraction_of_group_duration": fraction_of_group_duration,
        "fraction_of_node_duration": fraction_of_node_duration
    }


def _validate_time_fraction_dict(
    time_fraction_dict: dict,
    is_final_group: bool
) -> bool:
    """
    Return `True` if the the node intersections with a year group by
    more than 30% OR the year group represents more than 50% of a node's
    duration. Return `False` otherwise.

    This is to prevent cycles/managements being categorised into a year group
    when due to overlapping by just a few days. In these cases, nodes will only
    be counted in the year group if the majority of that node takes place in
    that year.
    """
    FRACTION_OF_GROUP_DURATION_THRESHOLD = 0.3
    FRACTION_OF_NODE_DURATION_THRESHOLD = 0.5

    return any([
        time_fraction_dict["fraction_of_group_duration"] > FRACTION_OF_GROUP_DURATION_THRESHOLD,
        time_fraction_dict["fraction_of_node_duration"] > FRACTION_OF_NODE_DURATION_THRESHOLD,
        is_final_group and time_fraction_dict["fraction_of_node_duration"] == FRACTION_OF_NODE_DURATION_THRESHOLD
    ])


def _build_update_dict(node: dict, years: list, target_year: int) -> dict:
    """
    Build an update dictionary containing values and dates from a node that fall within a given year.

    This is only required if when `group_nodes_by_year` `mode = GroupNodesByYearMode.DATES`

    Parameters
    ----------
    node : dict
        The node containing values and dates.
    year : int
        The year to be matched.

    Returns
    -------
    dict
        An update dictionary containing "value" and "dates" keys.
    """
    valid_indices = {
        i for i, y in enumerate(years) if y == target_year
    }
    return {
        "value": [node.get("value")[i] for i in valid_indices],
        "dates": [node.get("dates")[i] for i in valid_indices]
    }


def group_nodes_by_year(
    nodes: list[dict],
    default_node_duration: int = 1,
    sort_result: bool = True,
    inner_key: Union[Any, None] = None,
    mode: GroupNodesByYearMode = GroupNodesByYearMode.START_AND_END_DATE
) -> dict[int, list[dict]]:
    """
    Group nodes by year based on either their "startDate" and "endDate" fields or their
    "dates" field. Incomplete date strings are gap-filled automatically using `_gapfill_datestr`
    function.

    Parameters
    ----------
    nodes : list[dict]
        A list of nodes with start and end date information.
    default_node_duration : int, optional
        Default duration of a node years if start date is not available, by default 1.
    sort_result : bool, optional
        Flag to sort the result by year, by default True.
    inner_key: Any | None
        An optional inner dictionary key for the outputted annualised groups (can be used to merge annualised
        dictionaries together), default value: `None`.
    mode : GroupNodesByYearMode, optional
        The mode to determine how nodes are grouped by year. Options are defined in `GroupNodesByYearMode`.

    Returns
    -------
    dict[int, list[dict]]
        A dictionary where keys are years and values are lists of nodes.
    """

    should_run_node = GROUP_NODES_BY_YEAR_MODE_TO_SHOULD_RUN_NODE_FUNCTION[mode]
    get_node_datetime_range = GROUP_NODES_BY_YEAR_MODE_TO_GET_DATETIME_RANGE_FUNCTION[mode]

    valid_nodes = [node for node in nodes if should_run_node(node)]

    def group_node(groups: dict, index: int):
        node = valid_nodes[index]

        node_datetime_range = get_node_datetime_range(
            node, default_node_duration=default_node_duration
        )

        # pre-parse the "dates" field so it doesn't get re-calculated in each iteration of the for-loop
        years = (
            [safe_parse_date(datestr).year for datestr in node.get("dates", [])]
            if mode == GroupNodesByYearMode.DATES else []
        )

        range_start = node_datetime_range.start.year if node_datetime_range else 0
        range_end = node_datetime_range.end.year + 1 if node_datetime_range else 0

        for year in range(range_start, range_end):

            group_datetime_range = DatetimeRange(
                start=safe_parse_date(_gapfill_datestr(year, DatestrGapfillMode.START)),
                end=safe_parse_date(_gapfill_datestr(year, DatestrGapfillMode.END))
            )

            is_final_year = _datetime_within_range(node_datetime_range.end, group_datetime_range)

            time_fraction_dict = _build_time_fraction_dict(group_datetime_range, node_datetime_range)
            update_dict = _build_update_dict(node, years, year) if mode == GroupNodesByYearMode.DATES else {}

            should_run = (
                mode == GroupNodesByYearMode.DATES
                or _validate_time_fraction_dict(
                    time_fraction_dict,
                    is_final_year
                )
            )

            should_run and groups[year].append(
                node | time_fraction_dict | update_dict
            )

        return groups

    grouped = reduce(group_node, range(len(valid_nodes)), defaultdict(list))

    iterated = {
        year: {inner_key: group} if inner_key else group
        for year, group in grouped.items()
    }

    return dict(sorted(iterated.items())) if sort_result else iterated


def group_nodes_by_year_and_month(
    nodes: list[dict],
    default_node_duration: int = 1,
    sort_result: bool = True,
    inner_key: Union[Any, None] = None
) -> dict[int, list[dict]]:
    """
    Group nodes by year based on either their "startDate" and "endDate" fields. Incomplete date strings are gap-filled
    automatically using `_gapfill_datestr` function.

    Returns a dict in the shape:
    ```
    {
        year (int): {
            month (int): nodes (list[dict])  # for each month 1 - 12
        }
    }
    ```

    Parameters
    ----------
    nodes : list[dict]
        A list of nodes with start and end date information.
    default_node_duration : int, optional
        Default duration of a node years if start date is not available, by default 1.
    sort_result : bool, optional
        Flag to sort the result by year, by default True.
    inner_key: Any | None
        An optional inner dictionary key for the outputted annualised groups (can be used to merge annualised
        dictionaries together), default value: `None`.

    Returns
    -------
    dict[int, list[dict]]
        A dictionary where keys are years and values are lists of nodes.
    """
    valid_nodes = [node for node in nodes if _should_run_node_by_end_date(node)]

    def group_node(groups: dict, index: int):
        node = valid_nodes[index]

        node_datetime_range = _get_node_datetime_range_from_start_and_end_date(
            node, default_node_duration=default_node_duration
        )

        range_start = node_datetime_range.start.year if node_datetime_range else 0
        range_end = node_datetime_range.end.year + 1 if node_datetime_range else 0

        for year in range(range_start, range_end):
            for month in range(1, 13):

                group_datetime_range = DatetimeRange(
                    start=safe_parse_date(_gapfill_datestr(f"{year}-{month:02}", DatestrGapfillMode.START)),
                    end=safe_parse_date(_gapfill_datestr(f"{year}-{month}", DatestrGapfillMode.END))
                )

                is_final_month = _datetime_within_range(node_datetime_range.end, group_datetime_range)
                time_fraction_dict = _build_time_fraction_dict(group_datetime_range, node_datetime_range)
                should_run = _validate_time_fraction_dict(time_fraction_dict, is_final_month)

                should_run and groups[year][month].append(node)

        return groups

    grouped = reduce(group_node, range(len(valid_nodes)), defaultdict(lambda: defaultdict(list)))

    iterated = {
        year: {inner_key: dict(group)} if inner_key else dict(group)
        for year, group in grouped.items()
    }

    return dict(sorted(iterated.items())) if sort_result else iterated


# --- Group nodes by last date ---


def _get_last_date(datestrs: list[str]) -> Optional[str]:
    """
    Reduce a datestrs down to a single datestr by selecting the last one.

    Parameters
    ----------
    datestrs : list
        A list of datestrings, e.g. the value of a node's `dates` field.

    Returns
    -------
    str | None
        Returns the latest datestr or `None` if no valid datestr in list.

    """
    return sorted(datestrs)[-1] if len(datestrs) > 0 else None


def group_nodes_by_last_date(nodes: list) -> dict[str, list[dict]]:
    """
    Group a list of nodes by the last date of their `dates` field. Nodes with no `dates` field will be sorted into
    the `no-dates` group.

    Parameters
    ----------
    nodes : list[dict]
        A list of Hestia format nodes.

    Return
    ------
    dict
        A dictionary of nodes grouped by latest date, in the format `{date: list[node]}`.
    """
    DEFAULT_KEY = 'no-dates'

    def group_by(group: dict, node: dict):
        dates = node.get('dates', [])
        key = _get_last_date(dates) or DEFAULT_KEY
        return group | {key: group.get(key, []) + [node]}

    return reduce(group_by, nodes, {})
