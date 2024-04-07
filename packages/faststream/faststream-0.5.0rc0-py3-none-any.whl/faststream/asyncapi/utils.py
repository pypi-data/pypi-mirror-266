from typing import List, Tuple

from faststream.types import AnyDict


def to_camelcase(*names: str) -> str:
    """Converts a list of names to camel case.

    Args:
        *names: Variable length list of names to be converted to camel case.

    Returns:
        The camel case representation of the names.

    Example:
        >>> to_camelcase("hello_world")
        "HelloWorld"

    """
    return " ".join(names).replace("_", " ").title().replace(" ", "")


def resolve_payloads(
    payloads: List[Tuple[AnyDict, str]],
    extra: str = "",
    served_words: int = 1,
) -> AnyDict:
    """Resolve payloads.

    Args:
        payloads: A list of dictionaries representing payloads.
        extra: The extra string to be added to the title (default '').
        served_words: The number of words to be served (default 1).

    Returns:
        A dictionary representing the resolved payload.

    """
    ln = len(payloads)
    payload: AnyDict
    if ln > 1:
        one_of_payloads = {}

        for body, handler_name in payloads:
            title = body["title"]
            words = title.split(":")

            if len(words) > 1:  # not pydantic model case
                body["title"] = title = ":".join(
                    filter(
                        lambda x: bool(x),
                        (
                            handler_name,
                            extra if extra not in words else "",
                            *words[served_words:],
                        ),
                    )
                )

            one_of_payloads[title] = body

        payload = {"oneOf": one_of_payloads}

    elif ln == 1:
        payload = payloads[0][0]

    else:
        payload = {}

    return payload
