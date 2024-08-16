import types
import typing


def extract_items(data: list[...] | dict[...],
                  selectors: list[str | int | types.EllipsisType, ...],
                  join_with: str = None):
    """
    extracts items from a data-structure using a ``list`` of selectors

    :param data: the data to extract from
    :param selectors: the selectors to extract the data
    :param join_with: the ``string`` with which items should be joined
    :return: extracted data
    """
    assert isinstance(selectors, list)
    if selectors:
        assert isinstance(data, (list, dict))
    element = data
    while selectors:
        selector, *selectors = selectors
        if element is None:
            return 'None' if join_with else None
        elif selector is Ellipsis:
            if join_with:
                return join_with.join(str(extract_items(i, selectors, join_with=join_with)) for i in element)
            else:
                return [extract_items(i, selectors, join_with=join_with) for i in element]
        elif isinstance(selector, typing.Callable):
            if join_with:
                return str(selector(element))
            else:
                return selector(element)
        element = element[selector]
    if join_with:
        return str(element)
    else:
        return element


def map_extract_items(data: list[...] | dict[...],
                      selector_mapping: dict[str, list[str | int | types.EllipsisType, ...]],
                      join_with: str = None):
    """
    extracts items from a data-structure using a mapping of ``lists`` of selectors

    :param data: the data to extract from (a ``dict`` or a ``list`` of ``dict``\\ s)
    :param selector_mapping: the selector-mapping to extract the data
    :param join_with: the ``string`` with which items should be joined
    :return: a ``dictionary`` of the extracted data
    """
    assert isinstance(selector_mapping, dict)
    assert isinstance(data, (list, dict))
    if isinstance(data, dict):
        result = {}
        for key, selectors in selector_mapping.items():
            result[key] = extract_items(data, selectors, join_with=join_with)
        return result
    elif isinstance(data, list):
        return [
            map_extract_items(data=d, selector_mapping=selector_mapping, join_with=join_with)
            for d in data
        ]
