import os
import time
import base64
import requests
from glob import lob
from tqdm import tqdm
from pdf2image import convert_from_path

from dotenv import load_dotenv
# load config
load_dotenv("embedding_env")

headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}"
}
error_page = list()
for pdf in glob("data/documents/*.pdf"):
    pages = convert_from_path(pdf)

    docs_list = list()
    for idx, doc in tqdm(enumerate(pages), total=len(pages)):
        image_path = f'pages/file_{pdf.splot("/")[-1][:-4]}_{idx}.jpg'
        doc.save(image_path, "JPEG")
        
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
       
        flag = True
        cnt=0
        while True:
            try:
                cnt+=1
                payload = {
                    "model": "gpt-4o-2024-08-06",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "위 이미지에 대한 내용을 출력하고, markdown 형식으로 출력하세요. (표 내용을 포함)"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": 8192
                }
    
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                response_data = response.json()
                content = response_data['choices'][0]['message']['content']
            except Exception as e:
                print(e)
                if cnt > 2:
                    flag = False
                    
                cnt+=1
                time.sleep(3)
            if flag:
                break
                    
        if flag:
            docs_list.append(Document(page_content=content, metadata=dict(
                soruce=pdf,
                page=idx
            )))
        else:
            error_page.append(page)
            
    pre_docs_xlsx = pd.DataFrame(columns=["page_content", "source", "page"])
    for doc in docs_list:
        doc_content = dict(page_content=pre_doc.page_content)
        for k, v in doc.metadata.items():
            doc_content[k] = [v]
        pre_docs_xlsx = pd.concat([pre_docs_xlsx, pd.DataFrame(xx)], ignore_index=True)
    pre_docs_xlsx.to_excel(f"pre_{pdf.split("/")[-1][:-4]}.xlsx")
                        