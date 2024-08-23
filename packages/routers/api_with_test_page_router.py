from fastapi import APIRouter

import gradio as gr

from packages.config import DataInput, ChatOutput
from packages.config import ProjectConfig

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from model.rag import chain
from model.rag import system_prompt as PROMPT 

CATEGORY = ["all", "guideline", "baseline" ]

# Project config 설정
project_config = ProjectConfig('api_with_test_page')

api_with_test_page = APIRouter(prefix='/rag')

@api_with_test_page.get('/api/', tags=['api_only'])
async def api_only(question, category="all", threshold=1.5):
    if category not in CATEGORY:
        return f"{CATEGORY}, 카테고리를 확인해주세요."

    res = await chain.ainvoke({"question":question, "category":category, "threshold":threshold})
    print(res)
    
    return {"answer":res['answer'], "chat_history":res['chat_history']}

@api_with_test_page.post('/chat/', tags=['api_with_test_page'])
async def chat(question, history=[], category="all", threshold=1.5):
    if category not in CATEGORY:
        return f"{CATEGORY}, 카테고리를 확인해주세요."

    history_langchain_format = []
    history_langchain_format.append(SystemMessage(content=PROMPT))
    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))
    history_langchain_format.append(HumanMessage(content=question))
    
    res = await chain.ainvoke({"question":question, "category":category, "chat_history":history_langchain_format, "threshold":threshold})
    return res['answer']

testpage = gr.ChatInterface(
        fn=chat,
        textbox=gr.Textbox(placeholder="검색어를 입력해주세요.", container=False, scale=5),
        chatbot=gr.Chatbot(height=670),
        title="RAG 튜토리얼 테스트페이지",
        retry_btn="다시보내기 ↩",
        undo_btn="이전챗 삭제 ❌",
        clear_btn="전챗 삭제 💫",
        additional_inputs=[
            gr.Dropdown(
            CATEGORY, value="all", label="Category", info="검색을 원하시는 카테고리를 선택하세요(guideline : 마이데이터 기술 가이드라인, baseline : 마이데이터 표준 API 규격)"
            ),
            gr.Slider(0, 2.0, value=1.5, step=0.01, label="threshold"),
            # 추후 업데이트
            # gr.Textbox(placeholder="{question}, {summaries}, {chat_history}를 포함한 프롬프트를 입력해주세요.", container=False, scale=5, label="prompt"),            
        ]
)