from typing import List

from fastapi import HTTPException, Query
from typing_extensions import Annotated

from logiclayer_complexity.common import VALID_COMPARISONS, split_dict


def parse_alias(
    aliases: Annotated[
        List[str],
        Query(
            alias="alias",
            description=(
                "Changes the label of a Level in the response tidy data dictionaries."
            ),
        ),
    ] = [],
):
    """Alias dependency.

    Parses the alias parameter into a dict of {Level: Alias label}.

    The parameter is a list of strings, but each item is split by comma anyway
    to ensure compatibility with URLSearchParams of both formats:
    - `alias[]=label1:alias1&alias[]=label2:alias2`
    - `alias=label1:alias1,label2:alias2`
    """
    try:
        # Note keys and values are inverted,
        # this because values must be unique for DataFrame.rename()
        parsed_alias = {label: level for level, label in split_dict(aliases, ",")}
    except ValueError:
        raise HTTPException(400, "Malformed 'alias' parameter") from None

    # keys and values are inverted back here
    alias_dict = {level: label for label, level in parsed_alias.items()}
    alias_dict.update(
        {f"{level} ID": f"{label} ID" for level, label in alias_dict.items()}
    )
    return alias_dict


def parse_cuts(
    cuts: Annotated[
        List[str],
        Query(
            description=(
                "Limits the results returned by the output. Only members of a "
                "dimension matching one of the parameters will be kept in the response."
            ),
        ),
    ] = [],
):
    """Cuts dependency.

    Parses the cuts parameter into a dict of {Level: [Member1,...]}

    The parameter is a list of strings, but each item is split by semicolon to
    ensure compatibility with URLSearchParams of both formats:
    - `cuts[]=label1:1,2,3&cuts[]=label2:4,5,6`
    - `cuts=label1:1,2,3;label2:4,5,6`
    """
    try:
        return {
            key: tuple(sorted(str(value) for value in values.split(",")))
            for key, values in split_dict(cuts, ";")
        }
    except ValueError:
        raise HTTPException(400, "Malformed 'cuts' parameter") from None


def parse_filter(
    items: Annotated[
        List[str],
        Query(
            alias="filter",
            description=(
                "Limits the results returned by the output. Only members of a "
                "dimension matching one of the parameters will be kept in the response."
            ),
        ),
    ] = [],
):
    """Filter dependency.

    Parses the filter parameter into a dict of {Level: (Member IDs, ...)}.

    Each token in the parameter has the shape `Level:id1,id2...`
    """
    try:
        return {
            key: tuple(
                int(item) if item.isnumeric() else item for item in values.split(",")
            )
            for key, values in split_dict(items, ";")
        }
    except ValueError:
        raise HTTPException(400, "Malformed 'filter' parameter")


def parse_threshold_singleton(params: str):
    """Parses a threshold singleton from a string."""
    if ":" in params:
        comparison, value = params.split(":", maxsplit=1)
    else:
        comparison, value = "gte", params

    if comparison not in VALID_COMPARISONS:
        raise HTTPException(
            400,
            f"Malformed 'threshold' parameter, '{comparison}' is not a valid comparison keyword. "
            f"Accepted values are: {', '.join(VALID_COMPARISONS)}",
        )

    try:
        value = float(value)
    except ValueError:
        raise HTTPException(
            400, f"Malformed 'threshold' parameter, '{value}' must be numeric"
        )

    return comparison, value


def parse_threshold(
    threshold: Annotated[
        List[str],
        Query(
            description=(
                "Restricts the data to be used in the calculation, to rows where "
                "the sum of all values through the other dimension fulfills the condition."
            ),
        ),
    ] = [],
):
    """Threshold dependency.

    Parses the threshold parameter into a dict of {Level: (Comparison, Value)}.

    The parameter is a list of strings, but each item is split by comma anyway
    to ensure compatibility with URLSearchParams of both formats:
    - `threshold[]=level1:gte:10&threshold[]=level2:lt:20`
    - `threshold=level1:gte:10;level2:lt:20`
    """
    return {
        level: parse_threshold_singleton(params)
        for level, params in split_dict(threshold, ";")
    }
