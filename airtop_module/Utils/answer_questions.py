import openai
from Utils.constants import OPENAI_API_KEY
from PyPDF2 import PdfReader
import os
import re

openai.api_key = OPENAI_API_KEY
 
def get_response_from_prompt(json_format, resume):
    system_instruction="You are a helpful assistant. Provide the answer as short as possible"

    first_name=resume.get("personal_details").get("name").get("first")
    last_name=resume.get("personal_details").get("name").get("last")

    file_name=f"{first_name}_{last_name}_Resume.pdf"
    pdf_path = os.path.join(os.getcwd(), file_name)
    
    reader = PdfReader(pdf_path)
    text = ''.join(page.extract_text() for page in reader.pages)

    prompt = f"""
    You are an intelligent and precise data extraction assistant.

    You are given a context containing resume information, and a list of input questions. Your goal is to provide a short, relevant response for each question using information from the context or your general world knowledge.

    ### Instructions:

    **Context:**
    {text}
    
    **Input:**
    {json_format}

    1. Each question is provided as a JSON object with "type" and "name" fields.
    2. You must go through **each question** one by one.
    3. Extract the answer for each question using the given **context**.
    4. If an exact answer is **not found** in the context:
      - Use **reliable world knowledge** (e.g., city-to-country, city-to-zipcode mappings) to infer it.
      - For example, if city is “Surat”, infer:
        - State: Gujarat
        - Country: India
        - Zip/Postal Code: Use a known/realistic pincode (e.g., 395007)
    5. For the field `"Address"`:
      - If full address is missing, return any available **sub-parts** like city, state.
      - Format partial address clearly: e.g., `"Surat, Gujarat"` or `"Ahmedabad, Gujarat"` if only those are available.
      - Never return `"Not Found"` for address if any subcomponent is available.

    6. Only return `"Not Found"` if the answer:
      - Is not present in the context,
      - AND cannot be inferred even partially using common knowledge or not mentioned in the instruction.

    7. Your final answer must follow this format strictly:
    ```json
    {
      "output": [
        {
          "type": "text_field",
          "name": "Address",
          "response": "Surat, Gujarat"
        },
        {
          "type": "text_field",
          "name": "Address #2(optional)",
          "response": "Not Found"
        },
        {
          "type": "text_field",
          "name": "City",
          "response": "Surat"
        },
        {
          "type": "text_field",
          "name": "Zip/Postal Code",
          "response": "395007"
        },
        {
          "type": "select_field",
          "name": "Country",
          "response": "India"
        }
      ]
    }

    Strictly include all the input fields in the response as shown in the output

"""

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]
 
    try:
        chat = openai.ChatCompletion.create( 
            model="gpt-3.5-turbo", messages=messages 
        )
 
        # print(completion)

        reply = chat.choices[0].message.content.strip()
        print("Response:\n", reply)
        return reply
 
    except Exception as e:
        print("Error while calling OpenAI:", str(e))
        return None