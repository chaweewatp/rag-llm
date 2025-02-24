import os
from dotenv import load_dotenv
import streamlit as st
import requests
import time

load_dotenv()
BE_ENDPOINT = os.environ["BE_ENDPOINT"]
BE_ENDPOINT_RELEVENT = os.environ["BE_ENDPOINT_RELEVENT"]


def get_response(data, formatted_chat_history, use_history,
                 endpoint='http://127.0.0.1:8001/data'):
    payload = {'query': data, 'chat_history': formatted_chat_history,
               'use_history': use_history}
    r = requests.post(endpoint, json=payload)
    response = r.json()
    print("response is")
    print(response)
    ref_list = response['reference']
    return response['results']['choices'][0]['message']['content'], ref_list

def get_relevent_docs(data, formatted_chat_history, use_history,
                 endpoint='http://127.0.0.1:8001/relevent_doc'):
    payload = {'query': data, 'chat_history': formatted_chat_history,
               'use_history': use_history}
    r = requests.post(endpoint, json=payload)
    response = r.json()
    print("get_relevent_doc is ")
    print(response)
    ref_list = response['reference']
    return response['prompt'], ref_list

def convert_to_markdown(faq_list):
    markdown_text = ""
    for faq in faq_list:
        parts = faq.split('\n')
        question = parts[0].replace('FAQ: Question: ', '')
        answer = '\n'.join(parts[1:]).replace('Answer:', '')
        markdown_text += f"### {question}\n{answer}\n\n"
    return markdown_text


st.title("PEA chat assistant สอบถามเรื่อง พ.ร.บ. ความปลอดภัย - V.0")

# Toggle for enabling/disabling chat history
if "record_chat_history" not in st.session_state:
    st.session_state.record_chat_history = False  # Default is True

st.markdown("**Note:** Model may give inaccurate response", unsafe_allow_html=True)
# Update the session state based on the user's choice
st.session_state.record_chat_history = False

# Initialize the session state for storing messages if it does not exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def convert_to_dict(input_str):
    # Initialize a dictionary to store the results
    data_dict = {"results": "", "reference": ""}

    # Removing curly braces and splitting the string by commas
    entries = input_str.strip("{}").split(", '")

    for entry in entries:
        # Splitting each entry by the first colon to separate key and value
        key, value = entry.split("': ", 1)

        # Removing any leading or trailing single quotes in key and value
        key = key.strip("'")
        value = value.strip("'")

        # Handling escaped single quotes in value
        value = value.replace("\\'", "'")

        # Assigning the processed value to the corresponding key in the dictionary
        if key in data_dict:
            data_dict[key] = value

    return data_dict

# User input
question = st.chat_input("How can I help you today?")
if question:
    # Add user message to chat history and display immediately
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
        sources_place_holder = st.empty()
    print(f"FE init history")
    # Write chat history to file
    start = time.time()

    
    try:
        with st.spinner('loading relevent sources if any...'):
            results, concatenated_ref_sources = get_response(question, {},
                                            st.session_state.record_chat_history,
                                            BE_ENDPOINT)
        print(f"FE before r ")
        with st.chat_message("assistant"):
            st.markdown(results)
            # model_response_placeholder = st.empty()
            # full_response = ""
            # print(f" FE raw text {r}")
            # for chunk in r.iter_content(chunk_size=1024):
            #     print(chunk)
            #     if chunk:
            #         response = chunk.decode('utf-8')
            #         partial_message = response
            #         full_response += partial_message
            #         with model_response_placeholder.container():
            #             st.markdown(full_response)

        # Get response from the assistant, using chat history based on the toggle state
        # end = time.time()


        st.session_state.messages.append({"role": "assistant", "content": results})

        with sources_place_holder.container():
            if concatenated_ref_sources != "" and concatenated_ref_sources != []:
                st.markdown("<span style='color: blue;'> Relevant source founded </span>", unsafe_allow_html=True)
                with st.expander("Relevant Documents", expanded=False):
                    st.markdown(convert_to_markdown(concatenated_ref_sources))
            else:
                st.markdown("<span style='color: red;'>No relevant source founded..</span>", unsafe_allow_html=True)

    except Exception as e:
        with st.chat_message("assistant"):
            full_response = "Thank you for using our service. The system is in **cold start state currently**. Your question has **triggered the backend engine to start**. Please wait from **1-5 minute** and try asking the question again. If after waiting your still recieve the same message please contact our support team."
            st.markdown(full_response, unsafe_allow_html=True)
            print(f"An error occurred: {e}")
