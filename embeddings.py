import os
from dotenv import load_dotenv
# load config
load_dotenv("embeddings_env")

# ChromaDB config
DB_PATH = os.getenv("DB_PATH", "chromadb")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "tutorial")

# Model config
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
OVERLAP_SIZE = int(os.getenv("OVERLAP_SIZE", "1000"))

from langchain.schema.document import Document
from typing import Dict, List

from data.document_info import load_document_dict

from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)

'''
TEST
'''

import re
from tqdm import tqdm 

# vectorstore
import chromadb

from chromadbx import UUIDGenerator
from langchain_chroma import Chroma
from langchain.schema.document import Document
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


# Loader, Embedding
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DataFrameLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(collection_name=COLLECTION_NAME, embedding_function=embeddings, persist_directory=DB_PATH)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    "-p", "--pre", 
    dest="preprocessing", 
    help="embedding 모드 선택 시 전처리된 문서 사용 여부",
    action="store_true")


def set_document_content(document:List[Document], document_dict:Dict[str, str|int]) -> List[Document]:
    # 앞장 정리
    while True:
        if document[0].metadata.get("page") < document_dict.get('start_page',0):
            document.pop(0)
        else:
            break
    # 뒷장 정리
    while True:
        if document[-1].metadata.get("page") > document_dict.get('end_page', 99999):
            document.pop(-1)
        else:
            break
    
    print(f"### {document_dict['document_name']} 임베딩 시작")
    for idx, doc in tqdm(enumerate(document), total=len(document)):
        page = idx+1
        # 불필요 문자열 삭제
        for pattern in document_dict["custom_patterns"]:
            doc.page_content = re.sub(pattern, "", doc.page_content)

        # 메타데이터 설정
        # 문서 출처
        doc.metadata['source'] = document_dict['source'].format(page=page)
        # 문서 카테고리
        doc.metadata['category'] = document_dict['category']
        # 임베딩 문서 이름
        doc.metadata['filename'] = document_dict['document_name']
        # 문서 등록일
        doc.metadata['reg_date'] = document_dict['reg_date']
        # 문서 수정일자
        doc.metadata['edit_date'] = document_dict['edit_date']    
        # 문서 원본명
        doc.metadata['origin'] = document_dict['origin']    
    
    return document
    
def make_document_from_pdf(document_dict:Dict[str, str|int]) -> List[Document]:
    document_path = os.path.join(document_dict['documents_path'], document_dict['document_name'])
    loader = PyPDFLoader(document_path)
    document = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=OVERLAP_SIZE)
    document = text_splitter.split_documents(document)
    document = set_document_content(document, document_dict)
    
    return document

def make_document_from_xlsx(document_dict:Dict[str, str|int]) -> List[Document]:
    document_path = os.path.join(document_dict['documents_path'], document_dict['document_name'])            
    document_df = pd.read_excel(document_path, index_col=0)
    loader = DataFrameLoader(document_df[~document_df['page_content'].isna()], "page_content")
    document = loader.load()            
    document = set_document_content(document, document_dict)
    
    return document   

def embedding_from_preprocessed_document(documents_list:List[Dict]) -> None:
    for document_dict in documents_list:
        document = make_document_from_xlsx(document_dict)        
        vectorstore.add_documents(document)
        
    return None
    
def embedding_from_document(documents_list:List[Dict]) -> None:
    for document_dict in documents_list:
        document = make_docuemnt_from_pdf(document_dict)
        vectorstore.add_documents(document)
    return None
    
if __name__ == "__main__":    
    args = parser.parse_args()
    print("#### 임베딩 시작")
    
    preprocessing = args.preprocessing
    documents_list = load_document_dict(preprocessing)
    print("### 문서 정보 로드 완료")
    try:
        if preprocessing:
            print("### 전처리 문서 임베딩 시작")
            embedding_from_preprocessed_document(documents_list)
            
        elif preprocessing is False:
            print("### 원본 문서 임베딩 시작")
            embedding_from_document(documents_list)
        
        print("#### 임베딩 종료")
            
    except Exception as e:
            print(f"###'{e}' 해당 이유로 임베딩 실패")
    