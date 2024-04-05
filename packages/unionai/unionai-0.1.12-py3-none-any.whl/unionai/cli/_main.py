from os import getenv

from flytekit.clis.sdk_in_container.pyflyte import main as pyflyte_main

from unionai._config import _UNIONAI_CONFIG, _UNIONAI_CONFIG_ENV_VAR


def main(*args, **kwargs):
    """Main CLI entry point for directly calling `unionai`"""
    _UNIONAI_CONFIG.config = getenv(_UNIONAI_CONFIG_ENV_VAR)
    _UNIONAI_CONFIG.is_direct_unionai_cli_call = True
    return pyflyte_main(*args, **kwargs)
