import logging
from types import ModuleType
from typing import Callable

import lastmile_utils.lib.core.api as core_utils
from result import Err, Ok, Result

from aiconfig.editor.server.server_file_utils import (
    get_validated_path,
    import_module_from_path,
)

logging.getLogger("werkzeug").disabled = True

logging.basicConfig(format=core_utils.LOGGER_FMT)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def load_evaluation_module_if_exists(
    eval_module_path: str,
) -> dict[str, Callable[[], None]]:
    res = get_validated_path(eval_module_path).and_then(
        _load_evaluation_module
    )
    match res:
        case Ok(module):
            LOGGER.info(f"Loaded evaluation module from {eval_module_path}")
            return module
        case Err(e):
            LOGGER.warning(f"Failed to load evaluation module: {e}")
            return {}


def _load_evaluation_module(
    path_to_module: str,
) -> Result[dict[str, Callable[[], None]], str]:
    LOGGER.info(f"Importing evaluation module from {path_to_module}")
    eval_module = import_module_from_path(path_to_module)

    match eval_module:
        case Ok(module):
            try:
                eval_fns = _get_evaluation_module_fns(module)
                return Ok(eval_fns)
            except Exception as e:
                return Err(
                    f"Failed to obtain evaluation functions from module: {e}"
                )
        case Err(e):
            return Err(f"Failed to import evaluation module: {e}")


def _get_evaluation_module_fns(
    eval_module: ModuleType,
) -> dict[str, Callable[[], None]]:
    method_names = [
        "create_evaluation_set",
        "get_evaluation_results_columns",
        "get_evaluation_result_details",
        "get_evaluation_result_details_columns",
        "list_evaluation_data_sources",
        "list_evaluation_models",
        "list_evaluation_results",
        "list_evaluation_sets",
        "list_prompt_iteration_data_sources",
    ]

    module_fns: dict[str, Callable[[], None]] = {}
    for method_name in method_names:
        eval_fn = _load_fn_from_eval_module(eval_module, method_name)
        module_fns[method_name] = eval_fn

    return module_fns


def _load_fn_from_eval_module(
    eval_module: ModuleType,
    fn_name: str,
) -> Callable[[], None]:
    if not hasattr(eval_module, fn_name):
        raise Exception(
            f"Evaluation module {eval_module} does not have a {fn_name} function."
        )
    eval_fn = getattr(eval_module, fn_name)
    if not callable(eval_fn):
        raise Exception(
            f"Evaluation module {eval_module} does not have a {fn_name} function"
        )
    else:
        return eval_fn
