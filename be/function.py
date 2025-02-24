import os
# from ibm_watson_machine_learning.foundation_models import Model
from dotenv import load_dotenv
from pymilvus import connections,Collection
from sentence_transformers import SentenceTransformer, models
import requests


load_dotenv()
MILVUS_HOST = os.environ["MILVUS_HOST"]
MILVUS_PORT = os.environ["MILVUS_PORT"]
MILVUS_USERNAME = os.environ["MILVUS_USERNAME"]
MILVUS_SERVER_NAME = os.environ["MILVUS_SERVER_NAME"]
MILVUS_PASSWORD = os.environ["MILVUS_PASSWORD"]
MILVUS_COLLECTION = os.environ["MILVUS_COLLECTION_NAME"]
def get_model(model_name='airesearch/wangchanberta-base-att-spm-uncased', max_seq_length=768, condition=True):
    if condition:
        word_embedding_model = models.Transformer(model_name, max_seq_length=max_seq_length)
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension(),pooling_mode='cls') # We use a [CLS] token as representation
        model = SentenceTransformer(modules=[word_embedding_model, pooling_model])
    return model


def prompt_generation(reference, question, chat_history_json, use_history, model_based="test"):
    if model_based == "th":
        if reference == "":
            reference = "[no relevent source]"
    elif model_based == "test":
        prompt = f"""Hello"""
    prompt = f"""<s> [INST]
        คุณเป็นผู้เชี่ยวชาญด้านกฎระเบียบและข้อบังคับด้านความปลอดภัยที่มีประสบการณ์มากว่า 15 ปี ในการให้คำแนะนำและตอบคำถามเกี่ยวกับข้อบังคับด้านความปลอดภัยสำหรับพนักงานและผู้บริหาร คุณมีความสามารถในการทำให้ข้อมูลที่ซับซ้อนเข้าใจง่ายและนำไปใช้ได้จริง

        หน้าที่ของคุณคือการตอบคำถามที่เกี่ยวข้องกับกฎระเบียบด้านความปลอดภัย คุณจะได้รับข้อมูลเกี่ยวกับชื่อระเบียบ, เลขที่ระเบียบ, และรายละเอียดของระเบียบ จากนั้นคุณจะต้องตอบคำถามที่เกี่ยวข้องตามข้อมูลที่ให้มา

        ข้อมูลที่คุณจะได้รับมีดังนี้ -
        ชื่อระเบียบ: __
        เลขที่ระเบียบ: __
        รายละเอียดของระเบียบ: __

        คำถาม: {question}
        '''
        Reference: {reference}
        QUESTION: {question}
        '''
        - ตอบเป็นภาษาไทยครับ
        - หลีกเลี่ยงบรรทัดใหม่ให้มากที่สุด
        - ตอบแบบสั้นและกระชับ
        - หากคำตอบเป็นขั้นตอนการดำเนินการ กรุณาเขียนคำตอบเป็นข้อๆ แบบ bulleted answer
        - กรุณาเขียนให้เป็นภาษาเดียวกัน อย่าใช้ภาษาผสมเช่นในตัวอย่าง 
        'หมาYYY' ควรเป็น 'หมาย' 
        'ช่วยเหลpler' ควรเป็น 'ช่วยเหลือ', 
        "ขอแsorry" ควรเป็น 'ขอโทษ'
        "อัพเดตข้อมลัพทัTOAUTOMATICALLY" ควรเป็น "อัพเดตข้อมูลอัตโนมัติ"
        - ห้ามใช้ข้อมูลใดๆ นอกเหนือ "references" ที่ให้ไว้</s> 

        [INST] QUESTION: {question} [\\INST] ANSWER: """

    return prompt

OLLAMA_URL = os.environ["OLLAMA_URL"]
OLLAMA_PORT = os.environ["OLLAMA_PORT"]
OLLAMA_MODEL = os.environ["OLLAMA_MODEL"]
def send_to_ollama(prompt):
    # url="http://host.docker.internal:11434/v1/chat/completions"  # Replace 'ip' with your deployed IP address
    # url="http://{}:{}/v1/chat/completions".format(OLLAMA_URL,OLLAMA_PORT)  # Replace 'ip' with your deployed IP address
    url = "http://ollama:11434/v1/chat/completions"  # Update port to 11435

    data={
        "model": "llama3.2",
        "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "{}".format(prompt)
        }
        ],
        "temperature":0,
        "stream":False
    }
    response=requests.post(url=url,json=data).json()
    print(response)
    return response
