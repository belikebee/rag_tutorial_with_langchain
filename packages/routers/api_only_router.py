from fastapi import APIRouter

from packages.config import DataInput, ChatOutput
from packages.config import ProjectConfig


# Project config 설정
project_config = ProjectConfig('api_only')

api_only = APIRouter(prefix='/rag')

@api_only.get('/api', tags=['api_only'])
async def api():
    return {'msg' : 'Here is NFM'}

@api_only.post('/api_chat', tags=['api_only'], response_model=ChatOutput)
async def chat(question, history=None, threshold=1.5, prompt=None):
    
    user_id = data_request.user_id
    item_id = data_request.movie_id
    gender = data_request.gender
    age = data_request.age
    occupation = data_request.occupation
    genre = data_request.genre
    predict = model(torch.tensor( [[user_id, item_id]] ), torch.tensor( [[gender, age, occupation]] ), torch.tensor( [[genre]] ) )
    prob, prediction = predict, int(( predict > project_config.threshold ).float() * 1) 
    return {'prob' : prob, 'prediction' : prediction}