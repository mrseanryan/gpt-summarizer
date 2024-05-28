import config


def _is_local_via_ctransformers():
    return len(config.LOCAL_CTRANSFORMERS_MODEL_FILE_PATH) > 0


def _is_local_via_ollama():
    return len(config.OLLAMA_MODEL_NAME) > 0


def is_local_via_ctransformers():
    is_enabled = _is_local_via_ctransformers()
    if is_enabled and _is_local_via_ollama():
        raise ValueError(
            "Please check config.py: both local via ctransformers AND ollama are enabled"
        )
    return is_enabled


def is_local_via_ollama():
    is_enabled = _is_local_via_ollama()
    if is_enabled and _is_local_via_ctransformers():
        raise ValueError(
            "Please check config.py: both local via ctransformers AND ollama are enabled"
        )
    return is_enabled


def is_openai():
    return not _is_local_via_ctransformers() and not _is_local_via_ollama()


def is_json_not_yaml():
    if is_openai():
        return False
    return config.is_local__json_not_yaml
