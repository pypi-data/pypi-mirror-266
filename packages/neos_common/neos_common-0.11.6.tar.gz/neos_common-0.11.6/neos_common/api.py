import importlib
import inspect
import typing

from neos_common import schema


def get_error_codes(module_names: typing.Union[str, list[str]]) -> schema.ErrorCodes:
    """Get all error codes and messages from the error module."""
    errors = []

    if isinstance(module_names, str):
        module_names = [module_names]

    for module_name in module_names:
        module = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, "title"):
                o = obj("title")
                code = o.type
                title = o.title

                if code != "":
                    errors.append(
                        schema.ErrorCode(
                            class_name=name,
                            code=code,
                            title=title,
                        ),
                    )

    return schema.ErrorCodes(errors=errors)
