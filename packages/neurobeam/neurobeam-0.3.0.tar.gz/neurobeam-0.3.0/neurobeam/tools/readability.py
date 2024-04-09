from typing import Any
import weakref


"""
Some simple functions to make code more readable. Probably not ideal to use most of these in performance 
critical sections.
"""


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SENTINELS OR SENTINEL-LIKE FUNCTIONS FOR READABILITY
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


# noinspection PyPep8Naming
def HAS(thing: Any) -> bool:
    """
    Check if a thing is not None, not an empty string, not an empty tuple, not an empty list, and not an empty dict.

    :param thing: The thing to check
    :returns: True if the thing is not None, not an empty string, not an empty tuple, not an empty list,
        and not an empty dict.

    .. seealso:: :function:`EMPTY <RF_PROBE.tools.readability.EMPTY>`
    """

    return thing is not None and thing != '' and thing != () and thing != [] and thing != {}


# noinspection PyPep8Naming
def EMPTY(thing: Any) -> bool:
    """
    Check if a thing is None, an empty string, an empty tuple, an empty list, or an empty dict.

    :param thing: The thing to check
    :returns: True if the thing is None, an empty string, an empty tuple, an empty list, or an empty dict.

    .. seealso:: :function:`HAS <RF_PROBE.tools.readability.HAS>`
    """
    return thing is None or thing == '' or thing == () or thing == [] or thing == {}


"""
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// DICTIONARY FUNCTIONS
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""


def parse_empties(mapping: dict) -> dict:
    """
    Parse a dictionary and return a new dictionary with only the non-empty values.

    :param mapping: The dictionary to parse
    :returns: A new dictionary with only the non-empty values.
    """
    return {key: value for key, value in mapping.items() if HAS(value)}


def prune_keys(mapping: dict, keys: list) -> dict:
    """
    Prune a dictionary of specific keys.

    :param mapping: The dictionary to prune
    :param keys: The keys to remove
    :returns: A new dictionary with the specified keys removed
    """
    return {key: value for key, value in mapping.items() if key not in keys}
