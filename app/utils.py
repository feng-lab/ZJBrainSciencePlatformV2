import os


def is_debug_mode() -> bool:
    debug_mode_flag = os.environ["DEBUG_MODE"].strip()
    return debug_mode_flag == "True"
