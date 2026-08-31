from langchain_chroma import Chroma
from backend.common.config_handler import rag_config
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.common.path_tool import get_abs_path
from backend.common.logger_handler import logger
from langchain_community.embeddings import DashScopeEmbedding
from backend.common.file_handler import (
    listdir_with_allowed_type,
    pdf_loader,
    txt_loader,
    get_file_md5_hex
)
from langchain_core.documents import Document
import os

class VectorStoreService(object):
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=rag_config["chroma"]['collection_name'],
            embedding_function=DashScopeEmbedding(model = rag_config["summarise_model"]),
            persist_directory=rag_config["chroma"]['persist_directory'],
        )
        
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=rag_config["chroma"]['chunk_size'], 
            chunk_overlap=rag_config["chroma"]['chunk_overlap'],
            separators=rag_config["chroma"]['separators'],
            length_function=len
        )
        
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": rag_config["chroma"]['k']})
            
    def load_document(self):
        def check_md5_hex(md5_str: str) -> bool:
            if not os.path.exists(get_abs_path(rag_config["chroma"]['md5_hex_store'])):
                open(get_abs_path(rag_config["chroma"]['md5_hex_store']), 'w',encoding='utf-8').close()
                return False

            with open(get_abs_path(rag_config["chroma"]['md5_hex_store']), 'r',encoding='utf-8') as f:
                for line in f.readlines():
                    if line.strip() == md5_str:
                        return True

            return False  
                    
        def save_md5_hex(md5_str: str) -> None:
            with open(get_abs_path(rag_config["chroma"]['md5_hex_store']), 'a',encoding='utf-8') as f:
                f.write(md5_str + '\n')
                        
        def get_file_documents(file_path: str)-> list[Document|None]:
            if file_path.endswith('.pdf'):
                return pdf_loader(file_path)
            elif file_path.endswith('.txt'):
                return txt_loader(file_path)
                    
            return []
                
        allowed_files_path = listdir_with_allowed_type(
            get_abs_path(rag_config["chroma"]['data_path']), 
            allowed_types=tuple(rag_config["chroma"]['allowed_knowledge_file_types'])
        )
        for file_path in allowed_files_path:
            md5_hex = get_file_md5_hex(file_path)
            if check_md5_hex(md5_hex):
                logger.info(f"[load_document] {file_path} has been loaded, jumped")
                continue
            try:
                documents = get_file_documents(file_path)
                        
                if not documents: 
                    logger.info(f"[load_document] {file_path} has no content")
                    continue
                        
                split_docs:list[Document] = self.spliter.split_documents(documents)
                        
                if not split_docs: 
                    logger.info(f"[load_document] {file_path} has no content")
                    continue
                        
                self.vector_store.add_documents(split_docs)
                save_md5_hex(md5_hex)
                        
            except Exception as e:
                    logger.error(f"[load_document] {file_path} failed: {str(e)}",exc_info=True)
                            
                        
if __name__ == '__main__':
    vector_store = VectorStoreService()
    vector_store.load_document()
    retriever = vector_store.get_retriever()
    
    res = retriever.invoke("迷路")
    for r in res:
        print(r.page_content)
        print('*'*20)
                        
                    
                     