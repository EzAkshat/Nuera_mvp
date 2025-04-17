import google.generativeai as genai
import json
import re

def get_llm_response(command, api_key, system_prompt):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"{system_prompt}\n\nUser command: {command}\n\nRespond in JSON format only, with no additional text outside the JSON object."
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"},
            stream=False
        )
        response_text = response.text
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_str = match.group(0)
            llm_response = json.loads(json_str)
            return llm_response
        else:
            raise ValueError("No JSON object found in response")
    except (json.JSONDecodeError, ValueError) as e:
        error_response = {"type": "respond", "response": "Oops, my brain froze! Try again?"}
        return error_response
    except Exception as e:
        error_response = {"type": "respond", "response": "Oops, my brain froze! Try again?"}
        return error_response