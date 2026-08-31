from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from backend.agent.tools import rag_summarize, web_search
from backend.common.config_handler import agent_config
from backend.common.path_tool import get_abs_path
from backend.common.prompt_loader import load_system_prompt
import sqlite3
import os

model = init_chat_model(
  model=agent_config["model"],
  model_provider=agent_config["model_provider"],
  base_url=os.getenv("DASHSCOPE_BASE_URL"),
  api_key=os.getenv("DASHSCOPE_API_KEY"),

)

connection = sqlite3.connect(get_abs_path(agent_config["memory_path"]))
checkpointer = SqliteSaver(connection)
checkpointer.setup()

system_prompt = load_system_prompt()