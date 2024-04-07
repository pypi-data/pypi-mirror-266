import importlib
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Tuple

import typer

from faststream.app import FastStream
from faststream.exceptions import SetupError


def try_import_app(module: Path, app: str) -> FastStream:
    """Tries to import a FastStream app from a module.

    Args:
        module: Path to the module containing the app.
        app: Name of the FastStream app.

    Returns:
        The imported FastStream app object.

    Raises:
        FileNotFoundError: If the module file is not found.
        typer.BadParameter: If the module or app name is not provided correctly.

    """
    try:
        app_object = import_object(module, app)

    except FileNotFoundError as e:
        typer.echo(e, err=True)
        raise typer.BadParameter(
            "Please, input module like [python_file:faststream_app_name] or [module:attribute]"
        ) from e

    else:
        return app_object  # type: ignore


def import_object(module: Path, app: str) -> object:
    """Import an object from a module.

    Args:
        module: The path to the module file.
        app: The name of the object to import.

    Returns:
        The imported object.

    Raises:
        FileNotFoundError: If the module file is not found.
        ValueError: If the module has no loader.
        AttributeError: If the object is not found in the module.

    """
    spec = spec_from_file_location(
        "mode",
        f"{module}.py",
        submodule_search_locations=[str(module.parent.absolute())],
    )

    if spec is None:  # pragma: no cover
        raise FileNotFoundError(module)

    mod = module_from_spec(spec)
    loader = spec.loader

    if loader is None:  # pragma: no cover
        raise SetupError(f"{spec} has no loader")

    loader.exec_module(mod)

    try:
        obj = getattr(mod, app)
    except AttributeError as e:
        raise FileNotFoundError(module) from e

    return obj


def get_app_path(app: str) -> Tuple[Path, str]:
    """Get the application path.

    Args:
        app (str): The name of the application in the format "module:app_name".

    Returns:
        Tuple[Path, str]: A tuple containing the path to the module and the name of the application.

    Raises:
        ValueError: If the given app is not in the format "module:app_name".

    """
    if ":" not in app:
        raise SetupError(f"`{app}` is not a FastStream")

    module, app_name = app.split(":", 2)

    mod_path = Path.cwd()
    for i in module.split("."):
        mod_path = mod_path / i

    return mod_path, app_name


def import_from_string(import_str: str) -> Tuple[Path, FastStream]:
    """Import FastStream application from module specified by a string.

    Parameters:
        import_str (str): A string in the format "<module>:<attribute>" specifying the module and faststream application to import.

    Returns:
        Tuple[ModuleType, FastStream]: A tuple containing the imported module and the faststream application.

    Raises:
        typer.BadParameter: Raised if the given value is not of type string, if the import string is not in the format
            "<module>:<attribute>", if the module is not found, or if the faststream application is not found in the module.
    """
    if not isinstance(import_str, str):
        raise typer.BadParameter("Given value is not of type string")

    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        raise typer.BadParameter(
            f'Import string "{import_str}" must be in format "<module>:<attribute>"'
        )

    try:
        module = importlib.import_module(  # nosemgrep: python.lang.security.audit.non-literal-import.non-literal-import
            module_str
        )

    except ModuleNotFoundError:
        module_path, app_name = get_app_path(import_str)
        instance = try_import_app(module_path, app_name)

    else:
        attr = module
        try:
            for attr_str in attrs_str.split("."):
                attr = getattr(attr, attr_str)
            instance = attr  # type: ignore[assignment]

        except AttributeError as e:
            typer.echo(e, err=True)
            raise typer.BadParameter(
                f'Attribute "{attrs_str}" not found in module "{module_str}".'
            ) from e

        if module.__file__:
            module_path = Path(module.__file__).resolve().parent
        else:
            module_path = Path.cwd()

    return module_path, instance
