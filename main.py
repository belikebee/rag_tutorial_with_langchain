import os
from dotenv import load_dotenv
# load config
load_dotenv("api_env")
   
import argparse
import os

from fastapi import FastAPI
from packages import api_only, api_with_test_page, testpage
from packages import FastAPIRunner
import gradio as gr

# from packages.api_with_test_page import testpage

app = FastAPI()
app.include_router(api_with_test_page)
app = gr.mount_gradio_app(app, testpage, path="/testpage")


@app.get('/')
def read_results():
    return {'msg' : 'test'}
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument(
    #             "-m", "--mode", 
    #             dest="mode", 
    #             default="api_only", 
    #             choices=["api_only", "api_with_test_page"], 
    #             help="api_only / api_with_test_page 모드 중 선택하세요", 
    #             action="store",
    #             required=True
    # )
    parser.add_argument('--host', default="127.0.0.1")
    parser.add_argument('--port', default="8888")
    parser.add_argument('--api_name', default="rag_tutorial:app")
    args = parser.parse_args()

        
    api = FastAPIRunner(args)
    api.run()
    