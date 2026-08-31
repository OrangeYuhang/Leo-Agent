import os,hashlib
from backend.common.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader,PyPDFLoader
def get_file_md5_hex(file_path: str) -> str:
    if not os.path.exists(file_path):
        logger.error(f"[get_file_md5_hex] FILE:{file_path} not exists")
        return 

    if not os.path.isfile(file_path):
        logger.error(f"[get_file_md5_hex] FILE:{file_path} is not a file")
        return

    md5_obj = hashlib.md5()

    chunk_size = 4096 #4kb
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk)

            return  md5_obj.hexdigest()

    except Exception as e:
        logger.error(f"[get_file_md5_hex] computing FILE:{file_path} failed:{str(e)}")
        return

    return md5_obj.hexdigest()
def listdir_with_allowed_type(path: str, allowed_types: tuple[str]):
    files = []
    if not os.path.isdir(path):
        logger.error(f"[listdir_with_allowed_type] path:{path} is not a directory")
        
    for f in os.listdir(path):
        if f.endswith(allowed_types):
            files.append(os.path.join(path, f))
            
    return tuple(files)

def pdf_loader(file_path: str,passwd:str=None)->list[Document]:
    try:
        return PyPDFLoader(file_path,passwd).load()
    except Exception as e:
        logger.error(f"[pdf_loader] loading file:{file_path} failed:{str(e)}")
        return []

def txt_loader(file_path: str)->list[Document]:
    try:
        return TextLoader(file_path,encoding='utf-8').load()
    except Exception as e:
        logger.error(f"[txt_loader] loading file:{file_path} failed:{str(e)}")