from langchain.tools import tool
from backend.rag.rag_service import RagSummarizeService
from pydantic import BaseModel,Field
from langchain_tavily import TavilySearch

rag_summarize_service = RagSummarizeService()

search_tool = TavilySearch(
    max_result=5,
    topic="general", # general, news, finance
    # include_answer=False,
    # include_raw_contents=False,
    # include_images=False,
    # include_image_descriptionss=False,
    # search_depths="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None
)

# 向量搜索

@tool(discription="输入一个字符串，从用户本地向量库中搜索最相似的文本片段，并返回一个纯字符串")
def rag_summarize(query: str) -> str:
    return rag_summarize_service.rag_summarize(query)

class Reference(BaseModel):
    title: str = Field(descriptions="The title of the web page cited in the answer")
    url: str = Field(descriptions="The url of the web page cited in the answer")

class AnswerInfo(BaseModel):
    answer: str = Field(descriptions="The final answer for user")
    reference: list[Reference] = Field(descriptions="The web pages cited in the answer") 


# 网络搜索

@tool(description="输入查询进行网络搜索")
def web_search(query:str):
    return search_tool.invoke(query) 

