########################################################################################
import os 
from typing import List, Dict, Any, Optional

# vectorstore
import chromadb
from chromadbx import UUIDGenerator
from langchain_chroma import Chroma
from langchain.schema.document import Document
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

# embedding
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain

# prompt
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)

# custom
import inspect
from langchain_core.callbacks import (
    AsyncCallbackManagerForChainRun,
)

# cache, memory
from langchain.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory

########################################################################################

# set cache, memory
cache_instance = InMemoryCache()
set_llm_cache(cache_instance)
# memory = ConversationBufferMemory(input_key='question', output_key='answer', return_messages=True)
memory = ConversationBufferWindowMemory(input_key='question', output_key='answer', k=10) 

# set model
llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model=os.environ.get("EMBDDING_MODEL", "text-embedding-3-small"))

# set vectorstore
collection_name = os.getenv("COLLECTION_NAME")
vectorstore = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=os.getenv("DB_PATH"))
retriever = vectorstore.as_retriever()

########################################################################################

system_prompt ="""당신은 IT Speacialist입니다. 
당신의 이름은 RAG_TUTORIAL BOT 입니다.
당신이 누구인지 물어보는 경우, 친절하게 인사하고 당신의 역할을 말해주세요.
당신은 앞서 응답한 내용과 참고 문서를 기반으로 답해주세요.
앞서 응답한 내용 : {chat_history}
참고 문서 : {summaries}

먼저, 질문에 답하는 데 가장 관련 있는 문서를 찾아 최신순으로 순서대로 정리하세요.

그런 다음 질문에 답하세요. 참고 문서를 활용하여 주요 주제를 선정하고, 각 주제에 맞는 내용을 작성하고 원본 출처를 그대로 출력하세요.
답변에 인용된 내용을 그대로 포함하거나 언급하지 마세요. 답변할 때 “인용문 [1]에 따르면”이라고 하지 마세요. 대신 답변의 각 주제와과 관련된 인용문을 활용하고 원본 출처를 추가하여 참조하세요.

최소 1개, 최대 5개의 주제를 선정하고, 각 주제에 대한 내용을 작성하세요.
답변시 친절하게 인사하고, 각 주제에 마지막에 출처를 "[문서이름](URL)-페이지" 형식으로 필히 작성하세요.

질문은 다음과 같습니다 : {question}"""

messages = [
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template("{question}")
    ]
    
prompt = ChatPromptTemplate.from_messages(messages)
chain_type_kwargs = {"prompt": prompt}

########################################################################################

class CUSTOM_CHAIN(RetrievalQAWithSourcesChain):
    def _filtering_docs(self, docs: List[Document], threshold: float=1.5) -> List[Document]:
        return [ doc for doc, score in docs if score<threshold ]
        
    async def _aget_docs(
        self, inputs: Dict[str, Any], *, run_manager: AsyncCallbackManagerForChainRun
    ) -> List[Document]:
        # 임베딩 구축에 사용된 띄어쓰기 규칙과 동일하게 적용하여 검색할 수 있도록 spacing 적용
        question = inputs[self.question_key]
        category = inputs.get("category", "all")
        
        threshold = inputs.get("THRESHOLD", 1.5)
        
        results: List[Document] = list()    

        if category == "all":
            docs = await self.retriever.vectorstore.asimilarity_search_with_score(question)
            results = self._filtering_docs(docs)
        elif category == "guideline":
            docs = await self.retriever.vectorstore.asimilarity_search_with_score(question, filter={"category":"guideline"})    
            results = self._filtering_docs(docs)
        elif category == "baseline":
            docs = await self.retriever.vectorstore.asimilarity_search_with_score(question, filter={"category":"baseline"})
            results = self._filtering_docs(docs)
        else:
            results = []

        return self._reduce_tokens_below_limit(results)

    async def _acall(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[AsyncCallbackManagerForChainRun] = None,
    ) -> Dict[str, str]:
        _run_manager = run_manager or AsyncCallbackManagerForChainRun.get_noop_manager()
        accepts_run_manager = (
            "run_manager" in inspect.signature(self._aget_docs).parameters
        )

        result: Dict[str, Any] = dict()
        
        if accepts_run_manager:
            docs = await self._aget_docs(inputs, run_manager=_run_manager)
        else:
            docs = await self._aget_docs(inputs)  # type: ignore[call-arg]
    
        answer = await self.combine_documents_chain.arun(
            input_documents=docs, callbacks=_run_manager.get_child(), **inputs
        )
        answer, sources = self._split_sources(answer)

        result[self.answer_key] = answer
        result[self.sources_answer_key] = sources
        if self.return_source_documents:
            result["source_documents"] = docs
        return result

chain = CUSTOM_CHAIN.from_chain_type(
    llm=llm,
    chain_type="stuff",
    memory=memory,
    max_tokens_limit=1000,
    retriever = retriever,
    return_source_documents=False,
    chain_type_kwargs=chain_type_kwargs,
)