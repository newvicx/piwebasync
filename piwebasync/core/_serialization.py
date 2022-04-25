import re


def serialize_camel_case(key: str) -> None:
    """
    Convert snake case `param_a` to camel case `ParamA`
    """ 
    split = key.split('_')
    if len(split) > 1:
        key = ''.join(
            [val.title() for val in split]
        )
        return key
    else:
        return key.title()


def serialize_lower_camel_case(key: str) -> str:
    """
    Convert snake case `param_a` to lower camel case `paramA`
    """
    split = key.split('_')
    if len(split) > 1:
        key = split[0] + ''.join(
            [val.title() for val in split[1:]]
        )
    return key


def deserialize_camel_case(key: str) -> str:
    """
    Convert camel case `ParamA` to snake case `param_a`
    """
    split = re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', key)
    if split:
        return '_'.join([val.lower() for val in split])
    return key.lower()