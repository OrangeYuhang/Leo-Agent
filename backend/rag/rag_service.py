from rag.vector_store import VectorStoreService
from backend.common.prompt_loader import load_rag_summarize_prompt
from backend.common.config_handler import rag_config
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_community.chat_models.tongyi import Tongyi
class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.retriever = self.vector_store.get_retriever()
        self.prompt_text = load_rag_summarize_prompt()
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)
        self.model = Tongyi(model=rag_config["summarise_model"])
        self.chain = self.__init_chain()
        
    def __init_chain(self):
        return self.prompt_template | self.model | StrOutputParser()
    
    def retriver_docs(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
    
    def rag_summarize(self, query: str) -> str:
        docs = self.retriver_docs(query)
        references = ""
        for id, doc in enumerate(docs):
            references += f"[参考资料 {id}：内容：{doc.page_content}]，元数据{doc.metadata}\n"
        
        return self.chain.invoke({"input": query, "references": references})
    
if __name__ == "__main__":
    rag_service = RagSummarizeService()
    print(rag_service.rag_summarize(""))