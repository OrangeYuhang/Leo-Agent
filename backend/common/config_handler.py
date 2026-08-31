import json
from typing import Any,Literal
from backend.common.path_tool import get_abs_path


cfg = json.load(open(get_abs_path("config.json"), "r"))



rag_config = cfg["rag"]
prompts_config = cfg["prompts"]
agent_config = cfg["agent"]

if __name__ == "__main__":
    print(agent_config["memory_path"])
