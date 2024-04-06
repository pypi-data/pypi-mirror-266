import importlib
import importlib.util
import logging
import os
import sys
from types import ModuleType
from typing import NewType

import lastmile_utils.lib.core.api as core_utils
from result import Err, Ok, Result

UnvalidatedPath = NewType("UnvalidatedPath", str)
ValidatedPath = NewType("ValidatedPath", str)

logging.getLogger("werkzeug").disabled = True

logging.basicConfig(format=core_utils.LOGGER_FMT)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def resolve_path(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def get_validated_path(
    raw_path: str | None, allow_create: bool = False
) -> Result[ValidatedPath, str]:
    LOGGER.debug(f"{allow_create=}")
    if not raw_path:
        return Err("No path provided")
    resolved = resolve_path(raw_path)
    if not allow_create and not os.path.isfile(resolved):
        return Err(f"File does not exist: {resolved}")
    return Ok(ValidatedPath(resolved))


def import_module_from_path(path_to_module: str) -> Result[ModuleType, str]:
    LOGGER.debug(f"{path_to_module=}")
    resolved_path = resolve_path(path_to_module)
    LOGGER.debug(f"{resolved_path=}")
    module_name = os.path.basename(resolved_path).replace(".py", "")

    try:
        spec = importlib.util.spec_from_file_location(
            module_name, resolved_path
        )
        if spec is None:
            return Err(f"Could not import module from path: {resolved_path}")
        elif spec.loader is None:
            return Err(
                f"Could not import module from path: {resolved_path} (no loader)"
            )
        else:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return Ok(module)
    except Exception as e:
        return core_utils.ErrWithTraceback(e)
