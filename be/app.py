import os
import traceback
import time
from dotenv import load_dotenv
# from function import initialize_db_client, get_model, prompt_generation, send_to_watsonxai, send_to_watsonxai_streaming
from function import get_model, prompt_generation, send_to_ollama
from flask import Flask, request, Response
from flask import jsonify
from pymilvus import Collection
import requests
from pymilvus import connections, DataType

load_dotenv()
MILVUS_HOST = os.environ["MILVUS_HOST"]
MILVUS_PORT = os.environ["MILVUS_PORT"]
MILVUS_USERNAME = os.environ["MILVUS_USERNAME"]
MILVUS_SERVER_NAME = os.environ["MILVUS_SERVER_NAME"]
MILVUS_PASSWORD = os.environ["MILVUS_PASSWORD"]
MILVUS_COLLECTION = os.environ["MILVUS_COLLECTION_NAME"]



app = Flask(__name__)


connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT, server_name=MILVUS_SERVER_NAME)


# model = get_model(model_name='BAAI/bge-large-en-v1.5', max_seq_length=1024)
model_embedder = get_model(model_name='kornwtp/simcse-model-phayathaibert', max_seq_length=768)
@app.route('/live')
def liveness_check():
    return 'OK', 200


# Function to process the request data
def process_data(enrich_question, chat_history, use_history):
    try:
        start = time.time()

        query_encode = [list(i) for i in model_embedder.encode([enrich_question])]
        collection = Collection(MILVUS_COLLECTION)
        collection.load()
        documents = collection.search(data=query_encode, 
                                      anns_field="embeddings", 
                                      param={"metric": "IP", "offset": 0},
                                      output_fields=["text_to_encode", "RegTitle", "SectionNumber","SectionDetail"], 
                                      limit=3)


        full_docs = []
        end_marker = "\n\n--- End of Document ---\n\n"  # End marker for each document
        separator = "\n\n-----\n\n"  # This creates a visual break between sections
        
        reference_return = []
        refs = []
        for i, doc in enumerate(documents[0]):
            doc_details = f'ชื่อระเบียบ:\n{doc.RegTitle}\n'
            doc_details += f'เลขที่ระเบียบ:\n{doc.SectionNumber}\n'
            doc_details += f'รายละเอียด:\n{doc.SectionDetail}\n'
            reference_return.append(f'Refernce: {doc.text_to_encode}\n'.replace('_text', ''))
            # refs.append(f'FAQ: {doc.text_to_encode}\n'.replace('_text', ''))
            full_docs.append(doc_details)

        # Concatenating top 3 references sources
        # concatenated_ref_sources = ", ".join(top_ref_sources)
        prompt = prompt_generation("\n".join(full_docs), enrich_question, chat_history, use_history, model_based="th")

        end = time.time()
        return {
            "prompt": prompt,
            "concatenated_ref_sources": reference_return
        }
    except Exception as e:
        app.logger.error(f"Error in process_data: {e}")
        app.logger.error(traceback.format_exc())
        return None

def fix_encoding(text):
    try:
        # Attempt to decode the text using 'ISO-8859-1' and then re-encode it in 'UTF-8'
        fixed_text = text.encode('ISO-8859-1').decode('UTF-8')
    except UnicodeDecodeError:
        # If there's a decoding error, return the original text
        fixed_text = text
    return fixed_text

# # Function to generate the streaming response
# def generate_stream(prompt, concatenated_ref_sources):
#     print("CONCAT: ", concatenated_ref_sources)
#     try:
#         if concatenated_ref_sources == [""] or concatenated_ref_sources == []:
#             yield "Sorry, I cannot find a relevent source from the FAQ, please ask a question based on the FAQ."
#         else:
#             start = time.time()
#             model_stream = send_to_watsonxai_streaming(current_model_name,
#                                                     prompt,
#                                                     model_params)
#             print ("time to init streaming: ", time.time() - start)
#             for response in model_stream:
#                 print(response)
#                 wordstream = str(response)
#                 if wordstream:
#                     wordstream = fix_encoding(wordstream)
#                     yield wordstream
#             end = time.time()
#             print("Time step 4: ", end - start)
#     except Exception as e:
#         app.logger.error(f"Error in generate_stream: {e}")
#         app.logger.error(traceback.format_exc())
#         yield "Error in stream generation"

def generate_res_json(prompt, concatenated_ref_sources):
    try:
        # response = send_to_watsonxai(current_model_name,
        #                              prompt,
        #                              model_params)
        
        response = send_to_ollama(prompt)
        print('response from llm is')
        print(response)
        if concatenated_ref_sources == ""or concatenated_ref_sources == []:
            results = {"results": "Sorry, I cannot find a relevent source from the FAQ, please ask a question based on the FAQ.", "reference": concatenated_ref_sources}
        else:
            results = {"results": response, "reference": concatenated_ref_sources}
        return results
    except ValueError as e:
        results = {"error": str(e)}

# Function to extract request data
def extract_request_data():
    try:
        request_data = request.json
        if request_data is None:
            raise ValueError("Invalid or missing JSON in request")
        return {
            'enrich_question': request_data.get('query', ''),
            'chat_history': request_data.get('chat_history', ''),
            'use_history': request_data.get('use_history', '')
        }
    except Exception as e:
        app.logger.error(f"Error in extract_request_data: {e}")
        app.logger.error(traceback.format_exc())
        return None

# Function to extract request data
def extract_request_data_stream():
    try:
        request_data = request.json
        if request_data is None:
            raise ValueError("Invalid or missing JSON in request")
        return {
            'prompt': request_data.get('prompt', ''),
            'concatenated_ref_sources': request_data.get('concatenated_ref_sources', '')
        }
    except Exception as e:
        app.logger.error(f"Error in extract_request_data: {e}")
        app.logger.error(traceback.format_exc())
        return None


# Main route
@app.route('/data', methods=['POST'])
def data():
    data = extract_request_data()
    if data is None:
        print(" data is None")
        return jsonify({"error": "Error processing request data"}), 400

    processing_result = process_data(**data)
    print("processing_result is :")
    print(processing_result)
    if processing_result is None:
        print("processing_result is None")
        return jsonify({"error": "Error in data processing"}), 500
    return generate_res_json(processing_result["prompt"], processing_result["concatenated_ref_sources"])

@app.route('/relevent_doc', methods=['POST'])
def get_relevent_doc():
    data = extract_request_data()
    if data is None:
        return jsonify({"error": "Error processing request data"}), 400

    processing_result = process_data(**data)
    if processing_result is None:
        return jsonify({"error": "Error in data processing"}), 500
    
    return {"prompt": processing_result["prompt"], "reference": processing_result["concatenated_ref_sources"]}


# Main route
@app.route('/stream', methods=['POST'])
def stream():
    data = extract_request_data_stream()
    if data is None:
        return jsonify({"error": "Error processing request data"}), 400
    print("extract data:")
    print(data)
    # return Response(generate_stream(**data), content_type='text/event-stream')

    return Response(generate_res_json(**data), content_type='json')

if __name__ == '__main__':
    app.run(debug=True, port=8001, host="0.0.0.0")
