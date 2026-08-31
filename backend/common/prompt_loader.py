from backend.common.config_handler import prompts_config
from backend.common.path_tool import get_abs_path
from backend.common.logger_handler import logger

def load_system_prompt() -> str:
    try:
        system_prompt_path = get_abs_path(prompts_config['system_prompt_path'])
    except KeyError as e:
        logger.error(f"[load_system_prompt] the yaml config is missing:{str(e)}")
        raise e

    try:
        return open(system_prompt_path, 'r', encoding='utf-8').read()
    except Exception as e:
        logger.error(f"[load_system_prompt] loading system prompt failed:{str(e)}")


def load_rag_summarize_prompt() -> str:
    try:
        rag_summarize_prompt_path = get_abs_path(
            prompts_config["rag_summarize_prompt_path"]
        )
    except KeyError as e:
        logger.error(
            f"[load_rag_summarize_prompt] the yaml config is missing:{str(e)}"
        )
        raise e

    try:
        return open(rag_summarize_prompt_path, "r", encoding="utf-8").read()
    except Exception as e:
        logger.error(f"[load_rag_summarize_prompt] loading sag summarize prompt failed:{str(e)}")


if __name__ == "__main__":
    pass
